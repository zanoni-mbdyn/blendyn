# --------------------------------------------------------------------------
# Blendyn -- file plotlib.py
# Copyright (C) 2015 -- 2018 Andrea Zanoni -- andrea.zanoni@polimi.it
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

# TODO: check for unnecessary stuff

import bpy

import pygal
import cairosvg
import numpy as np

import logging

from .nodelib import *
from .elementlib import *
from .base import HAVE_PLOT

import os

try: 
    from netCDF4 import Dataset
except ImportError:
    print("Blendyn: could not find netCDF4 module. NetCDF import "\
        + "will be disabled.")

class BLENDYN_OT_plot_var_sxx(bpy.types.Operator):
    """ Plots the selected variable autospectrum (Sxx) in the image editor 
        and optionally save it as .svg in the 'plots' directory.
        The user can choose among all the variables of all the 
        MBDyn entitites found in the output NetCDF file."""
    bl_idname = "ops.mbdyn_plot_var_sxx_scene"
    bl_label = "Plot the selected MBDyn var autospectrum"

    var_index = bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.nc')
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
        if (mbs.plot_xrange_max != 0.0):
            if (mbs.plot_xrange_min >= 0) and (mbs.plot_xrange_max > mbs.plot_xrange_min):
                config.xrange = (mbs.plot_xrange_min, mbs.plot_xrange_max)
            else:
                message = 'Invalid range for abscissa'
                self.report({'ERROR'}, message)
                logging.error(message)
        chart = pygal.XY(config)

        # calculate autospectra and plot them
        if dim == 2:
            n,m = var.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            
            # FIXME: Check if this is still valid for a variable
            #        timestep simulation
            freq = np.arange(nfft)*1./time[-1];
            
            for mdx in range(m):
                if mbs.plot_comps[mdx]:
                    # normalized FFT
                    if mbs.fft_remove_mean:
                        comp_fft = np.fft.fft(var[:, mdx] - np.mean(var[:, mdx]))/nfft
                    else:
                        comp_fft = np.fft.fft(var[:, mdx])/nfft
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(nfft/2) 
                    Gxx[0] = Sxx[0]
                    Gxx[1:(nfft/2 - 1)] = 2*Sxx[1:(nfft/2 - 1)]
                    chart.add(varname + ".Sxx." + str(mdx + 1), \
                            [(freq[idx], Gxx[idx]) for idx in range(0, int(nfft/2), mbs.plot_frequency)])
        elif dim == 3:
            n,m,k = var.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft)*1./time[-1];
            
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
                    if mbs.fft_remove_mean:
                        comp_fft = np.fft.fft(var[:, dims1[mdx], dims2[mdx]] -
                                np.mean(var[:, dims2[mdx], dims2[mdx]]))
                    else:
                        comp_fft = np.fft.fft(var[:, dims1[mdx], dims2[mdx]])
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(nfft/2)
                    Gxx[0] = Sxx[0]
                    Gxx[1:(nfft/2 - 1)] = 2*Sxx[1:(nfft/2 - 1)]
                    chart.add(mbs.plot_var + ".Sxx." + dims_names[mdx], \
                            [(freq[idx], Gxx[idx]) \
                            for idx in range(0, int(nfft/2), mbs.plot_frequency)])
        else:
            if mbs.fft_remove_mean:
                var_fft = np.fft.fft(var - np.mean(var))
            else:
                var_fft = np.fft.fft(var)
                Sxx = np.multiply(np.conj(var_fft), var_fft)
                Gxx = np.zeros(nfft/2)
                Gxx[0] = Sxx[0]
                Gxx[1:(nfft/2 - 1)] = 2*Sxx[1:(nfft/2 - 1)]
                chart.add(varname + ".Sxx", [(freq[idx], Gxx[idx]) \
                        for idx in range(0, int(nfft/2), mbs.plot_frequency)])
        chart.x_title = "Frequency [Hz]"

        if not(bpy.data.is_saved):
            message = "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
 
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
           os.makedirs(plot_dir)

        basename = mbs.file_basename + ".Sxx." + varname
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        cairosvg.svg2png(file_obj = open(outfname + ".svg", "rb"), write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        message = "Variable " + varname + " autospectrum plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
        

class Object_OT_MBDyn_plot_var_sxx(bpy.types.Operator):
    """ Plots the object's selected variable autospectrum in the image editor 
        and optionally save it as .svg in the 'plots' directory """
    bl_idname = "ops.mbdyn_plot_var_sxx_obj"
    bl_label = "Plot the selected MBDyn var"

    def execute(self, context):
        mbo = context.object.mbdyn
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.nc')
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
        if (mbo.plot_xrange_max != 0.0):
            if (mbo.plot_xrange_min >= 0) and (mbo.plot_xrange_max > mbo.plot_xrange_min):
                config.xrange = (mbo.plot_xrange_min, mbo.plot_xrange_max)
            else:
                message = "Invalid range for abscissa"
                self.report({'ERROR'}, message)
                logging.error(message)
        chart = pygal.XY(config)

        # calculate autospectra and plot them
        if dim == 2:
            n,m = var.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            
            # FIXME: Check if this is still valid for a variable
            #        timestep simulation
            freq = np.arange(nfft)*1./time[-1];
            for mdx in range(m):
                if mbo.plot_comps[mdx]:
                    # normalized FFT
                    if mbo.fft_remove_mean:
                        comp_fft = np.fft.fft(var[:, mdx] - np.mean(var[:, mdx]))/nfft
                    else:
                        comp_fft = np.fft.fft(var[:, mdx])/nfft
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(nfft/2) 
                    Gxx[0] = Sxx[0]
                    Gxx[1:(nfft/2 - 1)] = 2*Sxx[1:(nfft/2 - 1)]
                    chart.add(mbo.plot_var + ".Sxx." + str(mdx + 1), \
                            [(freq[idx], Gxx[idx]) for idx in range(0, int(nfft/2), mbs.plot_frequency)])
        elif dim == 3:
            n,m,k = var.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft)*1./time[-1];
            
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
                    if mbs.fft_remove_mean:
                        comp_fft = np.fft.fft(var[:, dims1[mdx], dims2[mdx]] -
                                np.mean(var[:, dims2[mdx], dims2[mdx]]))
                    else:
                        comp_fft = np.fft.fft(var[:, dims1[mdx], dims2[mdx]])
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(nfft/2)
                    Gxx[0] = Sxx[0]
                    Gxx[1:(nfft/2 - 1)] = 2*Sxx[1:(nfft/2 - 1)]
                    chart.add(mbo.plot_var + ".Sxx." + dims_names[mdx], \
                            [(freq[idx], Gxx[idx]) \
                            for idx in range(0, int(nfft/2), mbs.plot_frequency)])
        else:
            if mbo.fft_remove_mean:
                var_fft = np.fft.fft(var - np.mean(var))
            else:
                var_fft = np.fft.fft(var)
                Sxx = np.multiply(np.conj(var_fft), var_fft)
                Gxx = np.zeros(nfft/2)
                Gxx[0] = Sxx[0]
                Gxx[1:(nfft/2 - 1)] = 2*Sxx[1:(nfft/2 - 1)]
                chart.add(varname + ".Sxx", [(freq[idx], Gxx[idx]) \
                        for idx in range(0, int(nfft/2), mbs.plot_frequency)])
            chart.add(mbo.plot_var, [(time[idx], var[idx]) \
                    for idx in range(0, len(time), mbs.plot_frequency)]) 
        chart.x_title = "time [s]"

        if not(bpy.data.is_saved):
            message = "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
           os.makedirs(plot_dir)

        basename = mbs.file_basename + ".Sxx." + mbo.plot_var
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        cairosvg.svg2png(file_obj = open(outfname + ".svg", "rb"), write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        message = "Variable " + mbo.plot_var + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}

