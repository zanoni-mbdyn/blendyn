# --------------------------------------------------------------------------
# Blendyn -- file totjlib.py
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
import os
from mathutils import *
from math import *

from .utilslib import *

def parse_total(rw, ed):
    """ Parses a total joint entry in .log file """
    ret_val = True
    try:
        el = ed['total_joint_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_total():", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_total():", el)
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[24])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1p = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion(); 

        R1r = Matrix().to_3x3()
        parse_rotmat(rw, 15, R1r)
        el.rotoffsets[1].value = R1r.to_quaternion(); 
        
        el.offsets[1].value = Vector(( float(rw[25]), float(rw[26]), float(rw[27]) ))

        R2p = Matrix().to_3x3()
        parse_rotmat(rw, 28, R2p)
        el.rotoffsets[2].value = R2p.to_quaternion();
        
        R2r = Matrix().to_3x3()
        parse_rotmat(rw, 37, R2r)
        el.rotoffsets[3].value = R2r.to_quaternion();

        # note: this is not really an offset, but a bool vector 
        #       indicating which position constraints are active
        el.offsets[2].value = Vector(( float(rw[46]), float(rw[47]), float(rw[48]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which velocity constraints are active
        el.offsets[3].value = Vector(( float(rw[49]), float(rw[50]), float(rw[51]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which rotation constraints are active
        el.offsets[4].value = Vector(( float(rw[52]), float(rw[53]), float(rw[54]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which angular velocity constraints are active
        el.offsets[5].value = Vector(( float(rw[55]), float(rw[56]), float(rw[57]) ))


        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True

         
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.joint'
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'total_joint'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_total():", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_total():", el) 

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[24])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1p = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion();

        el.rotoffsets.add()
        R1r = Matrix().to_3x3() 
        parse_rotmat(rw, 15, R1r)
        el.rotoffsets[1].value = R1r.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[25]), float(rw[26]), float(rw[27]) ))

        el.rotoffsets.add()
        R2p = Matrix().to_3x3()
        parse_rotmat(rw, 28, R2p)
        el.rotoffsets[2].value = R2p.to_quaternion();
        
        el.rotoffsets.add()
        R2r = Matrix().to_3x3()
        parse_rotmat(rw, 37, R2r)
        el.rotoffsets[3].value = R2r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which position constraints are active
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[46]), float(rw[47]), float(rw[48]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which velocity constraints are active
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[49]), float(rw[50]), float(rw[51]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which rotation constraints are active
        el.offsets.add()
        el.offsets[4].value = Vector(( float(rw[52]), float(rw[53]), float(rw[54]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which rotation constraints are active
        el.offsets.add()
        el.offsets[5].value = Vector(( float(rw[55]), float(rw[56]), float(rw[57]) ))
        
        el.import_function = "blendyn.import_total"
        el.info_draw = "total_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_total(rw, ed) function


def parse_total_pin(rw, ed):
    """ Parses a total pin joint entry in the .log file """
    ret_val = True
    try:
        el = ed['total_pin_joint_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_total_pin():", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_total_pin():", el)
        
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1p = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion(); 

        R1r = Matrix().to_3x3()
        parse_rotmat(rw, 15, R1r)
        el.rotoffsets[1].value = R1r.to_quaternion(); 
        
        # note: this is not really an offset, but a bool vector 
        #       indicating which position constraints are active
        el.offsets[1].value = Vector(( float(rw[45]), float(rw[46]), float(rw[47]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which velocity constraints are active
        el.offsets[2].value = Vector(( float(rw[48]), float(rw[49]), float(rw[50]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which rotation constraints are active
        el.offsets[3].value = Vector(( float(rw[51]), float(rw[52]), float(rw[53]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which angular velocity constraints are active
        el.offsets[4].value = Vector(( float(rw[54]), float(rw[55]), float(rw[56]) ))

        # FIXME: this is here to enhance backwards compatibility.
        # should disappear in future versions
        el.mbclass = 'elem.joint'
        
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name

    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'total_pin_joint'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_total_pin():", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_total_pin():", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1p = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1p)
        el.rotoffsets[0].value = R1p.to_quaternion();

        el.rotoffsets.add()
        R1r = Matrix().to_3x3()
        parse_rotmat(rw, 15, R1p)
        el.rotoffsets[1].value = R1r.to_quaternion();

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating the position constraints that are active
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[45]), float(rw[46]), float(rw[47]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which velocity constraints are active
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[48]), float(rw[49]), float(rw[50]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which rotation constraints are active
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[51]), float(rw[52]), float(rw[53]) ))

        # NOTE: This is not really an offset, but a bool vector 
        #       indicating which angular velocity constraints are active
        el.offsets.add()
        el.offsets[4].value = Vector(( float(rw[54]), float(rw[55]), float(rw[56]) ))

        el.import_function = "blendyn.import_total_pin"
        el.info_draw = "total_pin_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_total_pin(rw, ed) function


def spawn_total_joint_element(elem, context):
    """ Draws a total joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # rotation quaternion and matrices, and position offsets
    q1 = n1OBJ.rotation_quaternion
    q2 = n2OBJ.rotation_quaternion
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    fP1 = elem.offsets[0].value
    fP2 = elem.offsets[1].value

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe total joint object from the library
        lib_path = os.path.join(mbs.addon_path, 'library', 'joints.blend', 'Object')
        bpy.ops.wm.append(directory = lib_path, filename = 'total')

        # the append operator leaves just the imported object selected
        totjOBJ = bpy.context.selected_objects[0]
        totjOBJ.name = elem.name

        # place the joint object in the position defined relative to node 1
        totjOBJ.location = n1OBJ.location + R1@Vector(( fP1[0], fP1[1], fP1[2] ))
        totjOBJ.rotation_mode = 'QUATERNION'
        totjOBJ.rotation_quaternion = Quaternion(elem.rotoffsets[0].value[0:])@q1

        OBJs = list()
        OBJs.append(totjOBJ);

        # display traslation arrows
        pos = ['total.disp.x', 'total.disp.y', 'total.disp.z']
        for kk in range(3):
            if not(elem.offsets[2].value[kk]):
                app_retval = bpy.ops.wm.append(directory = lib_path, filename = pos[kk])
                if app_retval != {'FINISHED'}:
                    return {'LIBRARY_ERROR'}
            
                obj = bpy.context.selected_objects[0]
                OBJs.append(obj)

                # position it correctly, in global frame
                obj.location = n1OBJ.location + R1@Vector(( fP1[0], fP1[1], fP1[2] ))

                # rotate it according to "position orientation" w.r.t. node 1
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = Quaternion(elem.rotoffsets[0].value[0:])@q1
        
        # display rotation arrows
        rot = ['total.rot.x', 'total.rot.y', 'total.rot.z']
        for kk in range(3):
            if not(elem.offsets[4].value[kk]):
                app_retval = bpy.ops.wm.append(directory = lib_path, filename = rot[kk])
                if app_retval != {'FINISHED'}:
                    return {'LIBRARY_ERROR'}
    
                obj = bpy.context.selected_objects[0]
                OBJs.append(obj)
                
                # position it correctly
                obj.location = n1OBJ.location +R1@Vector(( elem.offsets[0].value[0:] ))
                
                # rotate it according to "rotation orientation" w.r.t. node 1
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = Quaternion(elem.rotoffsets[1].value[0:])@q1
     
        # TODO: display also velocity contraints arrows
    
        # join objects, with context override
        ctx = context.copy()
        ctx['active_object'] = OBJs[0]
        ctx['selected_editable_objects'] = OBJs
        bpy.ops.object.join(ctx)

        # automatic scaling
        s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + n2OBJ.scale.magnitude)
        totjOBJ.scale = Vector(( s, s, s ))

        # create an object representing the RF used to express the relative
        # position w.r.t. node 1, for model debuggingi
        RF1p = bpy.data.objects.new(totjOBJ.name + '_RF1_pos', None)
        RF1p.location = totjOBJ.location
        RF1p.empty_display_type = 'ARROWS'
        RF1p.rotation_mode = 'QUATERNION'
        RF1p.rotation_quaternion = Quaternion(elem.rotoffsets[0].value[0:])@q1
    
        # create an object representing the RF used to express the relative
        # orientation w.r.t. node 1, for model debugging
        RF1r = bpy.data.objects.new(totjOBJ.name + '_RF1_rot', None)
        RF1r.location = totjOBJ.location
        RF1r.empty_display_type = 'ARROWS'
        RF1r.rotation_mode = 'QUATERNION'
        RF1r.rotation_quaternion = Quaternion(elem.rotoffsets[1].value[0:])@q1
    
        # create an object representing the RF used to express the relative
        # position w.r.t. node 2, for model debugging
        RF2p = bpy.data.objects.new(totjOBJ.name + '_RF2_pos', None)
        RF2p.location = totjOBJ.location
        RF2p.empty_display_type = 'ARROWS'
        RF2p.rotation_mode = 'QUATERNION'
        RF2p.rotation_quaternion = Quaternion(elem.rotoffsets[2].value[0:])@q2
    
        # create an object representing the RF used to express the relative
        # orientation w.r.t. node 2, for model debugging
        RF2r = bpy.data.objects.new(totjOBJ.name + '_RF2_rot', None)
        RF2r.location = totjOBJ.location
        RF2r.empty_display_type = 'ARROWS'
        RF2r.rotation_mode = 'QUATERNION'
        RF2r.rotation_quaternion = Quaternion(elem.rotoffsets[3].value[0:])@q2
    
        # set mbdyn props of object
        elem.blender_object = totjOBJ.name
        totjOBJ.mbdyn.dkey = elem.name
        totjOBJ.mbdyn.type = 'element'

        # set parenting of wireframe obj
        parenting(totjOBJ, n1OBJ)
        # parent the RF objects to the corresponding nodes
        parenting(RF1p, n1OBJ)
        parenting(RF1r, n1OBJ)
        parenting(RF2p, n2OBJ)
        parenting(RF2r, n2OBJ)

        # link objects to element collection
        elcol.objects.link(RF1p)
        elcol.objects.link(RF1r)
        elcol.objects.link(RF2p)
        elcol.objects.link(RF2r)
        RF1p.hide_set(state = True)
        RF1r.hide_set(state = True)
        RF2p.hide_set(state = True)
        RF2r.hide_set(state = True)
        elcol.objects.link(n1OBJ)
        elcol.objects.link(n2OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_total(elem, context) function


def spawn_total_pin_joint_element(elem, context):
    """ Draws a total pin joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}
    
    # nodes' objects
    n1OBJ = bpy.data.objects[n1]

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)
    
        # load the wireframe total joint object from the library
        lib_path = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object')
        bpy.ops.wm.append(directory = lib_path, filename = 'total.pin')

        # the append operator leaves just the imported object selected
        totjOBJ = bpy.context.selected_objects[0]
        totjOBJ.name = elem.name
        # place the joint object in the position defined relative to node 1
        totjOBJ.location = elem.offsets[0].value
        totjOBJ.rotation_mode = 'QUATERNION'
        totjOBJ.rotation_quaternion = Quaternion(elem.rotoffsets[0].value)
   
        OBJs = list()
        OBJs.append(totjOBJ)

        # display traslation arrows
        pos = ['total.disp.x', 'total.disp.y', 'total.disp.z']
        for kk in range(3):
            if not(elem.offsets[1].value[kk]):
                app_retval = bpy.ops.wm.append(directory = lib_path, filename = pos[kk])
                if app_retval != {'FINISHED'}:
                    return {'LIBRARY_ERROR'}
                
                obj = bpy.context.selected_objects[0]
                OBJs.append(obj)
    
                # position it correctly
                obj.location = elem.offsets[0].value
                
                # rotate it according to "position orientation" w.r.t. node 1
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = Quaternion(elem.rotoffsets[0].value)
           
        # display rotation arrows
        rot = ['total.rot.x', 'total.rot.y', 'total.rot.z']
        for kk in range(3):
            if not(elem.offsets[3].value[kk]):
                app_retval = bpy.ops.wm.append(directory = lib_path, filename = rot[kk])
                if app_retval != {'FINISHED'}:
                    return {'LIBRARY_ERROR'}
    
                obj = bpy.context.selected_objects[0]
                OBJs.append(obj)
               
                # position it correctly
                obj.location = elem.offsets[0].value
    
                # rotate it according to "rotation orientation" w.r.t. node 1
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = Quaternion(elem.rotoffsets[0].value) 
    
        # TODO: display also velocity contraints arrows

        # join objects, with context override
        ctx = bpy.context.copy()
        ctx['active_object'] = OBJs[0]
        ctx['selected_editable_objects'] = OBJs
        bpy.ops.object.join(ctx)

        # automatic scaling
        s = (1./sqrt(3.))*n1OBJ.scale.magnitude
        totjOBJ.scale = Vector(( s, s, s ))
    
        # create an object representing the RF used to express the relative
        # position w.r.t. node 1, for model debugging
        RF1p = bpy.data.objects.new(totjOBJ.name + '_RF1_pos', None)
        RF1p.empty_display_type = 'ARROWS'
        RF1p.rotation_mode = 'QUATERNION'
        RF1p.rotation_quaternion = Quaternion(elem.rotoffsets[0].value)
    
        # create an object representing the RF used to express the relative
        # orientation w.r.t. node 1, for model debugging
        RF1r = bpy.data.objects.new(totjOBJ.name + '_RF1_rot', None)
        RF1r.empty_display_type = 'ARROWS'
        RF1r.rotation_mode = 'QUATERNION'
        RF1r.rotation_quaternion = Quaternion(elem.rotoffsets[1].value)
    
        # set parenting of wireframe obj
        parenting(totjOBJ, n1OBJ)
        # set parenting of RF objects
        parenting(RF1p, n1OBJ)
        parenting(RF1r, n1OBJ)
    
        # set objects' mbdyn props
        elem.blender_object = totjOBJ.name
        totjOBJ.mbdyn.dkey = elem.name
        totjOBJ.mbdyn.type = 'element'
    
        # link objects to element collection
        elcol.objects.link(n1OBJ)
        elcol.objects.link(RF1p)
        elcol.objects.link(RF1r)
        RF1p.hide_set(state = True)
        RF1r.hide_set(state = True)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_total_pin_joint_element(elem, context) function


def total_info_draw(elem, layout):
    """ Displays total joint infos in the tools panel """
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align = True)

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display offset from node 1
            row = layout.row()
            row.label(text = "offset 1 in node 1 R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)
            
            # Display position orientation -  node 1
            row = layout.row()
            row.label(text = "pos. orientation node 1 R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[0], "value", text = "", slider = False)

            # Display rotation orientation -  node 1
            row = layout.row()
            row.label(text = "rot. orientation node 1 R.F.")
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
            row.label(text = "offset 2 in node 2 R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[1], "value", text = "", slider = False)
            
            # Display position orientation -  node 2
            row = layout.row()
            row.label(text = "pos. orientation node 2 R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[2], "value", text = "", slider = False)

            # Display rotation orientation -  node 2
            row = layout.row()
            row.label(text = "rot. orientation node 2 R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[3], "value", text = "", slider = False)

            layout.separator()

            # Display total joint active components
            box = layout.box()
            split = box.split(1./8.)
           
            # position
            column = split.column()
            column.row().label(text = "pos.X:")
            column.row().label(text = "pos.Y:")
            column.row().label(text = "pos.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[2].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            # linear velocity
            column = split.column()
            column.row().label(text = "vel.X:")
            column.row().label(text = "vel.Y:")
            column.row().label(text = "vel.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[3].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            # rotation
            column = split.column()
            column.row().label(text = "rot.X:")
            column.row().label(text = "rot.Y:")
            column.row().label(text = "rot.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[4].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            # angular velocity 
            column = split.column()
            column.row().label(text = "angvel.X:")
            column.row().label(text = "angvel.Y:")
            column.row().label(text = "angvel.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[5].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

# -----------------------------------------------------------
# end of total_info_draw(elem, layout) function


def total_pin_info_draw(elem, layout):
    """ Displays total pin joint infos in the tools panel """
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
            row.label(text = "offset 1 in node R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)
            
            # Display position orientation -  node 1
            row = layout.row()
            row.label(text = "pos. orientation node R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[0], "value", text = "", slider = False)

            # Display rotation orientation -  node 1
            row = layout.row()
            row.label(text = "rot. orientation node R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[1], "value", text = "", slider = False)

            layout.separator()
            
            # Display total joint active components
            box = layout.box()
            split = box.split(1./8.)
           
            # position
            column = split.column()
            column.row().label(text = "pos.X:")
            column.row().label(text = "pos.Y:")
            column.row().label(text = "pos.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[1].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            # linear velocity
            column = split.column()
            column.row().label(text = "vel.X:")
            column.row().label(text = "vel.Y:")
            column.row().label(text = "vel.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[2].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            # rotation
            column = split.column()
            column.row().label(text = "rot.X:")
            column.row().label(text = "rot.Y:")
            column.row().label(text = "rot.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[3].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

            # angular velocity 
            column = split.column()
            column.row().label(text = "angvel.X:")
            column.row().label(text = "angvel.Y:")
            column.row().label(text = "angvel.Z:")

            column = split.column()
            for kk in range(3):
                if elem.offsets[4].value[kk]:
                    column.row().label(text = "active")
                else:
                    column.row().label(text = "inactive")

    pass
# -----------------------------------------------------------
# end of totpinj_info_draw(elem, layout) function


class BLENDYN_OT_import_total(bpy.types.Operator):
    """ Imports a total joint element into the Blender scene """
    bl_idname = "blendyn.import_total"
    bl_label = "Imports a total joint element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['total_joint_' + str(self.int_label)]
            retval = spawn_total_joint_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'FINISHED'}:
                eldbmsg({'IMPORT_SUCCESS'}, type(self).__name__ + '::execute()', elem)
                return retval
            else:
                # Should not be reached
                return retval
        except KeyError:
            eldbmsg({'DICT_ERROR'}, type(self).__name__ + '::execute()', elem)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_import_total class

class BLENDYN_OT_import_total_pin(bpy.types.Operator):
    """ Imports a total joint element into the Blender scene"""
    bl_idname = "blendyn.import_total_pin"
    bl_label = "Imports a total joint element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['total_pin_joint_' + str(self.int_label)]
            retval = spawn_total_pin_joint_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'FINISHED'}:
                eldbmsg({'IMPORT_SUCCESS'}, type(self).__name__ + '::execute()', elem)
                return retval
            else:
                # Should not be reached
                return retval
        except KeyError:
            eldbmsg({'DICT_ERROR'}, type(self).__name__ + '::execute()', elem)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_import_total_pin class
