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
import os

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

# helper function to parse revolute joints
def parse_revj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_revj(): Parsing revolute hinge joint " + rw[1])
    try:
        el = ed['revolute_hinge_' + str(rw[1])]
        print("parse_revj(): found existing entry in elements dictionary. Updating it.")
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
        print("parse_revj(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'revolute_hinge'
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

        el.import_function = "add.mbdyn_elem_revj"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
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
        el = ed['revolute_pin_' + str(rw[1])]
        print("parse_revpinj(): found existing entry in elements dictionary. Updating it.")
        el.nodes[0].int_label = int(rw[2])
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
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_revpinj(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'revolute_pin'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

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

        el.import_function = "add.mbdyn_elem_revpinj"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_revpinj(rw, ed) function

# Creates the object representing a revolute joint element
def spawn_revj_element(elem, context):
    """ Draws a revolute joint element, loading a wireframe
        object from the addon library """

    mbs = bpy.context.scene.mbdyn

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_revj_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return{'CANCELLED'}

    # TODO: Complete

    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'mbdyb-blender-master', 'library', 'cj.blend', \
            'Object'), filename = 'revolute')

    revobj = [obj for obj in bpy.data.objects if obj.select = True]
    revobj[0].name = elem.name

    return retval
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
    # TODO
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
    # TODO
    pass
# -------------------------------------------------------------------------- 
# end of revj_info_draf(elem, layout) function

# Displays revolute joint infos in the tools panel [ optional ]
def revpinj_info_draw(elem, layout):
    # TODO
    pass
# -------------------------------------------------------------------------- 
# end of revpinj_info_draf(elem, layout) function
