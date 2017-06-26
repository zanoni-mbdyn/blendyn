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
def parse_defdisp(rw, ed):
    ret_val = True
    # Debug message
    print("parse_defdispj(): Parsing deformable displacement joint " + rw[1])
    try:
        el = ed['defdisp_' + str(rw[1])]

        print("parse_defdisp(): found existing entry in elements dictionary. Updating it.")
        
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
        print("parse_defdisp(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'defdisp'
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

        el.import_function = "add.mbdyn_elem_defdisp"
        el.update = "update_defdisp"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_defdisp(rw, ed) function

def update_defdisp(elem, insert_keyframe = False):

    nd = bpy.context.scene.mbdyn.nodes

    defdispOBJ = bpy.data.objects[elem.blender_object]
    n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    q1 = elem.rotoffsets[0].value
    q2 = elem.rotoffsets[1].value

    # assign coordinates of knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1 * Vector((f1[0], f1[1], f1[2]))
    p2 = n2OBJ.location + R2 * Vector((f2[0], f2[1], f2[2]))

    R1h =  Quaternion(( q1[0], q1[1], q1[2], q1[3] )).to_matrix()

    defdispOBJ.location = (p2 + p1)/2
    def_vector = (p2 - p1)
    def_vector = R1h.transposed() * R1.transposed() * def_vector
    print(def_vector)
    axes = ['X', 'Y', 'Z']
    for ii in range(3):
        defdispChild = bpy.data.objects[defdispOBJ.name + '.' + axes[ii]]
        defdispChild.dimensions[2] = def_vector[ii]


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
    defdispobj_id = 'dist_' + str(elem.int_label)
    defdispcv_id = defdispobj_id + '_cvdata'

    # check if the object is already present. If it is, remove it.
    if defdispobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[defdispobj_id])

    # check if the curve is already present. If it is, remove it.
    if defdispcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[defdispcv_id])

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    q1 = elem.rotoffsets[0].value
    q2 = elem.rotoffsets[1].value

    # assign coordinates of knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1 * Vector((f1[0], f1[1], f1[2]))
    p2 = n2OBJ.location + R2 * Vector((f2[0], f2[1], f2[2]))

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    defdispOBJ = bpy.context.scene.objects.active
    defdispOBJ.location = (p2 +p1)/2
    defdispOBJ.rotation_mode = 'QUATERNION'
    defdispOBJ.rotation_quaternion = n2OBJ.rotation_quaternion * Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

    elem.blender_object = elem.name
    defdispOBJ.name = elem.name
    ude = bpy.context.scene.mbdyn.elems_to_update.add()
    ude.dkey = elem.name
    ude.name = elem.name

    length = (p2 - p1)
    length = Vector(map(abs, length))
    radius = 0.3 * length
    print(length, radius)
    turns = 20
    axes = ['X', 'Y', 'Z']
    for ii in range(3):
        bpy.ops.mesh.curveaceous_galore(ProfileType='Helix', helixHeight=length[ii],\
                                        helixWidth=radius[ii], helixEnd = 360* turns, helixPoints = 1000)
        defdispChild = bpy.context.scene.objects.active
        bpy.ops.object.origin_set(type = 'ORIGIN_CENTER_OF_MASS')
        track_axes = axes[:]
        track_axes.remove(track_axes[ii])
        defdispChild.location = (p2 +p1)/2
        defdispChild.rotation_mode = 'QUATERNION'
        axis_direction = Vector((0, 0, 0))
        axis_direction[ii] = 1
        defdispChild.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)
        defdispChild.name = defdispOBJ.name + '.' + axes[ii]

        #Set parent to defdispOBJ
        bpy.ops.object.select_all(action='DESELECT')
        defdispChild.select = True
        defdispOBJ.select = True
        bpy.context.scene.objects.active = defdispOBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    # Set parent to n1OBJ
    bpy.ops.object.select_all(action='DESELECT')
    defdispOBJ.select = True
    n1OBJ.select = True
    bpy.context.scene.objects.active = n1OBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    elem.is_imported = True

    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_defdispj_element(elem, context) function

## Imports a Deformable Displacement Joint in the scene -- TODO
class Scene_OT_MBDyn_Import_Deformable_Displacement_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_defdisp"
    bl_label = "MBDyn deformable displacement joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['defdisp_' + str(self.int_label)]
            return spawn_defdispj_element(elem, context)
        except KeyError:
            message = "Element defdisp_" + str(elem.int_label) \
                   + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Deformable_Displacement_Element class
