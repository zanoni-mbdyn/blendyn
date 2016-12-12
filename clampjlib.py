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

## Parses clamp joint entry in the .log file (see section E.2.8 of input manual for details)
#  Entry:
#   clamp: (int)<label> (int)<node_label> (Vec3Float)<position> (Mat3x3Float)<orientation> (Vec3Float)<nposition> (Mat3x3Float)<orientation>
def parse_clampj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_clampj(): Parsing Cardano hinge joint " + rw[1])
    try:
        pass
    except KeyError:
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_carj(rw, ed) function

## Spawns a Blender object representing a cardano joint
def spawn_clampj_elem(elem, context)
# -----------------------------------------------------------
# end of spawn_clampj_elem(elem, layout) function

## Displays cardano joint infos in the tools panel
def clampj_info_draw(elem, layout):
    pass
# -----------------------------------------------------------
# end of clampj_info_draw(elem, layout) function

