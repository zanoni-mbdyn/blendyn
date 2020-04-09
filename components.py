# --------------------------------------------------------------------------
# Blendyn -- file components.py
# Copyright (C) 2020 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import os

import bpy
from bpy.props import *

import logging
baseLogger = logging.getLogger()
baseLogger.setLevel(logging.DEBUG)

from mathutils import *
from math import *

from .blendyn import

class BLENDYN_PG_component_element(bpy.types.PropertyGroup):
    """ MBDyn Element, part of the component's structural model """
    elem: PointerProperty(
        type = BLENDYN_PG_elems_dictionary
        description = "Pointer to id_data of MBDyn element"
    )

    def elem(self, elem):
        self.elem = elem
        self.name = elem.name
        return self.elem
# -----------------------------------------------------------
# end of BLENDYN_PG_components_element class
bpy.utils.register_class(BLENDYN_PG_component_element)

class BLENDYN_PG_component_section(bpy.types.PropertyGroup):
    """ Section, part of the component's geometry (mesh) model """
    curve: PointerProperty(
        type = bpy.types.Curve
        description = "Pointer to id_data of section's curve"
    )

    def curve(self, curve):
        self.curve = curve
        self.name = curve.name
        return self.curve
# -----------------------------------------------------------
# end of BLENDYN_PG_components_section class
bpy.utils.register_class(BLENDYN_PG_component_section)

class BLENDYN_PG_components_dictionary(bpy.types.PropertyGroup):
    """ Data of a component (structural model + geometry) """
    type: EnumProperty(
            items: [('FROM_SECTIONS', "From sections", "From Sections", '', 1),\
                    ('MESH_OBJECT', "Mesh Object", "Mesh Object", '', 2)]
            name = "component type",
            default = 'FROM_SECTIONS'
    )
    elements: CollectionProperty(
            type = BLENDYN_PG_component_element
    )
    object: PointerProperty(
            type = bpy.types.Object
    )
    sections: CollectionProperty(
            type = BLENDYN_PG_component_section
    )
    arm_ns: IntProperty(
            name = "armature subdivisions",
            description = "number of subdivisions in components' armature",
            default = 5
    )
    mesh_ns: IntProperty(
            name = "mesh subdivisions",
            description = "number of subdivisions in components' mesh",
            default = 20
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_components_dictionary class
bpy.utils.register_class(BLENDYN_PG_components_dictionary)



