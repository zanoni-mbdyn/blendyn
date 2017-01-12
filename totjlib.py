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
import os

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

from .utilslib import parse_rotmat

## Parses total joint entry in .log file
def parse_total(rw, ed):
    ret_val = True
    # Debug message
    print("parse_total(): Parsing total joint " + rw[1])
    try:
        el = ed['total_joint_' + str(rw[1])]
        print("parse_total(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[24])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1p = Matrix()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion(); 

        R1r = Matrix()
        parse_rotmat(rw, 15, R1r)
        el.rotoffsets[1].value = R1r.to_quaternion(); 
        
        el.offsets[1].value = Vector(( float(rw[25]), float(rw[26]), float(rw[27]) ))

        R2p = Matrix()
        parse_rotmat(rw, 28, R2p)
        el.rotoffsets[2].value = R2p.to_quaternion();
        
        R2r = Matrix()
        parse_rotmat(rw, 37, R2r)
        el.rotoffsets[3].value = R2r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[2].value = Vector(( float(rw[46]), float(rw[47]), float(rw[48]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the rotation constraints that are active
        el.offsets[3].value = Vector(( float(rw[49]), float(rw[50]), float(rw[51]) ))


        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("parse_total(): didn't found en entry in elements dictionary. Creating one.")
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
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion();

        el.rotoffsets.add()
        R1r = Matrix() 
        parse_rotmat(rw, 15, R1r)
        el.rotoffsets[1].value = R1r.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[25]), float(rw[26]), float(rw[27]) ))

        el.rotoffsets.add()
        R2p = Matrix()
        parse_rotmat(rw, 28, R2p)
        el.rotoffsets[2].value = R2p.to_quaternion();
        
        el.rotoffsets.add()
        R2r = Matrix()
        parse_rotmat(rw, 37, R2r)
        el.rotoffsets[3].value = R2r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[46]), float(rw[47]), float(rw[48]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the rotation constraints that are active
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[49]), float(rw[50]), float(rw[51]) ))

        el.import_function = "add.mbdyn_elem_total"
        el.info_draw = "total_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_total(rw, ed) function

