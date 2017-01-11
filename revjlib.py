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

# helper function to parse revolute hinge joints
def parse_revolute_hinge(rw, ed):
    ret_val = True
    # Debug message
    print("parse_revolute_hinge(): Parsing revolute hinge joint " + rw[1])
    try:
        el = ed['revolute_hinge_' + str(rw[1])]
        print("parse_revolute_hinge(): found existing entry in elements dictionary. Updating it.")
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
        print("parse_revolute_hinge(): didn't found en entry in elements dictionary. Creating one.")
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

        el.import_function = "add.mbdyn_elem_revolute_hinge"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_revolue_hinge(rw, ed) function

# helper function to parse revolute pin joints
def parse_revolute_pin(rw, ed):
    ret_val = True
    # Debug message
    print("parse_revolute_pin(): Parsing revolute pin joint " + rw[1])
    try:
        el = ed['revolute_pin_' + str(rw[1])]
        print("parse_revolute_pin(): found existing entry in elements dictionary. Updating it.")
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
        print("parse_revolute_pin(): didn't found en entry in elements dictionary. Creating one.")
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

        el.import_function = "add.mbdyn_elem_revolute_pin"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_revolute_pin(rw, ed) function

# Creates the object representing a revolute hinge joint element
def spawn_revolute_hinge_element(elem, context):
    """ Draws a revolute hinge joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_revolute_hinge_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_revolute_hinge_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_revolute_hinge_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # load the wireframe revolute joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'mbdyn-blender-master', 'library', 'joints.blend', \
            'Object'), filename = 'revolute')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        revjOBJ = bpy.context.selected_objects[0]
        revjOBJ.name = elem.name

        # automatic scaling
        s = .5*(n1OBJ.scale.magnitude*(1./sqrt(3.)) + \
        n2OBJ.scale.magnitude*(1./sqrt(3.)))
        revjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
        f2 = elem.offsets[1].value
        q1 = elem.rotoffsets[0].value
        q2 = elem.rotoffsets[1].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        R2 = n2OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
        p2 = n2OBJ.location + R2*Vector(( f2[0], f2[1], f2[2] ))
    
        # place the joint object in the position defined relative to node 1
        revjOBJ.location = p1
        revjOBJ.rotation_mode = 'QUATERNION'
        revjOBJ.rotation_quaternion = \
                n1OBJ.rotation_quaternion * Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # create an object representing the second RF used by the joint
        # for model debugging
        bpy.ops.object.empty_add(type = 'ARROWS', location = p2)
        RF2 = bpy.context.selected_objects[0]
        RF2.rotation_mode = 'QUATERNION'
        RF2.rotation_quaternion = \
                n2OBJ.rotation_quaternion * Quaternion(( q2[0], q2[1], q2[2], q2[3] ))
        RF2.scale = .33*revjOBJ.scale
        RF2.name = revjOBJ.name + '_RF2'
        RF2.select = True
        bpy.context.scene.objects.active = revjOBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
        RF2.hide = True

        # set parenting of wireframe obj
        bpy.ops.object.select_all(action = 'DESELECT')
        revjOBJ.select = True
        n1OBJ.select = True
        bpy.context.scene.objects.active = n1OBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
# -----------------------------------------------------------
# end of spawn_revolute_hinge_element(elem, context) function

# Imports a Revolute Joint in the scene
class Scene_OT_MBDyn_Import_Revolute_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_revolute_hinge"
    bl_label = "MBDyn revolute joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['revolute_hinge_' + str(self.int_label)]
            retval = spawn_revolute_hinge_element(elem, context)
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
            self.report({'ERROR'}, "Element revolute_hinge_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Revolute_Joint_Element class
 
# Creates the object representing a revolute joint element
def spawn_revolute_pin_element(elem, context):
    """ Draws a revolute pin joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_revolute_pin_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_revolute_pin_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    # nodes' objects
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe revolute joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'mbdyn-blender-master', 'library', 'joints.blend', \
            'Object'), filename = 'revolute.pin')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        revjOBJ = bpy.context.selected_objects[0]
        revjOBJ.name = elem.name

        # automatic scaling
        s = n1OBJ.scale.magnitude*(1./sqrt(3.))
        revjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
        q1 = elem.rotoffsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    
        # place the joint object in the position defined relative to node 1
        revjOBJ.location = p1
        revjOBJ.rotation_mode = 'QUATERNION'
        revjOBJ.rotation_quaternion = \
                n1OBJ.rotation_quaternion * Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # set parenting of wireframe obj
        bpy.ops.object.select_all(action = 'DESELECT')
        revjOBJ.select = True
        n1OBJ.select = True
        bpy.context.scene.objects.active = n1OBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
# -----------------------------------------------------------
# end of spawn_revolute_pin_element(elem, context) function

# Imports a Revolute Pin Joint in the scene
class Scene_OT_MBDyn_Import_Revolute_Pin_Joint_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_revolute_pin"
    bl_label = "MBDyn revolute pin joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['revolute_pin_' + str(self.int_label)]
            retval = spawn_revpinj_element(elem, context)
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
            self.report({'ERROR'}, "Element revolute_pin_" + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Revolute_Pin_Joint_Element class

# Displays revolute joint infos in the tools panel [ optional ]
def revolute_hinge_info_draw(elem, layout):
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
            
            # Display rotation offset from node 1
            row = layout.row()
            row.label(text = "rot. offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[0], "value", text = "", slider = False)

            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            row = layout.row()
            col = layout.column(align = True)
            col.prop(node, "int_label", text = "Node 2 ID ")
            col.prop(node, "string_label", text = "Node 2 label ")
            col.prop(node, "blender_object", text = "Node 2 Object: ")
            col.enabled = False

            # Display offset from node 2
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[2], "value", text = "", slider = False)
            
            # Display rotation offset from node 2
            row = layout.row()
            row.label(text = "rot. offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[1], "value", text = "", slider = False)

            layout.separator()
# -----------------------------------------------------------
# end of revolute_hinge_info_draw() function
    
# Displays revolute joint infos in the tools panel [ optional ]
def revolute_pin_info_draw(elem, layout):
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
            
            # Display rotation offset from node 1
            row = layout.row()
            row.label(text = "rot. offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.rotoffsets[0], "value", text = "", slider = False)

            layout.separator()
    pass
# -------------------------------------------------------------------------- 
# end of revolute_pin_info_draw(elem, layout) function
