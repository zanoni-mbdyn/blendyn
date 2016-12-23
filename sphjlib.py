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
        el = ed['spherical_hinge_' + str(rw[1])]
        print("parse_sphj(): found existing entry in elements dictionary. Updating it.")
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        R1 = Matrix()
        R1[0][0] = float(rw[6])
        R1[0][1] = float(rw[7])
        R1[0][2] = float(rw[8])
        R1[1][0] = float(rw[9])
        R1[1][1] = float(rw[10])
        R1[1][2] = float(rw[11])
        R1[2][0] = float(rw[12])
        R1[2][1] = float(rw[13])
        R1[2][2] = float(rw[14])
        el.rotoffsets[0].value = R1.to_quaternion(); 
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))
        R2 = Matrix()
        R2[0][0] = float(rw[19])
        R2[0][1] = float(rw[20])
        R2[0][2] = float(rw[21])
        R2[1][0] = float(rw[22])
        R2[1][1] = float(rw[23])
        R2[1][2] = float(rw[24])
        R2[2][0] = float(rw[25])
        R2[2][1] = float(rw[26])
        R2[2][2] = float(rw[27])
        el.rotoffsets[1].value = R2.to_quaternion(); 
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_sphj(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'spherical_hinge'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[15])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix()
        R1[0][0] = float(rw[6])
        R1[0][1] = float(rw[7])
        R1[0][2] = float(rw[8])
        R1[1][0] = float(rw[9])
        R1[1][1] = float(rw[10])
        R1[1][2] = float(rw[11])
        R1[2][0] = float(rw[12])
        R1[2][1] = float(rw[13])
        R1[2][2] = float(rw[14])
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        el.rotoffsets.add()
        R2 = Matrix()
        R2[0][0] = float(rw[19])
        R2[0][1] = float(rw[20])
        R2[0][2] = float(rw[21])
        R2[1][0] = float(rw[22])
        R2[1][1] = float(rw[23])
        R2[1][2] = float(rw[24])
        R2[2][0] = float(rw[25])
        R2[2][1] = float(rw[26])
        R2[2][2] = float(rw[27])
        el.rotoffsets[1].value = R2.to_quaternion();

        el.import_function = "add.mbdyn_elem_sphj"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_sphj(rw, ed) function

## Creates the objet representing a spherical joint
def spawn_sphj_element(elem, context):
    # TODO
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
    # TODO
    pass
# -------------------------------------------------------------------------- 
# end of sphj_info_draw(elem, layout) function

