# --------------------------------------------------------------------------
# Blendyn -- file beamsliderlib.py
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

# helper function which parse information of beam slider in .log file
def parse_beam_slider(rw, ed):
    ret_val = True
    try:
        el = ed['beamslider_' + str(rw[1])]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beamslider()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_beamslider()", el)

        el.nodes[0].int_label = int(rw[2])

        el.offsets[0].value = Vector((float(rw[3]), float(rw[4]), float(rw[5])))

        R = Matrix().to_3x3()
        parse_rotmat(rw, 6, R)
        el.rotoffsets[0].value = R.to_quaternion()

        el.beam_number = int(rw[15])

        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'beamslider'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beamslider()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_beamslider()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector((float(rw[3]), float(rw[4]), float(rw[5])))

        R = Matrix().to_3x3()
        parse_rotmat(rw, 6, R)
        el.rotoffsets.add()
        el.rotoffsets[0].value = R.to_quaternion()

        el.beam_number = int(rw[15])

        el.import_function = "blendyn.import_beamslider"
        # el.info_draw = "beamslider_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# --------------------------------------------------------------------------
# end of function parse_beam_slider()


# function that displays beam slider info in panel -- [ optional ]
def beam_slider_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try:
        node = nd['node_' + str(elem.nodes[0].int_label)]
        # Display beam slider node info
        col.prop(node, "int_label", text="Node ID ")
        col.prop(node, "string_label", text="Node label ")
        col.prop(node, "blender_object", text="Node Object: ")
        col.enabled = False

        # Display offset of beam slider node info
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
# end of beam_slider_info_draw() function

# Create an object representing beam slider joint element
def spawn_beam_slider_element(elem, context):
    """ Draws a beam slider joint element, loading a wireframe
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
                                                 'library', 'joints.blend', 'Object'), filename='beamslider.arrow')

        # the append operator leaves just the imported object selected
        beamsliderjOBJa = bpy.context.selected_objects[0]
        beamsliderjOBJ = beamsliderjOBJa.constraints[0].target
        beamsliderjOBJ.name = elem.name
        beamsliderjOBJa.name = elem.name + '.arrow'

        # automatic scaling
        s = nOBJ.scale.magnitude*(1./sqrt(3.))
        print("beam slider node scale")
        print(nOBJ.scale.magnitude)
        beamsliderjOBJ.scale = Vector((s, s, s))

        # project offsets in global frame
        pN, q, S = nOBJ.matrix_basis.decompose()

        # place the joint object in the position defined relative to node
        # beamsliderjOBJ.location = nOBJ.location + R@Vector(elem.offsets[0].value[0:])
        beamsliderjOBJ.location = pN + q.to_matrix() @ Vector(elem.offsets[0].value[0:])
        beamsliderjOBJ.rotation_mode = 'QUATERNION'
        beamsliderjOBJ.rotation_quaternion = Quaternion(elem.rotoffsets[0].value[0:])

        # set parenting of wireframe obj
        parenting(beamsliderjOBJ, nOBJ)

        beamsliderjOBJ.mbdyn.dkey = elem.name
        beamsliderjOBJ.mbdyn.type = 'element'
        elem.blender_object = beamsliderjOBJ.name

        # set collections
        elcol.objects.link(nOBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_beam_slider_element() function


class BLENDYN_OT_import_beam_slider(bpy.types.Operator):
    """ Imports and beam slider joint element
        into the Blender scene """
    bl_idname = "blendyn.import_beamslider"
    bl_label = "Imports and beam slider joint element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['beamslider_' + str(self.int_label)]
            retval = spawn_beam_slider_element(elem, context)
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
# end of BLENDYN_OT_import_beam_slider class.




