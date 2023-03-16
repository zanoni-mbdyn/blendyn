# --------------------------------------------------------------------------
# Blendyn -- file plotlib.py
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

from .elementlib import *
from .matplotlib import *
from .pygalplotlib import *
from .bokehplotlib import *
import os

class BLENDYN_UL_plot_var_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text = item.name)
# -----------------------------------------------------------
# end of BLENDYN_UL_plot_var_list class
bpy.utils.register_class(BLENDYN_UL_plot_var_list)


class BLENDYN_UL_object_plot_var_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text = item.name)
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        obj = context.object
        hf = bpy.types.UI_UL_list
        try:
            dictitem = get_dict_item(context, obj)
            flt_flags = hf.filter_items_by_name(dictitem.mbclass + '.' + \
                    str(dictitem.int_label), self.bitflag_filter_item, items)
            return flt_flags, []
        except KeyError:
            return [], []
        except AttributeError:
            return [], []
# -----------------------------------------------------------
# end of BLENDYN_UL_object_plot_var_list class
bpy.utils.register_class(BLENDYN_UL_object_plot_var_list)

class BLENDYN_UL_render_vars_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text = item.name)
        layout.label(text = item.variable + comp_repr(item.components, item.variable, context))
# -----------------------------------------------------------
# end of BLENDYN_UL_render_vars_list class
bpy.utils.register_class(BLENDYN_UL_render_vars_list)



## Simple operator to set plot frequency for
class BLENDYN_OT_set_plot_freq(bpy.types.Operator):
    """ Sets the plot frequency for the current object plot variable equal
        to the import frequency of the MBDyn results """
    bl_idname = "blendyn.set_plot_freq"
    bl_label = "Sets the plot frequency for the scene equal to the load frequency"
    is_object: bpy.props.BoolProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn
        if self.is_object:
            pvar = mbs.plot_vars[context.object.mbdyn.plot_var_index]
        else:
            pvar = mbs.plot_vars[mbs.plot_var_index]
        
        pvar.plot_frequency = int(context.scene.mbdyn.load_frequency)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_set_plot_freq class 

