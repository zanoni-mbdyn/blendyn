# --------------------------------------------------------------------------
# MBDynImporter -- file beamlib.py
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
import numpy as np
import csv

from mathutils import *
from math import *

import pdb

from bpy.app.handlers import persistent
from .utilslib import *

# helper function to parse beam2
def parse_beam2(rw, ed):
 
    ret_val = True

    # Debug message
    print("parse_beam2(): Parsing beam2 " + rw[1])
    try:
        el = ed['beam2_' + rw[1]]
        print("parse_beam2(): found existing entry in elements dictionary for element "\
                + rw[1] + ". Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        
        el.is_imported = True

        pass
    except KeyError:
        print("parse_beam2(): didn't find entry in elements dictionary. Creating one.")
        
        el = ed.add()
        el.type = 'beam2'
        el.int_label = int(rw[1])
        
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])
        
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        
        el.import_function = "add.mbdyn_elem_beam2"
        el.info_draw = "beam2_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        
        el.is_imported = True
        ret_val = False
        pass 
    return ret_val
# -----------------------------------------------------------
# end of parse_beam2(rw, ed) function

def parse_beam3(rw, ed):
    
    ret_val = True 
    # Debug message
    print("parse_beam3(): Parsing beam3 " + rw[1])
    
    try:

        el = ed['beam3_' + rw[1]]
        el.is_imported = False
        print("parse_beam3(): found existing entry in elements dictionary for element "\
                + rw[1] + ". Updating it.")
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])
        el.nodes[2].int_label = int(rw[10])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets[1].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))

        el.is_imported = True

        pass
    except KeyError:
        print("parse_beam3(): didn't find entry in elements dictionary. Creating one.")
        
        el = ed.add()
        el.is_imported = False
        el.type = 'beam3'
        el.int_label = int(rw[1])
        
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])
        
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        
        el.nodes.add()
        el.nodes[2].int_label = int(rw[10])
        
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
        
        el.import_function = "add.mbdyn_elem_beam3"
        el.info_draw = "beam3_info_draw"
        el.update = "update_beam3"
        el.name = el.type + "_" + str(el.int_label)
        
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_beam3(rw, ed) function

