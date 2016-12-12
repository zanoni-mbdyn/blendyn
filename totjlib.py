# --------------------------------------------------------------------------
# MBDynImporter -- file totjlib.py
# Copyright (C) 2016 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

## Parses total joint entry in .log file
#  Entry:
#    totaljoint: (int)<label> (int)<node_1_label> (Vec3Float)<node_1_offset> (Mat3x3Float)<node_1_rot_offset> (int)<node_2_label> (Vec3Float)<node_2_offset> (Mat3x3Float)<node_2_rot_offset>
def parse_totj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_totj(): Parsing total joint " + rw[1])
    try:
        pass
    except KeyError:
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_totj(rw, ed) function

## Displays total joint infos in the tools panel
def totj_info_draw(elem, layout):
    pass
# -----------------------------------------------------------
# end of totj_info_draw( function

## Creates the object representing a Total Joint element
def spawn_totj_element(elem, context):
    pass
# -----------------------------------------------------------
# end of spawn_totj_element(elem, context) function

class Scene_OT_MBDyn_Import_TotalJoint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_totj"
    bl_label = "MBDyn total joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['totj_' + str(self.int_label)]
            return spawn_totj_element(elem, context)
        except KeyError:
            self.report({'ERROR'}, "Element totj_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_TotalJoint_Element class


## Parses total pin joint entry in the .log file
#  Entry:
#    totalpinjoint: (int)<label> (int)<node_1_label> (Vec3Float)<node_1_offset> (Mat3x3Float)<node_1_rot_offset>
def parse_totpinj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_totpinj(): Parsing total pin joint " + rw[1])
    try:
        pass
    except KeyError:
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_totpinj(rw, ed) function

## Displays total pin joint infos in the tools panel
def totpinj_info_draw(elem, layout):
    pass
# -----------------------------------------------------------
# end of totpinj_info_draw(elem, layout) function

## Creates the object representing a Total Joint element
def spawn_totpinj_element(elem, context):
    pass
# -----------------------------------------------------------
# end of spawn_totpinj_element(elem, context) function

class Scene_OT_MBDyn_Import_TotalPinJoint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_totpinj"
    bl_label = "MBDyn total joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['totpinj_' + str(self.int_label)]
            return spawn_totj_element(elem, context)
        except KeyError:
            self.report({'ERROR'}, "Element totpinj_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_TotalPinJoint_Element class
