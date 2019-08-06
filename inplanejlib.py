# --------------------------------------------------------------------------
# Blendyn -- file inplanejlib.py
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

from .utilslib import *

# helper function to parse inplane joints
def parse_inplane(rw, ed):
    ret_val = True
    try:
        el = ed['inplane_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_inplane()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_inplane()", el)

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion(); 
        
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2) 
        el.rotoffsets[1].value = R2.to_quaternion(); 
        
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
        el.type = 'inplane'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_inplane()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_inplane()", el)

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

        el.import_function = "blendyn.import_inplane"
        el.info_draw = "inplane_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_inplane(rw, ed) function

# function that displays inplane info in panel -- [ optional ]
def inplane_info_draw(elem, layout):
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

        row = layout.row()
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
        n1OBJ = bpy.data.objects[n1]
        q1 = elem.rotoffsets[0].value
        direction = Vector((0, 0, 1))
        q = Quaternion(( q1[0], q1[1], q1[2], q1[3] ))
        direction.rotate(q)
        direction = list(map(str, direction))
        direction = ', '.join(direction)
        row.label(text = "Normal to InPlane Joint" + direction)

        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of inplane_info_draw(elem, layout) function

# Creates the object representing a inplane joint element
def spawn_inplane_element(elem, context):
    """ Draws a inplane joint element, loading a wireframe
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

    # load the wireframe inplane joint object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'inplane')
    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        inplanejOBJ = bpy.context.selected_objects[0]
        inplanejOBJ.name = elem.name

        # automatic scaling
        s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + \
        n2OBJ.scale.magnitude)
        inplanejOBJ.scale = Vector(( s, s, s ))

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
    
        # place the joint object in the position defined relative to node 2
        inplanejOBJ.location = p1
        inplanejOBJ.rotation_mode = 'QUATERNION'
        inplanejOBJ.rotation_quaternion = Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # set parenting of wireframe obj
        parenting(inplanejOBJ, n1OBJ)

        grouping(context, inplanejOBJ, [n1OBJ])

        inplanejOBJ.mbdyn.dkey = elem.name
        inplanejOBJ.mbdyn.type = 'element'
        elem.blender_object = inplanejOBJ.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
# -----------------------------------------------------------
# end of spawn_inplane_element(elem, context) function

# Imports a inplane Joint in the scene
class BLENDYN_OT_import_inplane(bpy.types.Operator):
    bl_idname = "blendyn.import_inplane"
    bl_label = "MBDyn inplane joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['inplane_' + str(self.int_label)]
            retval = spawn_inplane_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
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
# end of BLENDYN_OT_import_inplane class. 
