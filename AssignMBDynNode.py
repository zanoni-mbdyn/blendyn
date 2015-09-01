bl_info = {
    "name": "MBDyn Motion Paths -- select node",
    "author": "Andrea Zanoni - <a.zanoni.mbdyn@gmail.com>",
    "version": (0, 2),
    "blender": (2, 65, 0),
    "location": "Properties -> Object -> MBDyn node select",
    "description": "...",
    "warning": "Alpha stage",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"
}

import bpy

class OBJECT_MB_NODE_SEL(bpy.types.Panel):
    bl_label = "MBdyn node select"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        obj = context.object
        mbs = context.scene.mbdyn_settings
        layout = self.layout
        layout.alignment = 'LEFT'
        row = layout.row(align=True)
        box = row.box()
        box.alignment = 'LEFT'
        nd = context.scene.mbdyn_settings.nodes_dictionary
        for nd_entry in nd:
            lab = str(nd_entry.int_label) + " -- " + nd_entry.string_label
            box.operator("sel.mbdynnode", text=lab, emboss=False).int_label = nd_entry.int_label
        
class OBJECT_MB_NODE_SEL_BUTTON(bpy.types.Operator):
    bl_idname = "sel.mbdynnode"
    bl_label = "MBDyn Node Sel Button"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        context.object.mbdyn_settings.int_label = self.int_label
        # DEBUG message to console
        print("Object " + context.object.name + " MBDyn node association updated to node " + str(context.object.mbdyn_settings.int_label))
        return{'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_MB_NODE_SEL)
    bpy.utils.register_class(OBJECT_MB_NODE_SEL_BUTTON)
def unregister():
    bpy.utils.unregister_class(OBJECT_MB_NODE_SEL)
    bpy.utils.unregister_class(OBJECT_MB_NODE_SEL_BUTTON)

if __name__ == "__main__":
    register()
