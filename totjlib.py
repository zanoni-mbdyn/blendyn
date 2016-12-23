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
def parse_totj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_totj(): Parsing total joint " + rw[1])
    try:
        el = ed['total_joint_' + str(rw[1])]
        print("parse_totj(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[24])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1p = Matrix()
        R1p[0][0] = float(rw[6])
        R1p[0][1] = float(rw[7])
        R1p[0][2] = float(rw[8])
        R1p[1][0] = float(rw[9])
        R1p[1][1] = float(rw[10])
        R1p[1][2] = float(rw[11])
        R1p[2][0] = float(rw[12])
        R1p[2][1] = float(rw[13])
        R1p[2][2] = float(rw[14])

        el.rotoffsets[0].value = R1p.to_quaternion(); 

        R1r = Matrix()
        R2r[0][0] = float(rw[15])
        R2r[0][1] = float(rw[16])
        R2r[0][2] = float(rw[17])
        R2r[1][0] = float(rw[18])
        R2r[1][1] = float(rw[19])
        R2r[1][2] = float(rw[20])
        R2r[2][0] = float(rw[21])
        R2r[2][1] = float(rw[22])
        R2r[2][2] = float(rw[23])

        el.rotoffsets[1].value = R1r.to_quaternion(); 
        
        el.offsets[1].value = Vector(( float(rw[25]), float(rw[26]), float(rw[27]) ))

        R2p = Matrix()
        R2p[0][0] = float(rw[28])
        R2p[0][1] = float(rw[29])
        R2p[0][2] = float(rw[30])
        R2p[1][0] = float(rw[31])
        R2p[1][1] = float(rw[32])
        R2p[1][2] = float(rw[33])
        R2p[2][0] = float(rw[34])
        R2p[2][1] = float(rw[35])
        R2p[2][2] = float(rw[36])
        el.rotoffsets[2].value = R2p.to_quaternion();
        
        R2r = Matrix()
        R2r[0][0] = float(rw[37])
        R2r[0][1] = float(rw[38])
        R2r[0][2] = float(rw[39])
        R2r[1][0] = float(rw[40])
        R2r[1][1] = float(rw[41])
        R2r[1][2] = float(rw[42])
        R2r[2][0] = float(rw[43])
        R2r[2][1] = float(rw[44])
        R2r[2][2] = float(rw[45])
        el.rotoffsets[3].value = R2r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[2].value = Vector(( float(rw[46]), float(rw[47]), float(rw[48]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[3].value = Vector(( float(rw[49]), float(rw[50]), float(rw[51]) ))


        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_totj(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'total_joint'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[24])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1p = Matrix()
        R1p[0][0] = float(rw[6])
        R1p[0][1] = float(rw[7])
        R1p[0][2] = float(rw[8])
        R1p[1][0] = float(rw[9])
        R1p[1][1] = float(rw[10])
        R1p[1][2] = float(rw[11])
        R1p[2][0] = float(rw[12])
        R1p[2][1] = float(rw[13])
        R1p[2][2] = float(rw[14])
        el.rotoffsets[0].value = R1p.to_quaternion();

        el.rotoffsets.add()
        R1r = Matrix() 
        R1p[0][0] = float(rw[15])
        R1p[0][1] = float(rw[16])
        R1p[0][2] = float(rw[17])
        R1p[1][0] = float(rw[18])
        R1p[1][1] = float(rw[19])
        R1p[1][2] = float(rw[20])
        R1p[2][0] = float(rw[21])
        R1p[2][1] = float(rw[22])
        R1p[2][2] = float(rw[23])
        el.rotoffsets[1].value = R1r.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[25]), float(rw[26]), float(rw[27]) ))

        el.rotoffsets.add()
        R2p = Matrix()
        R2p[0][0] = float(rw[28])
        R2p[0][1] = float(rw[29])
        R2p[0][2] = float(rw[30])
        R2p[1][0] = float(rw[31])
        R2p[1][1] = float(rw[32])
        R2p[1][2] = float(rw[33])
        R2p[2][0] = float(rw[34])
        R2p[2][1] = float(rw[35])
        R2p[2][2] = float(rw[36])
        el.rotoffsets[2].value = R2p.to_quaternion();
        
        el.rotoffsets.add()
        R2r = Matrix()
        R2r[0][0] = float(rw[37])
        R2r[0][1] = float(rw[38])
        R2r[0][2] = float(rw[39])
        R2r[1][0] = float(rw[40])
        R2r[1][1] = float(rw[41])
        R2r[1][2] = float(rw[42])
        R2r[2][0] = float(rw[43])
        R2r[2][1] = float(rw[44])
        R2r[2][2] = float(rw[45])
        el.rotoffsets[3].value = R2r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[46]), float(rw[47]), float(rw[48]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[49]), float(rw[50]), float(rw[51]) ))

        el.import_function = "add.mbdyn_elem_totj"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_totj(rw, ed) function