# function that displays beam2 info in panel -- [ optional ]
def beam2_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try: 
        node = nd['node_' + str(elem.nodes[0].int_label)]
        # Display node 1 info
        col.prop(node, "int_label", text = "Node 1 ID ")
        col.prop(node, "string_label", text = "Node 1 label ")
        col.prop(node, "blender_object", text = "Node 1 Object: ")
        col.enabled = False
           
        # Display offset of node 1 info
        row = layout.row()
        row.label(text = "offset 1 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[0], "value", text = "", slider = False)

        node = nd['node_' + str(elem.nodes[0].int_label)]
        
        # Display node 2 info
        col.prop(node, "int_label", text = "Node 2 ID ")
        col.prop(node, "string_label", text = "Node 2 label ")
        col.prop(node, "blender_object", text = "Node 2 Object: ")
        col.enabled = False
           
        # Display offset of node 2 info
        row = layout.row()
        row.label(text = "offset 2 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[1], "value", text = "", slider = False)
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of beam2_info_draw(elem, layout) function

# function that displays beam3 info in panel -- [ optional ]
def beam3_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try: 
        node = nd['node_' + str(elem.nodes[0].int_label)]
        # Display node 1 info
        col.prop(node, "int_label", text = "Node 1 ID ")
        col.prop(node, "string_label", text = "Node 1 label ")
        col.prop(node, "blender_object", text = "Node 1 Object: ")
        col.enabled = False
           
        # Display offset of node 1 info
        row = layout.row()
        row.label(text = "offset 1 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[0], "value", text = "", slider = False)

        node = nd['node_' + str(elem.nodes[1].int_label)] 
        # Display node 2 info
        col.prop(node, "int_label", text = "Node 2 ID ")
        col.prop(node, "string_label", text = "Node 2 label ")
        col.prop(node, "blender_object", text = "Node 2 Object: ")
        col.enabled = False
           
        # Display offset of node 2 info
        row = layout.row()
        row.label(text = "offset 2 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[1], "value", text = "", slider = False)
        layout.separator()

        node = nd['node_' + str(elem.nodes[2].int_label)] 
        # Display node 3 info
        col.prop(node, "int_label", text = "Node 3 ID ")
        col.prop(node, "string_label", text = "Node 3 label ")
        col.prop(node, "blender_object", text = "Node 3 Object: ")
        col.enabled = False
           
        # Display offset of node 3 info
        row = layout.row()
        row.label(text = "offset 3 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[2], "value", text = "", slider = False)
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of beam3_info_draw(elem, layout) function

# Creates the object representing a beam2 element
def spawn_beam2_element(elem, context):
    """ Draws a two node beam element as a line connecting two points 
        belonging to two objects """

    nd = context.scene.mbdyn.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_beam2_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return{'CANCELLED'}
 
    # try to find Blender objects associated with the nodes that 
    # the element connects
    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_beam2_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_beam2_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}
   
    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # names for curve and object
    beamobj_id = 'beam2_' + str(elem.int_label)
    beamcv_id = beamobj_id + '_cvdata'

    # check if the object is already present. If it is, remove it.
    if beamobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[beamobj_id])
       
    # check if the curve is already present. If it is, remove it.
    if beamcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[beamcv_id])

    # create a new curve
    cvdata = bpy.data.curves.new(beamcv_id, type = 'CURVE')
    cvdata.dimensions = '3D'
    polydata = cvdata.splines.new('POLY')
    polydata.points.add()

    # get offsets in local frame
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # assign coordinates of curve knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    p2 = n2OBJ.location + R2*Vector(( f2[0], f2[1], f2[2] ))

    polydata.points[0].co = p1.to_4d()
    polydata.points[1].co = p2.to_4d()

    # create the object
    beamOBJ = bpy.data.objects.new(beamobj_id, cvdata)
    beamOBJ.mbdyn.type = 'elem.beam'
    beamOBJ.mbdyn.dkey = elem.name
    beamOBJ.mbdyn.int_label = elem.int_label
    bpy.context.scene.objects.link(beamOBJ)
    elem.blender_object = beamOBJ.name

    # P1 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n1OBJ.select = True
    beamOBJ.select = True
    bpy.context.scene.objects.active = beamOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    beamOBJ.data.splines[0].points[0].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # P2 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n2OBJ.select = True
    beamOBJ.select = True
    bpy.context.scene.objects.active = beamOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    beamOBJ.data.splines[0].points[1].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # add drivers for bevel section rotation
    drv_tilt_P1 = beamOBJ.data.splines[0].points[0].driver_add('tilt')
    xrot_P1 = drv_tilt_P1.driver.variables.new()
    xrot_P1.name = "xrot_P1"
    xrot_P1.type = 'TRANSFORMS'
    xrot_P1.targets[0].id = n1OBJ
    xrot_P1.targets[0].data_path = 'rotation.x'
    xrot_P1.targets[0].transform_type = 'ROT_X'
    xrot_P1.targets[0].transform_space = 'WORLD_SPACE'
    drv_tilt_P1.driver.expression = "xrot_P1"

    drv_tilt_P2 = beamOBJ.data.splines[0].points[1].driver_add('tilt')
    xrot_P2 = drv_tilt_P2.driver.variables.new()
    xrot_P2.name = "xrot_P2"
    xrot_P2.type = 'TRANSFORMS'
    xrot_P2.targets[0].id = n2OBJ
    xrot_P2.targets[0].data_path = 'rotation.x'
    xrot_P2.targets[0].transform_type = 'ROT_X'
    xrot_P2.targets[0].transform_space = 'WORLD_SPACE'
    drv_tilt_P2.driver.expression = "xrot_P2"

    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')

    # create group for element
    beamOBJ.select = True
    n1OBJ.select = True
    n2OBJ.select = True
    bpy.ops.group.create(name = beamOBJ.name)

    elem.is_imported = True
    return {'FINISHED'}

# -----------------------------------------------------------
# end of spawn_beam2_element(elem, context) function

## Creates the object representing a beam3 element
def spawn_beam3_element(elem, context):
    """ Draws a beam3 element as a nurbs order 3 curve connecting three
        points belonging to three objects (and their associated MBDyn nodes """

    nd = context.scene.mbdyn.nodes
    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_beam3_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return{'CANCELLED'}

    # try to find Blender objects associated with the nodes that 
    # the element connects

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_beam3_element()): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_beam3_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}
    
    try:
        n3 = nd['node_' + str(elem.nodes[2].int_label)].blender_object
    except KeyError:
        print("spawn_beam3_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[2].int_label))
        return {'NODE3_NOTFOUND'}

    # Create the NURBS order 3 curve
    beamobj_id = 'beam3_' + str(elem.int_label)
    beamcv_id = beamobj_id + '_cvdata'

    # Check if the object is already present. If it is, remove it.
    if beamobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[beamobj_id])
    
    # check if the curve is already present. If it is, remove it.
    if beamcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[beamcv_id])

    cvdata = bpy.data.curves.new(beamcv_id, type = 'CURVE')
    cvdata.dimensions = '3D'
    polydata = cvdata.splines.new('NURBS')
    polydata.points.add(3)
    polydata.order_u = 3
    polydata.use_endpoint_u = True
    
    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    f3 = elem.offsets[2].value

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]
    n3OBJ = bpy.data.objects[n3]

    # refline points in global frame
    P1 = n1OBJ.matrix_world*Vector(( f1[0], f1[1], f1[1], 1.0 ))
    P2 = n2OBJ.matrix_world*Vector(( f2[0], f2[1], f2[1], 1.0 ))
    P3 = n3OBJ.matrix_world*Vector(( f3[0], f3[1], f3[1], 1.0 ))

    # define the two intermediate control points
    t1 = -3*P1 + 4*P2 - P3
    t1.normalize()

    t2 = -P1 + P3
    t2.normalize()

    T = np.zeros((4,2))
    T[:,0] = t1
    T[:,1] = -t2

    d = np.linalg.pinv(T).dot(np.array((P2 - P1)))

    M1 = Vector(( P2 + Vector((d[1]*t2)) ))
    M2 = Vector(( P2 - Vector((d[1]*t2)) ))
    
    polydata.points[0].co = P1
    polydata.points[1].co = M1
    polydata.points[2].co = M2
    polydata.points[3].co = P3

    # set the tilt angles of the sections
    t3 = P3 - M2
    t3.normalize()

    phi1, theta1 = n1OBJ.matrix_world.to_quaternion().to_axis_angle()
    phi2, theta2 = n2OBJ.matrix_world.to_quaternion().to_axis_angle()
    phi3, theta3 = n3OBJ.matrix_world.to_quaternion().to_axis_angle()
    
    polydata.points[0].tilt = t1.to_3d()*(theta1*phi1)
    polydata.points[1].tilt = t2.to_3d()*(theta2*phi2)
    polydata.points[2].tilt = t2.to_3d()*(theta2*phi2)
    polydata.points[3].tilt = t3.to_3d()*(theta3*phi3)

    # create the object
    beamOBJ = bpy.data.objects.new(beamobj_id, cvdata)
    beamOBJ.mbdyn.type = 'elem.beam'
    beamOBJ.mbdyn.dkey = elem.name
    ude = bpy.context.scene.mbdyn.elems_to_update.add()
    ude.dkey = elem.name
    ude.name = elem.name
    beamOBJ.mbdyn.int_label = elem.int_label

    bpy.context.scene.objects.link(beamOBJ)
    elem.blender_object = beamOBJ.name
    beamOBJ.select = True

    # Hook control points
    bpy.ops.object.empty_add(type = 'PLAIN_AXES', location = M1[0:3])
    obj2 = bpy.context.scene.objects.active
    obj2.name = beamOBJ.name + '_M1'
    obj2.select = False

    bpy.ops.object.empty_add(type = 'PLAIN_AXES', location = M2[0:3])
    obj3 = bpy.context.scene.objects.active
    obj3.name = beamOBJ.name + '_M2'
    obj3.select = False

    # P1 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n1OBJ.select = True
    beamOBJ.select = True
    bpy.context.scene.objects.active = beamOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    beamOBJ.data.splines[0].points[0].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # M1 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    obj2.select = True
    beamOBJ.select = True
    bpy.context.scene.objects.active = beamOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    beamOBJ.data.splines[0].points[1].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # M2 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    obj3.select = True
    beamOBJ.select = True
    bpy.context.scene.objects.active = beamOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    beamOBJ.data.splines[0].points[2].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # P3 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n3OBJ.select = True
    beamOBJ.select = True
    bpy.context.scene.objects.active = beamOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    beamOBJ.data.splines[0].points[3].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
 
    bpy.ops.object.select_all(action = 'DESELECT')

    if False:   # NOT CORRECT! -- Moved to update_beam3
        # P1 driver for bevel section rotation
        drv_tilt_P1 = beamOBJ.data.splines[0].points[0].driver_add('tilt')
        xrot_P1 = drv_tilt_P1.driver.variables.new()
        xrot_P1.name = "xrot_P1"
        xrot_P1.type = 'TRANSFORMS'
        xrot_P1.targets[0].id = n1OBJ
        xrot_P1.targets[0].data_path = 'rotation.x'
        xrot_P1.targets[0].transform_type = 'ROT_X'
        xrot_P1.targets[0].transform_space = 'WORLD_SPACE'
        drv_tilt_P1.driver.expression = "xrot_P1"
    
        # P3 driver for bevel section rotation
        drv_tilt_P3 = beamOBJ.data.splines[0].points[3].driver_add('tilt')
        xrot_P3 = drv_tilt_P3.driver.variables.new()
        xrot_P3.name = "xrot_P3"
        xrot_P3.type = 'TRANSFORMS'
        xrot_P3.targets[0].id = n3OBJ
        xrot_P3.targets[0].data_path = 'rotation.x'
        xrot_P3.targets[0].transform_type = 'ROT_X'
        xrot_P3.targets[0].transform_space = 'WORLD_SPACE'
        drv_tilt_P3.driver.expression = "xrot_P3"
    
        # M1 driver for bevel section rotation (TODO: check correctness)
        drv_tilt_M1 = beamOBJ.data.splines[0].points[1].driver_add('tilt')
        xrot_P2_1 = drv_tilt_M1.driver.variables.new()
        xrot_P2_1.name = "xrot_P2"
        xrot_P2_1.type = 'TRANSFORMS'
        xrot_P2_1.targets[0].id = n2OBJ
        xrot_P2_1.targets[0].data_path = 'rotation.x'
        xrot_P2_1.targets[0].transform_type = 'ROT_X'
        xrot_P2_1.targets[0].transform_space = 'WORLD_SPACE'
        drv_tilt_M1.driver.expression = "xrot_P2"
        
        # M2 driver for bevel section rotation (TODO: check correctness)
        drv_tilt_M2 = beamOBJ.data.splines[0].points[2].driver_add('tilt')
        xrot_P2_2 = drv_tilt_M2.driver.variables.new()
        xrot_P2_2.name = "xrot_P2"
        xrot_P2_2.type = 'TRANSFORMS'
        xrot_P2_2.targets[0].id = n2OBJ
        xrot_P2_2.targets[0].data_path = 'rotation.x'
        xrot_P2_2.targets[0].transform_type = 'ROT_X'
        xrot_P2_2.targets[0].transform_space = 'WORLD_SPACE'
        drv_tilt_M2.driver.expression = "xrot_P2"
        
    beamOBJ.select = True
    n1OBJ.select = True
    n2OBJ.select = True
    n3OBJ.select = True
    obj2.select = True
    obj3.select = True
    bpy.ops.group.create(name = beamOBJ.name)
    elem.is_imported = True

    obj2.hide = True
    obj3.hide = True

    bpy.ops.object.select_all(action = 'DESELECT')
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_beam3_element(elem, context) function

