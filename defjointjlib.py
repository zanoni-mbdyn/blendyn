# --------------------------------------------------------------------------
# Blendyn -- file defjointlib.py
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
from .nurbsPoints import calc_nurbs

# helper function to parse deformable hinge joints
def parse_defjoint(rw, ed):
    ret_val = True
    # Debug message
    print("parse_defjointj(): Parsing deformable hinge joint " + rw[1])
    try:
        el = ed['defjoint_' + str(rw[1])]

        print("parse_defjoint(): found existing entry in elements dictionary. Updating it.")

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
        print("parse_defjoint(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'defjoint'
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

        el.import_function = "add.mbdyn_elem_defjoint"
        el.update = "update_defjoint"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_defjoint(rw, ed) function

def update_defjoint(elem, insert_keyframe = False):

    nd = bpy.context.scene.mbdyn.nodes

    defjointOBJ = bpy.data.objects[elem.blender_object]
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

    #Linear Deformation Vector
    R1h =  Quaternion(( q1[0], q1[1], q1[2], q1[3] )).to_matrix()

    def_vector = (p2 - p1)
    def_vector = R1h.transposed() * R1.transposed() * def_vector

    #Angular Deformation Vector
    q1h_tilde = Quaternion((q1))
    rotation1 = n1OBJ.matrix_world.to_quaternion()
    q2h_tilde = Quaternion((q1))
    rotation2 = n2OBJ.matrix_world.to_quaternion()

    q1h = q1h_tilde*rotation1
    q2h = q2h_tilde*rotation2
    qrel = q2h*q1h.conjugated()
    n, theta = qrel.to_axis_angle()
    phi = n*theta

    axes = ['X', 'Y', 'Z']
    previous = Vector((0, 0, 0))
    obj_loc = def_vector / 2
    for ii in range(3):
        defjointChild = bpy.data.objects[defjointOBJ.name + '.disp.' + axes[ii]]

        #Apply Linear Deformation
        defjointChild.location = defjointOBJ.rotation_quaternion * (Vector(obj_loc[:ii+1] + (0, )* (2 - ii)) + previous)
        previous = Vector(obj_loc[:ii + 1] + (0, )* (2 - ii))
        defjointChild.dimensions[2] = def_vector[ii]

        beamobj_id = defjointOBJ.name + '.curve.' + axes[ii]
        bpy.context.scene.objects.active = bpy.data.objects[beamobj_id]
        bpy.ops.object.mode_set(mode='EDIT')

        beamcv_id = beamobj_id + '_cvdata'

        cvdata = bpy.data.curves[beamcv_id]
        polydata = cvdata.splines[0]

        angle = degrees(phi[ii])
        nurbsPoints = calc_nurbs(angle, 1, ii)

        for jj in range(9):
            polydata.points[jj].co = (p1 + nurbsPoints[jj][0]).to_4d()
            polydata.points[jj].co[3] = nurbsPoints[jj][1]

        bpy.ops.object.mode_set(mode='OBJECT')


# Creates the object representing a deformable hinge joint element
def spawn_defjointj_element(elem, context):
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
    defjointobj_id = 'dist_' + str(elem.int_label)
    defjointcv_id = defjointobj_id + '_cvdata'

    # check if the object is already present. If it is, remove it.
    if defjointobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[defjointobj_id])

    # check if the curve is already present. If it is, remove it.
    if defjointcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[defjointcv_id])

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

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    defjointOBJ = bpy.context.scene.objects.active
    defjointOBJ.rotation_mode = 'QUATERNION'
    defjointOBJ.rotation_quaternion = n1OBJ.rotation_quaternion * Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

    # Set parent to n1OBJ
    bpy.ops.object.select_all(action='DESELECT')
    defjointOBJ.select = True
    n1OBJ.select = True
    bpy.context.scene.objects.active = n1OBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    defjointOBJ.location = p1

    elem.blender_object = elem.name
    defjointOBJ.name = elem.name
    ude = bpy.context.scene.mbdyn.elems_to_update.add()
    ude.dkey = elem.name
    ude.name = elem.name

    q1h_tilde = Quaternion((q1))
    rotation1 = n1OBJ.matrix_world.to_quaternion()
    q2h_tilde = Quaternion((q1))
    rotation2 = n2OBJ.matrix_world.to_quaternion()

    q1h = q1h_tilde*rotation1
    q2h = q2h_tilde*rotation2
    qrel = q2h*q1h.conjugated()
    n, theta = qrel.to_axis_angle()
    phi = n*theta

    axes = ['X', 'Y', 'Z']

    for ii in range(3):

        # Create the NURBS order 3 curve
        beamobj_id = defjointOBJ.name + '.curve.' + axes[ii]
        beamcv_id = beamobj_id + '_cvdata'

        # Check if the object is already present. If it is, remove it.
        if beamobj_id in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[beamobj_id])

        # check if the curve is already present. If it is, remove it.
        if beamcv_id in bpy.data.curves.keys():
            bpy.data.curves.remove(bpy.data.curves[beamcv_id])

        # create a new curve
        cvdata = bpy.data.curves.new(beamcv_id, type = 'CURVE')
        cvdata.dimensions = '3D'
        cvdata.use_stretch = True
        cvdata.use_deform_bounds = True
        polydata = cvdata.splines.new('NURBS')
        polydata.points.add(8)

        angle = degrees(phi[ii])
        nurbsPoints = calc_nurbs(angle, 1, ii)


        for jj in range(9):
            polydata.points[jj].co = (p1 + nurbsPoints[jj][0]).to_4d()
            polydata.points[jj].co[3] = nurbsPoints[jj][1]

        defjointCurveOBJ = bpy.data.objects.new(beamobj_id, cvdata)
        cvdata.splines[0].use_endpoint_u = True
        bpy.context.scene.objects.link(defjointCurveOBJ)

        bpy.context.scene.objects.active = defjointCurveOBJ
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')


        bpy.ops.object.select_all(action='DESELECT')
        defjointCurveOBJ.select = True
        defjointOBJ.select = True
        bpy.context.scene.objects.active = defjointOBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    for ii in range(3):

        length = 2*pi*1
        radius = 0.05*length
        turns = 5*length
        bpy.ops.mesh.curveaceous_galore(ProfileType='Helix', helixHeight=length,\
                                        helixWidth=radius, helixEnd = 360 * turns, helixPoints = 1000)
        defjointChild = bpy.context.scene.objects.active

        defjointChild.location = p1

        defjointChild.name = defjointOBJ.name + '.rot.' + axes[ii]

        bpy.context.scene.objects.active = defjointChild
        bpy.ops.object.modifier_add(type='CURVE')
        defjointChild.modifiers['Curve'].object = bpy.data.objects[defjointOBJ.name + '.curve.' + axes[ii]]
        defjointChild.modifiers['Curve'].deform_axis = 'POS_Z'

        #Set parent to defjointOBJ
        bpy.ops.object.select_all(action='DESELECT')
        defjointChild.select = True
        defjointOBJ.select = True
        bpy.context.scene.objects.active = defjointOBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    length = (p2 - p1)
    length = R1h.transposed() * R1.transposed() * length
    length = Vector(map(abs, length))
    radius = 0.3 * length
    turns = 15

    previous = Vector((0, 0, 0))

    for ii in range(3):
        rad_helix, len_helix = radius[ii], length[ii]
        if rad_helix < 0.1:
            rad_helix = 0.02
            len_helix = rad_helix/ 0.3
        bpy.ops.mesh.curveaceous_galore(ProfileType='Helix', helixHeight=len_helix,\
                                        helixWidth=rad_helix, helixEnd = 360* turns, helixPoints = 1000)
        bpy.ops.object.origin_set(type = 'ORIGIN_CENTER_OF_MASS')
        defjointChild = bpy.context.scene.objects.active

        defjointChild.location = Vector((0, 0, 0))
        #Set parent to defjointOBJ
        bpy.ops.object.select_all(action='DESELECT')
        defjointChild.select = True
        defjointOBJ.select = True
        bpy.context.scene.objects.active = defjointOBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        track_axes = axes[:]
        track_axes.remove(track_axes[ii])
        obj_loc = (p2 - p1)
        obj_loc = R1h.transposed() * R1.transposed() * obj_loc
        obj_loc = obj_loc / 2
        defjointChild.location = defjointOBJ.rotation_quaternion * (Vector(obj_loc[:ii+1] + (0, )* (2 - ii)) + previous)
        previous = Vector(obj_loc[:ii + 1] + (0, )* (2 - ii))
        defjointChild.rotation_mode = 'QUATERNION'
        axis_direction = Vector((0, 0, 0))
        axis_direction[ii] = 1
        defjointChild.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)
        defjointChild.rotation_quaternion =  defjointOBJ.rotation_quaternion *\
                                            defjointChild.rotation_quaternion
        defjointChild.name = defjointOBJ.name + '.disp.' + axes[ii]

    elem.is_imported = True

    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_defjointj_element(elem, context) function

# Imports a Deformable Joint in the scene -- TODO
class Scene_OT_MBDyn_Import_Deformable_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_defjoint"
    bl_label = "MBDyn deformable joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['defjoint_' + str(self.int_label)]
            return spawn_defjointj_element(elem, context)
        except KeyError:
            message = "Element defjoint_" + str(elem.int_label) \
                   + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Deformable_Joint_Element class