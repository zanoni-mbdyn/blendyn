# --------------------------------------------------------------------------
# MBDynImporter -- file plotlib.py
# Copyright (C) 2016 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of MBDynImporter, add-on script for Blender.
#
#    MBDynImporter is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MBDynImporter  is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with MBDynImporter.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

# TODO: check for unnecessary stuff
import os

# from mathutils import *
# from math import *

import bpy

import pygal
import cairosvg

from .nodelib import *
from .elementlib import *

import pdb

try: 
    from netCDF4 import Dataset
except ImportError:
    print("mbdyn-blender: could not find netCDF4 module. NetCDF import "\
        + "will be disabled.")

import pdb

def get_plot_vars_glob(self, context):
    mbs = context.scene.mbdyn

    if mbs.use_netcdf:
        ncfile = mbs.file_path + mbs.file_basename + ".nc"
        nc = Dataset(ncfile, 'r', format='NETCDF3')
        N = len(nc.variables["time"])

        var_list = list()
        for var in nc.variables:
            m = nc.variables[var].shape
            if m[0] == N:
                plotvar = mbs.plot_vars.add()
                plotvar.name = var 

def get_plot_vars(self, context):
    mbs = context.scene.mbdyn
    mbo = context.active_object.mbdyn

    if mbs.use_netcdf:
        ncfile = mbs.file_path + mbs.file_basename + ".nc"
        nc = Dataset(ncfile, 'r', format='NETCDF3')
        key = mbo.type + "." + str(mbo.int_label)

        var_list = list()
        for var in nc.variables:
            if key in var and key != var:
                var_list.append(var)

        return [(var, var, 'Variable "%s"'%var) for var in var_list]
    else:
        return [('none', 'none', 'none', 1)]

