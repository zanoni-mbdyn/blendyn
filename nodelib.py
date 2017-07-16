# --------------------------------------------------------------------------
# Blendyn -- file nodelib.py
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

# TODO: check for unnecessary stuff
import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import logging

import ntpath, os, csv, math
from collections import namedtuple

import pdb

axes = {'1': 'X', '2': 'Y', '3': 'Z'}

class RotKeyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
# -----------------------------------------------------------
# end of RotKeyError class 

def set_obj_locrot_mov(obj, rw):

    # Position
    obj.location[0] = rw[1]
    obj.location[1] = rw[2]
    obj.location[2] = rw[3]
    
    obj.keyframe_insert(data_path = "location")

    # Orientation
    parametrization = obj.mbdyn.parametrization
    
    if parametrization[0:5] == 'EULER':
        obj.rotation_euler = Euler(Vector(( math.radians(rw[4]),\
                                            math.radians(rw[5]),\
                                            math.radians(rw[6]))),\
                     axes[parametrization[7]] + axes[parametrization[6]] + axes[parametrization[5]])
        obj.keyframe_insert(data_path = "rotation_euler")
    elif parametrization == 'PHI':
        rotvec = Vector((rw[4], rw[5], rw[6]))
        rotvec_norm = rotvec.normalized()
        obj.rotation_axis_angle = Vector((rotvec.magnitude, \
                                            rotvec_norm[0], rotvec_norm[1], rotvec_norm[2]))
        obj.keyframe_insert(data_path = "rotation_axis_angle")
    elif parametrization == 'MATRIX':
        R = Matrix(((rw[4], rw[5], rw[6], 0.0),\
                    (rw[7], rw[8], rw[9], 0.0),\
                    (rw[10], rw[11], rw[12], 0.0),\
                    (0.0, 0.0, 0.0, 1.0)))
        obj.rotation_quaternion = R.to_quaternion()
        obj.keyframe_insert(data_path = "rotation_quaternion")
    else:
        # Should not be reached
        print("Error: unsupported rotation parametrization")

    return
# -----------------------------------------------------------
# end of set_obj_locrot_mov() function 

def update_parametrization(obj):
    ret_val = ''
    param = obj.mbdyn.parametrization
    if param == 'PHI':
        obj.rotation_mode = 'AXIS_ANGLE'
        ret_val = 'FINISHED'
    elif param[0:5] == 'EULER':
        obj.rotation_mode = axes[param[7]] + axes[param[6]] + axes[param[5]]
        ret_val = 'FINISHED'
    elif param == 'MATRIX':
        obj.rotation_mode = 'QUATERNION'
        ret_val = 'FINISHED'
    else:
        # Cannot be reached
        print("Error: unsupported rotation parametrization")
        ret_val = 'ROT_NOT_SUPPORTED'

    return ret_val
# -----------------------------------------------------------
# end of update_parametrization() function 

def update_label(self, context):
    
    # utility renaming
    obj = context.object
    nd = context.scene.mbdyn.nodes
    
    # Debug Messages
    try:
        print("MBDynPanel::update_label(): updating MBDyn node associated to object " + obj.name)
        print("MBDynPanel::update_label(): selected MBDyn node = ", str(obj.mbdyn.int_label))
    except AttributeError:
        pass
    
    # Search for int label and assign corresponding string label, if found.
    # If not, signal it by assign the "not found" label
    node_string_label = "not_found"
    obj.mbdyn.is_assigned = False
    for item in nd:
        if item.int_label == obj.mbdyn.int_label:
            node_string_label = item.string_label
            item.blender_object = obj.name
            obj.mbdyn.is_assigned = True
    
    obj.mbdyn.string_label = node_string_label
    if obj.mbdyn.is_assigned:
        ret_val = update_parametrization(obj)

    if ret_val == 'ROT_NOT_SUPPORTED':
        message = "Rotation parametrization not supported, node " \
            + obj.mbdyn.string_label
        self.report({'ERROR'}, message)
        logging.error(message)
    return
# -----------------------------------------------------------
# end of update_label() function <-- FIXME: Duplicate? 

## Function that parses the single row of the .log file and stores
#  the node element definition in elems
def parse_node(context, rw):
    objects = context.scene.objects
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    # helper function to convert any kind of orientation definition to quaternion
    def orient_to_quat(rw):

        type = rw[6];

        if type == 'mat':
            R = Matrix()
            R[0][0] = float(rw[7])
            R[0][1] = float(rw[8])
            R[0][2] = float(rw[9])
            R[1][0] = float(rw[10])
            R[1][1] = float(rw[11])
            R[1][2] = float(rw[12])
            R[2][0] = float(rw[13])
            R[2][1] = float(rw[14])
            R[2][2] = float(rw[15])
            return R.to_quaternion(), 'MATRIX'
        elif type[0:5] == 'euler':
            angles = Euler(Vector(( radians(float(rw[7])), radians(float(rw[8])), radians(float(rw[9])) )),\
                            axes[type[7]] + axes[type[6]] + axes[type[5]])
            return angles.to_quaternion(), 'EULER' + type[5:8]
        elif type == 'phi':
            vec = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            angle = vec.magnitude
            sin_angle = sin(angle)
            vec.normalize()
            return Quaternion(( cos(angle/2), vec[0]*sin_angle, vec[1]*sin_angle, vec[2]*sin_angle )), 'PHI'
        else:
            raise RotKeyError("Error: rotation mode " + type + " not recognised")

    print("parse_node(): Parsing node " + rw[2])
    try:
        node = nd['node_' + str(rw[2])]
        node.is_imported = True
        print("parse_node(): found existing entry in nodes dictionary for node " + rw[2]\
                + ". Updating it.")
        node.initial_pos = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        try:
            node.initial_rot, node.parametrization = orient_to_quat(rw)
        except RotKeyError:
            pass
        ret_val = True
    except KeyError:
        print("parse_node(): didn't find an existing entry in nodes dictionary for node " + rw[2]\
                + ". Creating it.")
        node = nd.add()
        node.is_imported = True
        node.int_label = int(rw[2])
        node.name = "node_" + rw[2]
        node.initial_pos = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        try:
            node.initial_rot, node.parametrization = orient_to_quat(rw)
        except RotKeyError:
            pass
        pass
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_node() function <-- FIXME: Duplicate?

## Simple function that adds to the scene the default Blender object
#  representing an MBDyn node
def spawn_node_obj(context, node):
    mbs = context.scene.mbdyn

    if mbs.node_object == "ARROWS":
        bpy.ops.object.empty_add(type = 'ARROWS', location = node.initial_pos)
        return True
    elif mbs.node_object == "AXES":
        bpy.ops.object.empty_add(type = 'PLAIN_AXES', location = node.initial_pos)
        return True
    elif mbs.node_object == "CUBE":
        bpy.ops.mesh.primitive_cube_add(location = node.initial_pos)
        return True
    elif mbs.node_object == "UVSPHERE":
        bpy.ops.mesh.primitive_uv_sphere_add(location = node.initial_pos)
        return True
    elif mbs.node_object == "NSPHERE":
        bpy.ops.surface.primitive_nurbs_surface_sphere_add(location = node.initial_pos)
        return True
    elif mbs.node_object == "CONE":
        bpy.ops.mesh.primitive_cone_add(location = node.initial_pos)
        return True
    else:
        return False
# -----------------------------------------------------------
# end of spawn_node_obj() function

