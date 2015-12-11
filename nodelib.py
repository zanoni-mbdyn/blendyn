# --------------------------------------------------------------------------
# MBDynImporter -- file node.py
# Copyright (C) 2015 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of MBDynImporter, add-on script for Blender.
#
#    MBDynImporter is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MBDynImporter  is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with MBDynImporter.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

# TODO: check for unnecessary stuff
import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import BoolProperty, IntProperty, IntVectorProperty, FloatVectorProperty
from bpy.props import StringProperty, BoolVectorProperty, PointerProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper

import ntpath, os, csv, math
from collections import namedtuple

class RotKeyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
# -----------------------------------------------------------
# end of RotKeyError class 

def update_parametrization(obj):
    axes = {'1': 'X', '2': 'Y', '3': 'Z'}
    ret_val = ''
    param = obj.mbdyn_settings.parametrization
    if param == 'phi':
        obj.rotation_mode = 'AXIS_ANGLE'
        ret_val = 'FINISHED'
    elif param[0:5] == 'euler':
        obj.rotation_mode = axes[param[7]] + axes[param[6]] + axes[param[5]]
        ret_val = 'FINISHED'
    elif param == 'mat':
        obj.rotation_mode = 'QUATERNION'
        ret_val = 'FINISHED'
    else:
        print("update_parametrization(): rotation parametrization for node " + \
                obj.mbdyn_settings.int_label + " not supported (yet!).")
        ret_val = 'ROT_NOT_SUPPORTED'

    return ret_val
# -----------------------------------------------------------
# end of update_parametrization() function 

def update_label(self, context):
    
    # utility renaming
    obj = context.object
    nd = context.scene.mbdyn_settings.nodes_dictionary
    
    # Debug Messages
    print("MBDynPanel::update_label(): updating MBDyn node associated to object " + obj.name)
    print("MBDynPanel::update_label(): selected MBDyn node = ", str(obj.mbdyn_settings.int_label))
    
    # Search for int label and assign corresponding string label, if found.
    # If not, signal it by assign the "not found" label
    node_string_label = "not_found"
    obj.mbdyn_settings.is_assigned = False
    for item in nd:
        if item.int_label == obj.mbdyn_settings.int_label:
            node_string_label = item.string_label
            item.blender_object = obj.name
            obj.mbdyn_settings.is_assigned = True
    
    obj.mbdyn_settings.string_label = node_string_label
    if obj.mbdyn_settings.is_assigned:
        ret_val = update_parametrization(obj)

    if ret_val == 'ROT_NOT_SUPPORTED':
        self.report({'ERROR'}, "Rotation parametrization not supported, node " \
            + obj.mbdyn_settings.string_label) 
    return
# -----------------------------------------------------------
# end of update_label() function <-- FIXME: Duplicate? 

## Function that parses the single row of the .log file and stores
#  the node element definition in elems_dictionary
def parse_node(context, rw):
    objects = context.scene.objects
    mbs = context.scene.mbdyn_settings
    nd = mbs.nodes_dictionary

    # helper function to convert any kind of orientation definition to quaternion
    def orient_to_quat(rw):

        type = rw[6];
        axes = {'1': 'X', '2': 'Y', '3': 'Z'}
        
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
            return R.to_quaternion()
        elif type[0:5] == 'euler':
            angles = Euler(Vector(( radians(float(rw[7])), radians(float(rw[8])), radians(float(rw[9])) )),\
                            axes[type[7]] + axes[type[6]] + axes[type[5]])
            return angles.to_quaternion()
        elif type == 'phi':
            vec = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            angle = vec.magnitude
            sin_angle = sin(angle)
            vec.normalize()
            return Quaternion(( cos(angle/2), vec[0]*sin_angle, vec[1]*sin_angle, vec[2]*sin_angle ))
        else:
            raise RotKeyError("Error: rotation mode " + type + " not recognised")

    print("parse_node(): Parsing node " + rw[2])
    try:
        node = nd['node_' + str(rw[2])]
        print("parse_node(): found existing entry in nodes dictionary for node " + rw[2]\
                + ". Updating it.")
        node.initial_pos = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        node.parametrization = rw[6]
        try:
            node.initial_rot = orient_to_quat(rw)
        except RotKeyError:
            pass
        ret_val = True
    except KeyError:
        print("parse_node(): didn't find an existing entry in nodes dictionary for node " + rw[2]\
                + ". Creating it.")
        node = nd.add()
        node.int_label = int(rw[2])
        node.name = "node_" + rw[2]
        node.initial_pos = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        node.parametrization = rw[6]
        try:
            node.initial_rot = orient_to_quat(rw)
        except RotKeyError:
            pass
        pass
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_node() function <-- FIXME: Duplicate? 
