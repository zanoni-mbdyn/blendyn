# --------------------------------------------------------------------------
# Blendyn -- file elementlib.py
# Copyright (C) 2015 -- 2021 Andrea Zanoni -- andrea.zanoni@polimi.it
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
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

import ntpath, os, csv, math
from collections import namedtuple

import logging

from .aerolib import *
from .angularjlib import *
from .axialrotjlib import *
from .beamlib import *
from .beamsliderlib import *
from .bodylib import *
from .brakejlib import *
from .carjlib import *
from .clampjlib import *
from .defdispjlib import *
from .distjlib import *
from .drivejlib import *
from .forcelib import *
from .gimbaljlib import *
from .inlinejlib import *
from .inplanejlib import *
from .linearjlib import *
from .modallib import *
from .prismjlib import *
from .revjlib import *
from .rodjlib import *
from .shell4lib import *
from .membrane4lib import *
from .sphjlib import *
from .totjlib import *
from .utilslib import *

## Function that parses the single row of the .log file and stores
#  the element definition in elems
def parse_elements(context, jnt_type, rw):
    objects = context.scene.objects
    ed = context.scene.mbdyn.elems

    joint_types  = {    
            "aero0": parse_aero0,
            "aero2": parse_aero2,
            "aero3": parse_aero3,
            "beam2": parse_beam2,
            "beam3": parse_beam3,
            "beamslider": parse_beam_slider,
            "body": parse_body,
            "cardanohinge": parse_cardano_hinge,
            "cardanopin": parse_cardano_pin,
            "clamp": parse_clamp,
            "deformabledisplacementjoint": parse_deformable_displacement,
            "modal": parse_modal,
            "revolutehinge": parse_revolute_hinge,
            "revolutepin": parse_revolute_pin,
            "revoluterotation": parse_revolute_rot,
            "rod": parse_rod,
            # "rod bezier": parse_rod_bezier,
            "shell4" : parse_shell4,
            "membrane4" : parse_membrane4,
            "sphericalhinge": parse_spherical_hinge,
            "spericalpin": parse_spherical_pin,
            "structural absolute force": parse_structural_absolute_force,
            "structural absolute couple": parse_structural_absolute_couple,
            "structural follower force": parse_structural_follower_force,
            "structural follower couple": parse_structural_follower_couple,
            "totaljoint": parse_total,
            "totalpinjoint": parse_total_pin,
            "prismatic": parse_prismatic,
            "inplane": parse_inplane,
            "inline": parse_inline,
            "axialrotation": parse_axialrot,
            "distance": parse_distance,
            "gimbalrotation": parse_gimbal,
            "brake": parse_brake,
            "linearvelocity": parse_linearvelocity,
            "linearacceleration": parse_linearacceleration,
            "angularvelocity": parse_angularvelocity,
            "angularacceleration": parse_angularacceleration,
            "drivedisplacement": parse_drive_displacement
            }
 
    try:
        ret_val = joint_types[jnt_type](rw, ed)
    except KeyError as kerr:
        message = "BLENDYN::parse_elements(): " \
                + "Element type " + jnt_type \
                + " not implemented yet. Skipping..."
        print(message)
        logging.warning(message)
        ret_val = True
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_elements() function

## Displays "generic" element infos in the tools panel
def elem_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    col = layout.column(align=True)
     
    row = layout.row()
    col = row.column()

    kk = 0
    for elnode in elem.nodes:
        kk = kk + 1
        for node in nd:
             if node.int_label == elnode.int_label:
                col.prop(node, "int_label", text = "Node " + str(kk) + " ID")
                col.prop(node, "string_label", text = "Node " + str(kk) + " label")
                col.prop(node, "blender_object", text = "Node " + str(kk) + " Object")
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
        row.label(text = "orientation offset " + str(kk))
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

    # Blender 2.8 way of updating the scene
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()

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


def get_fem_connect_node1(self, context):
    mbs = context.scene.mbdyn
    elem = mbs.elems[mbs.comp_selected_elem]
    node1_int = [node.int_label for node in elem.nodes]
    return [(str(node_int), str(node_int), "") for node_int in node1_int]

def get_fem_connect_node2(self, context):
    mbs = context.scene.mbdyn
    elem = mbs.elems[mbs.comp_selected_elem]
    node2_int = [node.int_label for node in elem.nodes]
    return [(str(node_int), str(node_int), "") for node_int in node2_int]


def get_nodes_for_modal(self, context):
    mbs = context.scene.mbdyn
    nd = mbs.nodes
    selected_nodes = []
    for node in nd:
        int_label = node.int_label
        if int_label not in [node.int_label for node in mbs.elems[mbs.comp_selected_elem].nodes]:
            selected_nodes.append(int_label)
    return [(str(int_label), str(int_label), "") for int_label in selected_nodes]


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
class BLENDYN_PT_bevel(bpy.types.Panel):
    """ Bevel section panel in data properties """
    bl_label = "Curve section"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        ed = context.scene.mbdyn.elems
        curve = context.curve
        layout = self.layout
        col = layout.column()

        # Types of elements for which the panel is useful
        eltypes = {'beam2', 'beam3', 'rodj'}

        try:
            if ed[context.object.name].type in eltypes:
                col.operator(BLENDYN_OT_load_section.bl_idname, text="Load profile (Selig)")
                if ed[context.object.name].type == 'beam3':
                    col.operator(BLENDYN_OT_update_beam3.bl_idname, text="Update configuration")
        except KeyError:
            pass
# -----------------------------------------------------------
# end of BLENDYN_PT_bevel class
