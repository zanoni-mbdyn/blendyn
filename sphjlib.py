# --------------------------------------------------------------------------
# Blendyn -- file sphjlib.py
# Copyright (C) 2015 -- 2018 Andrea Zanoni -- andrea.zanoni@polimi.it
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
import os.path

import logging

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

from .utilslib import *

## Parses spherical hinge joint .log file entry
def parse_spherical_hinge(rw, ed):
    ret_val = True
    # Debug message
    print("Blendyn::parse_spherical_hinge(): Parsing spherical joint " + rw[1])
    try:
        el = ed['spherical_hinge_' + str(rw[1])]

        print("Blendyn::parse_spherical_hinge(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion(); 
        
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))
        
        # FIXME: this is here to enhance backwards compatibility.
        # should disappear in future versions
        el.mbclass = 'elem.joint'
        
        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion(); 
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("Blendyn::parse_spherical_hinge(): didn't find an entry in elements dictionary. Creating one.")
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'spherical_hinge'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[15])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        el.rotoffsets.add()
        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        el.import_function = "add.mbdyn_elem_spherical_hinge"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_spherical_hinge(rw, ed) function

## Parses spherical pin joint .log file entry
def parse_spherical_pin(rw, ed):
    ret_val = True
    # Debug message
    print("Blendyn::parse_spherical_pin(): Parsing spherical pin joint " + rw[1])
    try:
        el = ed['spherical_pin_' + str(rw[1])]

        print("Blendyn::parse_spherical_pin(): found existing entry in elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion(); 
        
        # FIXME: this is here to enhance backwards compatibility.
        # should disappear in future versions
        el.mbclass = 'elem.joint'
        
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        print("Blendyn::parse_spherical_pin(): didn't find an entry in elements dictionary. Creating one.")
        el = ed.add()
        el.mbclass = 'elem.joint' 
        el.type = 'spherical_pin'
        el.int_label = int(rw[1])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.import_function = "add.mbdyn_elem_spherical_pin"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_sphj(rw, ed) function

## Creates the objet representing a Spherical Hinge joint
def spawn_spherical_hinge_element(elem, context):
    """ Draws a spherical hinge joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("Blendyn::spawn_spherical_hinge_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("Blendyn::spawn_spherical_hinge_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("Blendyn::spawn_spherical_hinge_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # load the wireframe revolute joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'spherical')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        sphjOBJ = bpy.context.selected_objects[0]
        sphjOBJ.name = elem.name

        # automatic scaling
        s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + \
            n2OBJ.scale.magnitude)
        sphjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
        f2 = elem.offsets[1].value
        q1 = elem.rotoffsets[0].value
        q2 = elem.rotoffsets[1].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        R2 = n2OBJ.rotation_quaternion.to_matrix()
        p1 = Vector(( f1[0], f1[1], f1[2] ))
        p2 = Vector(( f2[0], f2[1], f2[2] ))
    
        # place the joint object in the position defined relative to node 1
        sphjOBJ.location = p1
        sphjOBJ.rotation_mode = 'QUATERNION'
        sphjOBJ.rotation_quaternion = Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # create an object representing the second RF used by the joint
        # for model debugging
        bpy.ops.object.empty_add(type = 'ARROWS', location = p2)
        RF2 = bpy.context.selected_objects[0]
        RF2.rotation_mode = 'QUATERNION'
        RF2.rotation_quaternion = Quaternion(( q2[0], q2[1], q2[2], q2[3] ))
        RF2.scale = .33*sphjOBJ.scale
        RF2.name = sphjOBJ.name + '_RF2'
        parenting(RF2, sphjOBJ)
        RF2.hide = True

        # set parenting of wireframe obj
        parenting(sphjOBJ, n1OBJ)

        grouping(context, sphjOBJ, [n1OBJ])

        sphjOBJ.mbdyn.dkey = elem.name
        sphjOBJ.mbdyn.type = 'element'
        elem.blender_object = sphjOBJ.name 

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
    pass
# -------------------------------------------------------------------------- 
# end of spawn_spherical_hinge_element(element, context) function

## Creates the objet representing a spherical joint
def spawn_spherical_pin_element(elem, context):
    """ Draws a spherical pin joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("Blendyn::spawn_spherical_pin_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("Blendyn::spawn_spherical_pin_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    

    # node object
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'spherical.pin')

    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        sphjOBJ = bpy.context.selected_objects[0]
        sphjOBJ.name = elem.name

        # automatic scaling
        s = .5*(n1OBJ.scale.magnitude*(1./sqrt(3.)))
        sphjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
        q1 = elem.rotoffsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = Vector(( f1[0], f1[1], f1[2] ))
    
        # place the joint object in the position defined relative to node 1
        sphjOBJ.location = p1
        sphjOBJ.rotation_mode = 'QUATERNION'
        sphjOBJ.rotation_quaternion = Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # set parenting of wireframe obj
        parenting(sphjOBJ, n1OBJ)

        grouping(context, sphjOBJ, [n1OBJ])

        elem.blender_object = sphjOBJ.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
    pass
# -------------------------------------------------------------------------- 
# end of spawn_spherpical_pin_element(element, context) function

## Imports a Spherical Joint element in the scene
class Scene_OT_MBDyn_Import_Spherical_Hinge_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_spherical_hinge"
    bl_label = "MBDyn spherical joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['spherical_hinge_' + str(self.int_label)]
            retval = spawn_spherical_hinge_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "Found the Object " + elem.blender_object + \
                    " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                message = "Could not import element: Blender object " +\
                    "associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                message = "Could not import element: Blender object " +\
                        "associated to Node " + str(elem.nodes[1].int_label) + " not found"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                message = "Could not import element: could not " +\
                        "load library object"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element spherical_hinge_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Spherical_Hinge_Joint_Element class

## Imports a Spherical Pin Joint element in the scene
class Scene_OT_MBDyn_Import_Spherical_Pin_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_spherical_pin"
    bl_label = "MBDyn spherical joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        
        try:
            elem = ed['spherical_pin_' + str(self.int_label)]
            retval = spawn_spherical_pin_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "Found the Object " + elem.blender_object + \
                    " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                message = "Could not import element: Blender object " +\
                    "associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                message = "Could not import element: could not " +\
                        "load library object"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element spherical_pin_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Spherical_Pin_Joint_Element class
