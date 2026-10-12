"""The MBDyn model node tree: blocks of the model builder catalog as Blender nodes.

One generic node class, `BLENDYN_N_model_block`, stands for every block
kind: its `kind` names the catalog entry, from which its sockets and
property fields are made. Ports are sockets typed by what they carry
(structural node, frame, scalar drive, ...), and each property is a field
whose slots one widget edits (see `fields`).
"""

from __future__ import annotations

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, IntProperty,
                       PointerProperty, StringProperty)

from . import fields, library

TREE_TYPE = "BlendynModelTree"
NODE_TYPE = "BlendynModelBlock"

# Port types of the catalog, with the colour of their sockets.
PORT_COLORS = {
    "node": (0.19, 0.42, 0.66), "displacement_node": (0.35, 0.58, 0.82),
    "dummy_node": (0.25, 0.50, 0.72), "abstract_node": (0.55, 0.55, 0.20),
    "electric_node": (0.85, 0.75, 0.15), "hydraulic_node": (0.15, 0.65, 0.75),
    "thermal_node": (0.85, 0.35, 0.20), "parameter_node": (0.60, 0.60, 0.60),
    "frame": (0.57, 0.45, 0.19), "scalar_drive": (0.35, 0.70, 0.35),
    "vector_drive": (0.20, 0.55, 0.30), "const_law": (0.70, 0.35, 0.60),
    "scalar_function": (0.50, 0.75, 0.50), "fluid": (0.30, 0.45, 0.80),
    "c81_data": (0.75, 0.55, 0.35), "element": (0.47, 0.32, 0.55),
    "file_driver": (0.45, 0.45, 0.45),
}


def reset_caches() -> None:
    """Forget what came from the previous builder, after the checkout changed."""
    _ITEMS_CACHE.clear()


def socket_idname(port_type: str) -> str:
    return "BlendynModelSocket_" + (port_type if port_type in PORT_COLORS else "any")


def _socket_class(port_type: str, color) -> type:
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (*color, 1.0)

    return type(f"BLENDYN_NS_model_{port_type}", (bpy.types.NodeSocket,), {
        "bl_idname": socket_idname(port_type), "bl_label": port_type.replace("_", " "),
        "port_type": port_type, "draw": draw, "draw_color": draw_color,
        "draw_color_simple": classmethod(lambda cls: (*color, 1.0))})


SOCKET_CLASSES = [_socket_class(port, color) for port, color in PORT_COLORS.items()] + [
    _socket_class("any", (0.8, 0.8, 0.8))]


def _block_spec(kind):
    try:
        return library.module("model").BLOCKS.get(kind)
    except RuntimeError:
        return None


def check_links(tree) -> None:
    """Mark the links that join sockets of incompatible port types as invalid."""
    for link in tree.links:
        node = link.to_node
        if getattr(node, "bl_idname", "") != NODE_TYPE:
            continue
        spec = _block_spec(node.kind)
        binding = spec.input_bindings.get(link.to_socket.identifier) if spec else None
        source = getattr(link.from_socket, "port_type", None)
        accepted = (binding.get("accept", [binding.get("type", "node")]) if binding else ())
        valid = source in accepted
        if link.is_valid != valid:
            link.is_valid = valid


_ITEMS_CACHE: dict = {}


def _choice_items(self, context):
    """The choices of a field's widget, kept alive as Blender requires."""
    key = (self.kind, self.name, self.widget)
    if key not in _ITEMS_CACHE:
        spec = _block_spec(self.kind)
        binding = spec.property_bindings.get(self.name, {}) if spec else {}
        values = fields.choices(binding, self.widget) if spec else []
        _ITEMS_CACHE[key] = [("UNSET", "(unset)", "")] + [(value, value, "") for value in values
                                                           if value]
    return _ITEMS_CACHE[key]


def _choice_items_position(self, context):
    return _choice_items(self, context)


def _label_update(self, context):
    pointer = self.as_pointer()
    for node in self.id_data.nodes:
        label = node.fields.get("label") if node.bl_idname == NODE_TYPE else None
        if label is not None and label.as_pointer() == pointer:
            node.update_label()
            return


class BLENDYN_PG_model_field(bpy.types.PropertyGroup):
    """One property of a block, in the slots of its widget."""
    kind: StringProperty()
    widget: StringProperty()
    text: StringProperty(name="Value")
    integer: IntProperty(name="Label", min=0, update=_label_update)
    flag: EnumProperty(items=[("UNSET", "Default", ""), ("YES", "Yes", ""), ("NO", "No", "")])
    choice: EnumProperty(items=_choice_items)
    pos_type: EnumProperty(name="Type", items=_choice_items_position)
    reference: EnumProperty(name="Frame", items=[(r or "NONE", r or "(default)", "")
                                                 for r in fields.REFERENCES])
    first_axis: IntProperty(name="First axis", min=1, max=3, default=1)
    first_vector: StringProperty(name="First vector")
    second_axis: IntProperty(name="Second axis", min=1, max=3, default=2)
    second_vector: StringProperty(name="Second vector")
    raw: BoolProperty(name="Raw", description="Give the value as a raw MBDynLib expression")

    def slots(self) -> dict:
        return {"text": self.text, "integer": self.integer, "flag": self.flag,
                "choice": "" if self.choice == "UNSET" else self.choice,
                "pos_type": "" if self.pos_type == "UNSET" else self.pos_type,
                "reference": "" if self.reference == "NONE" else self.reference,
                "first_axis": self.first_axis, "first_vector": self.first_vector,
                "second_axis": self.second_axis, "second_vector": self.second_vector,
                "raw": self.raw}

    def set_slots(self, slots: dict) -> None:
        for name, value in slots.items():
            if name in ("choice", "pos_type"):
                value = value or "UNSET"
            elif name == "reference":
                value = value or "NONE"
            setattr(self, name, value)


