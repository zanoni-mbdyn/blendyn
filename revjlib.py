# --------------------------------------------------------------------------
# MBDynImporter -- file revjlib.py
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

# helper function to parse revolute joints
def parse_revj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_revj(): Parsing revolute joint " + rw[1])
    try:
        pass
    except KeyError:
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_revj(rw, ed) function

# helper function to parse revolute pin joints
def parse_revpinj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_revpinj(): Parsing revolute pin joint " + rw[1])
    try:
        pass
    except KeyError:
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_revpinj(rw, ed) function

# Creates the object representing a revolute joint element
def spawn_revj_element(elem, context):
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_revj_element(elem, context) function

# Imports a Deformable Displacement Joint in the scene -- TODO
    class Scene_OT_MBDyn_Import_RevJoint_Element(bpy.types.Operator):
        bl_idname = "add.mbdyn_elem_revj"
        bl_label = "MBDyn revolute joint element importer"
        int_label = bpy.props.IntProperty()

        def draw(self, context):
            layout = self.layout
            layout.alignment = 'LEFT'

        def execute(self, context):
            ed = bpy.context.scene.mbdyn.elems
            nd = bpy.context.scene.mbdyn.nodes
        
            try:
                elem = ed['revj_' + str(self.int_label)]
                return spawn_revj_element(elem, context)
            except KeyError:
                self.report({'ERROR'}, "Element revj_" + str(elem.int_label) + "not found")
                return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_RevJoint_Element class
 
# Creates the object representing a revolute joint element
def spawn_revpinj_element(elem, context):
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_revpinj_element(elem, context) function

# Imports a Deformable Displacement Joint in the scene -- TODO
    class Scene_OT_MBDyn_Import_RevPinJoint_Element(bpy.types.Operator):
        bl_idname = "add.mbdyn_elem_revpinj"
        bl_label = "MBDyn revolute pin joint element importer"
        int_label = bpy.props.IntProperty()

        def draw(self, context):
            layout = self.layout
            layout.alignment = 'LEFT'

        def execute(self, context):
            ed = bpy.context.scene.mbdyn.elems
            nd = bpy.context.scene.mbdyn.nodes
        
            try:
                elem = ed['revpinj_' + str(self.int_label)]
                return spawn_revpinj_element(elem, context)
            except KeyError:
                self.report({'ERROR'}, "Element revpinj_" + str(elem.int_label) + "not found")
                return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_RevPinJoint_Element class

# Displays revolute joint infos in the tools panel [ optional ]
def revj_info_draw(elem, layout):
    pass
# -------------------------------------------------------------------------- 
# end of revj_info_draf(elem, layout) function

# Displays revolute joint infos in the tools panel [ optional ]
def revpinj_info_draw(elem, layout):
    pass
# -------------------------------------------------------------------------- 
# end of revpinj_info_draf(elem, layout) function
