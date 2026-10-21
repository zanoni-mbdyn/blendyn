# --------------------------------------------------------------------------
# Blendyn -- file beamlib.py
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
import numpy as np

from mathutils import *
from math import *

from .utilslib import *

import logging

# helper function to parse beam2
def parse_beam2(rw, ed):
    ret_val = True
    try:
        el = ed['beam2_' + rw[1]]

        eldbmsg({'PARSE_ELEM'}, 'BLENDYN::parse_beam2()', el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_beam2()", el)

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.beam'

        el.is_imported = True

        pass

    except KeyError:

        el = ed.add()
        el.mbclass = 'elem.beam'
        el.type = 'beam2'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beam2()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_beam2()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        el.info_draw = "beam2_info_draw"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_beam2(rw, ed) function

def parse_beam3(rw, ed):

    ret_val = True
    try:
        el = ed['beam3_' + rw[1]]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beam3()", el)
        eldbmsg({'FOUND_IN_DICT'}, "BLENDYN::parse_beam3()", el)

        el.is_imported = False

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])
        el.nodes[2].int_label = int(rw[10])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))

        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.beam'

        el.is_imported = True

        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.beam'
        el.type = 'beam3'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beam3()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_beam3()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        el.nodes.add()
        el.nodes[2].int_label = int(rw[10])

        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))

        el.info_draw = "beam3_info_draw"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_beam3(rw, ed) function

# function that displays beam2 info in panel -- [ optional ]
def beam2_info_draw(elem, layout):
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
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of beam2_info_draw(elem, layout) function

# function that displays beam3 info in panel -- [ optional ]
def beam3_info_draw(elem, layout):
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
        layout.separator()

        node = nd['node_' + str(elem.nodes[2].int_label)]
        # Display node 3 info
        col.prop(node, "int_label", text = "Node 3 ID ")
        col.prop(node, "string_label", text = "Node 3 label ")
        col.prop(node, "blender_object", text = "Node 3 Object: ")
        col.enabled = False

        # Display offset of node 3 info
        row = layout.row()
        row.label(text = "offset 3 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[2], "value", text = "", slider = False)
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of beam3_info_draw(elem, layout) function
