# --------------------------------------------------------------------------
# Blendyn -- file gimbaljlib.py
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

import logging

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

from .utilslib import *

# helper function to parse gimbal joints
def parse_gimbal(rw, ed):
    ret_val = True
    # Debug message
    print("parse_gimbal(): Parsing gimbal joint " + rw[1])
    try:
        el = ed['gimbal_' + str(rw[1])]

        print("parse_gimbal(): found existing entry in elements dictionary. Updating it.")

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1 = Matrix()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion(); 

        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        R2 = Matrix()
        parse_rotmat(rw, 19, R2) 
        el.rotoffsets[1].value = R2.to_quaternion(); 

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_gimbal(): didn't find an entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'gimbal'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[15])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        el.rotoffsets.add()
        R2 = Matrix()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        el.import_function = "add.mbdyn_elem_gimbal"
        el.info_draw = "gimbal_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_gimbal(rw, ed) function

# function that displays gimbal info in panel -- [ optional ]
def gimbal_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try:
        node = nd['node_' + str(elem.nodes[0].int_label)]
        # Display node 1 info
        col.prop(node, "int_label", text = "Node 1 ID ")
        col.prop(node, "string_label", text = "Node 1 label ")
        col.prop(node, "blender_object", text = "Node 1 Object: ")
        col.enabled = False

        # Display offset of node 1 info
        row = layout.row()
        row.label(text = "offset 1 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[0], "value", text = "", slider = False)

        node = nd['node_' + str(elem.nodes[1].int_label)]

        # Display node 2 info
        col.prop(node, "int_label", text = "Node 2 ID ")
        col.prop(node, "string_label", text = "Node 2 label ")
        col.prop(node, "blender_object", text = "Node 2 Object: ")
        col.enabled = False

        # Display offset of node 2 info
        row = layout.row()
        row.label(text = "offset 2 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[1], "value", text = "", slider = False)
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of gimbal_info_draw(elem, layout) function

# Creates the object representing a gimbal joint element
def spawn_gimbal_element(elem, context):
    """ Draws a gimbal joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_gimbal_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_gimbal_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_gimbal_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # load the wireframe gimbal joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'gimbal')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        gimbaljOBJ = bpy.context.selected_objects[0]
        gimbaljOBJ.name = elem.name
    else:
        return {'LIBRARY_ERROR'}

    # automatic scaling
    s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + \
    n2OBJ.scale.magnitude)
    gimbaljOBJ.scale = Vector(( s, s, s ))

    # joint offsets with respect to nodes
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    q1 = elem.rotoffsets[0].value
    q2 = elem.rotoffsets[1].value

    # project offsets in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    p2 = n2OBJ.location + R2*Vector(( f2[0], f2[1], f2[2] ))

    # place the joint object in the position defined relative to node 2
    gimbaljOBJ.location = p1
    gimbaljOBJ.rotation_mode = 'QUATERNION'
    gimbaljOBJ.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'gimbal_child')
    if app_retval != {'FINISHED'}:
        return {'LIBRARY_ERROR'}

    gimbal_childobj = bpy.context.selected_objects[0]

    # position it correctly
    gimbal_childobj.location = gimbaljOBJ.location

    # rotate it according to "position orientation" w.r.t. node 1
    gimbal_childobj.rotation_mode = 'QUATERNION'
    gimbal_childobj.rotation_quaternion = \
            n2OBJ.rotation_quaternion * Quaternion(( q2[0], q2[1], q2[2], q2[3] ))

    bpy.ops.object.select_all(action = 'DESELECT')
    gimbal_childobj.select = True    
    gimbaljOBJ.select = True
    bpy.context.scene.objects.active = gimbaljOBJ
    bpy.ops.object.join()

    # set parenting of wireframe obj
    parenting(gimbaljOBJ, n1OBJ)

    grouping(context, gimbaljOBJ, [n1OBJ, n2OBJ, gimbal_childobj])

    elem.blender_object = gimbaljOBJ.name

    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_gimbal_element(elem, context) function

# Imports a gimbal Joint in the scene
class Scene_OT_MBDyn_Import_gimbal_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_gimbal"
    bl_label = "MBDyn gimbal joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['gimbal_' + str(self.int_label)]
            retval = spawn_gimbal_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                message = "Found the Object " + elem.blender_object + \
                    " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                message = "Could not import element: Blender object " +\
                    "associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == 'NODE2_NOTFOUND':
                message = "Could not import element: Blender object " +\
                        "associated to Node " + str(elem.nodes[1].int_label) + " not found"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                message = "Could not import element: could not " +\
                        "load library object"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element gimbal_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_gimbal_Joint_Element class. Creates the object representing a gimbal joint element
