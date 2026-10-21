# --------------------------------------------------------------------------
# Blendyn -- file shell4lib.py
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

from .utilslib import *

# shell4 elements are drawn by the flexible components (flexlib.py),
# not by objects of their own

def parse_shell4(rw, ed):
    """ Parses a shell4 element entry in the .log file """

    ret_val = True
    try:
        el = ed['shell4_' + str(rw[1])]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_shell4()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_shell4()", el)

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[3])
        el.nodes[2].int_label = int(rw[4])
        el.nodes[3].int_label = int(rw[5])
        # the prefix of the element variables in the NetCDF output
        el.mbclass = 'elem.shell4'

        el.is_imported = True
    except KeyError:

        el = ed.add()
        el.mbclass = 'elem.shell4'
        el.type = 'shell4'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_shell4()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_shell4()", el)

        for ndx in range(4):
            el.nodes.add()
            el.nodes[ndx].int_label = int(rw[2 + ndx])

        el.info_draw = "shell4_info_draw"
        el.name = el.type + '_' + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass

    return ret_val
# -----------------------------------------------------------
# end of parse_shell4(rw, ed) function

# function that displays shell4 info in panel -- [ optional ]
def shell4_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try:
        for ndx in range(4):
            node = nd['node_' + str(elem.nodes[ndx].int_label)]
            # Display node info
            col.prop(node, "int_label", text = "Node " + str(ndx + 1) + " ID ")
            col.prop(node, "string_label", text = "Node " + str(ndx + 1) + " label ")
            col.prop(node, "blender_object", text = "Node " + str(ndx + 1) + " Object: ")
        col.enabled = False
        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}
# -----------------------------------------------------------
# end of shell4_info_draw(elem, layout) function