class BLENDYN_OT_plot_variables_list(bpy.types.Operator):
    """Plot all the variables in the Variables List"""
    bl_idname = "ops.mbdyn_plot_var_variables"
    bl_label = "Plot all the variables in Variables List"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if not(bpy.data.is_saved):
            message = "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        # set up pygal
        config = pygal.Config()
        config.show_dots = False
        config.legend_at_bottom = True
        config.truncate_legend = -1

        if mbs.plot_group:
            config.title = mbs.display_enum_group

        chart = pygal.XY(config)


        for variable in mbs.render_vars:

            # get requested netCDF variable
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, 'r', format='NETCDF3')

            # get its dimensions
            varname = variable.value
            var = nc.variables[varname]
            dim = len(var.shape)

            # get time vector
            time = nc.variables["time"]

            units = '[{}]'.format(var.units) if 'units' in dir(var) else ''

            # create plot
            if dim == 2:
                n,m = var.shape
                for mdx in range(m):
                    if variable.components[mdx]:
                        chart.add('{0}.{1}  {2}'.format(varname, mdx+1, units), \
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
                    if variable.components[mdx]:
                        chart.add('{0}.{1}  {2}'.format(varname, dims_names[mdx], units), \
                                [(time[idx], var[idx, dims1[mdx], dims2[mdx]]) \
                                for idx in range(0, n, mbs.plot_frequency)])
            else:
                chart.add('{0}  {1}'.format(varname, units), [(time[idx], var[idx]) \
                        for idx in range(0, len(time), mbs.plot_frequency)])

        chart.x_title = "time [s]"
 
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
           os.makedirs(plot_dir)

        basename = mbs.file_basename

        if mbs.plot_group:
            basename += '..' + mbs.display_enum_group

        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        cairosvg.svg2png(file_obj = open(outfname + ".svg", "rb"), write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        message = "Variable " + varname + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}


class BLENDYN_OT_plot_var(bpy.types.Operator):
    """ Plots the selected variable in the image editor
        and optionally save it as .svg in the 'plots' directory.
        The user can choose among all the variables of all the
        MBDyn entitites found in the output NetCDF fila."""
    bl_idname = "ops.mbdyn_plot_var_scene"
    bl_label = "Plot the selected MBDyn var"

    var_index = bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn

        if not(bpy.data.is_saved):
            message = "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        # get requested netCDF variable
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r', format='NETCDF3')

        # get its dimensions
        varname = mbs.plot_vars[mbs.plot_var_index].name
        var = nc.variables[varname]
        dim = len(var.shape)
        units = '[{}]'.format(var.units) if 'units' in dir(var) else ''


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
                    chart.add('{0}.{1}  {2}'.format(varname, mdx+1, units), \
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
                    chart.add('{0}.{1}  {2}'.format(varname, dims_names[mdx], units), \
                            [(time[idx], var[idx, dims1[mdx], dims2[mdx]]) \
                            for idx in range(0, n, mbs.plot_frequency)])
        else:
            chart.add('{0}  {1}'.format(varname, units), [(time[idx], var[idx]) \
                    for idx in range(0, len(time), mbs.plot_frequency)])

        chart.x_title = "time [s]"

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
        cairosvg.svg2png(file_obj = open(outfname + ".svg", "rb"), write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        message = "Variable " + varname + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
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
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.nc')
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
                            [(time[idx], var[idx,mdx]) for idx in range(0, n, mbs.plot_frequency)])
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
                            for idx in range(0, n, mbs.plot_frequency)])
        else:
            chart.add(mbo.plot_var, [(time[idx], var[idx]) \
                    for idx in range(0, len(time), mbs.plot_frequency)])
        
        chart.x_title = "time [s]"

        if not(bpy.data.is_saved):
            message = "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
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
        cairosvg.svg2png(file_obj = open(outfname + ".svg", "rb"), write_to = outfname + ".png")
        bpy.ops.image.open(filepath = outfname + ".png")


        message = "Variable " + mbo.plot_var + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}