## Creates the object representing a Total Joint element
def spawn_total_element(elem, context):
    """ Draws a total joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_total_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_total_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_total_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # load the wireframe total joint object from the library
    lib_path = os.path.join(mbs.addon_path,\
            'mbdyn-blender-master', 'library', 'joints.blend', \
            'Object')
    app_retval = bpy.ops.wm.append(directory = lib_path, filename = 'total')

    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        totjOBJ = bpy.context.selected_objects[0]
        totjOBJ.name = elem.name
    else:
        return {'LIBRARY_ERROR'}

    # joint offsets with respect to nodes
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # "position orientation" w.r.t. node 1
    qp1 = elem.rotoffsets[0].value

    # "rotation orientation" w.r.t node 1
    qr1 = elem.rotoffsets[1].value

    # "position orientation" w.r.t. node 2
    qp2 = elem.rotoffsets[2].value

    # "rotation orientation" w.r.t. node 2
    qr2 = elem.rotoffsets[3].value

    # project offsets in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    p2 = n2OBJ.location + R2*Vector(( f2[0], f2[1], f2[2] ))

    # place the joint object in the position defined relative to node 1
    totjOBJ.location = p1
    totjOBJ.rotation_mode = 'QUATERNION'
    totjOBJ.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( qp1[0], qp1[1], qp1[2], qp1[3] ))

    # display traslation arrows
    pos = ['total.disp.x', 'total.disp.y', 'total.disp.z']
    for kk in range(3):
        if not(elem.offsets[2].value[kk]):
            app_retval = bpy.ops.wm.append(directory = lib_path, filename = pos[kk])
            if app_retval != {'FINISHED'}:
                return {'LIBRARY_ERROR'}
            
            obj = bpy.context.selected_objects[0]
            
            # rotate it according to "position orientation" w.r.t. node 1
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = \
                    n1OBJ.rotation_quaternion * Quaternion(( qp1[0], qp1[1], qp1[2], qp1[3] ))
            
            totjOBJ.select = True
            bpy.context.scene.objects.active = totjOBJ
            bpy.ops.object.join()

    rot = ['total.rot.x', 'total.rot.y', 'total.rot.z']
    for kk in range(3):
        if not(elem.offsets[3].value[kk]):
            app_retval = bpy.ops.wm.append(directory = lib_path, filename = rot[kk])
            if app_retval != {'FINISHED'}:
                return {'LIBRARY_ERROR'}

            obj = bpy.context.selected_objects[0]
            
            # rotate it according to "rotation orientation" w.r.t. node 1
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = \
                    n1OBJ.rotation_quaternion * Quaternion(( qr1[0], qr1[1], qr1[2], qr1[3] ))
            totjOBJ.select = True
            bpy.context.scene.objects.active = totjOBJ
            bpy.ops.object.join()

    # automatic scaling
    s = .5*(1./sqrt(3.))*(n1OBJ.scale.magnitude + \
            n2OBJ.scale.magnitude)
    totjOBJ.scale = Vector(( s, s, s ))

    # create an object representing the RF used to express the relative
    # position w.r.t. node 1, for model debugging
    bpy.ops.object.empty_add(type = 'ARROWS', location = p1)
    RF1p = bpy.context.selected_objects[0]
    RF1p.rotation_mode = 'QUATERNION'
    RF1p.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( qp1[0], qp1[1], qp1[2], qp1[3] ))
    RF1p.scale = .33*totjOBJ.scale
    RF1p.name = totjOBJ.name + '_RF1_pos'
    RF1p.select = True
    bpy.context.scene.objects.active = totjOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    RF1p.hide = True

    # create an object representing the RF used to express the relative
    # orientation w.r.t. node 1, for model debugging
    bpy.ops.object.empty_add(type = 'ARROWS', location = p1)
    RF1r = bpy.context.selected_objects[0]
    RF1r.rotation_mode = 'QUATERNION'
    RF1r.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( qr1[0], qr1[1], qr1[2], qr1[3] ))
    RF1r.scale = .33*totjOBJ.scale
    RF1r.name = totjOBJ.name + '_RF1_rot'
    RF1r.select = True
    bpy.context.scene.objects.active = totjOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    RF1r.hide = True

    # create an object representing the RF used to express the relative
    # position w.r.t. node 2, for model debugging
    bpy.ops.object.empty_add(type = 'ARROWS', location = p2)
    RF2p = bpy.context.selected_objects[0]
    RF2p.rotation_mode = 'QUATERNION'
    RF2p.rotation_quaternion = \
            n2OBJ.rotation_quaternion * Quaternion(( qp2[0], qp2[1], qp2[2], qp2[3] ))
    RF2p.scale = .33*totjOBJ.scale
    RF2p.name = totjOBJ.name + '_RF2_pos'
    RF2p.select = True
    bpy.context.scene.objects.active = totjOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    RF2p.hide = True

    # create an object representing the RF used to express the relative
    # orientation w.r.t. node 2, for model debugging
    bpy.ops.object.empty_add(type = 'ARROWS', location = p2)
    RF2r = bpy.context.selected_objects[0]
    RF2r.rotation_mode = 'QUATERNION'
    RF2r.rotation_quaternion = \
            n2OBJ.rotation_quaternion * Quaternion(( qr2[0], qr2[1], qr2[2], qr2[3] ))
    RF2r.scale = .33*totjOBJ.scale
    RF2r.name = totjOBJ.name + '_RF2_rot'
    RF2r.select = True
    bpy.context.scene.objects.active = totjOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    RF2r.hide = True

    # set parenting of wireframe obj
    bpy.ops.object.select_all(action = 'DESELECT')
    totjOBJ.select = True
    n1OBJ.select = True
    bpy.context.scene.objects.active = n1OBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    elem.blender_object = totjOBJ.name

    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_total(elem, context) function

## Displays total joint infos in the tools panel
def total_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display offset from node 1
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)
            
            # Display position orientation -  node 1
            row = layout.row()
            row.label(text = "pos. orientation node 1" + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[0], "value", text = "", slider = False)

            # Display rotation orientation -  node 1
            row = layout.row()
            row.label(text = "rot. orientation node 1" + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[1], "value", text = "", slider = False)

            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            col.prop(node, "int_label", text = "Node 2 ID ")
            col.prop(node, "string_label", text = "Node 2 label ")
            col.prop(node, "blender_object", text = "Node 2 Object: ")
            col.enabled = False

            # Display offset from node 2
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[1], "value", text = "", slider = False)
            
            # Display position orientation -  node 2
            row = layout.row()
            row.label(text = "pos. orientation node 2" + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[2], "value", text = "", slider = False)

            # Display rotation orientation -  node 2
            row = layout.row()
            row.label(text = "rot. orientation node 2" + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[3], "value", text = "", slider = False)

            layout.separator()

            # Display total joint active components
            box = layout.box()
            split = box.split(1./2.)
            
            column = split.column()
            column.row().label(text = "pos.X")
            column.row().label(text = "pos.Y")
            column.row().label(text = "pos.Z")

            column = split.column()
            for kk in range(3):
                if elem.offsets[2].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            column = split.column()
            column.row().label(text = "rot.X")
            column.row().label(text = "rot.Y")
            column.row().label(text = "rot.Z")

            column = split.column()
            for kk in range(3):
                if elem.offsets[3].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

# -----------------------------------------------------------
# end of total_info_draw(elem, layout) function

class Scene_OT_MBDyn_Import_Total_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_total"
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
            retval = spawn_total_element(elem, context)
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
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element total_joint_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Total_Joint_Element class


## Parses total pin joint entry in the .log file
def parse_total_pin(rw, ed):
    ret_val = True
    # Debug message
    print("parse_total_pin(): Parsing total pin joint " + rw[1])
    try:
        el = ed['total_pin_joint_' + str(rw[1])]
        print("parse_total_pin(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1p = Matrix()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion(); 

        R1r = Matrix()
        parse_rotmat(rw, 15, R1r)
        el.rotoffsets[1].value = R1r.to_quaternion(); 
        
        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[1].value = Vector(( float(rw[24]), float(rw[25]), float(rw[26]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets[2].value = Vector(( float(rw[27]), float(rw[28]), float(rw[29]) ))

        pass
    except KeyError:
        print("parse_total_pin(): didn't found en entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'total_pin_joint'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1p = Matrix()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion();

        el.rotoffsets.add()
        R1r = Matrix()
        parse_rotmat(rw, 15, R1p)
        el.rotoffsets[1].value = R1r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[24]), float(rw[25]), float(rw[26]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[27]), float(rw[28]), float(rw[29]) ))

        el.import_function = "add.mbdyn_elem_total_pin"
        el.info_draw = "total_pin_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_total_pin(rw, ed) function

## Displays total pin joint infos in the tools panel
def totpinj_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display offset from node 1
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)
            
            # Display position orientation -  node 1
            row = layout.row()
            row.label(text = "pos. orientation node 1" + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[0], "value", text = "", slider = False)

            # Display rotation orientation -  node 1
            row = layout.row()
            row.label(text = "rot. orientation node 1" + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[1], "value", text = "", slider = False)

            layout.separator()
    pass
# -----------------------------------------------------------
# end of totpinj_info_draw(elem, layout) function

## Creates the object representing a Total Joint element
def spawn_total_pin_element(elem, context):
    """ Draws a total pin joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_total_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_total_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    # nodes' objects
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe total joint object from the library
    lib_path = os.path.join(mbs.addon_path,\
            'mbdyn-blender-master', 'library', 'joints.blend', \
            'Object')
    app_retval = bpy.ops.wm.append(directory = lib_path, filename = 'total.pin')

    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        totjOBJ = bpy.context.selected_objects[0]
        totjOBJ.name = elem.name
    else:
        return {'LIBRARY_ERROR'}

    # joint offsets with respect to nodes
    f1 = elem.offsets[0].value

    # "position orientation" w.r.t. node
    qp1 = elem.rotoffsets[0].value

    # "rotation orientation" w.r.t node
    qr1 = elem.rotoffsets[1].value

    # project offsets in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))

    # place the joint object in the position defined relative to node 1
    totjOBJ.location = p1
    totjOBJ.rotation_mode = 'QUATERNION'
    totjOBJ.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( qp1[0], qp1[1], qp1[2], qp1[3] ))

    # display traslation arrows
    pos = ['total.disp.x', 'total.disp.y', 'total.disp.z']
    for kk in range(3):
        if not(elem.offsets[2].value[kk]):
            app_retval = bpy.ops.wm.append(directory = lib_path, filename = pos[kk])
            if app_retval != {'FINISHED'}:
                return {'LIBRARY_ERROR'}
            
            obj = bpy.context.selected_objects[0]
            
            # rotate it according to "position orientation" w.r.t. node 1
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = \
                    n1OBJ.rotation_quaternion * Quaternion(( qp1[0], qp1[1], qp1[2], qp1[3] ))
            
            totjOBJ.select = True
            bpy.context.scene.objects.active = totjOBJ
            bpy.ops.object.join()

    rot = ['total.rot.x', 'total.rot.y', 'total.rot.z']
    for kk in range(3):
        if not(elem.offsets[3].value[kk]):
            app_retval = bpy.ops.wm.append(directory = lib_path, filename = rot[kk])
            if app_retval != {'FINISHED'}:
                return {'LIBRARY_ERROR'}

            obj = bpy.context.selected_objects[0]
            
            # rotate it according to "rotation orientation" w.r.t. node 1
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = \
                    n1OBJ.rotation_quaternion * Quaternion(( qr1[0], qr1[1], qr1[2], qr1[3] ))
            totjOBJ.select = True
            bpy.context.scene.objects.active = totjOBJ
            bpy.ops.object.join()

    # automatic scaling
    s = .5*(1./sqrt(3.))*n1OBJ.scale.magnitude
    totjOBJ.scale = Vector(( s, s, s ))

    # create an object representing the RF used to express the relative
    # position w.r.t. node 1, for model debugging
    bpy.ops.object.empty_add(type = 'ARROWS', location = p1)
    RF1p = bpy.context.selected_objects[0]
    RF1p.rotation_mode = 'QUATERNION'
    RF1p.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( qp1[0], qp1[1], qp1[2], qp1[3] ))
    RF1p.scale = .33*totjOBJ.scale
    RF1p.name = totjOBJ.name + '_RF1_pos'
    RF1p.select = True
    bpy.context.scene.objects.active = totjOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    RF1p.hide = True

    # create an object representing the RF used to express the relative
    # orientation w.r.t. node 1, for model debugging
    bpy.ops.object.empty_add(type = 'ARROWS', location = p1)
    RF1r = bpy.context.selected_objects[0]
    RF1r.rotation_mode = 'QUATERNION'
    RF1r.rotation_quaternion = \
            n1OBJ.rotation_quaternion * Quaternion(( qr1[0], qr1[1], qr1[2], qr1[3] ))
    RF1r.scale = .33*totjOBJ.scale
    RF1r.name = totjOBJ.name + '_RF1_rot'
    RF1r.select = True
    bpy.context.scene.objects.active = totjOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
    RF1r.hide = True

    # set parenting of wireframe obj
    bpy.ops.object.select_all(action = 'DESELECT')
    totjOBJ.select = True
    n1OBJ.select = True
    bpy.context.scene.objects.active = n1OBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    elem.blender_object = totjOBJ.name

    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_totpinj_element(elem, context) function

class Scene_OT_MBDyn_Import_Total_Pin_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_total_pin"
    bl_label = "MBDyn total joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['total_pin_joint_' + str(self.int_label)]
            retval = spawn_total_element(elem, context)
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
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element total_pin_joint_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Total_Pin_Joint_Element class
