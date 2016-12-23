# --------------------------------------------------------------------------
# MBDynImporter -- file clamipjlib.py
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

# helper function to parse clamp joints
def parse_clampj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_clampj(): Parsing Cardano hinge joint " + rw[1])
    try:
        el = ed['clampj_' + str(rw[1])]
        print("parse_clampj(): found existing entry in elements dictionary. Updating it.")
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
        pass
        print("parse_clampj(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'clamp_joint_'
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

        el.import_function = "add.mbdyn_elem_carj"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_clampj(rw, ed) function

## Spawns a Blender object representing a clamp joint
def spawn_clampj_elem(elem, context)
    # TODO
    pass
# -----------------------------------------------------------
# end of spawn_clampj_elem(elem, layout) function

## Displays clamp joint infos in the tools panel
def clampj_info_draw(elem, layout):
    # TODO
    pass
# -----------------------------------------------------------
# end of clampj_info_draw(elem, layout) function

