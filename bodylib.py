# --------------------------------------------------------------------------
# Blendyn -- file bodylib.py
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
from bpy.types import Operator, Panel
from bpy.props import *

from .utilslib import *

# Parses body entry in the .log file (see section E.2.8 of input manual for details)
def parse_body(rw, ed):
    ret_val = True
    try:
        el = ed['body_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_body()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_body()", el)
        
        el.nodes[0].int_label = int(rw[2])
        el.magnitude = float(rw[3])     # mass
        
        el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
        
        # FIXME this is the inertia matrix... And this is a (dirty) trick 
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))
        
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.body'
         
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass

    except KeyError:

        el = ed.add()
        el.mbclass = 'elem.body'
        el.type = 'body'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_body()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_body()", el)
        
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.magnitude = float(rw[3])
        
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))

        # FIXME this is the inertia matrix... And this is a (dirty) trick 
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))

        el.import_function = "blendyn.import_body"
        el.info_draw = "body_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_body(rw, ed) function

## Spawns a Blender object representing a body element (CG representation)
def spawn_body_element(elem, context):
    """ Draws a body element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}

    # node object
    n1OBJ = bpy.data.objects[n1]
    
    try:
        
        set_active_collection('bodies')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['bodies'].children.link(elcol)
        set_active_collection(elcol.name)
        
        # load the wireframe body object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'other.blend', 'Object'), filename = 'cg')
        # the append operator leaves just the imported object selected
        bodyOBJ = bpy.context.selected_objects[0]
        bodyOBJ.name = elem.name

        # automatic scaling
        s = n1OBJ.scale.magnitude*(1./sqrt(3.))
        print("body node scale")
        print(n1OBJ.scale.magnitude)
        bodyOBJ.scale = Vector(( s, s, s ))

        # element offset with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1@Vector(( f1[0], f1[1], f1[2] ))
    
        # place the body object in the position defined relative to node 1
        bodyOBJ.location = p1
        bodyOBJ.rotation_mode = 'QUATERNION'

        # set mbdyn props of object
        bodyOBJ.mbdyn.dkey = elem.name
        bodyOBJ.mbdyn.type = 'element'

        # set parenting of wireframe obj
        parenting(bodyOBJ, n1OBJ)
        elem.blender_object = bodyOBJ.name

        # set collections
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_body_elem(elem, layout) function

# Imports a Body in the scene
class BLENDYN_OT_import_body(bpy.types.Operator):
    bl_idname = "blendyn.import_body"
    bl_label = "Imports a body"
    int_label: bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['body_' + str(self.int_label)]
            retval = spawn_body_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + ':execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
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
# end of BLENDYN_OT_import_body class

# Displays body element info in the tools panel
def body_info_draw(elem, layout): 
    nd = bpy.context.scene.mbdyn.nodes
    
    col = layout.column(align = True)

    col.prop(elem, "magnitude", text = "mass")

    row = layout.row()
    col = layout.column(align = True)
    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node ID ")
            col.prop(node, "string_label", text = "Node label ")
            col.prop(node, "blender_object", text = "Node Object: ")
            col.enabled = False

            # Display offset from node 1
            row = layout.row()
            row.label(text = "CG offset in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)

    row = layout.row()
    row.label(text = "Inertia tensor")
    
    box = layout.box()
    split = box.split(.33)
    column = split.column()
    column.row().prop(elem.offsets[1], 'value', index = 0, text = 'Jxx')
    column.row().prop(elem.offsets[2], 'value', index = 0, text = 'Jyx')
    column.row().prop(elem.offsets[3], 'value', index = 0, text = 'Jzx')
    column = split.column()
    column.row().prop(elem.offsets[1], 'value', index = 1, text = 'Jxy')
    column.row().prop(elem.offsets[2], 'value', index = 1, text = 'Jyy')
    column.row().prop(elem.offsets[3], 'value', index = 1, text = 'Jzy')
    column = split.column()
    column.row().prop(elem.offsets[1], 'value', index = 2, text = 'Jxz')
    column.row().prop(elem.offsets[2], 'value', index = 2, text = 'Jyz')
    column.row().prop(elem.offsets[3], 'value', index = 2, text = 'Jzz')

    pass
# -----------------------------------------------------------
# end of body_info_draw(elem, layout) function