## Simple operator to set plot frequency for
class BLENDYN_OT_set_plot_freq(bpy.types.Operator):
    """ Sets the plot frequency for the current object plot variable equal
        to the import frequency of the MBDyn results """
    bl_idname = "ops.mbdyn_set_plot_freq_scene"
    bl_label = "Sets the plot frequency for the scene equal to the load frequency"
    is_object = bpy.props.BoolProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn
        if is_object:
            pvar = mbs.plot_vars[context.object.mbdyn.plot_var_index]
        else:
            pvar = mbs.plot_vars[mbs.plot_var_index]
        pvar.frequency = context.scene.mbdyn.load_frequency
        return {'FINISHED'}

class BLENDYN_OT_set_render_variable(bpy.types.Operator):
    """ Sets the NetCDF variables to be\
        displayed in the rendered frame """

    bl_idname = "sel.set_render_variable"
    bl_label = "Set Render Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        idx = [mbs.render_vars[key].idx for key in range(len(mbs.render_vars))]

        try:
            mbs.render_vars[idx].varname = mbs.render_var_name
        except ValueError:
            rend = mbs.render_vars.add()
            rend.varname = mbs.render_var_name
            rend.variable = mbs.plot_vars[mbs.plot_var_index].name
            rend.components = mbs.plot_vars[mbs.plot_var_index].components

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_render_variable class
bpy.utils.register_class(BLENDYN_OT_set_render_variable)

