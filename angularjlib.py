# --------------------------------------------------------------------------
# Blendyn -- file angularjlib.py
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

from .utilslib import parse_rotmat
from .utilslib import parenting

import pdb

# helper function to parse angularvelocity joints
def parse_angularvelocity(rw, ed):
    ret_val = True
    # Debug message
    print("parse_angularvelocity(): Parsing angularvelocity joint " + rw[1])
    try:
        el = ed['angularvelocity_' + str(rw[1])]

        print("parse_angularvelocity(): found existing entry in elements dictionary. Updating it.")

        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_angularvelocity(): didn't find an entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'angularvelocity'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.import_function = "add.mbdyn_elem_angularvelocity"
        # el.info_draw = "angularvelocity_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_angularvelocity(rw, ed) function

# helper function to parse angularacceleration joints
def parse_angularacceleration(rw, ed):
    ret_val = True
    # Debug message
    print("parse_angularacceleration(): Parsing angularacceleration joint " + rw[1])
    try:
        el = ed['angularacceleration_' + str(rw[1])]

        print("parse_angularacceleration(): found existing entry in elements dictionary. Updating it.")

        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_angularacceleration(): didn't find an entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'angularacceleration'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.import_function = "add.mbdyn_elem_angularacceleration"
        # el.info_draw = "angularacceleration_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_angularacceleration(rw, ed) function

# function that displays angularvelocity info in panel -- [ optional ]
def angularvelocity_info_draw(elem, layout):
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
        col.enabled = False

        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of angularvelocity_info_draw(elem, layout) function

# Creates the object representing a angularvelocity joint element
def spawn_angularvelocity_element(elem, context):
    """ Draws a angularvelocity joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_angularvelocity_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_angularvelocity_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe angularvelocity joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'angvel.w')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        angularvelocityjOBJw = bpy.context.selected_objects[0]
        angularvelocityjOBJ = angularvelocityjOBJw.constraints[0].target

        angularvelocityjOBJ.name = elem.name
        angularvelocityjOBJw.name = elem.name + '.w'

        # automatic scaling
        s = (1.0/sqrt(3.))*(n1OBJ.scale.magnitude)
        angularvelocityjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
    
        # place the joint object in the position defined relative to node 2
        angularvelocityjOBJ.location = n1OBJ.location
        angularvelocityjOBJ.rotation_mode = 'QUATERNION'
        axis_direction = Vector(elem.offsets[0].value)
        axis_direction.normalize()
        angularvelocityjOBJ.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)
        angularvelocityjOBJ.rotation_quaternion = n1OBJ.rotation_quaternion * angularvelocityjOBJ.rotation_quaternion

        # set parenting of wireframe obj
        parenting(angularvelocityjOBJ, n1OBJ)

        elem.blender_object = angularvelocityjOBJ.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
# -----------------------------------------------------------
# end of spawn_angularvelocity_element(elem, context) function

# Creates the object representing a angularacceleration joint element
def spawn_angularacceleration_element(elem, context):
    """ Draws a angularacceleration joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_angularacceleration_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_angularacceleration_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    # nodes objects
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe angularacceleration joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'angacc.a')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        angularaccelerationjOBJa = bpy.context.selected_objects[0]
        pdb.set_trace()
        angularaccelerationjOBJ = angularaccelerationjOBJa.constraints[0].target

        angularaccelerationjOBJ.name = elem.name
        angularaccelerationjOBJa.name = elem.name + '.a'

        # automatic scaling
        s = (1.0/sqrt(3.))*(n1OBJ.scale.magnitude)
        angularaccelerationjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
    
        # place the joint object in the position defined relative to node 2
        angularaccelerationjOBJ.location = n1OBJ.location
        angularaccelerationjOBJ.rotation_mode = 'QUATERNION'
        axis_direction = Vector(elem.offsets[0].value)
        axis_direction.normalize()
        angularaccelerationjOBJ.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)
        angularaccelerationjOBJ.rotation_quaternion = n1OBJ.rotation_quaternion * angularaccelerationjOBJ.rotation_quaternion

        # set parenting of wireframe obj
        parenting(angularaccelerationjOBJ, n1OBJ)

        elem.blender_object = angularaccelerationjOBJ.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
# -----------------------------------------------------------
# end of spawn_angularacceleration_element(elem, context) function

# Imports a angularvelocity Joint in the scene
class Scene_OT_MBDyn_Import_angularvelocity_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_angularvelocity"
    bl_label = "MBDyn angularvelocity joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['angularvelocity_' + str(self.int_label)]
            retval = spawn_angularvelocity_element(elem, context)
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
            elif retval == 'LIBRARY_ERROR':
                message = "Could not import element: could not " +\
                        "load library object"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element angularvelocity_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_angularvelocity_Joint_Element class. Creates the object representing a angularvelocity joint element

# Imports a angularacceleration Joint in the scene
class Scene_OT_MBDyn_Import_angularacceleration_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_angularacceleration"
    bl_label = "MBDyn angularacceleration joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['angularacceleration_' + str(self.int_label)]
            retval = spawn_angularacceleration_element(elem, context)
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
            elif retval == 'LIBRARY_ERROR':
                message = "Could not import element: could not " +\
                        "load library object"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element angularacceleration_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_angularacceleration_Joint_Element class. Creates the object representing a angularacceleration joint element
