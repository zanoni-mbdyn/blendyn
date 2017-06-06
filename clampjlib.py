# --------------------------------------------------------------------------
# Blendyn -- file clamipjlib.py
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

import pdb

## Parses clamp joint entry in the .log file (see section E.2.8 of input manual for details)
def parse_clamp(rw, ed):
    ret_val = True
    # Debug message
    print("parse_clamp(): Parsing Cardano hinge joint " + rw[1])
    try:
        el = ed['clamp_' + str(rw[1])]
        
        print("parse_clamp(): found existing entry in elements dictionary. Updating it.")
        
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
        pass
        print("parse_clamp(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'clamp'
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

        el.import_function = "add.mbdyn_elem_clamp"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_clamp(rw, ed) function

## Spawns a Blender object representing a clamp joint
def spawn_clamp_element(elem, context):
    """ Draws a clamp joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_clamp_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_clamp_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    # node object
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'clamp')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        clampjOBJ = bpy.context.selected_objects[0]
        clampjOBJ.name = elem.name

        # automatic scaling
        s = n1OBJ.scale.magnitude*(1./sqrt(3.))*elem.scale_factor
        clampjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
        q1 = elem.rotoffsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    
        # place the joint object in the position defined relative to node 1
        clampjOBJ.location = p1
        clampjOBJ.rotation_mode = 'QUATERNION'
        clampjOBJ.rotation_quaternion = \
                n1OBJ.rotation_quaternion * Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # set parenting of wireframe obj
        bpy.ops.object.select_all(action = 'DESELECT')
        clampjOBJ.select = True
        n1OBJ.select = True
        bpy.context.scene.objects.active = n1OBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        elem.blender_object = clampjOBJ.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
    pass
    pass
# -----------------------------------------------------------
# end of spawn_clamp_elem(elem, layout) function

# Imports a Clamp Joint in the scene
class Scene_OT_MBDyn_Import_Clamp_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_clamp"
    bl_label = "MBDyn clamp joint element importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['clamp_' + str(self.int_label)]
            retval = spawn_clamp_element(elem, context)
            pdb.set_trace()
            if retval == {'OBJECT_EXISTS'}:
                message = "Found the Object " + elem.blender_object + \
                    " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                message = "Could not import element: Blender object " +\
                    "associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                message = "Could not import element: could not " +\
                        "load library object"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element clamp_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Clamp_Joint_Element class
