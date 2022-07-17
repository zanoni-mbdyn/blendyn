# --------------------------------------------------------------------------
# Blendyn -- file modallib.py
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

# helper function which parse information of modal in .log file
def parse_modal(rw, ed):
    ret_val = True
    try:
        el = ed['modal_' + str(rw[1])]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beamslider()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_beamslider()", el)

        el.nodes[0].int_label = int(rw[2])

        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'modal'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beamslider()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_beamslider()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.import_function = "blendyn.import_modal"
        # el.info_draw = "beamslider_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# --------------------------------------------------------------------------
# end of function parse_modal()


# function that displays modal info in panel -- [ optional ]
def modal_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try:
        node = nd['node_' + str(elem.nodes[0].int_label)]
        # Display modal node info
        col.prop(node, "int_label", text="Node ID ")
        col.prop(node, "string_label", text="Node label ")
        col.prop(node, "blender_object", text="Node Object: ")
        col.enabled = False

        # Display offset of modal node info
        row = layout.row()
        row.label(text="offset 1 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align=True)
        col.prop(elem.offsets[0], "value", text="", slider=False)

        node = nd['node_' + str(elem.nodes[1].int_label)]

        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of modal_info_draw() function

# Create an object representing modal joint element
def spawn_modal_element(elem, context):
    """ Draws a modal joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE_NOTFOUND'}

    # nodes' objects
    nOBJ = bpy.data.objects[n]

    try:
        set_active_collection('joints')
        elcol = bpy.data.collections.new(name=elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe beam slider joint object from the library
        bpy.ops.wm.append(directory=os.path.join(mbs.addon_path, \
                                                 'library', 'joints.blend', 'Object'), filename='modal')

        # the append operator leaves just the imported object selected
        modaljOBJ = bpy.context.selected_objects[0]
        modaljOBJ.name = elem.name

        # automatic scaling
        s = nOBJ.scale.magnitude*(1./sqrt(3.))
        modaljOBJ.scale = Vector((s, s, s))

        # project offsets in global frame
        pN, q, S = nOBJ.matrix_basis.decompose()

        # place the joint object in the position of the node (no offset)
        modaljOBJ.location = pN
        modaljOBJ.rotation_mode = 'QUATERNION'
        modaljOBJ.rotation_quaternion = Quaternion(q)

        # set parenting of wireframe obj
        parenting(modaljOBJ, nOBJ)

        modaljOBJ.mbdyn.dkey = elem.name
        modaljOBJ.mbdyn.type = 'element'
        elem.blender_object = modaljOBJ.name

        # set collections
        elcol.objects.link(nOBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_modal_element() function


class BLENDYN_OT_import_modal(bpy.types.Operator):
    """ Imports and modal joint element
        into the Blender scene """
    bl_idname = "blendyn.import_modal"
    bl_label = "Imports and modal joint element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['modal_' + str(self.int_label)]
            retval = spawn_modal_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE_NOTFOUND'}:
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
                # Should nod be reached
                return retval
        except KeyError:
            eldbmsg({'DICT_ERROR'}, type(self).__name__ + '::execute()', None)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_modal_slider class.




