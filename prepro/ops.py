"""Operators of the MBDyn model editor."""

from __future__ import annotations

import os
from pathlib import Path

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

from . import document, library
from .tree import NODE_TYPE, TREE_TYPE

ERROR_COLOR = (0.55, 0.12, 0.12)


def active_tree(context):
    space = context.space_data
    tree = getattr(space, "edit_tree", None)
    return tree if tree is not None and tree.bl_idname == TREE_TYPE else None


class _TreeOperator:
    @classmethod
    def poll(cls, context):
        return active_tree(context) is not None


def mark_error(tree, exc) -> None:
    """Show an error on the node of the block it names."""
    block_id = getattr(exc, "block_id", None)
    for node in document.block_nodes(tree):
        if block_id and node.block_id == block_id:
            node.error = str(exc).splitlines()[0][:200]
            node.use_custom_color, node.color = True, ERROR_COLOR


def clear_errors(tree) -> None:
    for node in document.block_nodes(tree):
        if node.error:
            node.error = ""
            node.use_custom_color = False


def compile_tree(tree) -> str:
    """The MBDyn input of the tree; errors are marked on their nodes and re-raised."""
    clear_errors(tree)
    try:
        return library.module("compiler").compile_document(document.tree_to_document(tree))
    except ValueError as exc:  # ModelError and the document's own checks
        mark_error(tree, exc)
        raise


class BLENDYN_OT_model_new(bpy.types.Operator):
    """Create an MBDyn model and show it in this node editor"""
    bl_idname = "blendyn.model_new"
    bl_label = "New MBDyn Model"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tree = bpy.data.node_groups.new("MBDyn Model", TREE_TYPE)
        tree.use_fake_user = True  # kept in the .blend file even when no editor shows it
        if context.space_data and context.space_data.type == "NODE_EDITOR":
            context.space_data.tree_type = TREE_TYPE
            context.space_data.node_tree = tree
        return {"FINISHED"}


class BLENDYN_OT_model_add_block(_TreeOperator, bpy.types.Operator):
    """Add a block of the MBDyn model"""
    bl_idname = "blendyn.model_add_block"
    bl_label = "Add MBDyn Block"
    bl_options = {"REGISTER", "UNDO"}

    kind: StringProperty()

    def execute(self, context):
        tree = active_tree(context)
        for node in tree.nodes:
            node.select = False
        node = tree.nodes.new(NODE_TYPE)
        try:
            node.setup(self.kind)
        except (RuntimeError, KeyError) as exc:
            tree.nodes.remove(node)
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        node.location = getattr(context.space_data, "cursor_location", (0, 0))
        node.select = True
        tree.nodes.active = node
        return {"FINISHED"}

    def invoke(self, context, event):
        result = self.execute(context)
        if result == {"FINISHED"}:
            bpy.ops.node.translate_attach_remove_on_cancel("INVOKE_DEFAULT")
        return result


_KIND_ITEMS: list = []


def reset_caches() -> None:
    _KIND_ITEMS.clear()


def _kind_items(self, context):
    if not _KIND_ITEMS:
        try:
            blocks = library.module("model").BLOCKS
        except RuntimeError:
            return [("", "Set the MBDyn source checkout in the preferences", "")]
        _KIND_ITEMS.extend(
            (kind, f"{spec.title}  ({' › '.join(spec.palette_category)})", spec.class_name)
            for kind, spec in blocks.items() if kind != "component")
    return _KIND_ITEMS


class BLENDYN_OT_model_search_block(_TreeOperator, bpy.types.Operator):
    """Search the blocks of the MBDyn model by name, class or menu"""
    bl_idname = "blendyn.model_search_block"
    bl_label = "Search MBDyn Block"
    bl_property = "kind"
    bl_options = {"REGISTER", "UNDO"}

    kind: EnumProperty(items=_kind_items)

    def execute(self, context):
        return bpy.ops.blendyn.model_add_block("INVOKE_DEFAULT", kind=self.kind)

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}


