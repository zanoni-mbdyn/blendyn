"""Check the model editor in headless Blender.

    BLENDER_USER_RESOURCES=<resources with blendyn linked as user_default/blendyn> \\
        blender -b --factory-startup --python-exit-code 1 \\
        --python prepro/test/blender_model_editor.py -- <MBDyn checkout> <scratch dir>

For every example diagram of the model builder: document -> node tree ->
document gives the same document and the same MBDyn input; the tree survives
saving and reopening the .blend file; and adding blocks, allocating labels
and marking errors work.
"""

import glob
import json
import os
import sys
import traceback

import addon_utils
import bpy

source, scratch = sys.argv[sys.argv.index("--") + 1:][:2]
addon_utils.enable("bl_ext.user_default.blendyn", default_set=True)
package = "bl_ext.user_default.blendyn"
bpy.context.preferences.addons[package].preferences.mbdyn_source_path = source

prepro = sys.modules[package + ".prepro"]
from importlib import import_module  # noqa: E402
document = import_module(package + ".prepro.document")
library = import_module(package + ".prepro.library")
ops = import_module(package + ".prepro.ops")
model = library.module("model")
compiler = library.module("compiler")

failures = []


def check(name, condition, detail=""):
    if not condition:
        failures.append(f"{name}: {detail}")
        print("FAIL", name, detail[:2000])


def normalized(data):
    """A document as a dict, without what is not the model's (unknown extras)."""
    return {"blocks": [{key: block[key] for key in ("kind", "properties", "id", "x", "y")}
                       for block in data["blocks"]],
            # The order of the edges carries no meaning: a port's order is their index.
            "edges": sorted(json.dumps(edge, sort_keys=True) for edge in data["edges"]),
            "parameters": data["parameters"]}


examples = sorted(glob.glob(os.path.join(source, "contrib", "PythonModelBuilder", "examples",
                                         "*.json")))
check("examples found", len(examples) > 20, str(len(examples)))
trees = {}
for path in examples:
    name = os.path.basename(path)[:-5]
    try:
        original = model.Document.load(path)
        tree = bpy.data.node_groups.new(name, prepro.tree.TREE_TYPE)
        tree.use_fake_user = True
        document.document_to_tree(original, tree)
        trees[name] = tree
        converted = document.tree_to_document(tree)
        if original.definitions:
            original = original.flattened()
        mine, theirs = normalized(converted.to_dict()), normalized(original.to_dict())
        detail = ([f"block {a} != {b}" for a, b in zip(mine["blocks"], theirs["blocks"]) if a != b]
                  + [f"edges {sorted(map(str, mine['edges']))} != "
                     f"{sorted(map(str, theirs['edges']))}"] * (mine["edges"] != theirs["edges"])
                  + [f"parameters {mine['parameters']} != {theirs['parameters']}"]
                  * (mine["parameters"] != theirs["parameters"]))
        check(f"{name} document", mine == theirs, "\n".join(detail))
        check(f"{name} input", compiler.compile_document(converted) ==
              compiler.compile_document(original))
    except Exception:
        check(name, False, traceback.format_exc())

# Saving and reopening keeps the trees.
compiled = {name: compiler.compile_document(document.tree_to_document(tree))
            for name, tree in trees.items()}
blend = os.path.join(scratch, "model_editor.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.wm.open_mainfile(filepath=blend)
for name, source_text in compiled.items():
    tree = bpy.data.node_groups[name]
    check(f"{name} reopened", compiler.compile_document(document.tree_to_document(tree)) ==
          source_text)

# A new model: blocks get the next free label in their namespace and their sockets.
tree = bpy.data.node_groups.new("new", prepro.tree.TREE_TYPE)
nodes = []
for kind in ("DynamicNode", "dynamic_node", "StaticNode", "RevoluteHinge", "revolute_hinge",
             "Beam", "GenelClamp"):
    node = tree.nodes.new(prepro.tree.NODE_TYPE)
    node.setup(kind)
    nodes.append(node)
labels = [node.fields["label"].integer for node in nodes]
check("labels", labels == [1, 2, 3, 1, 2, 1, 1], str(labels))
check("multi-input", nodes[5].inputs["nodes"].is_multi_input)
check("nested port", "node.node" in nodes[6].inputs)
check("node label", nodes[3].label == "RevoluteHinge 1", nodes[3].label)
nodes[3].fields["label"].integer = 7
check("label update", nodes[3].label == "RevoluteHinge 7", nodes[3].label)

# Node > Add sets the kind of an empty node.
node = tree.nodes.new(prepro.tree.NODE_TYPE)
node.kind = "ConstDriveCaller"
check("kind update", "const_value" in node.fields and "scalar_drive" in node.outputs,
      str(list(node.fields.keys())))

# An incompatible link is invalid, and is left out of the document.
link = tree.links.new(node.outputs["scalar_drive"], nodes[3].inputs["node_1"])
prepro.tree.check_links(tree)
check("invalid link", not link.is_valid)
check("invalid link left out", all(edge.port != "node_1" or edge.source != node.block_id
                                   for edge in document.tree_to_document(tree).edges))

# Errors are marked on the block they name.
tree = bpy.data.node_groups["two_nodes"]
hinge = next(node for node in tree.nodes if node.kind == "spherical_hinge")
tree.links.remove(hinge.inputs["node_2"].links[0])
try:
    ops.compile_tree(tree)
    check("error", False, "compiled without node_2")
except ValueError as exc:
    check("error marked", hinge.error and hinge.use_custom_color, str(exc))

# A parameter edited as text becomes a number or an expression.
check("parameter values", (document.parameter_value("const real", "2.5"),
                           document.parameter_value("const real", "M / 2"),
                           document.parameter_value("bool", "true")) ==
      (2.5, {"expr": "M / 2"}, True))

# The forms only name properties that exist.
class Layout:
    """Records what a draw function asks for, checking the property names."""
    alert = False

    def prop(self, data, name, **kwargs):
        if name not in data.bl_rna.properties:
            raise AttributeError(f"{type(data).__name__} has no property {name}")

    def __getattr__(self, name):
        return lambda *args, **kwargs: self


ui = import_module(package + ".prepro.ui")
for tree in bpy.data.node_groups:
    if tree.bl_idname == prepro.tree.TREE_TYPE:
        for node in document.block_nodes(tree):
            try:
                ui.draw_block(Layout(), node)
            except Exception:
                check(f"draw {tree.name} {node.name}", False, traceback.format_exc())

# Setting the checkout made the Add menus and the search list.
check("menus", len(ui._menu_classes) > 10, str(len(ui._menu_classes)))
check("search", len(ops._kind_items(None, None)) > 290)

print(f"{len(failures)} failures")
sys.exit(1 if failures else 0)
