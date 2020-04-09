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

from .elements import BLENDYN_PG_elems_dictionary

class BLENDYN_PG_component_element(bpy.types.PropertyGroup):
    """ Element associated to a component """
    elem: StringProperty(
            name = "name of component element",
            description = "Name of component element in elements collection"
    )
    str_idx: IntProperty(
            name = "index of element",
            description = "Index of element in component structure"
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_components_element class
bpy.utils.register_class(BLENDYN_PG_component_element)

class BLENDYN_PG_component_section(bpy.types.PropertyGroup):
    """ Section, part of the component's geometry (mesh) model """
    curve: PointerProperty(
            type = bpy.types.Curve,
            description = "Pointer to id_data of section's curve"
    )
    scale: FloatProperty(
            name = "scale",
            description = "Section scale factor",
            min = 0.01,
            default = 1.0,
    )
    element: StringProperty(
            name = "element",
            description = "Element the section is assigned to",
            default = '',
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_components_section class
bpy.utils.register_class(BLENDYN_PG_component_section)
 
class BLENDYN_PG_components_dictionary(bpy.types.PropertyGroup):
    """ Data of a component (structural model + geometry) """
    type: EnumProperty(
            items = [('FROM_SECTIONS', "From sections", "From Sections", '', 1),\
                    ('MESH_OBJECT', "Mesh Object", "Mesh Object", '', 2)],
            name = "component type",
            default = 'FROM_SECTIONS'
    )
    elements: CollectionProperty(
            type = BLENDYN_PG_component_element,
            description = "Pointer to id_data of MBDyn elements"
    )
    el_index: IntProperty(
            name = "Component element index",
            default = 0
    )
    object: PointerProperty(
            type = bpy.types.Object
    )
    sections: CollectionProperty(
            type = BLENDYN_PG_component_section,
            description = "Pointer to id_data of section's curves"
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


class BLENDYN_UL_components_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'MESH_DATA'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_components_list class
bpy.utils.register_class(BLENDYN_UL_components_list)


class BLENDYN_UL_component_elements_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'CONSTRAINT'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = '{:<4}{}'.format(item.str_idx, item.elem), icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_component_elements_list class
bpy.utils.register_class(BLENDYN_UL_component_elements_list)


class BLENDYN_OT_component_add(bpy.types.Operator):
    """ Sets the adding_component flag to True  """
    bl_idname = "blendyn.add_component"
    bl_label = "Add an MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        comp = mbs.components.add()
        comp.name = 'component_' + str(len(mbs.components))
        mbs.adding_component = True
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add class


class BLENDYN_OT_component_add_confirm(bpy.types.Operator):
    """ Adds the component and sets adding_component flag to False  """
    bl_idname = "blendyn.add_component_confirm"
    bl_label = "Add an MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        mbs.adding_component = False
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add_confirm class


class BLENDYN_OT_component_add_elem(bpy.types.Operator):
    """ Adds and element to the component list, checking
        that is not already present """
    bl_idname = "blendyn.component_add_elem"
    bl_label = "Add an MBDyn component"

    comp_idx: bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn
        component = mbs.components[self.comp_idx]
        if mbs.comp_add_elem not in component.elements.keys():
            celem = component.elements.add()
            celem.elem = mbs.elems[mbs.comp_add_elem].name
            celem.str_idx = len(component.elements) - 1
            celem.name = mbs.elems[mbs.comp_add_elem].name
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add_confirm class
