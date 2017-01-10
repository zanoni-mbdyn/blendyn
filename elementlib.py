# --------------------------------------------------------------------------
# MBDynImporter -- file elementlib.py
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

# TODO: check for unnecessary stuff
import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

import ntpath, os, csv, math
from collections import namedtuple

from .beamlib import *
from .carjlib import *
from .clampjlib import *
from .defdispjlib import *
from .revjlib import *
from .rodjlib import *
from .shell4lib import *
from .sphjlib import *
from .totjlib import *
from .utilslib import *

## Function that parses the single row of the .log file and stores
#  the joint element definition in elems
def parse_joint(context, jnt_type, rw):
    objects = context.scene.objects
    ed = context.scene.mbdyn.elems

    joint_types  = {    
            "beam2": parse_beam2,
            "beam3": parse_beam3,
            "cardanohinge": parse_carj,
            "clamp": parse_clampj,
            "deformabledisplacementjoint": parse_defdispj,
            "revolutehinge": parse_revj,
            "revolutepin": parse_revpinj,
            "rod": parse_rodj,
            "rod bezier": parse_rodbezj,
            "shell4" : parse_shell4,
            "sphericalhinge": parse_sphj,
            "totaljoint": parse_totj,
            "totalpinjoint": parse_totpinj
            }
 
    try:
        ret_val = joint_types[jnt_type](rw, ed)
    except KeyError:
        print("parse_joint(): Element type " + jnt_type + " not implemented yet. \
                Skipping...")
        ret_val = True
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_joint() function

## Displays "generic" element infos in the tools panel
def elem_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    col = layout.column(align=True)
    kk = 0
    for elnode in elem.nodes:
        kk = kk + 1
        for node in nd:
             if node.int_label == elnode.int_label:
                col.prop(node, "int_label", text = "Node " + str(kk) + " ID: ")
                col.prop(node, "string_label", text = "Node " + str(kk) + " label: ")
                col.prop(node, "blender_object", text = "Node " + str(kk) + " Object: ")
                col.enabled = False
    
    kk = 0
    for off in elem.offsets:
        kk = kk + 1
        row = layout.row()
        row.label(text = "offset " + str(kk))
        col = layout.column(align = True)
        col.prop(off, "value", text = "", slider = False)
    
    kk = 0
    for rotoff in elem.rotoffsets:
        kk = kk + 1
        row = layout.row()
        row.label(text = "rot. offset" + str(kk))
        col = layout.column(align = True)
        col.prop(rotoff, "value", text = "", slider = False)
# -----------------------------------------------------------
# end of elem_info_draw() function

# App handler to update the configuration of deformable elements
# after the location of the nodes has been updated

@persistent
def update_elements(scene):
    ed = scene.mbdyn.elems
    eu = scene.mbdyn.elems_to_update
    for elem in eu:
        element = ed[elem.name]
        eval(ed[elem.name].update + "(element, True)")

bpy.app.handlers.frame_change_post.append(update_elements)

# Retrieves the types of elements present in the scene and populates 
# the list to be shown in the Scene panel
def get_elems_types(self, context):
    mbs = context.scene.mbdyn
    ed = mbs.elems

    elem_types = list()
    for elem in ed:
        if elem.type not in elem_types:
            elem_types.append(elem.type)

    return [(etype, etype, "%s elements"%etype) for etype in elem_types]

## Utility functions
def fmin(x):
    min = x[0]
    loc = 0
    for idx in range(1, len(x)):
        if x[idx] < min:
            min = x[idx]
            loc = idx
    return (min, loc)
# -----------------------------------------------------------
# end of fmin function

def fmax(x):
    max = x[0]
    loc = 0
    for idx in range(1, len(x)):
        if x[idx] > max:
            max = x[idx]
            loc = idx
    return (max, loc)
# -----------------------------------------------------------
# end of fmax function

## Bevel object panel, for curves
class Data_OT_MBDyn_Elems_Beams(bpy.types.Panel):
    """ Beam operators panel in data properties panel """
    bl_label = "MBDyn props"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    def draw(self, context):
        ed = context.scene.mbdyn.elems
        curve = context.curve
        layout = self.layout
        col = layout.column()

        # Types of elements for which the panel is useful
        eltypes = {'beam2', 'beam3', 'rodj'}

        try:
            if ed[context.object.name].type in eltypes:
                col.operator(Object_OT_MBDyn_load_section.bl_idname, text="Load profile (Selig)")
                if ed[context.object.name].type == 'beam3':
                    col.operator(Object_OT_MBDyn_update_beam3.bl_idname, text="Update configuration")
        except KeyError:
            pass
# -----------------------------------------------------------
# end of Data_OT_MBDyn_Elems_Beams class

