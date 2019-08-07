# --------------------------------------------------------------------------
# Blendyn -- file linearjlib.py
# Copyright (C) 2015 -- 2019 Andrea Zanoni -- andrea.zanoni@polimi.it
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

from .utilslib import parse_rotmat
from .utilslib import parenting

# helper function to parse linearvelocity joints
def parse_linearvelocity(rw, ed):
    ret_val = True
    try:
        el = ed['linearvelocity_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, 'BLENDYN::parse_linearvelocity()', el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_linearvelocity()", el)
        
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
        el.type = 'linearvelocity'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, 'BLENDYN::parse_linearvelocity()', el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_linearvelocity()", el) 

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.joint'

        el.import_function = "blendyn.import_linearvelocity"
        # el.info_draw = "linearvelocity_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_linearvelocity(rw, ed) function

# helper function to parse linearacceleration joints
def parse_linearacceleration(rw, ed):
    ret_val = True
    try:
        el = ed['linearacceleration_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, 'BLENDYN::parse_linearacceleration()', el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_linearacceleration()", el)

        el.nodes[0].int_label = int(rw[2])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'linearacceleration'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, 'BLENDYN::parse_linearacceleration()', el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_linearacceleration()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.import_function = "blendyn.import_linearacceleration"
        # el.info_draw = "linearacceleration_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_linearacceleration(rw, ed) function

# function that displays linearvelocity info in panel -- [ optional ]
def linearvelocity_info_draw(elem, layout):
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
# end of linearvelocity_info_draw(elem, layout) function

# Creates the object representing a linearvelocity joint element
def spawn_linearvelocity_element(elem, context):
    """ Draws a linearvelocity joint element, loading a wireframe
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

        # load the wireframe linearvelocity joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
           'library', 'joints.blend', 'Object'), filename = 'linvel.v')
        
        # the append operator leaves just the imported object selected
        linearvelocityjOBJv = bpy.context.selected_objects[0]
        linearvelocityjOBJ = bpy.context.selected_objects[1]
        
        linearvelocityjOBJ.name = elem.name
        linearvelocityjOBJv.name = elem.name + '.v'
        bpy.context.view_layer.objects.active = linearvelocityjOBJ

        # automatic scaling
        s = (1.0/sqrt(3.))*(n1OBJ.scale.magnitude)
        linearvelocityjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
    
        # place the joint object in the position defined relative to node 2
        linearvelocityjOBJ.location = n1OBJ.location
        linearvelocityjOBJ.rotation_mode = 'QUATERNION'
        axis_direction = Vector(elem.offsets[0].value)
        axis_direction.normalize()
        linearvelocityjOBJ.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)

        # set parenting of wireframe obj
        parenting(linearvelocityjOBJ, n1OBJ)

        linearvelocityOBJ.mbdyn.dkey = elem.name
        linearvelocityOBJ.mbdyn.type = 'element'
        elem.blender_object = linearvelocityjOBJ.name
        
        # link objects to element collection
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_linearvelocity_element(elem, context) function

# Creates the object representing a linearacceleration joint element
def spawn_linearacceleration_element(elem, context):
    """ Draws a linearacceleration joint element, loading a wireframe
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

        # load the wireframe linearacceleration joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'linacc.a')
        
        # the append operator leaves just the imported object selected
        linearaccelerationjOBJa = bpy.context.selected_objects[0]
        linearaccelerationjOBJ = bpy.context.selected_objects[1]

        linearaccelerationjOBJ.name = elem.name
        linearaccelerationjOBJa.name = elem.name + '.a'

        # automatic scaling
        s = (1.0/sqrt(3.))*(n1OBJ.scale.magnitude)
        linearaccelerationjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value

        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
    
        # place the joint object in the position defined relative to node 2
        linearaccelerationjOBJ.location = n1OBJ.location
        linearaccelerationjOBJ.rotation_mode = 'QUATERNION'
        axis_direction = Vector(elem.offsets[0].value)
        axis_direction.normalize()
        linearaccelerationjOBJ.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis_direction)

        # set parenting of wireframe obj
        parenting(linearaccelerationjOBJ, n1OBJ)

        elem.blender_object = linearaccelerationjOBJ.name

        # link objects to element collection
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_linearacceleration_element(elem, context) function

# Imports a linearvelocity Joint in the scene
class BLENDYN_OT_import_linearvelocity(bpy.types.Operator):
    """ Imports a linearvelocity joint element into the
        Blender scene """
    bl_idname = "blendyn.import_linearvelocity"
    bl_label = "Import a linearvelocity joint element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['linearvelocity_' + str(self.int_label)]
            retval = spawn_linearvelocity_element(elem, context)
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
# end of BLENDYN_OT_import_linearvelocity class. 

# Imports a linearacceleration Joint in the scene
class BLENDYN_OT_import_linearacceleration(bpy.types.Operator):
    """ Imports a linearacceleration joint element
        into the Blender scene """
    bl_idname = "blendyn.import_linearacceleration"
    bl_label = "Imports a linearacceleration joint element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['linearacceleration_' + str(self.int_label)]
            retval = spawn_linearacceleration_element(elem, context)
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
# end of BLENDYN_OT_import_linearacceleration class.
