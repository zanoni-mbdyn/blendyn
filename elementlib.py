# --------------------------------------------------------------------------
# MBDynImporter -- file element.py
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

## Function that parses the single row of the .log file and stores
#  the joint element definition in elems_dictionary
def parse_joint(context, jnt_type, rw):
    objects = context.scene.objects
    ed = context.scene.mbdyn_settings.elems_dictionary

    # helper function to parse beam2
    def parse_beam2():
        ret_val = True
        # Debug message
        print("parse_beam2(): Parsing beam2 " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val

    # helper function to parse beam3
    def parse_beam3():
        ret_val = True
        # Debug message
        print("parse_beam3(): Parsing beam3 " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val

    # helper function to parse deformable displacement joints
    def parse_defdispj():
        ret_val = True
        # Debug message
        print("parse_defdispj(): Parsing deformable displacement joint " + rw[1])
        try:
            el = ed['defdisp_' + str(rw[1])]
            print("parse_rodj(): found existing entry in elements dictionary. Updating it.")
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
            el.is_imported = True
            if el.name in bpy.data.objects.keys():
                el.blender_object = el.name
                el.is_imported = True 
        except KeyError:
            print("parse_rodj(): didn't found en entry in elements dictionary. Creating one.")
            el = ed.add()
            el.type = 'deformable displacement joint'
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

            el.import_function = "add.mbdyn_elem_defdisp"
            el.name = el.type + "_" + str(el.int_label)
            el.is_imported = True
            ret_val = False
        return ret_val

    # helper function to parse revolute joints
    def parse_revj():
        ret_val = True
        # Debug message
        print("parse_revj(): Parsing revolute joint " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val
        # ...

    # helper function to parse revolute pin joints
    def parse_revpinj():
        ret_val = True
        # Debug message
        print("parse_revpinj(): Parsing revolute pin joint " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val
    # ...
    
    # helper function to parse rod joints
    def parse_rodj():
        ret_val = True
        # Debug message
        print("parse_rodj(): Parsing rod " + rw[1])

        try:
            el = ed['rod_' + str(rw[1])]
            print("parse_rodj(): found existing entry in elements dictionary for element "\
                    + rw[1] + ". Updating it.")
            el.nodes[0].int_label = int(rw[2])
            el.nodes[1].int_label = int(rw[6])
            el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
            el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            el.is_imported = True
            if el.name in bpy.data.objects.keys():
                el.blender_object = el.name
                el.is_imported = True
        except KeyError:
            print("parse_rodj(): didn't find entry in elements dictionary. Creating one.")
            el = ed.add()
            el.type = 'rod'
            el.int_label = int(rw[1])
            el.nodes.add()
            el.nodes[0].int_label = int(rw[2])
            el.offsets.add()
            el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
            el.nodes.add()
            el.nodes[1].int_label = int(rw[6])
            el.offsets.add()
            el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            el.import_function = "add.mbdyn_elem_rod"
            el.name = el.type + "_" + str(el.int_label)
            el.is_imported = True
            ret_val = False
            pass 

        return ret_val

    # helper function to parse rod bezier joint
    def parse_rodbezj():
        ret_val = True
        # Debug message
        print("parse_rodbezj(): Parsing rod bezier " + rw[2])
        try:
            el = ed['rod_bezier_' + rw[2]]
            print("parse_rodbezj(): found existing entry in elements dictionary.\
                    Updating it.")
            el.nodes[0].int_label = int(rw[3])
            el.nodes[1].int_label = int(rw[10])
            el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
            el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
            el.offsets[3].value = Vector(( float(rw[14]), float(rw[15]), float(rw[16]) ))
            if el.name in bpy.data.objects.keys():
                el.blender_object = el.name
                el.is_imported = True
        except KeyError:
            print("parse_rodbezj(): didn't find entry in elements dictionary. Creating one.")
            el = ed.add()
            el.type = 'rod bezier'
            el.int_label = int(rw[2])
            el.nodes.add()
            el.nodes[0].int_label = int(rw[3])
            el.offsets.add()
            el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
            el.offsets.add()
            el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            el.nodes.add()
            el.nodes[1].int_label = int(rw[10])
            el.offsets.add()
            el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
            el.offsets.add()
            el.offsets[3].value = Vector(( float(rw[14]), float(rw[15]), float(rw[16]) ))
            el.import_function = "add.mbdyn_elem_rodbez"
            el.info_draw = "rodbez_info_draw"
            el.update_info_operator = "update.rodbez"
            el.write_operator = "write.rodbez"
            el.name = "rod_bezier_" + str(el.int_label)
            ret_val = False
            pass
        return ret_val

    # helper function to parse spherical joints
    def parse_sphj():
        ret_val = True
        # Debug message
        print("parse_sphj(): Parsing spherical joint " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val
    # ...

    # helper function to parse cardano joints
    def parse_carj():
        ret_val = True
        # Debug message
        print("parse_carj(): Parsing Cardano hinge joint " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val
    # ...

    # helper function to parse total pin joints
    def parse_totpinj():
        ret_val = True
        # Debug message
        print("parse_totpinj(): Parsing total pin joint " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val
    # ...


    # helper function to parse total joints
    def parse_totj():
        ret_val = True
        # Debug message
        print("parse_totj(): Parsing total joint " + rw[1])
        try:
            pass
        except KeyError:
            pass
        return ret_val
    # ...


    joint_types  = {    
            "beam2": parse_beam2,
            "beam3": parse_beam3,
            "deformabledisplacementjoint": parse_defdispj,
            "revolute": parse_revj,
            "revolute pin": parse_revpinj,
            "rod": parse_rodj,
            "rod bezier": parse_rodbezj,
            "spherical hinge": parse_sphj,
            "total joint": parse_totj,
            "total pin joint": parse_totpinj
            }
 
    try:
        ret_val = joint_types[jnt_type]()
    except KeyError:
        print("parse_joint(): Element type " + jnt_type + " not implemented yet. \
                Skipping...")
        ret_val = True
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_joint() function

## Displays the element infos in the tools panel
def elem_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
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


## Function that displays Rod Element info in panel
def rod_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
    row = layout.row()
    col = layout.column(align=True)

    # Data of Rod curve
    cvdata = bpy.data.curves["rod_" + str(elem.int_label) + "_cvdata"].splines[0]

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display offset of node 1 info
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)

            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            row = layout.row()
            col = layout.column(align = True)
            col.prop(node, "int_label", text = "Node 2 ID ")
            col.prop(node, "string_label", text = "Node 2 label ")
            col.prop(node, "blender_object", text = "Node 2 Object: ")
            col.enabled = False

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[2], "value", text = "", slider = False)

            layout.separator()
# -----------------------------------------------------------
# end of rod_info_draw() function

## Function that displays Bezier Rod Element info in panel
def rodbez_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
    row = layout.row()
    col = layout.column(align=True)
    
    # curve data for blender object representing the element
    cvdata = bpy.data.curves[elem.blender_object + "_cvdata"].splines[0]

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:
 
            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display first offset of node 1 info
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)

            # Display second offset of node 1 info
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[1], "value", text = "", slider = False)
            # col.enabled = False
            
            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            row = layout.row()
            col = layout.column(align = True)
            col.prop(node, "int_label", text = "Node 2 ID ")
            col.prop(node, "string_label", text = "Node 2 label ")
            col.prop(node, "blender_object", text = "Node 2 Object: ")
            col.enabled = False

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[2], "value", text = "", slider = False)

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[3], "value", text = "", slider = False)

            layout.separator()
# -----------------------------------------------------------
# end of rodbez_info_draw() function


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
