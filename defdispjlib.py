# --------------------------------------------------------------------------
# Blendyn -- file defdisplib.py
# Copyright (C) 2015 -- 2017 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import logging

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

from .utilslib import parse_rotmat

# helper function to parse deformable displacement joints
def parse_deformable_displacement(rw, ed):
    ret_val = True
    # Debug message
    print("parse_deformable_displacementj(): Parsing deformable displacement joint " + rw[1])
    try:
        el = ed['deformable_displacement_' + str(rw[1])]

        print("parse_deformable_displacement(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        R1 = Matrix()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion(); 
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))
        
        R2 = Matrix()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion(); 
        
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True 
    except KeyError:
        print("parse_deformable_displacement(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'deformable_displacement'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[15])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        el.rotoffsets.add()
        R2 = Matrix()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        el.import_function = "add.mbdyn_elem_deformable_displacement"
        el.update = "update_defdisp"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_deformable_displacement(rw, ed) function

def update_defdisp(elem, insert_keyframe = False):

    nd = bpy.context.scene.mbdyn.nodes

    distOBJ = bpy.data.objects[elem.blender_object]
    n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # assign coordinates of knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1 * Vector((f1[0], f1[1], f1[2]))
    p2 = n2OBJ.location + R2 * Vector((f2[0], f2[1], f2[2]))

    distOBJ.location = (p2 + p1)/2
    length = (p2 - p1).length
    change = length - elem.magnitude
    distOBJ.modifiers['SimpleDeform'].factor = change



# Creates the object representing a deformable displacement joint element
def spawn_defdispj_element(elem, context):
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_distance_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_distance_element(): Could not find a Blender \
                object associated to Node " + \
              str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_distance_element(): Could not find a Blender \
                object associated to Node " + \
              str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # creation of line representing the dist
    distobj_id = 'dist_' + str(elem.int_label)
    distcv_id = distobj_id + '_cvdata'

    # check if the object is already present. If it is, remove it.
    if distobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[distobj_id])

    # check if the curve is already present. If it is, remove it.
    if distcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[distcv_id])

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # assign coordinates of knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1 * Vector((f1[0], f1[1], f1[2]))
    p2 = n2OBJ.location + R2 * Vector((f2[0], f2[1], f2[2]))

    # create a new curve
    length = (p2 - p1).length
    elem.magnitude = length
    radius = 0.3 * length
    turns = 20
    bpy.ops.mesh.curveaceous_galore(ProfileType='Helix', helixHeight=length, helixWidth=radius, helixEnd = 360* turns, helixPoints = 1000)
    distOBJ = bpy.context.scene.objects.active
    bpy.ops.object.origin_set(type = 'ORIGIN_CENTER_OF_MASS')

    distOBJ.location = (p2 +p1)/2
    elem.blender_object = elem.name
    distOBJ.name = elem.name
    ude = bpy.context.scene.mbdyn.elems_to_update.add()
    ude.dkey = elem.name
    ude.name = elem.name

    # Give the object an elastic nature
    bpy.ops.object.select_all(action='DESELECT')
    distOBJ.select = True
    bpy.context.scene.objects.active = distOBJ
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    distOBJ.modifiers['SimpleDeform'].deform_method = 'STRETCH'
    distOBJ.modifiers['SimpleDeform'].lock_x = True
    distOBJ.modifiers['SimpleDeform'].lock_y = True
    distOBJ.modifiers['SimpleDeform'].factor = 0.0

    # create group for element
    distOBJ.select = True
    n1OBJ.select = True
    n2OBJ.select = True
    bpy.ops.group.create(name=distOBJ.name)

    elem.is_imported = True

    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_deformable_displacament_element(elem, context) function

## Imports a Deformable Displacement Joint in the scene -- TODO
class Scene_OT_MBDyn_Import_Deformable_Displacement_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_deformable_displacement"
    bl_label = "MBDyn deformable displacement joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['deformable_displacement_' + str(self.int_label)]
            return spawn_defdispj_element(elem, context)
        except KeyError:
            message = "Element deformable_displacement_" + str(elem.int_label) \
                   + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Deformable_Displacement_Element class