class BLENDYN_OT_delete_render_variable(bpy.types.Operator):
    """Delete Render variables"""
    bl_idname = "sel.delete_render_variable"
    bl_label = "Delete Render Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.render_vars.remove(mbs.render_index)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_delete_render_variable class
bpy.utils.register_class(BLENDYN_OT_delete_render_variable)

class BLENDYN_OT_delete_all_render_variables(bpy.types.Operator):
    bl_idname = "sel.delete_all_render_variables"
    bl_label = "Delete all Render variables"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.render_vars.clear()

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_delete_all_render_variables class
bpy.utils.register_class(BLENDYN_OT_delete_all_render_variables)

class MBDynShowDisplayGroup(bpy.types.Operator):
    bl_idname = "ops.show_plot_group"
    bl_label = "show display group"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if mbs.display_enum_group is '':
            message = 'No Groups set'
            self.report({'ERROR'}, message)
            logging.error(message)

        mbs.render_vars.clear()

        for var in mbs.display_vars_group[mbs.display_enum_group].group:
            rend = mbs.render_vars.add()
            rend.variable = var.variable
            rend.value = var.value
            rend.components = var.components

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of MBDynShowDisplayGroup class
bpy.utils.register_class(MBDynShowDisplayGroup)

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
bpy.utils.register_class(BLENDYN_OT_set_display_group)


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
        pvar = mbs.plot_vars[mbo.plot_var_index]

        if mbs.use_netcdf:
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, 'r', format='NETCDF3')
            row.template_list("MBDynPlotVar_Object_UL_List", \
                    "MBDyn variable to plot", mbs, "plot_vars", \
                    mbo, "plot_var_index")
            row = layout.row()
            row.prop(pvar, "as_driver")
            try:
                dim = len(nc.variables[pvar.name].shape)
                if dim == 2:     # vec3
                    box = layout.box()
                    split = box.split(1./3.)
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 0, text = "x")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 1, text = "y")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 2, text = "z")
                elif dim == 3:
                    if pvar.name[-1] == 'R':
                        box = layout.box()
                        split = box.split(1./3.)
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
                        split = box.split(1./3.)
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
                col.operator(BLENDYN_OT_set_plot_freq.bl_idname, text = "Use Import frequency")
                row = layout.row()
                row.prop(pvar, "plot_type", text="Plot type:")
                row = layout.row()
                row.prop(pvar, "plot_xrange_min")
                row = layout.row()
                row.prop(pvar, "plot_xrange_max")
                row = layout.row()
                if pvar.plot_type == "TIME HISTORY":
                    row.operator(Object_OT_MBDyn_plot_var.bl_idname, text = "Plot variable")
                elif pvar.plot_type == "AUTOSPECTRUM":
                    row = layout.row()
                    row.prop(pvar, "fft_remove_mean")
                    row = layout.row()
                    row.operator(Object_OT_MBDyn_plot_var_sxx.bl_idname,
                        text="Plot variable Autospectrum")
            except KeyError:
                pass
        else:
            row = layout.row()
            row.label(text = "Plotting from text output")
            row.label(text = "is not supported yet.")