## Displays total joint infos in the tools panel
def totj_info_draw(elem, layout):
    # TODO
    pass
# -----------------------------------------------------------
# end of totj_info_draw( function

## Creates the object representing a Total Joint element
def spawn_totj_element(elem, context):
    # TODO
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
            elem = ed['total_joint_' + str(self.int_label)]
            return spawn_totj_element(elem, context)
        except KeyError:
            self.report({'ERROR'}, "Element total_joint_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_TotalJoint_Element class


## Parses total pin joint entry in the .log file
def parse_totpinj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_totpinj(): Parsing total pin joint " + rw[1])
    try:
        el = ed['total_pin_joint_' + str(rw[1])]
        print("parse_totpinj(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1p = Matrix()
        R1p[0][0] = float(rw[6])
        R1p[0][1] = float(rw[7])
        R1p[0][2] = float(rw[8])
        R1p[1][0] = float(rw[9])
        R1p[1][1] = float(rw[10])
        R1p[1][2] = float(rw[11])
        R1p[2][0] = float(rw[12])
        R1p[2][1] = float(rw[13])
        R1p[2][2] = float(rw[14])

        el.rotoffsets[0].value = R1p.to_quaternion(); 

        R1r = Matrix()
        R2r[0][0] = float(rw[15])
        R2r[0][1] = float(rw[16])
        R2r[0][2] = float(rw[17])
        R2r[1][0] = float(rw[18])
        R2r[1][1] = float(rw[19])
        R2r[1][2] = float(rw[20])
        R2r[2][0] = float(rw[21])
        R2r[2][1] = float(rw[22])
        R2r[2][2] = float(rw[23])

        el.rotoffsets[1].value = R1r.to_quaternion(); 
        
        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[1].value = Vector(( float(rw[24]), float(rw[25]), float(rw[26]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[2].value = Vector(( float(rw[27]), float(rw[28]), float(rw[29]) ))

        pass
    except KeyError:
        print("parse_totpinj(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'total_pin_joint'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1p = Matrix()
        R1p[0][0] = float(rw[6])
        R1p[0][1] = float(rw[7])
        R1p[0][2] = float(rw[8])
        R1p[1][0] = float(rw[9])
        R1p[1][1] = float(rw[10])
        R1p[1][2] = float(rw[11])
        R1p[2][0] = float(rw[12])
        R1p[2][1] = float(rw[13])
        R1p[2][2] = float(rw[14])
        el.rotoffsets[0].value = R1p.to_quaternion();

        el.rotoffsets.add()
        R1r = Matrix() 
        R1p[0][0] = float(rw[15])
        R1p[0][1] = float(rw[16])
        R1p[0][2] = float(rw[17])
        R1p[1][0] = float(rw[18])
        R1p[1][1] = float(rw[19])
        R1p[1][2] = float(rw[20])
        R1p[2][0] = float(rw[21])
        R1p[2][1] = float(rw[22])
        R1p[2][2] = float(rw[23])
        el.rotoffsets[1].value = R1r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[24]), float(rw[25]), float(rw[26]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[27]), float(rw[28]), float(rw[29]) ))

        el.import_function = "add.mbdyn_elem_totpinj"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_totpinj(rw, ed) function

## Displays total pin joint infos in the tools panel
def totpinj_info_draw(elem, layout):
    # TODO
    pass
# -----------------------------------------------------------
# end of totpinj_info_draw(elem, layout) function

## Creates the object representing a Total Joint element
def spawn_totpinj_element(elem, context):
    # TODO
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