def update_beam3(elem, insert_keyframe = False):
    """ Updates the configuration of a 3-node beam by re-computing 
        the positions of the two intermediate control points """

    cvdata = bpy.data.objects[elem.blender_object].data
    nd = bpy.context.scene.mbdyn.nodes

    # find nodes' Blender objects
    try:
        cp2 = bpy.data.objects[elem.blender_object + '_M1'] 
        cp3 = bpy.data.objects[elem.blender_object + '_M2'] 
        n1 = bpy.data.objects[nd['node_' + str(elem.nodes[0].int_label)].blender_object]
        n2 = bpy.data.objects[nd['node_' + str(elem.nodes[1].int_label)].blender_object]
        n3 = bpy.data.objects[nd['node_' + str(elem.nodes[2].int_label)].blender_object]
    except KeyError:
        print("update_beam3(): Could not find a Blender object " + \
                str(elem.nodes[1].int_label))
        return {'OBJECTS_NOTFOUND'}

    # offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    f3 = elem.offsets[2].value

    # points on beam
    P1 = n1.matrix_world*Vector(( f1[0], f1[1], f1[2], 1.0 ))
    P2 = n2.matrix_world*Vector(( f2[0], f2[1], f2[2], 1.0 ))
    P3 = n3.matrix_world*Vector(( f3[0], f3[1], f3[2], 1.0 ))

    # redefine the two intermediate control points
    t1 = -3*P1 + 4*P2 - P3
    t1.normalize()

    t2 = -P1 + P3
    t2.normalize()

    T = np.zeros((4,2))
    T[:,0] = t1
    T[:,1] = -t2

    d = np.linalg.pinv(T).dot(np.array((P2 - P1)))

    cp2.location = Vector(( P2 + Vector((d[1]*t2)) )).to_3d()
    cp3.location = Vector(( P2 - Vector((d[1]*t2)) )).to_3d()

    # set the tilt angles of the sections
    t3 = P3.to_3d() - cp2.location
    t3.normalize()

    phi1, theta1 = n1.matrix_world.to_quaternion().to_axis_angle()
    phi2, theta2 = n2.matrix_world.to_quaternion().to_axis_angle()
    phi3, theta3 = n3.matrix_world.to_quaternion().to_axis_angle()
    
    cvdata.splines[0].points[0].tilt = t1.to_3d()*(theta1*phi1)
    cvdata.splines[0].points[1].tilt = t2.to_3d()*(theta2*phi2)
    cvdata.splines[0].points[2].tilt = t2.to_3d()*(theta2*phi2)
    cvdata.splines[0].points[3].tilt = t3.to_3d()*(theta3*phi3)
    

    if insert_keyframe:
        try:
            cp2.select = True
            cp2.keyframe_insert(data_path = "location")
            
            cp3.select = True
            cp3.keyframe_insert(data_path = "location")
            
        except RuntimeError as err:
            if 'context is incorrect' in str(err):
                pass
            else:
                self.report({'WARNING'}, str(err))
        except TypeError:
            pass

    return {'FINISHED'}