class BLENDYN_PG_model_parameter(bpy.types.PropertyGroup):
    """An MBDyn variable, declared before the model (`name` is its MBDyn name)."""
    var_type: StringProperty(name="Type", default="const real",
                             description="real, integer, bool or string, optionally preceded "
                                         "by ifndef and then const")
    value: StringProperty(name="Value", description="A literal or an expression over the "
                                                    "parameters above")


class BLENDYN_PG_model_settings(bpy.types.PropertyGroup):
    """What the model editor keeps with the tree: parameters and output paths."""
    parameters: CollectionProperty(type=BLENDYN_PG_model_parameter)
    parameter_index: IntProperty()
    output_path: StringProperty(name="MBDyn input", subtype="FILE_PATH",
                                description="Where Export and Run write the MBDyn input file")
    document_path: StringProperty(name="Diagram", subtype="FILE_PATH",
                                  description="The JSON diagram last opened or saved")
    document_extras: StringProperty(description="The opened document, for the fields "
                                                "this editor does not edit")


class BLENDYN_NT_model(bpy.types.NodeTree):
    """An MBDyn model built from the blocks of the Python preprocessor"""
    bl_idname = TREE_TYPE
    bl_label = "MBDyn Model"
    bl_icon = "MOD_PHYSICS"

    mbdyn_model: PointerProperty(type=BLENDYN_PG_model_settings)

    def update(self):
        check_links(self)


_setting_up = set()


def _kind_update(self, context):
    # Node > Add sets the kind of a new node, which then needs its sockets and fields.
    if self.kind and id(self) not in _setting_up and not self.fields and not self.inputs:
        self.setup(self.kind)


class BLENDYN_N_model_block(bpy.types.Node):
    """A block of an MBDyn model: a node, an element, a drive, a constitutive law, ..."""
    bl_idname = NODE_TYPE
    bl_label = "MBDyn Block"
    bl_width_default = 200

    kind: StringProperty(update=_kind_update)
    block_id: StringProperty()
    fields: CollectionProperty(type=BLENDYN_PG_model_field)
    error: StringProperty()

    @classmethod
    def poll(cls, tree):
        return tree.bl_idname == TREE_TYPE

    def setup(self, kind: str, properties: dict | None = None, block_id: str | None = None):
        """Make the sockets and fields of a block of this kind, with its properties."""
        model = library.module("model")
        spec = model.BLOCKS[kind]
        _setting_up.add(id(self))
        try:
            self._setup(model, spec, kind, properties, block_id)
        finally:
            _setting_up.discard(id(self))

    def _setup(self, model, spec, kind, properties, block_id):
        if self.kind != kind:
            self.kind = kind
        if properties is None:
            properties = model.Block.create(kind).properties
            if "label" in properties:
                document = tree_blocks(self.id_data, exclude=self)
                properties["label"] = model.next_label(kind, document)
        self.block_id = block_id or model.Block.create(kind).id
        self.inputs.clear()
        self.outputs.clear()
        for name, binding in spec.input_bindings.items():
            socket = self.inputs.new(socket_idname(binding.get("type", "node")), name, identifier=name,
                                     use_multi_input=binding.get("form") == "ref_list")
            socket.hide = binding.get("form") == "label" and binding.get("auto", False)
        for name, port_type in spec.outputs.items():
            self.outputs.new(socket_idname(port_type), name, identifier=name)
        self.fields.clear()
        for name, default in spec.defaults.items():
            if kind == "component":
                break
            field = self.fields.add()
            field.name, field.kind = name, kind
            field.widget = fields.widget(name, spec.property_bindings.get(name, {}), default)
            self.set_value(name, properties.get(name))
        self.update_label()

    def binding(self, name: str) -> dict:
        spec = _block_spec(self.kind)
        return spec.property_bindings.get(name, {}) if spec else {}

    def value(self, name: str):
        field = self.fields[name]
        return fields.from_slots(field.widget, self.binding(name), field.slots())

    def set_value(self, name: str, value) -> None:
        field = self.fields[name]
        field.set_slots(fields.to_slots(field.widget, self.binding(name), value))

    def properties(self) -> dict:
        """The block's properties, leaving out unset automatic ones."""
        found = {}
        for field in self.fields:
            value = self.value(field.name)
            if value is not None or not self.binding(field.name).get("auto"):
                found[field.name] = value
        return found

    def update_label(self) -> None:
        spec = _block_spec(self.kind)
        title = spec.title if spec else self.kind
        if "label" in self.fields:
            title += f" {self.fields['label'].integer}"
        self.label = title

    def draw_buttons(self, context, layout):
        if self.error:
            layout.label(text=self.error, icon="ERROR")

    def draw_buttons_ext(self, context, layout):
        from .ui import draw_block
        draw_block(layout, self)

    def draw_label(self):
        return self.label or self.kind


def tree_blocks(tree, exclude=None) -> list:
    """The tree's blocks, enough to allocate labels: kind and properties."""
    model = library.module("model")
    return [model.Block(node.kind, {"label": node.fields["label"].integer}
                        if "label" in node.fields else {}, node.block_id)
            for node in tree.nodes
            if node.bl_idname == NODE_TYPE and node.kind
            and (exclude is None or node.as_pointer() != exclude.as_pointer())]


classes = (*SOCKET_CLASSES, BLENDYN_PG_model_field, BLENDYN_PG_model_parameter,
           BLENDYN_PG_model_settings, BLENDYN_NT_model, BLENDYN_N_model_block)
