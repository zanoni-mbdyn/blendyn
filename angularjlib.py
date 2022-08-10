# --------------------------------------------------------------------------
# Blendyn -- file angularjlib.py
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

# helper function to parse angularvelocity joints
def parse_angularvelocity(rw, ed):
    ret_val = True
    try:
        el = ed['angularvelocity_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_angularvelocity()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_angularvelocity()", el)

        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'angularvelocity'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_angularvelocity()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_angularvelocity()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.import_function = "blendyn.import_angularvelocity"
        # el.info_draw = "angularvelocity_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_angularvelocity(rw, ed) function

# helper function to parse angularacceleration joints
def parse_angularacceleration(rw, ed):
    ret_val = True
    try:
        el = ed['angularacceleration_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_angularacceleration()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_angularacceleration()", el)

        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.joint'
        
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'angularacceleration'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_angularacceleration()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_angularacceleration()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.import_function = "blendyn.import_angularacceleration"
        # el.info_draw = "angularacceleration_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_angularacceleration(rw, ed) function

# function that displays angularvelocity info in panel -- [ optional ]
def angularvelocity_info_draw(elem, layout):
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
        col.enabled = False

        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of angularvelocity_info_draw(elem, layout) function

# Creates the object representing a angularvelocity joint element
def spawn_angularvelocity_element(elem, context):
    """ Draws a angularvelocity joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if elem.blender_object in bpy.data.objects:
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        bpy.data.objects[elem.blender_object].mbdyn.mbclass = 'elem.joint'
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

        # load the wireframe angularvelocity joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'angvel.w')
        # the append operator leaves just the imported object selected
        angularvelocityjOBJw = bpy.context.selected_objects[0]
        angularvelocityjOBJ = angularvelocityjOBJw.constraints[0].target

        angularvelocityjOBJ.name = elem.name
        angularvelocityjOBJw.name = elem.name + '.w'

        # automatic scaling
        s = (1.0/sqrt(3.))*(n1OBJ.scale.magnitude)
        angularvelocityjOBJ.scale = Vector(( s, s, s ))

        # place the joint object in the position defined relative to node 2
        angularvelocityjOBJ.location = n1OBJ.location
        angularvelocityjOBJ.rotation_mode = 'QUATERNION'
        axis_direction = Vector(elem.offsets[0].value)
        axis_direction.normalize()
        angularvelocityjOBJ.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)
        angularvelocityjOBJ.rotation_quaternion = n1OBJ.rotation_quaternion @ angularvelocityjOBJ.rotation_quaternion

        # set parenting of wireframe obj
        parenting(angularvelocityjOBJ, n1OBJ)

        # connection with dictionary item
        elem.blender_object = angularvelocityjOBJ.name
        angularvelocityjOBJ.mbdyn.type = 'element'
        angularvelocityjOBJ.mbdyn.dkey = elem.name
        
        # set collections
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}

    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_angularvelocity_element(elem, context) function

# Creates the object representing a angularacceleration joint element
def spawn_angularacceleration_element(elem, context):
    """ Draws a angularacceleration joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}

    # nodes objects
    n1OBJ = bpy.data.objects[n1]

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe angularacceleration joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'angacc.a')
        
        # the append operator leaves just the imported object selected
        angularaccelerationjOBJa = bpy.context.selected_objects[0]
        angularaccelerationjOBJ = angularaccelerationjOBJa.constraints[0].target

        angularaccelerationjOBJ.name = elem.name
        angularaccelerationjOBJa.name = elem.name + '.a'

        # automatic scaling
        s = (1.0/sqrt(3.))*(n1OBJ.scale.magnitude)
        angularaccelerationjOBJ.scale = Vector(( s, s, s ))

        # place the joint object in the position defined relative to node 2
        angularaccelerationjOBJ.location = n1OBJ.location
        angularaccelerationjOBJ.rotation_mode = 'QUATERNION'
        axis_direction = Vector(elem.offsets[0].value)
        axis_direction.normalize()
        angularaccelerationjOBJ.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)
        angularaccelerationjOBJ.rotation_quaternion = n1OBJ.rotation_quaternion @ angularaccelerationjOBJ.rotation_quaternion

        # set parenting of wireframe obj
        parenting(angularaccelerationjOBJ, [n1OBJ])

        # association with dictionary element
        elem.blender_object = angularaccelerationjOBJ.name
        angularaccelerationjOBJ.mbdyn.type = 'element'
        angularaccelerationjOBJ.mbdyn.dkey = elem.name

        # set collections
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_angularacceleration_element(elem, context) function

# Imports a angularvelocity Joint in the scene
class BLENDYN_OT_import_angularvelocity(bpy.types.Operator):
    """ Imports an angularvelocity joint element 
        into the Blender scene """
    bl_idname = "blendyn.import_angularvelocity"
    bl_label = "MBDyn angularvelocity joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['angularvelocity_' + str(self.int_label)]
            retval = spawn_angularvelocity_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
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
# end of BLENDYN_OT_import_angularvelocity class.

# Imports a angularacceleration Joint in the scene
class BLENDYN_OT_import_angularacceleration(bpy.types.Operator):
    """ Imports an angularacceleration joint element 
        into the Blender scene """
    bl_idname = "blendyn.import_angularacceleration"
    bl_label = "MBDyn angularacceleration joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['angularacceleration_' + str(self.int_label)]
            retval = spawn_angularacceleration_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
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
# end of BLENDYN_OT_import_angularacceleration class. 