## Panel in Scene toolbar
class MBDYN_PT_plot_scene(bpy.types.Panel):
    """ Plotting of MBDyn entities private data """
    bl_label = "MBDyn Data Plot"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    
    def draw(self, context):
        mbs = context.scene.mbdyn
        pvar = mbs.plot_vars[mbs.plot_var_index]
        layout = self.layout
        row = layout.row()

        if mbs.use_netcdf:
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, 'r', format='NETCDF3')
            row.template_list("MBDynPlotVar_UL_List", "MBDyn variable to plot", mbs, "plot_vars",
                    mbs, "plot_var_index")
            try:
                dim = len(nc.variables[pvar.name].shape)
                if dim == 2:     # Vec3
                    box = layout.box()
                    split = box.split(1./3.)
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 0, text = "x")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 1, text = "y")
                    column = split.column()
                    column.prop(pvar, "plot_comps", index = 2, text = "z")
                elif dim == 3:  # Mat3x3
                    if pvar.name[-1] == 'R':
                        box = layout.box()
                        split = box.split(1./3.)
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
                        split = box.split(1./3.)
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
                if HAVE_PLOT:
                    row = layout.row()
                    col = layout.column()
                    col.prop(pvar, "plot_frequency")
                    col.operator(BLENDYN_OT_set_plot_freq.bl_idname, text = "Use Import freq")
                    row = layout.row()
                    row.prop(pvar, "plot_type")
                    row = layout.row()
                    row.prop(pvar, "plot_xrange_min")
                    row = layout.row()
                    row.prop(pvar, "plot_xrange_max")
                    row = layout.row()
                    if pvar.plot_type == "TIME HISTORY":
                        row.operator(BLENDYN_OT_plot_var.bl_idname, 
                                text="Plot variable")
                    elif mbs.plot_type == "AUTOSPECTRUM":
                        row = layout.row()
                        row.prop(mbs, "fft_remove_mean")
                        row = layout.row()
                        row.operator(BLENDYN_OT_plot_var_sxx.bl_idname,
                                text="Plot variable Autospectrum")
            except IndexError:
                pass

            layout.separator()
            layout.separator()

            row = layout.row()
            row.template_list('BLENDYN_UL_render_vars_list', \
                    "MBDyn Variables to Render", mbs, "render_vars",\
                    mbs, "render_index")
            row = layout.row()
            row.prop(mbs, "render_var_name")

            row = layout.row()
            row.operator(BLENDYN_OT_set_render_variable.bl_idname, text = 'Set Display Variable')

            row = layout.row()
            row.operator(BLENDYN_OT_delete_render_variable.bl_idname, \
                    text = 'Delete Display Variable')
            row.operator(BLENDYN_OT_delete_all_render_variables.bl_idname, text = 'Clear')

            if HAVE_PLOT:
                row = layout.row()
                row.operator(BLENDYN_OT_plot_variables_list.bl_idname, \
                        text="Plot variables in List")

                row.prop(mbs, "plot_group", text = "Plot Group")
                layout.separator()
                layout.separator()

                row = layout.row()
                row.prop(mbs, "group_name")
                row.operator(BLENDYN_OT_set_display_group.bl_idname, text="Set Display Group")

                row = layout.row()
                row.prop(mbs, "display_enum_group")
                row.operator(MBDynShowDisplayGroup.bl_idname, text = "Show Display Group")

        else:
            row = layout.row()
            row.label(text="Plotting from text output")
            row.label(text="is not supported yet.")
# -----------------------------------------------------------
# end of MBDYN_PT_plot_scene class
bpy.utils.register_class(MBDYN_PT_plot_scene)
