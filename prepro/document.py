"""Convert between a model node tree and a model builder document.

The document is the JSON format of the model builder's Qt editor, so a
diagram drawn there opens here and the other way round. A block's position
is the node's location with y pointing down, as in the Qt editor. Links
into a port that takes several entities are ordered as they were connected
(Blender lists the latest on top).
"""

from __future__ import annotations

import json

from . import library
from .tree import NODE_TYPE


def parameter_text(var_type: str, value) -> str:
    if isinstance(value, dict) and set(value) == {"expr"}:
        return value["expr"]
    if var_type.endswith("string"):
        return value
    return json.dumps(value)


def parameter_value(var_type: str, text: str):
    if var_type.endswith("string"):
        return text
    stripped = text.strip()
    if var_type.endswith("bool") and stripped.lower() in ("true", "false"):
        return stripped.lower() == "true"
    try:
        value = json.loads(stripped)
    except ValueError:
        return {"expr": stripped}
    return value if type(value) in (int, float, bool) else {"expr": stripped}


def block_nodes(tree):
    return [node for node in tree.nodes if node.bl_idname == NODE_TYPE and node.kind]


def tree_to_document(tree):
    model = library.module("model")
    nodes = block_nodes(tree)
    blocks = [model.Block(node.kind, node.properties(), node.block_id,
                          round(node.location.x, 3), round(-node.location.y, 3))
              for node in nodes]
    edges = []
    for node in nodes:
        spec = model.BLOCKS[node.kind]
        for socket in node.inputs:
            links = [link for link in socket.links if link.is_valid and not link.is_muted
                     and link.from_node.bl_idname == NODE_TYPE]
            collects = spec.input_bindings.get(socket.identifier, {}).get("form") == "ref_list"
            for index, link in enumerate(sorted(links, key=lambda link: link.multi_input_sort_id)):
                edges.append(model.Edge(link.from_node.block_id, node.block_id,
                                        socket.identifier, link.from_socket.identifier,
                                        index if collects else None))
    settings = tree.mbdyn_model
    parameters = [model.Parameter(item.name, item.var_type,
                                  parameter_value(item.var_type, item.value))
                  for item in settings.parameters]
    document = model.Document(blocks=blocks, edges=edges, parameters=parameters)
    document._raw = json.loads(settings.document_extras or "{}")
    return document


def document_to_tree(document, tree) -> None:
    """Replace the tree's content with the document's; components are expanded."""
    if document.definitions or any(block.kind == "component" for block in document.blocks):
        document = document.flattened()
    tree.nodes.clear()
    nodes = {}
    for block in document.blocks:
        node = tree.nodes.new(NODE_TYPE)
        node.location = (block.x, -block.y)
        node.setup(block.kind, dict(block.properties), block.id)
        nodes[block.id] = node
    for edge in sorted(document.edges, key=lambda edge: edge.index or 0):
        tree.links.new(nodes[edge.source].outputs[edge.source_port],
                       nodes[edge.target].inputs[edge.port])
    settings = tree.mbdyn_model
    settings.parameters.clear()
    for parameter in document.parameters:
        item = settings.parameters.add()
        item.name, item.var_type = parameter.name, parameter.var_type
        item.value = parameter_text(parameter.var_type, parameter.value)
    # Fields this editor does not know, such as a block's colour in the Qt
    # editor, go back into the document when it is saved.
    settings.document_extras = json.dumps(getattr(document, "_raw", {}))