class BLENDYN_OT_model_open(ImportHelper, bpy.types.Operator):
    """Open a model builder diagram (JSON) as a new MBDyn model"""
    bl_idname = "blendyn.model_open"
    bl_label = "Open Diagram"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context):
        try:
            model = library.module("model")
            source = model.Document.load(self.filepath)
            tree = bpy.data.node_groups.new(Path(self.filepath).stem, TREE_TYPE)
            tree.use_fake_user = True
            document.document_to_tree(source, tree)
        except (RuntimeError, OSError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        tree.mbdyn_model.document_path = self.filepath
        tree.mbdyn_model.output_path = str(Path(self.filepath).with_suffix(".mbd"))
        if context.space_data and context.space_data.type == "NODE_EDITOR":
            context.space_data.tree_type = TREE_TYPE
            context.space_data.node_tree = tree
        return {"FINISHED"}


class BLENDYN_OT_model_save(_TreeOperator, ExportHelper, bpy.types.Operator):
    """Save the MBDyn model as a model builder diagram (JSON)"""
    bl_idname = "blendyn.model_save"
    bl_label = "Save Diagram"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        path = active_tree(context).mbdyn_model.document_path
        if path:
            self.filepath = bpy.path.abspath(path)
        return super().invoke(context, event)

    def execute(self, context):
        tree = active_tree(context)
        try:
            document.tree_to_document(tree).save(self.filepath)
        except (RuntimeError, OSError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        tree.mbdyn_model.document_path = self.filepath
        return {"FINISHED"}


class BLENDYN_OT_model_validate(_TreeOperator, bpy.types.Operator):
    """Check the model and write its MBDyn input to a text, marking the blocks in error"""
    bl_idname = "blendyn.model_validate"
    bl_label = "Validate"

    def execute(self, context):
        tree = active_tree(context)
        try:
            source = compile_tree(tree)
        except (RuntimeError, ValueError) as exc:
            self.report({"ERROR"}, str(exc).splitlines()[0])
            return {"CANCELLED"}
        name = f"{tree.name}.mbd"
        text = bpy.data.texts.get(name) or bpy.data.texts.new(name)
        text.from_string(source)
        self.report({"INFO"}, f"The model is valid; its input is in the text {name}")
        return {"FINISHED"}


def _write(tree, path) -> str:
    source = compile_tree(tree)
    path = bpy.path.abspath(path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as stream:
        stream.write(source)
    return path


class BLENDYN_OT_model_export(_TreeOperator, bpy.types.Operator):
    """Write the MBDyn input file of the model"""
    bl_idname = "blendyn.model_export"
    bl_label = "Export MBDyn Input"

    def execute(self, context):
        tree = active_tree(context)
        if not tree.mbdyn_model.output_path:
            self.report({"ERROR"}, "Choose where to write the MBDyn input")
            return {"CANCELLED"}
        try:
            path = _write(tree, tree.mbdyn_model.output_path)
        except (RuntimeError, OSError, ValueError) as exc:
            self.report({"ERROR"}, str(exc).splitlines()[0])
            return {"CANCELLED"}
        self.report({"INFO"}, f"Wrote {path}")
        return {"FINISHED"}


class BLENDYN_OT_model_run(_TreeOperator, bpy.types.Operator):
    """Write the MBDyn input of the model and run MBDyn on it, as Run simulation does"""
    bl_idname = "blendyn.model_run"
    bl_label = "Run MBDyn"

    def execute(self, context):
        tree = active_tree(context)
        if not tree.mbdyn_model.output_path:
            self.report({"ERROR"}, "Choose where to write the MBDyn input")
            return {"CANCELLED"}
        try:
            path = _write(tree, tree.mbdyn_model.output_path)
        except (RuntimeError, OSError, ValueError) as exc:
            self.report({"ERROR"}, str(exc).splitlines()[0])
            return {"CANCELLED"}
        mbs = context.scene.mbdyn
        mbs.input_path = path
        mbs.file_path = os.path.dirname(path)
        mbs.file_basename = Path(path).stem
        return bpy.ops.blendyn.run_mbdyn_simulation("INVOKE_DEFAULT")


class BLENDYN_OT_model_parameter_add(_TreeOperator, bpy.types.Operator):
    """Add an MBDyn parameter"""
    bl_idname = "blendyn.model_parameter_add"
    bl_label = "Add Parameter"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = active_tree(context).mbdyn_model
        item = settings.parameters.add()
        names = {parameter.name for parameter in settings.parameters}
        index = len(settings.parameters)
        while f"P{index}" in names:
            index += 1
        item.name, item.var_type, item.value = f"P{index}", "const real", "1.0"
        settings.parameter_index = len(settings.parameters) - 1
        return {"FINISHED"}


class BLENDYN_OT_model_parameter_remove(_TreeOperator, bpy.types.Operator):
    """Remove the selected MBDyn parameter"""
    bl_idname = "blendyn.model_parameter_remove"
    bl_label = "Remove Parameter"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = active_tree(context).mbdyn_model
        if 0 <= settings.parameter_index < len(settings.parameters):
            settings.parameters.remove(settings.parameter_index)
            settings.parameter_index = max(0, settings.parameter_index - 1)
        return {"FINISHED"}


classes = (BLENDYN_OT_model_new, BLENDYN_OT_model_add_block, BLENDYN_OT_model_search_block,
           BLENDYN_OT_model_open, BLENDYN_OT_model_save, BLENDYN_OT_model_validate,
           BLENDYN_OT_model_export, BLENDYN_OT_model_run, BLENDYN_OT_model_parameter_add,
           BLENDYN_OT_model_parameter_remove)
