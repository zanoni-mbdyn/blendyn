# --------------------------------------------------------------------------
# Blendyn -- file bodylib.py
# Copyright (C) 2015 -- 2017 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of Blendyn, add-on script for Blender.
#
#    Blendyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Blendyn  is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Blendyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

import bpy
import os

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

## Parses body entry in the .log file (see section E.2.8 of input manual for details)
def parse_body(rw, ed):
    ret_val = True
    # Debug message
    print("parse_body(): Parsing body " + rw[1])
    try:
        el = ed['body_' + str(rw[1])]
        
        print("parse_body(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        el.magnitude = float(rw[3])     # mass
        
        el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
        
        J = Matrix()

        # FIXME this is the inertia matrix... And this is a (dirty) trick 
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))
         
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        pass
        print("parse_body(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'body'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.magnitude = float(rw[3])
        
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))

        # FIXME this is the inertia matrix... And this is a (dirty) trick 
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))

        el.import_function = "add.mbdyn_elem_body"
        el.info_draw = "body_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_body(rw, ed) function

## Spawns a Blender object representing a body element (CG representation)
def spawn_body_element(elem, context):
    """ Draws a body element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_body_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_body_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    # node object
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe body object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'other.blend', 'Object'), filename = 'cg')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        bodyOBJ = bpy.context.selected_objects[0]
        bodyOBJ.name = elem.name

        # automatic scaling
        s = n1OBJ.scale.magnitude*(1./sqrt(3.))
        bodyOBJ.scale = Vector(( s, s, s ))*elem.scale_factor

        # element offset with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    
        # place the body object in the position defined relative to node 1
        bodyOBJ.location = p1
        bodyOBJ.rotation_mode = 'QUATERNION'

        # set parenting of wireframe obj
        bpy.ops.object.select_all(action = 'DESELECT')
        bodyOBJ.select = True
        n1OBJ.select = True
        bpy.context.scene.objects.active = n1OBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        elem.blender_object = bodyOBJ.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
    pass
    pass
# -----------------------------------------------------------
# end of spawn_body_elem(elem, layout) function

# Imports a Body in the scene
class Scene_OT_MBDyn_Import_Body_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_body"
    bl_label = "MBDyn body element importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['body_' + str(self.int_label)]
            retval = spawn_body_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element body_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Body_Element class

# Displays body element info in the tools panel
def body_info_draw(elem, layout): 
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align = True)

    col.prop(elem, "scale_factor")
    col.prop(elem, "magnitude", text = "mass")

    row = layout.row()
    col = layout.column(align = True)
    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node ID ")
            col.prop(node, "string_label", text = "Node label ")
            col.prop(node, "blender_object", text = "Node Object: ")
            col.enabled = False

            # Display offset from node 1
            row = layout.row()
            row.label(text = "CG offset in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)

    row = layout.row()
    row.label(text = "Inertia tensor")
    
    box = layout.box()
    split = box.split(.33)
    column = split.column()
    column.row().prop(elem.offsets[1], 'value', index = 0, text = 'Jxx')
    column.row().prop(elem.offsets[2], 'value', index = 0, text = 'Jyx')
    column.row().prop(elem.offsets[3], 'value', index = 0, text = 'Jzx')
    column = split.column()
    column.row().prop(elem.offsets[1], 'value', index = 1, text = 'Jxy')
    column.row().prop(elem.offsets[2], 'value', index = 1, text = 'Jyy')
    column.row().prop(elem.offsets[3], 'value', index = 1, text = 'Jzy')
    column = split.column()
    column.row().prop(elem.offsets[1], 'value', index = 2, text = 'Jxz')
    column.row().prop(elem.offsets[2], 'value', index = 2, text = 'Jyz')
    column.row().prop(elem.offsets[3], 'value', index = 2, text = 'Jzz')

    pass