# -----------------------------------------------------------
# end of update_beam3() function


## Imports a Beam 2 element in the scene as a line joining two nodes
class Scene_OT_MBDyn_Elems_Import_Beam2(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_beam2"
    bl_label = "MBDyn rod element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        try: 
            elem = ed['beam2_' + str(self.int_label)]
            retval = spawn_beam2_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'NODE2_NOTFOUND':
                self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[1].int_label) + " not found")
                return {'CANCELLED'}
            else:
                return retval

        except KeyError:
            self.report({'ERROR'}, "Element beam2_" + str(elem.int_label) + "not found.")
            return {'CANCELLED'}
            
        return {'FINISHED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Elems_Import_Beam2 class

## Imports a Beam 3 element in the scene as a line joining two nodes
class Scene_OT_MBDyn_Elems_Import_Beam3(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_beam3"
    bl_label = "MBDyn rod element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        try: 
            elem = ed['beam3_' + str(self.int_label)]
            retval = spawn_beam3_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'NODE2_NOTFOUND':
                self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[1].int_label) + " not found")
                return {'CANCELLED'}
            elif retval == 'NODE3_NOTFOUND':
                self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[2].int_label) + " not found")
                return {'CANCELLED'}
            else:
                return retval

        except KeyError:
            self.report({'ERROR'}, "Element beam3_" + str(elem.int_label) + "not found.")
            return {'CANCELLED'}
            
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Elems_Import_Beam3 class

class Object_OT_MBDyn_update_beam3(bpy.types.Operator):
    """ Calls the update_beam3() function to update the current configuration
        of the curve representing the beam3 element """
    bl_idname = "update.mbdyn_beam3"
    bl_label = "Updates beam3 curve configuration"

    def execute(self, context):
        ed = context.scene.mbdyn.elems
        ret_val = update_beam3(ed[context.object.name])
        if ret_val == 'OBJECTS_NOTFOUND':
            self.report({'ERROR'}, "Unable to find Blender objects needed")
            return {'CANCELLED'}
        else:
            return ret_val
        pass

