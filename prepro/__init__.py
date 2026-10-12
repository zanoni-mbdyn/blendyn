"""The MBDyn model editor: build MBDyn models as node trees, write and run them.

Blocks come from the model builder of an MBDyn source checkout
(`contrib/PythonModelBuilder`), which writes the input through MBDynLib;
set the checkout in the Blendyn preferences.
"""

import bpy

from . import ops, tree, ui

classes = (*tree.classes, *ops.classes, *ui.classes)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_add.append(ui.draw_add_menu)
    ui.register_menus()


def unregister():
    ui.unregister_menus()
    bpy.types.NODE_MT_add.remove(ui.draw_add_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
