# --------------------------------------------------------------------------
# MBDynImporter -- file sphjlib.py
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

## Parses of spherical joint .log file entry
def parse_sphj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_sphj(): Parsing spherical joint " + rw[1])
    try:
        pass
    except KeyError:
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_sphj(rw, ed) function

## Creates the objet representing a spherical joint
def spawn_sphj_element(elem, context):
    pass
# -------------------------------------------------------------------------- 
# end of spawn_sphj_element(element, context) function

## Imports a Spherical Joint element in the scene
class Scene_OT_MBDyn_Import_SphericalJoint_Element(bpy.types.Operator):

    bl_idname = "add.mbdyn_elem_sphj"
    bl_label = "MBDyn spherical joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['sphj_' + str(self.int_label)]
            return spawn_defdispj_element(elem, context)
        except KeyError:
            self.report({'ERROR'}, "Element sphj_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_SphericalJoint_Element class

## Displays spherical joint element infos in the tools panel
def sphj_info_draw(elem, layout):
    pass
# -------------------------------------------------------------------------- 
# end of sphj_info_draw(elem, layout) function