class BLENDYN_OT_set_render_variable(bpy.types.Operator):
    """ Sets the NetCDF variables to be\
        displayed in the rendered frame """

    bl_idname = "blendyn.set_render_variable"
    bl_label = "Set Render Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if not(mbs.render_var_name in mbs.render_vars.keys()):
            rend = mbs.render_vars.add()
            rend.name = mbs.plot_vars[mbs.plot_var_index].name
            rend.varname = mbs.render_var_name
            rend.variable = mbs.plot_vars[mbs.plot_var_index].name
            rend.components = mbs.plot_vars[mbs.plot_var_index].plot_comps
            return {'FINISHED'}
        else:
            message = "BLENDYN_OT_set_render_variable::execute() "\
                    + "Variable already set for display"
            self.report({'WARNING'}, message)
            logging.warning(message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_render_variable class

class BLENDYN_OT_delete_render_variable(bpy.types.Operator):
    """ Delete a render variable """
    bl_idname = "blendyn.delete_render_variable"
    bl_label = "Delete Render Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        message = "BLENDYN_OT_delete_render_variable::execute() "\
                + "Deleting render variable "\
                + mbs.render_vars[mbs.render_index].varname
        self.report({'INFO'}, message)
        logging.info(message)
        
        mbs.render_vars.remove(mbs.render_index)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_delete_render_variable class

class BLENDYN_OT_delete_all_render_variables(bpy.types.Operator):
    """ Deleted all variables set for display in render frames """
    bl_idname = "blendyn.delete_all_render_variables"
    bl_label = "Delete all Render variables"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.render_vars.clear()

        message = "BLENDYN_OT_delete_all_render_variables::execute() "\
                + "Deleted all render variables"
        self.report({'INFO'}, message)
        logging.info(message)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_delete_all_render_variables class

class BLENDYN_OT_show_display_group(bpy.types.Operator):
    """ Shows the selected display group """
    bl_idname = "blendyn.show_display_group"
    bl_label = "Show display group"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if mbs.display_enum_group == '':
            message = "BLENDYN_OT_show_display_group::execute() "\
                    + "No Groups set"
            self.report({'ERROR'}, message)
            logging.error(message)

        mbs.render_vars.clear()

        for var in mbs.display_vars_group[mbs.display_enum_group].group:
            rend = mbs.render_vars.add()
            rend.idx = var.idx
            rend.varname = var.varname
            rend.variable = var.variable
            rend.components = var.components

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_show_display_group class

class BLENDYN_OT_set_display_group(bpy.types.Operator):
    """ Set group of variables to display in rendered frames """
    bl_idname = "sel.set_display_group"
    bl_label = "Set Display Group"

    def execute(self, context):
        mbs = context.scene.mbdyn

        exist_display_groups = [mbs.display_vars_group[var].name for var in range(len(mbs.display_vars_group))]

        try:
            index = exist_display_groups.index(mbs.group_name)
            mbs.display_vars_group[index].group.clear()

            vargroup = mbs.display_vars_group[mbs.group_name]

            for ii in list(range(len(mbs.render_vars))):
                rend = vargroup.group.add()
                rend.idx = mbs.render_vars[ii].idx
                rend.varname = mbs.render_vars[ii].varname
                rend.variable = mbs.render_vars[ii].variable
                rend.components = mbs.render_vars[ii].components


        except ValueError:
            vargroup = mbs.display_vars_group.add()
            vargroup.name = mbs.group_name

            for ii in list(range(len(mbs.render_vars))):
                rend = vargroup.group.add()
                rend.idx = mbs.render_vars[ii].idx
                rend.varname = mbs.render_vars[ii].varname
                rend.variable = mbs.render_vars[ii].variable
                rend.components = mbs.render_vars[ii].components

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_display_group class

## Panel in object properties toolbar
class BLENDYN_PT_object_plot(bpy.types.Panel):
    """ Plotting of MBDyn NetCDF variables:
        Object properties panel"""
    bl_label = "MBDyn data plot"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mbs = context.scene.mbdyn
        mbo = context.object.mbdyn
        try:
            pvar = mbs.plot_vars[mbo.plot_var_index]
        except IndexError:
            return
        layout = self.layout
        row = layout.row()

        if mbs.use_netcdf:
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, 'r')
            row.template_list('BLENDYN_UL_object_plot_var_list', \
                    "MBDyn variable to plot", \
                    mbs, "plot_vars", \
                    mbo, "plot_var_index")
            row = layout.row()
            row.prop(pvar, "as_driver")
            row = layout.row()
            row.prop(mbs, "plot_engine", text = "Plot engine:")
            try:
                dim = len(nc.variables[pvar.name].shape)
                if dim == 2 and mbs.plot_type != "TRAJECTORY":     # vec3
                    box = layout.box()
                    split = box.split(factor = 1./3.)
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 0, text = "x")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 1, text = "y")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 2, text = "z")
                elif dim == 3 and mbs.plot_type != "TRAJECTORY":
                    if pvar.name[-1] == 'R':
                        box = layout.box()
                        split = box.split(factor = 1./3.)
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 0, text = "(1,1)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(pvar, "plot_comps", index = 3, text = "(2,2)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(pvar, "plot_comps", index = 4, text = "(2,3)")
                        column.row().prop(pvar, "plot_comps", index = 5, text = "(3,3)")
                    else:
                        box = layout.box()
                        split = box.split(factor = 1./3.)
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 0, text = "(1,1)")
                        column.row().prop(pvar, "plot_comps", index = 3, text = "(2,1)")
                        column.row().prop(pvar, "plot_comps", index = 6, text = "(3,1)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(pvar, "plot_comps", index = 4, text = "(2,2)")
                        column.row().prop(pvar, "plot_comps", index = 7, text = "(3,2)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(pvar, "plot_comps", index = 5, text = "(2,3)")
                        column.row().prop(pvar, "plot_comps", index = 8, text = "(3,3)")
                row = layout.row()
                col = layout.column()
                col.prop(pvar, "plot_frequency")
                col.operator(BLENDYN_OT_set_plot_freq.bl_idname, \
                        text = "Use Import frequency").is_object = True
                row = layout.row()
                row.prop(mbs, "plot_type", text="Plot type:")
                row = layout.row()
                if mbs.plot_type == "TIME_HISTORY":
                    if mbs.plot_engine == "PYGAL":
                        row = layout.row()
                        row.operator(BLENDYN_OT_plot_var_object.bl_idname,\
                                text = "Plot variable")
                    elif mbs.plot_engine == "MATPLOTLIB":
                        row = layout.row()
                        row.operator(BLENDYN_OT_mplot_var_object.bl_idname,\
                                text = "Plot variable")
                    elif mbs.plot_engine == "BOKEH":
                        box = layout.box()
                        split = box.split(factor=1. / 2.)
                        column = split.column()
                        column.prop(mbs, "show_in_localhost", text="Show in localhost")
                        column = split.column()
                        column.prop(mbs, "save_as_png", index=1, text="Save as png")
                        row = layout.row()
                        row.operator(BLENDYN_OT_bplot_var_object.bl_idname, \
                                     text="Plot variable")
                elif mbs.plot_type == "AUTOSPECTRUM":
                    row = layout.row()
                    row.prop(pvar, "plot_xrange_min", text="Plot frequency min")
                    row = layout.row()
                    row.prop(pvar, "plot_xrange_max", text="Plot frequency max")
                    row = layout.row()
                    row.prop(pvar, "fft_remove_mean")
                    if mbs.plot_engine == "PYGAL":
                        row = layout.row()
                        row.operator(BLENDYN_OT_plot_var_sxx_object.bl_idname,\
                                     text="Plot variable Autospectrum")
                    elif mbs.plot_engine == "MATPLOTLIB":
                        row = layout.row()
                        row.operator(BLENDYN_OT_mplot_var_sxx_object.bl_idname,\
                                     text="Plot variable Autospectrum")
                    elif mbs.plot_engine == "BOKEH":
                        box = layout.box()
                        split = box.split(factor=1. / 2.)
                        column = split.column()
                        column.prop(mbs, "show_in_localhost", text="Show in localhost")
                        column = split.column()
                        column.prop(mbs, "save_as_png", index=1, text="Save as png")
                        row = layout.row()
                        row.operator(BLENDYN_OT_bplot_var_sxx_object.bl_idname, \
                                     text="Plot variable Autospectrum")
                elif mbs.plot_type == "TRAJECTORY":
                    if mbs.plot_engine == "PYGAL":
                        row = layout.row()
                        row.label(text="This engine is not support!")
                    elif mbs.plot_engine == "MATPLOTLIB":
                        row = layout.row()
                        row.operator(BLENDYN_OT_mplot_trajectory_object.bl_idname, \
                                     text="Plot variable trajectory")
                    elif mbs.plot_engine == "BOKEH":
                        box = layout.box()
                        split = box.split(factor=1. / 2.)
                        column = split.column()
                        column.prop(mbs, "show_in_localhost", text="Show in localhost")
                        column = split.column()
                        column.prop(mbs, "save_as_png", index=1, text="Save as png")
                        row = layout.row()
                        row.operator(BLENDYN_OT_bplot_trajectory_object.bl_idname, \
                                     text="Plot variable trajectory")
            except KeyError:
                pass
        else:
            row = layout.row()
            row.label(text = "Plotting from text output")
            row.label(text = "is not supported yet.")
# -----------------------------------------------------
# end of BLENDYN_PT_object_plot class

## Panel in Scene toolbar
class BLENDYN_PT_plot_scene(bpy.types.Panel):
    """ Plotting of MBDyn NetCDF variables:  
        Scene properties panel"""
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_options = {'DEFAULT_CLOSED'}
    bl_label = "MBDyn Data Plot"
    
    def draw(self, context):
        mbs = context.scene.mbdyn
        try:
            pvar = mbs.plot_vars[mbs.plot_var_index]
        except IndexError:
            return    
        layout = self.layout
        row = layout.row()

        if mbs.use_netcdf:
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, 'r')
            row.template_list('BLENDYN_UL_plot_var_list', \
                    "MBDyn variable to plot", \
                    mbs, "plot_vars",
                    mbs, "plot_var_index")
            row = layout.row()
            row.prop(mbs, "plot_engine", text = "Plot engine:")
            try:
                dim = len(nc.variables[pvar.name].shape)
                if dim == 2 and mbs.plot_type != "TRAJECTORY":     # Vec3
                    box = layout.box()
                    split = box.split(factor = 1./3.)
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 0, text = "x")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 1, text = "y")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 2, text = "z")
                elif dim == 3 and mbs.plot_type != "TRAJECTORY":  # Mat3x3
                    if pvar.name[-1] == 'R':
                        box = layout.box()
                        split = box.split(factor = 1./3.)
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 0, text = "(1,1)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(pvar, "plot_comps", index = 3, text = "(2,2)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(pvar, "plot_comps", index = 4, text = "(2,3)")
                        column.row().prop(pvar, "plot_comps", index = 5, text = "(3,3)")
                    else:
                        box = layout.box()
                        split = box.split(factor = 1./3.)
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 0, text = "(1,1)")
                        column.row().prop(pvar, "plot_comps", index = 3, text = "(2,1)")
                        column.row().prop(pvar, "plot_comps", index = 6, text = "(3,1)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(pvar, "plot_comps", index = 4, text = "(2,2)")
                        column.row().prop(pvar, "plot_comps", index = 7, text = "(3,2)")
                        column = split.column()
                        column.row().prop(pvar, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(pvar, "plot_comps", index = 5, text = "(2,3)")
                        column.row().prop(pvar, "plot_comps", index = 8, text = "(3,3)")
                # plot controls
                row = layout.row()
                col = layout.column()
                col.prop(pvar, "plot_frequency")
                col.operator(BLENDYN_OT_set_plot_freq.bl_idname, \
                        text = "Use Import freq").is_object = False
                row = layout.row()
                row.prop(mbs, "plot_type")
                if mbs.plot_type == "TIME_HISTORY":
                    if mbs.plot_engine == "PYGAL":
                        row = layout.row()
                        row.operator(BLENDYN_OT_plot_var_scene.bl_idname,\
                                text="Plot variable")
                    elif mbs.plot_engine == "MATPLOTLIB":
                        row = layout.row()
                        row.operator(BLENDYN_OT_mplot_var_scene.bl_idname,\
                                     text = "Plot variable")
                    elif mbs.plot_engine == "BOKEH":
                        box = layout.box()
                        split = box.split(factor=1. / 2.)
                        column = split.column()
                        column.prop(mbs, "show_in_localhost", text="Show in localhost")
                        column = split.column()
                        column.prop(mbs, "save_as_png", index=1, text="Save as png")
                        row = layout.row()
                        row.operator(BLENDYN_OT_bplot_var_scene.bl_idname, \
                                     text="Plot variable")
                elif mbs.plot_type == "AUTOSPECTRUM":
                    row = layout.row()
                    row.prop(pvar, "fft_remove_mean")
                    row = layout.row()
                    row.prop(pvar, "plot_xrange_min", text = "Plot frequency min")
                    row = layout.row()
                    row.prop(pvar, "plot_xrange_max", text = "Plot frequency max")
                    if mbs.plot_engine == "PYGAL":
                        row = layout.row()
                        row.operator(BLENDYN_OT_plot_var_sxx_scene.bl_idname,\
                                text = "Plot variable Autospectrum")
                    elif mbs.plot_engine == "MATPLOTLIB":
                        row = layout.row()
                        row.operator(BLENDYN_OT_mplot_var_sxx_scene.bl_idname,\
                                     text = "Plot variable Autospectrum")
                    elif mbs.plot_engine == "BOKEH":
                        box = layout.box()
                        split = box.split(factor=1. / 2.)
                        column = split.column()
                        column.prop(mbs, "show_in_localhost", text="Show in localhost")
                        column = split.column()
                        column.prop(mbs, "save_as_png", index=1, text="Save as png")
                        row = layout.row()
                        row.operator(BLENDYN_OT_bplot_var_sxx_scene.bl_idname, \
                                     text="Plot variable Autospectrum")
                elif mbs.plot_type == "TRAJECTORY":
                    if mbs.plot_engine == "PYGAL":
                        row = layout.row()
                        row.label(text="This plot engine is not support!")
                    elif mbs.plot_engine == "MATPLOTLIB":
                        row = layout.row()
                        row.operator(BLENDYN_OT_mplot_trajectory_scene.bl_idname,\
                                     text = "Plot variable trajectory")
                    elif mbs.plot_engine == "BOKEH":
                        box = layout.box()
                        split = box.split(factor=1. / 2.)
                        column = split.column()
                        column.prop(mbs, "show_in_localhost", text="Show in localhost")
                        column = split.column()
                        column.prop(mbs, "save_as_png", index=1, text="Save as png")
                        row = layout.row()
                        row.operator(BLENDYN_OT_bplot_trajectory_scene.bl_idname, \
                                     text="Plot variable trajectory")
            except IndexError:
                pass

            layout.separator()
            layout.separator()

            row = layout.row()
            row.template_list('BLENDYN_UL_render_vars_list', \
                    "MBDyn Variables to Render", \
                    mbs, "render_vars",\
                    mbs, "render_index")
            row = layout.row()
            row.prop(mbs, "render_var_name")

            row = layout.row()
            row.operator(BLENDYN_OT_set_render_variable.bl_idname, text = 'Set Display Variable')

            row = layout.row()
            row.operator(BLENDYN_OT_delete_render_variable.bl_idname, \
                    text = 'Delete Display Variable')
            row = layout.row()
            row.operator(BLENDYN_OT_delete_all_render_variables.bl_idname, text = 'Clear')

            # plot controls
            if mbs.plot_engine == "PYGAL":
                row = layout.row()
                row.operator(BLENDYN_OT_plot_variables_list.bl_idname, \
                        text="Plot variables in List")
            elif mbs.plot_engine == "MATPLOTLIB":
                row = layout.row()
                row.operator(BLENDYN_OT_mplot_variables_list.bl_idname,\
                        text="Plot variables in List")
            elif mbs.plot_engine == "BOKEH":
                box = layout.box()
                split = box.split(factor=1. / 2.)
                column = split.column()
                column.prop(mbs, "show_in_localhost", text="Show in localhost")
                column = split.column()
                column.prop(mbs, "save_as_png", index=1, text="Save as png")
                row = layout.row()
                row.operator(BLENDYN_OT_bplot_variables_list.bl_idname, \
                             text="Plot variables in List")

            row.prop(mbs, "plot_group", text = "Plot Group")
            layout.separator()
            layout.separator()

            row = layout.row()
            row.prop(mbs, "group_name")
            row.operator(BLENDYN_OT_set_display_group.bl_idname, text="Set Display Group")

            row = layout.row()
            row.prop(mbs, "display_enum_group")
            row.operator(BLENDYN_OT_show_display_group.bl_idname, text = "Show Display Group")

        else:
            row = layout.row()
            row.label(text = "Plotting from text output")
            row.label(text = "is not supported yet.")
# -----------------------------------------------------------
# end of BLENDYN_PT_plot_scene class
