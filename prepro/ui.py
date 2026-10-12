"""Panels, lists and menus of the MBDyn model editor (Node Editor, sidebar tab "MBDyn")."""

from __future__ import annotations

import hashlib

import bpy

from . import fields, library
from .ops import active_tree
from .tree import NODE_TYPE, TREE_TYPE


def draw_field(layout, node, field) -> None:
    binding = node.binding(field.name)
    title = field.name.replace("_", " ").capitalize()
    widget = field.widget
    if field.raw and widget != "json":
        row = layout.row(align=True)
        row.prop(field, "text", text=title)
        row.prop(field, "raw", text="", icon="SCRIPT")
        return
    if widget == "label":
        layout.prop(field, "integer", text="Label")
    elif widget in ("expr", "vector", "text", "json"):
        row = layout.row(align=True)
        row.prop(field, "text", text=title)
        if binding.get("auto"):
            row.prop(field, "raw", text="", icon="SCRIPT")
    elif widget == "flag":
        layout.prop(field, "flag", text=title)
    elif widget == "choice":
        layout.prop(field, "choice", text=title)
    elif widget == "position":
        box = layout.box()
        row = box.row(align=True)
        row.prop(field, "pos_type", text=title)
        if binding.get("auto"):
            row.prop(field, "raw", text="", icon="SCRIPT")
        kind = field.pos_type
        if kind in fields.POSITION_LENGTHS:
            box.prop(field, "text", text="Values")
        if kind == "axes" or binding.get("form") == "orientation_axes" and kind == "axes":
            row = box.row(align=True)
            row.prop(field, "first_axis", text="")
            row.prop(field, "first_vector", text="")
            row = box.row(align=True)
            row.prop(field, "second_axis", text="")
            row.prop(field, "second_vector", text="")
        if binding.get("auto") and kind in fields.POSITION_TYPES:
            box.prop(field, "reference")


def draw_block(layout, node) -> None:
    """The form of a block: its label, then its properties in the class's order."""
    spec = library.module("model").BLOCKS.get(node.kind)
    if spec is None:
        layout.label(text=f"Unknown block kind {node.kind}", icon="ERROR")
        return
    layout.label(text=f"{spec.title} — {spec.class_name}")
    if node.error:
        box = layout.box()
        box.alert = True
        box.label(text=node.error, icon="ERROR")
    column = layout.column()
    for field in node.fields:
        draw_field(column, node, field)


class _EditorPanel:
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "MBDyn"

    @classmethod
    def poll(cls, context):
        return getattr(context.space_data, "tree_type", "") == TREE_TYPE


class BLENDYN_PT_model_editor(_EditorPanel, bpy.types.Panel):
    bl_label = "MBDyn model"

    def draw(self, context):
        layout = self.layout
        ok, message = library.status()
        row = layout.row()
        row.alert = not ok
        row.label(text=message, icon="CHECKMARK" if ok else "ERROR")
        row = layout.row(align=True)
        row.operator("blendyn.model_new", icon="ADD", text="New")
        row.operator("blendyn.model_open", icon="FILE_FOLDER", text="Open")
        row.operator("blendyn.model_save", icon="FILE_TICK", text="Save")
        tree = active_tree(context)
        if tree is None:
            return
        layout.operator("blendyn.model_search_block", icon="VIEWZOOM", text="Add block…")
        layout.prop(tree.mbdyn_model, "output_path")
        row = layout.row(align=True)
        row.operator("blendyn.model_validate", icon="CHECKMARK")
        row.operator("blendyn.model_export", icon="EXPORT", text="Export")
        row.operator("blendyn.model_run", icon="PLAY", text="Run")


class BLENDYN_UL_model_parameters(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "name", text="", emboss=False)
        row.prop(item, "var_type", text="")
        row.prop(item, "value", text="")


class BLENDYN_PT_model_parameters(_EditorPanel, bpy.types.Panel):
    bl_label = "Parameters"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        tree = active_tree(context)
        if tree is None:
            return
        row = self.layout.row()
        row.template_list("BLENDYN_UL_model_parameters", "", tree.mbdyn_model, "parameters",
                          tree.mbdyn_model, "parameter_index", rows=3)
        column = row.column(align=True)
        column.operator("blendyn.model_parameter_add", icon="ADD", text="")
        column.operator("blendyn.model_parameter_remove", icon="REMOVE", text="")


class BLENDYN_PT_model_block(_EditorPanel, bpy.types.Panel):
    bl_label = "Block"

    @classmethod
    def poll(cls, context):
        tree = active_tree(context)
        node = tree.nodes.active if tree else None
        return node is not None and node.bl_idname == NODE_TYPE and bool(node.kind)

    def draw(self, context):
        draw_block(self.layout, active_tree(context).nodes.active)


# The Add menu follows the catalog's palette categories; its submenus are
# classes, made when the builder loads.
_menu_classes: list = []


def _menu_idname(path) -> str:
    return "BLENDYN_MT_model_add_" + hashlib.md5("/".join(path).encode()).hexdigest()[:12]


class BLENDYN_MT_model_add(bpy.types.Menu):
    bl_idname = "BLENDYN_MT_model_add"
    bl_label = "MBDyn"

    def draw(self, context):
        layout = self.layout
        layout.operator("blendyn.model_search_block", icon="VIEWZOOM", text="Search…")
        if not _menu_classes:
            layout.label(text="Set the MBDyn source checkout in the Blendyn preferences")
            return
        _draw_menu(layout, ())


_menu_tree: dict = {}


def _draw_menu(layout, path) -> None:
    submenus, kinds = _menu_tree.get(path, ([], []))
    for child in submenus:
        layout.menu(_menu_idname(child), text=child[-1])
    if submenus and kinds:
        layout.separator()
    for kind, title in kinds:
        layout.operator("blendyn.model_add_block", text=title).kind = kind


def register_menus() -> None:
    """Make the Add submenus of the loaded catalog (again, if the checkout changed)."""
    unregister_menus()
    try:
        blocks = library.module("model").BLOCKS
    except RuntimeError:
        return
    for kind, spec in blocks.items():
        if kind == "component":
            continue
        path = tuple(spec.palette_category or ("Other",))
        for depth in range(len(path)):
            parent, child = path[:depth], path[:depth + 1]
            submenus = _menu_tree.setdefault(parent, ([], []))[0]
            if child not in submenus:
                submenus.append(child)
        _menu_tree.setdefault(path, ([], []))[1].append((kind, spec.title))
    def drawer(path):
        def draw(self, context):
            _draw_menu(self.layout, path)
        return draw

    for path in _menu_tree:
        if not path:
            continue
        cls = type(_menu_idname(path), (bpy.types.Menu,), {
            "bl_idname": _menu_idname(path), "bl_label": path[-1], "draw": drawer(path)})
        bpy.utils.register_class(cls)
        _menu_classes.append(cls)


def unregister_menus() -> None:
    for cls in _menu_classes:
        bpy.utils.unregister_class(cls)
    _menu_classes.clear()
    _menu_tree.clear()


def draw_add_menu(self, context):
    if getattr(context.space_data, "tree_type", "") == TREE_TYPE:
        self.layout.menu("BLENDYN_MT_model_add")


classes = (BLENDYN_PT_model_editor, BLENDYN_UL_model_parameters, BLENDYN_PT_model_parameters,
           BLENDYN_PT_model_block, BLENDYN_MT_model_add)