class Scene_OT_MBDyn_plot_var(bpy.types.Operator):
    """ Plots the selected variable in the image editor 
        and optionally save it as .svg in the 'plots' directory.
        The user can choose among all the variables of all the 
        MBDyn entitites found in the output NetCDF fila."""
    bl_idname = "ops.mbdyn_plot_var_scene"
    bl_label = "Plot the selected MBDyn var"

    var_index = bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = mbs.file_path + mbs.file_basename + ".nc"
        nc = Dataset(ncfile, 'r', format='NETCDF3')

        # get its dimensions
        varname = mbs.plot_vars[mbs.plot_var_index].name
        var = nc.variables[varname]
        dim = len(var.shape)
        
        # get time vector
        time = nc.variables["time"]
        
        # set up pygal
        config = pygal.Config()
        config.show_dots = False
        config.legend_at_bottom = True
        config.truncate_legend = -1
        chart = pygal.XY(config)

        # create plot
        if dim == 2:
            n,m = var.shape
            for mdx in range(m):
                if mbs.plot_comps[mdx]:
                    chart.add(varname + "." + str(mdx + 1), \
                            [(time[idx], var[idx,mdx]) for idx in range(0, n, mbs.plot_frequency)])
        elif dim == 3:
            n,m,k = var.shape
            if mbs.plot_var[-1] == 'R':
                dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 2]
                dims2 = [0, 1, 2, 1, 2, 2]
            else:
                dims_names = ["(1,1)", "(1,2)", "(1,3)",\
                              "(2,1)", "(2,2)", "(2,3)",\
                              "(3,1)", "(3,2)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                dims2 = [0, 1, 2, 0, 1, 3, 0, 1, 2]
            for mdx in range(len(dims_names)):
                if mbs.plot_comps[mdx]:
                    chart.add(varname + dims_names[mdx], \
                            [(time[idx], var[idx, dims1[mdx], dims2[mdx]]) \
                            for idx in range(0, n, mbs.plot_frequency)])
        else:
            chart.add(varname, [(time[idx], var[idx]) \
                    for idx in range(0, len(time), mbs.plot_frequency)])
        chart.x_title = "time [s]"

        if not(bpy.data.is_saved):
            self.report({'ERROR'}, "Please save current Blender file first")
            return {'CANCELLED'}
 
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
           os.makedirs(plot_dir)

        basename = mbs.file_basename + "." + varname
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        cairosvg.svg2png(url = outfname + ".svg", write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        self.report({'INFO'}, "Variable " + varname + " plotted")
        return {'FINISHED'}
        

class Object_OT_MBDyn_plot_var(bpy.types.Operator):
    """ Plots the object's selected variable in the image editor 
        and optionally save it as .svg in the 'plots' directory """
    bl_idname = "ops.mbdyn_plot_var_obj"
    bl_label = "Plot the selected MBDyn var"

    def execute(self, context):
        mbo = context.object.mbdyn
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = mbs.file_path + mbs.file_basename + ".nc"
        nc = Dataset(ncfile, 'r', format='NETCDF3')

        # get its dimensions
        var = nc.variables[mbo.plot_var]
        dim = len(var.shape)

        # get time vector
        time = nc.variables["time"]
        
        # set up pygal
        config = pygal.Config()
        config.show_dots = False
        config.legend_at_bottom = True
        config.truncate_legend = -1
        chart = pygal.XY(config)

        # create plot
        if dim == 2:
            n,m = var.shape
            for mdx in range(m):
                if mbo.plot_comps[mdx]:
                    chart.add(mbo.plot_var + "." + str(mdx + 1), \
                            [(time[idx], var[idx,mdx]) for idx in range(0, n, mbo.plot_frequency)])
        elif dim == 3:
            n,m,k = var.shape
            if mbo.plot_var[-1] == 'R':
                dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 2]
                dims2 = [0, 1, 2, 1, 2, 2]
            else:
                dims_names = ["(1,1)", "(1,2)", "(1,3)",\
                              "(2,1)", "(2,2)", "(2,3)",\
                              "(3,1)", "(3,2)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                dims2 = [0, 1, 2, 0, 1, 3, 0, 1, 2]
            for mdx in range(len(dims_names)):
                if mbo.plot_comps[mdx]:
                    chart.add(mbo.plot_var + dims_names[mdx], \
                            [(time[idx], var[idx, dims1[mdx], dims2[mdx]]) \
                            for idx in range(0, n, mbo.plot_frequency)])
        else:
            chart.add(mbo.plot_var, [(time[idx], var[idx]) \
                    for idx in range(0, len(time), mbo.plot_frequency)])
        
        chart.x_title = "time [s]"

        if not(bpy.data.is_saved):
            self.report({'ERROR'}, "Please save current Blender file first")
            return {'CANCELLED'}
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
           os.makedirs(plot_dir)

        basename = mbs.file_basename + "." + mbo.plot_var
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        cairosvg.svg2png(url = outfname + ".svg", write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        self.report({'INFO'}, "Variable " + mbo.plot_var + " plotted")
        return {'FINISHED'}

## Simple operator to set plot frequency for object
class Object_OT_MBDyn_plot_freq(bpy.types.Operator):
    """ Sets the plot frequency for the current Object equal
        to the import frequency of the MBDyn results """
    bl_idname = "ops.mbdyn_set_plot_freq_obj"
    bl_label = "Sets the plot frequency for the object equal to the load frequency"

    def execute(self, context):
        context.object.mbdyn.plot_frequency = context.scene.mbdyn.load_frequency
        return {'FINISHED'}

## Simple operator to set plot frequency for scene
class Scene_OT_MBDyn_plot_freq(bpy.types.Operator):
    """ Sets the plot frequency for the current Object equal
        to the import frequency of the MBDyn results """
    bl_idname = "ops.mbdyn_set_plot_freq_scene"
    bl_label = "Sets the plot frequency for the scene equal to the load frequency"

    def execute(self, context):
        context.scene.mbdyn.plot_frequency = context.scene.mbdyn.load_frequency
        return {'FINISHED'}

## Panel in object properties toolbar
class MBDynPlotPanelObject(bpy.types.Panel):
    """ Plotting of MBDyn entities private data """
    bl_label = "MBDyn data plot"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        mbs = context.scene.mbdyn
        mbo = context.object.mbdyn
        layout = self.layout
        row = layout.row()

        if mbs.use_netcdf:
            ncfile = mbs.file_path + mbs.file_basename + ".nc"
            nc = Dataset(ncfile, 'r', format='NETCDF3')
            row.prop(mbo, "plot_var")
            try:
                dim = len(nc.variables[mbo.plot_var].shape)
                if dim == 2:     # Vec3: FIXME check if other possibilities exist
                    box = layout.box()
                    split = box.split(1./3.)
                    column = split.column()
                    column.prop(mbo, "plot_comps", index = 0, text = "x")
                    column = split.column()
                    column.prop(mbo, "plot_comps", index = 1, text = "y")
                    column = split.column()
                    column.prop(mbo, "plot_comps", index = 2, text = "z")
                elif dim == 3:
                    if mbo.plot_var[-1] == 'R':
                        box = layout.box()
                        split = box.split(1./3.)
                        column = split.column()
                        column.row().prop(mbo, "plot_comps", index = 0, text = "(1,1)")
                        column = split.column()
                        column.row().prop(mbo, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(mbo, "plot_comps", index = 3, text = "(2,2)")
                        column = split.column()
                        column.row().prop(mbo, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(mbo, "plot_comps", index = 4, text = "(2,3)")
                        column.row().prop(mbo, "plot_comps", index = 5, text = "(3,3)")
                    else:
                        box = layout.box()
                        split = box.split(1./3.)
                        column = split.column()
                        column.row().prop(mbo, "plot_comps", index = 0, text = "(1,1)")
                        column.row().prop(mbo, "plot_comps", index = 3, text = "(2,1)")
                        column.row().prop(mbo, "plot_comps", index = 6, text = "(3,1)")
                        column = split.column()
                        column.row().prop(mbo, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(mbo, "plot_comps", index = 4, text = "(2,2)")
                        column.row().prop(mbo, "plot_comps", index = 7, text = "(3,2)")
                        column = split.column()
                        column.row().prop(mbo, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(mbo, "plot_comps", index = 5, text = "(2,3)")
                        column.row().prop(mbo, "plot_comps", index = 8, text = "(3,3)")
                row = layout.row()
                col = layout.column()
                col.prop(mbo, "plot_frequency")
                col.operator(Object_OT_MBDyn_plot_freq.bl_idname, text="Use Import freq")
                row = layout.row()
                row.operator(Object_OT_MBDyn_plot_var.bl_idname, text="Plot variable")
            except KeyError:
                pass
        else:
            row = layout.row()
            row.label(text="Plotting from text output")
            row.label(text="is not supported yet.")

## Panel in object properties toolbar
class MBDynPlotPanelScene(bpy.types.Panel):
    """ Plotting of MBDyn entities private data """
    bl_label = "MBDyn data plot"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        mbs = context.scene.mbdyn
        layout = self.layout
        row = layout.row()

        if mbs.use_netcdf:
            ncfile = mbs.file_path + mbs.file_basename + ".nc"
            nc = Dataset(ncfile, 'r', format='NETCDF3')
            # row.prop(mbs, 'plot_var')
            row.template_list("MBDynPlotVar_UL_List", "MBDyn variable to plot", mbs, "plot_vars",
                    mbs, "plot_var_index")
            try:
                dim = len(nc.variables[mbs.plot_vars[mbs.plot_var_index].name].shape)
                if dim == 2:     # Vec3: FIXME check if other possibilities exist
                    box = layout.box()
                    split = box.split(1./3.)
                    column = split.column()
                    column.prop(mbs, "plot_comps", index = 0, text = "x")
                    column = split.column()
                    column.prop(mbs, "plot_comps", index = 1, text = "y")
                    column = split.column()
                    column.prop(mbs, "plot_comps", index = 2, text = "z")
                elif dim == 3:
                    if mbs.plot_var[-1] == 'R':
                        box = layout.box()
                        split = box.split(1./3.)
                        column = split.column()
                        column.row().prop(mbs, "plot_comps", index = 0, text = "(1,1)")
                        column = split.column()
                        column.row().prop(mbs, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(mbs, "plot_comps", index = 3, text = "(2,2)")
                        column = split.column()
                        column.row().prop(mbs, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(mbs, "plot_comps", index = 4, text = "(2,3)")
                        column.row().prop(mbs, "plot_comps", index = 5, text = "(3,3)")
                    else:
                        box = layout.box()
                        split = box.split(1./3.)
                        column = split.column()
                        column.row().prop(mbs, "plot_comps", index = 0, text = "(1,1)")
                        column.row().prop(mbs, "plot_comps", index = 3, text = "(2,1)")
                        column.row().prop(mbs, "plot_comps", index = 6, text = "(3,1)")
                        column = split.column()
                        column.row().prop(mbs, "plot_comps", index = 1, text = "(1,2)")
                        column.row().prop(mbs, "plot_comps", index = 4, text = "(2,2)")
                        column.row().prop(mbs, "plot_comps", index = 7, text = "(3,2)")
                        column = split.column()
                        column.row().prop(mbs, "plot_comps", index = 2, text = "(1,3)")
                        column.row().prop(mbs, "plot_comps", index = 5, text = "(2,3)")
                        column.row().prop(mbs, "plot_comps", index = 8, text = "(3,3)")
                row = layout.row()
                col = layout.column()
                col.prop(mbs, "plot_frequency")
                col.operator(Scene_OT_MBDyn_plot_freq.bl_idname, text="Use Import freq")
                row = layout.row()
                row.operator(Scene_OT_MBDyn_plot_var.bl_idname, text="Plot variable")
                row = layout.row()
            except IndexError:
                pass
        else:
            row = layout.row()
            row.label(text="Plotting from text output")
            row.label(text="is not supported yet.")
