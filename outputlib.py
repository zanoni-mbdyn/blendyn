# --------------------------------------------------------------------------
# Blendyn -- file outputlib.py
# Copyright (C) 2015 -- 2017 Andrea Zanoni -- andrea.zanoni@polimi.it
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
from bpy.props import *

class MBDynOutputElemsDictionary(bpy.types.PropertyGroup):

    int_label = IntProperty(
        name = "Integer label of output element",
        description = ""
        )

    type = StringProperty(
        name = "Type of MBDyn output element",
        description = ""
        )

    name = StringProperty(
        name = "Name of File Output element",
        description =""
        )

    path = StringProperty(
        name = "Path of sock file if UNIX socket used",
        )

    host = StringProperty(
        name = "Hostname of output element",
        default = ""
        )

    port = IntProperty(
        name = "Port Address of output element",
        default = 9011
        )

    protocol = StringProperty(
        name = "Protocol used in output element",
        description = ""
        )

    create = BoolProperty(
        name = "Check if socket is created",
        default = True
        )

    output_frequency = IntProperty(
        name = "Output frequency"
        )

    motion_content = IntVectorProperty(
        name = "Output Flags",
        size = 5
        )

    nodes = StringProperty(
        name = "Order of Nodes"
        )
bpy.utils.register_class(MBDynOutputElemsDictionary)
# -----------------------------------------------------------
# end of MBDynOutputElemsDictionary class 


def parse_output_elem(context, rw):
    mbs = context.scene.mbdyn
    out_ed = mbs.output_elems

    def update_output_elem(output_element, rw):
        # output_element.host = rw[5]
        # Change this after Andrea's changes
        output_element.type = rw[3]

        if output_element.type == 'UNIX':
            output_element.path = rw[5]
        else:
            output_element.port = int(rw[5])

        output_element.protocol = rw[6]
        output_element.create = bool(rw[7])
        vector1 = list(map(int, rw[14: 14 + 5]))
        vector2 = [3, 9, 9, 3, 3]
        output_element.motion_content = [x*y for x, y in zip(vector2, vector1)]
        print(output_element.motion_content)
        output_element.nodes = " ".join(rw[19:])

    try:
        output_element = out_ed["{0}_{1}".format(rw[4], rw[1])]
        print("parse_output_elem(): found existing entry in output elements dictionary for output " + rw[1]\
        + ". Updating it.")
        update_output_elem(output_element, rw)
    except KeyError:
        output_element = out_ed.add()
        output_element.int_label = int(rw[1])
        output_element.name = "{0}_{1}".format(rw[4], rw[1])
        update_output_elem(output_element, rw)
