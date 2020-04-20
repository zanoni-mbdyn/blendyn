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

from .componentlib import *

import pdb

class BLENDYN_PG_component_element(bpy.types.PropertyGroup):
    """ Element associated to a component """
    elem: StringProperty(
            name = "name of component element",
            description = "Name of component element in elements collection"
    )
    str_idx: IntProperty(
            name = "index of element",
            description = "Index of element in component structure",
            update = update_elem_str_idx
    )
    arm_ns: IntProperty(
            name = "armature subdivisions",
            description = "number of subdivisions in components' element armature",
            default = 5,
            min = 2
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_components_element class
bpy.utils.register_class(BLENDYN_PG_component_element)


class BLENDYN_PG_components_dictionary(bpy.types.PropertyGroup):
    """ Data of a component (structural model + geometry) """
    elements: CollectionProperty(
            type = BLENDYN_PG_component_element,
            description = "Pointer to id_data of MBDyn elements"
    )
    el_index: IntProperty(
            name = "Component element index",
            default = 0
    )
    object: EnumProperty(
            items = get_comp_mesh_objects,
            name = "Mesh Object",
    )
    mesh_ns: IntProperty(
            name = "mesh subdivisions",
            description = "number of subdivisions in components' mesh",
            default = 20
    )
    armature: PointerProperty(
            type = bpy.types.Armature,
            name = "Armature",
            description = "Component armature"
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_components_dictionary class
bpy.utils.register_class(BLENDYN_PG_components_dictionary)

class BLENDYN_UL_component_object_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'MESH_DATA'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", icon = custom_icon, emboss = False, text = "")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_component_object_list class
bpy.utils.register_class(BLENDYN_UL_component_object_list)


class BLENDYN_UL_components_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'MESH_DATA'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", icon = custom_icon, emboss = False, text = "")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_components_list class
bpy.utils.register_class(BLENDYN_UL_components_list)


class BLENDYN_UL_component_elements_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            split = row.split(factor = 0.2)
            col = split.column()
            col.prop(item, "str_idx", icon = 'CUBE', text = "" )
            col = split.column()
            split = col.split(factor = .67)
            col = split.column()
            col.label(text = item.elem)
            col = split.column()
            col.prop(item, "arm_ns", icon = 'MOD_ARRAY', text = "" )
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = 'CUBE')
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
        mbs.cd_index = len(mbs.components) - 1 
        mbs.adding_component = True
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add class


class BLENDYN_OT_component_remove(bpy.types.Operator):
    """ Removes component  """
    bl_idname = "blendyn.remove_component"
    bl_label = "Remove selected MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        component = mbs.components[mbs.cd_index]
        bpy.data.armatures.remove(component.armature)
        mbs.components.remove(mbs.cd_index)
        mbs.cd_index -= 1
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_remove class


class BLENDYN_OT_component_add_cancel(bpy.types.Operator):
    """ Cancels adding the component """
    bl_idname = "blendyn.add_component_cancel"
    bl_label = "Cancel add of MBDyn component"

    def execute(self, context):
        selftag = "BLENDYN_OT_component_add_cancel::execute(): "
        mbs = context.scene.mbdyn
        mbs.components.remove(mbs.cd_index)
        mbs.adding_component = False
        mbs.cd_index -= 1

        message = "component add aborted."
        print(message)
        baseLogger.info(selftag + message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add_cancel class

class BLENDYN_OT_component_add_confirm(bpy.types.Operator):
    """ Adds the component and sets adding_component flag to False  """
    bl_idname = "blendyn.add_component_confirm"
    bl_label = "Confirm add of MBDyn component"

    def execute(self, context):
        selftag = "BLENDYN_OT_component_add_confirm::execute(): "
        mbs = context.scene.mbdyn
        component = mbs.components[mbs.cd_index]
        if component.type == 'MESH_OBJECT':
            retval = add_mesh_component(context, component)
        elif component.type == 'FROM_SECTIONS':
            retval = add_sections_component(context, component)
        else:
            # should not be reached!
            message = "unknown component type!"
            print(message)
            baseLogger.error(selftag + message)
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
        mbs.adding_component = False

        if retval == {'ELEM_TYPE_UNSUPPORTED'}:
            # should not be reached
            message = "unknown element type in component!"
            print(message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}
        elif retval == {'ARMATURE_PARENT_FAILED'}:
            message = "unable to parent mesh to armature."
            print(message)
            baseLogger.warning(selftag + message)
            return {'CANCELLED'}
        elif retval == {'FINISHED'}:
            message = "Added component " + component.name + "."
            print(message)
            baseLogger.info(selftag + message)
            return retval
    
    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add_confirm class


class BLENDYN_OT_component_add_elem(bpy.types.Operator):
    """ Adds and element to the component list, checking
        that is not already present """
    bl_idname = "blendyn.component_add_elem"
    bl_label = "Add an element to a MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        component = mbs.components[mbs.cd_index]
        if mbs.comp_selected_elem not in component.elements.keys():
            celem = component.elements.add()
            celem.elem = mbs.elems[mbs.comp_selected_elem].name
            celem.str_idx = len(component.elements) - 1
            celem.name = mbs.elems[mbs.comp_selected_elem].name
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add_elem class


class BLENDYN_OT_component_remove_elem(bpy.types.Operator):
    """ Removes and element to the component list, reordering
        the others """
    bl_idname = "blendyn.component_remove_elem"
    bl_label = "Remove an element from a MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        component = mbs.components[mbs.cd_index]
        component.elements.remove(component.el_index)
        for idx in range(len(component.elements)):
            component.elements[idx].str_idx = idx
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_remove_elem class

class BLENDYN_OT_component_remove_elem(bpy.types.Operator):
    """ Removes an element to the component list and reorders
        the others """
    bl_idname = "blendyn.component_remove_elem"
    bl_label = "Remove an element from a MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        component = mbs.components[mbs.cd_index]
        component.elements.remove(component.el_index)
        for idx in range(len(component.elements)):
            component.elements[idx].str_idx = idx
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_remove_elem class

class BLENDYN_OT_component_remove_all_elems(bpy.types.Operator):
    """ Removes all elements to the component list """
    bl_idname = "blendyn.component_remove_all_elems"
    bl_label = "Remove an element from a MBDyn component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        component = mbs.components[mbs.cd_index]
        component.elements.clear()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_remove_all_elems class

class BLENDYN_OT_component_add_selected_elems(bpy.types.Operator):
    """ Add all the selected elements into the component list """
    bl_idname = "blendyn.component_add_selected_elems"
    bl_label = "Add selected elements to component"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        component = mbs.components[mbs.cd_index]
        sel_elems = [ed[obj.mbdyn.dkey] for obj in bpy.context.selected_objects \
                if (obj.mbdyn.type == 'element') and (ed[obj.mbdyn.dkey].type in DEFORMABLE_ELEMENTS) ]
        for idx in range(len(sel_elems)):
            celem = component.elements.add()
            celem.elem = sel_elems[idx].name
            celem.str_idx = idx
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_component_add_selected_elems class
