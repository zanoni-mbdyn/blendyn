# --------------------------------------------------------------------------
# Blendyn -- file bokehplotlib.py
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

try:
    from html2image import Html2Image
    import bokeh
    from bokeh.plotting import figure, save, show
    from bokeh.io import output_file
    from bokeh.models import Range1d
    from bokeh.layouts import row
    from netCDF4 import Dataset
except ModuleNotFoundError as ierr:
    print("BLENDYN::bokehplotlib.py: could not import dependencies. Plotting using Bokeh " \
          + "will be disabled. The reported error was:")
    print("{0}".format(ierr))

import numpy as np
import logging
from .nodelib import *
from .elementlib import *
import os
from pathlib import Path
colors = ["blue", "red", "gray", "yellow", "purple", "black", "orange", "green", "pink"]

class BLENDYN_OT_bplot_var_scene(bpy.types.Operator):
    """ Plots the selected variable in the image editor
        and optionally save it as .html in the 'plots' directory.
        The user can choose among all the variables of all the
        MBDyn entitites found in the output NetCDF file."""
    bl_idname = "blendyn.bplot_var_scene"
    bl_label = "Plot the selected MBDyn var with bokeh"

    var_index: bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')

        # get its dimensions
        pvar = mbs.plot_vars[mbs.plot_var_index]
        ncvar = nc.variables[pvar.name]
        dim = len(ncvar.shape)
        units = '[{}]'.format(ncvar.units) if 'units' in dir(ncvar) else ''

        # get time vector
        time = nc.variables["time"]

        # set up bokeh
        p = figure(plot_width = 800, plot_height = 800, title = "TIME HISTORY", background_fill_color="#fafafa")
        p.x_range = Range1d(float(min([time[i] for i in range(len(time))])),
                            float(max([time[i] for i in range(len(time))])))

        # create plot
        if dim == 2:
            n, m = ncvar.shape
            p.y_range = Range1d(float(min([ncvar[i, mdx] for i in range(n)
                                           for mdx in range(m) if pvar.plot_comps[mdx]])),
                                float(max([ncvar[i, mdx] for i in range(n)
                                           for mdx in range(m) if pvar.plot_comps[mdx]])))
            for mdx in range(m):
                if pvar.plot_comps[mdx]:
                    ptime_data = [time[idx] for idx in range(0, n, pvar.plot_frequency)]
                    pvar_data = [ncvar[idx, mdx] for idx in range(0, n, pvar.plot_frequency)]
                    p.line(ptime_data, pvar_data, legend_label='{0}.{1}'.format(pvar.name, mdx + 1), line_width = 2,
                           color = colors[mdx])

        elif dim == 3:
            n, m, k = ncvar.shape

            if pvar.name[-1] == 'R':
                dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 2]
                dims2 = [0, 1, 2, 1, 2, 2]
            else:
                dims_names = ["(1,1)", "(1,2)", "(1,3)", \
                              "(2,1)", "(2,2)", "(2,3)", \
                              "(3,1)", "(3,2)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                dims2 = [0, 1, 2, 0, 1, 2, 0, 1, 2]

            p.y_range = Range1d(float(min([ncvar[i, dims1[mdx], dims2[mdx]] for i in range(n)
                                    for mdx in range(len(dims_names)) if pvar.plot_comps[mdx]])),
                                float(max([ncvar[i, dims1[mdx], dims2[mdx]] for i in range(n)
                                    for mdx in range(len(dims_names)) if pvar.plot_comps[mdx]])))
            for mdx in range(len(dims_names)):
                if pvar.plot_comps[mdx]:
                    ptime_data = [time[idx] for idx in range(0, n, pvar.plot_frequency)]
                    pvar_data = [ncvar[idx, dims1[mdx], dims2[mdx]] for idx in range(0, n, pvar.plot_frequency)]
                    p.line(ptime_data, pvar_data, legend_label='{0}.{1}'.format(pvar.name, dims_names[mdx]), line_width=2,
                           color=colors[mdx])

        else:
            p.y_range = Range1d(float(min([ncvar[i] for i in range(len(ncvar))])),
                                float(max([ncvar[i] for i in range(len(ncvar))])))
            ptime_data = [time[idx] for idx in range(0, len(time), pvar.plot_frequency)]
            pvar_data = [ncvar[idx] for idx in range(0, len(time), pvar.plot_frequency)]
            p.line(ptime_data, pvar_data, legend_label='{0}'.format(pvar.name), line_width=2,
                   color=colors[0])

        p.xaxis.axis_label = "time [s]"
        p.yaxis.axis_label = "{0}".format(units)

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_var_scene::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        ## Create directory for saving file
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        basename = mbs.file_basename + "." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)

        ## Save image in .html format and .png format
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        print(rel_path)
        output_file(filename = rel_path+".html")
        save(p)
        if mbs.show_in_localhost:
            show(p)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (820,820))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_var_scene::execute() " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_bplot_var_scene class



class BLENDYN_OT_bplot_var_sxx_scene(bpy.types.Operator):
    """ Plots the selected variable autospectrum (Sxx) in the image editor
        and optionally save it as .png in the 'plots' directory.
        The user can choose among all the variables of all the
        MBDyn entitites found in the output NetCDF file."""
    bl_idname = "blendyn.bplot_var_sxx_scene"
    bl_label = "Plot the selected MBDyn var autospectrum with bokeh"

    var_index: bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')

        # get its dimensions
        pvar = mbs.plot_vars[mbs.plot_var_index]
        ncvar = nc.variables[pvar.name]
        dim = len(ncvar.shape)

        # get time vector
        time = nc.variables["time"]

        # set up bokeh
        p = figure(plot_width = 800, plot_height = 800, title = "AUTOSPECTRUM", background_fill_color="#fafafa")

        if (pvar.plot_xrange_max != 0.0):
            if (pvar.plot_xrange_min >= 0) and (pvar.plot_xrange_max > pvar.plot_xrange_min):
                p.x_range = Range1d(pvar.plot_xrange_min, pvar.plot_xrange_max)
            else:
                message = 'Invalid range for abscissa'
                self.report({'ERROR'}, message)
                logging.error("BLENDYN_OT_bplot_var_sxx_scene::execute(): " + message)

        # calculate autospectra and plot them
        if dim == 2:
            n, m = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            # FIXME: Check if this is still valid for a variable
            #        timestep simulation
            # ANSWER: No, it is not, but so are a lot of other
            #         assumptions we make inside of Blendyn.
            #         Fixed timestep output is needed everywhere.
            freq = np.arange(nfft) * 1. / time[-1]

            for mdx in range(m):
                if pvar.plot_comps[mdx]:
                    # normalized FFT
                    if pvar.fft_remove_mean:
                        comp_fft = np.fft.fft(ncvar[:, mdx] - np.mean(ncvar[:, mdx])) / nfft
                    else:
                        comp_fft = np.fft.fft(ncvar[:, mdx]) / nfft
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(int(nfft / 2))
                    Gxx[0] = Sxx[0]
                    Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                    fvar_plot = [freq[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    Gxx_plot = [Gxx[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    p.line(fvar_plot, Gxx_plot, legend_label=pvar.name + str(mdx + 1), line_width=2,
                           color=colors[mdx])

        elif dim == 3:
            n, m, k = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft) * 1. / time[-1]

            if mbs.plot_var[-1] == 'R':
                dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 2]
                dims2 = [0, 1, 2, 1, 2, 2]
            else:
                dims_names = ["(1,1)", "(1,2)", "(1,3)", \
                              "(2,1)", "(2,2)", "(2,3)", \
                              "(3,1)", "(3,2)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                dims2 = [0, 1, 2, 0, 1, 2, 0, 1, 2]
            for mdx in range(len(dims_names)):
                if pvar.plot_comps[mdx]:
                    if pvar.fft_remove_mean:
                        comp_fft = np.fft.fft(ncvar[:, dims1[mdx], dims2[mdx]] -
                                              np.mean(ncvar[:, dims2[mdx], dims2[mdx]]))
                    else:
                        comp_fft = np.fft.fft(ncvar[:, dims1[mdx], dims2[mdx]])
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(int(nfft / 2))
                    Gxx[0] = Sxx[0]
                    Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                    fvar_plot = [freq[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    Gxx_plot = [Gxx[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    p.line(fvar_plot, Gxx_plot, legend_label=pvar.name + dims_names[mdx], line_width=2,
                           color=colors[mdx])
        else:
            nfft = int(np.power(2, np.round(np.log2(len(time)) + .5)))
            freq = np.arange(nfft) * 1. / time[-1]
            if pvar.fft_remove_mean:
                ncvar_fft = np.fft.fft(ncvar - np.mean(ncvar))
            else:
                ncvar_fft = np.fft.fft(ncvar)
            Sxx = np.multiply(np.conj(ncvar_fft), ncvar_fft)
            Gxx = np.zeros(int(nfft / 2))
            Gxx[0] = Sxx[0]
            Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
            fvar_plot = [freq[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
            Gxx_plot = [Gxx[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
            p.line(fvar_plot, Gxx_plot, legend_label=pvar.name, line_width=2,
                   color=colors[0])

        p.xaxis.axis_label = "Frequency [Hz]"
        p.yaxis.axis_label = "Intensity"


        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_var_sxx_scene::execute() : " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        basename = mbs.file_basename + ".Sxx." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)

        ## Save plot as .html and .png file
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        output_file(filename = rel_path+".html")
        save(p)
        if mbs.show_in_localhost:
            show(p)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (820,820))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_var_sxx_scene::execute(): " \
                  + "Variable " + pvar.name + " autospectrum plotted"
        self.report({'INFO'}, message)
        baseLogger.info(message)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_bplot_var_sxx_scene class


class BLENDYN_OT_bplot_var_sxx_object(bpy.types.Operator):
    """ Plots the object's selected variable autospectrum in the image editor
        and optionally save it as .png in the 'plots' directory """
    bl_idname = "blendyn.bplot_var_sxx_object"
    bl_label = "Plot the selected MBDyn var object autospectrum with bokeh "

    def execute(self, context):
        mbo = context.object.mbdyn
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')

        # get its dimensions
        pvar = mbs.plot_vars[mbo.plot_var_index]
        ncvar = nc.variables[pvar.name]
        dim = len(ncvar.shape)

        # get time vector
        time = nc.variables["time"]

        # set up bokeh
        p = figure(plot_width = 800, plot_height = 800, title = "AUTOSPECTRUM", background_fill_color="#fafafa")

        if (pvar.plot_xrange_max != 0.0):
            if (pvar.plot_xrange_min >= 0) and (pvar.plot_xrange_max > pvar.plot_xrange_min):
                p.x_range = bokeh.models.Range1d(pvar.plot_xrange_min, pvar.plot_xrange_max)
            else:
                message = 'Invalid range for abscissa'
                self.report({'ERROR'}, message)
                logging.error("BLENDYN_OT_bplot_var_sxx_object::execute(): " + message)

        # calculate autospectra and plot them
        if dim == 2:
            n, m = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            # FIXME: Check if this is still valid for a variable
            #        timestep simulation
            # ANSWER: No, it is not, but so are a lot of other
            #         assumptions we make inside of Blendyn.
            #         Fixed timestep output is needed everywhere.
            freq = np.arange(nfft) * 1. / time[-1]

            for mdx in range(m):
                if pvar.plot_comps[mdx]:
                    # normalized FFT
                    if pvar.fft_remove_mean:
                        comp_fft = np.fft.fft(ncvar[:, mdx] - np.mean(ncvar[:, mdx])) / nfft
                    else:
                        comp_fft = np.fft.fft(ncvar[:, mdx]) / nfft
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(int(nfft / 2))
                    Gxx[0] = Sxx[0]
                    Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                    fvar_plot = [freq[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    Gxx_plot = [Gxx[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    p.line(fvar_plot, Gxx_plot, legend_label = pvar.name + str(mdx + 1), line_width = 2,
                           color = colors[mdx])

        elif dim == 3:
            n, m, k = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft) * 1. / time[-1]

            if mbs.plot_var[-1] == 'R':
                dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 2]
                dims2 = [0, 1, 2, 1, 2, 2]
            else:
                dims_names = ["(1,1)", "(1,2)", "(1,3)", \
                              "(2,1)", "(2,2)", "(2,3)", \
                              "(3,1)", "(3,2)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                dims2 = [0, 1, 2, 0, 1, 2, 0, 1, 2]
            for mdx in range(len(dims_names)):
                if pvar.plot_comps[mdx]:
                    if pvar.fft_remove_mean:
                        comp_fft = np.fft.fft(ncvar[:, dims1[mdx], dims2[mdx]] -
                                              np.mean(ncvar[:, dims2[mdx], dims2[mdx]]))
                    else:
                        comp_fft = np.fft.fft(ncvar[:, dims1[mdx], dims2[mdx]])
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(int(nfft / 2))
                    Gxx[0] = Sxx[0]
                    Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                    fvar_plot = [freq[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    Gxx_plot = [Gxx[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
                    p.line(fvar_plot, Gxx_plot, legend_label = pvar.name + dims_names[mdx], line_width = 2,
                           color = colors[mdx])
        else:
            nfft = int(np.power(2, np.round(np.log2(len(time)) + .5)))
            freq = np.arange(nfft) * 1. / time[-1]
            if pvar.fft_remove_mean:
                ncvar_fft = np.fft.fft(ncvar - np.mean(ncvar))
            else:
                ncvar_fft = np.fft.fft(ncvar)
            Sxx = np.multiply(np.conj(ncvar_fft), ncvar_fft)
            Gxx = np.zeros(int(nfft / 2))
            Gxx[0] = Sxx[0]
            Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
            fvar_plot = [freq[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
            Gxx_plot = [Gxx[idx] for idx in range(0, int(nfft / 2), pvar.plot_frequency)]
            p.line(fvar_plot, Gxx_plot, legend_label=pvar.name, line_width=2,
                   color=colors[0])

        p.xaxis.axis_label = "Frequency [Hz]"
        p.yaxis.axis_label = "Intensity"

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_var_sxx_scene::execute() : " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        basename = mbs.file_basename + ".Sxx." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)
        # Save graph as .html and .png file
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        print(rel_path)
        output_file(filename = rel_path+".html")
        save(p)
        if mbs.show_in_localhost:
            show(p)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (820,820))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_var_sxx_object::execute(): " \
                  + "Variable " + pvar.name + " autospectrum plotted"
        self.report({'INFO'}, message)
        baseLogger.info(message)
        return {'FINISHED'}
# ---------------------------------------------------------------------
# End of BLENDYN_OT_bplot_var_sxx_object


class BLENDYN_OT_bplot_var_object(bpy.types.Operator):
    """ Plots the object's selected variable in the image editor
        and optionally save it as .png in the 'plots' directory """
    bl_idname = "blendyn.bplot_var_object"
    bl_label = "Plot the selected MBDyn var object with bokeh"

    def execute(self, context):
        mbo = context.object.mbdyn
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        pvar = mbs.plot_vars[mbo.plot_var_index]
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')
        ncvar = nc.variables[pvar.name]
        dim = len(ncvar.shape)
        units = '[{}]'.format(ncvar.units) if 'units' in dir(ncvar) else ''

        # get time vector
        time = nc.variables["time"]

        # set up bokeh
        p = figure(plot_width = 800, plot_height = 800, title = "TIME HISTORY", background_fill_color="#fafafa")
        p.x_range = Range1d(float(min([time[i] for i in range(len(time))])),
                            float(max([time[i] for i in range(len(time))])))

        # create plot
        if dim == 2:
            n, m = ncvar.shape
            p.y_range = Range1d(float(min([ncvar[i, mdx] for i in range(n)
                                           for mdx in range(m) if pvar.plot_comps[mdx]])),
                                float(max([ncvar[i, mdx] for i in range(n)
                                           for mdx in range(m) if pvar.plot_comps[mdx]])))
            for mdx in range(m):
                if pvar.plot_comps[mdx]:
                    ptime_data = [time[idx] for idx in range(0, n, pvar.plot_frequency)]
                    pvar_data = [ncvar[idx, mdx] for idx in range(0, n, pvar.plot_frequency)]
                    p.line(ptime_data, pvar_data, legend_label = '{0}.{1}'.format(pvar.name, mdx + 1), line_width = 2,
                           color = colors[mdx])

        elif dim == 3:
            n, m, k = ncvar.shape

            if pvar.name[-1] == 'R':
                dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 2]
                dims2 = [0, 1, 2, 1, 2, 2]
            else:
                dims_names = ["(1,1)", "(1,2)", "(1,3)", \
                              "(2,1)", "(2,2)", "(2,3)", \
                              "(3,1)", "(3,2)", "(3,3)"]
                dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                dims2 = [0, 1, 2, 0, 1, 2, 0, 1, 2]

            p.y_range = Range1d(float(min([ncvar[i, dims1[mdx], dims2[mdx]] for i in range(n)
                                           for mdx in range(len(dims_names)) if pvar.plot_comps[mdx]])),
                                float(max([ncvar[i, dims1[mdx], dims2[mdx]] for i in range(n)
                                           for mdx in range(len(dims_names)) if pvar.plot_comps[mdx]])))

            for mdx in range(len(dims_names)):
                if pvar.plot_comps[mdx]:
                    ptime_data = [time[idx] for idx in range(0, n, pvar.plot_frequency)]
                    pvar_data = [ncvar[idx, dims1[mdx], dims2[mdx]] for idx in range(0, n, pvar.plot_frequency)]
                    p.line(ptime_data, pvar_data, legend_label = '{0}.{1}'.format(pvar.name, dims_names[mdx]), line_width = 2,
                           color = colors[mdx])

        else:
            p.y_range = Range1d(float(min([ncvar[i] for i in range(len(ncvar))])),
                                float(max([ncvar[i] for i in range(len(ncvar))])))
            ptime_data = [time[idx] for idx in range(0, len(time), pvar.plot_frequency)]
            pvar_data = [ncvar[idx] for idx in range(0, len(time), pvar.plot_frequency)]
            p.line(ptime_data, pvar_data, legend_label = '{0}'.format(pvar.name), line_width = 2,
                   color = colors[0])

        p.xaxis.axis_label = "time [s]"
        p.yaxis.axis_label = "{0}".format(units)


        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_var_object::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        ## Create directory for saving file
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        basename = mbs.file_basename + "." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)

        ## Save image in .html and .png format
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        output_file(filename = rel_path+".html")
        save(p)
        if mbs.show_in_localhost:
            show(p)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (820,820))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_var_object::execute() " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_bplot_var_object class


class BLENDYN_OT_bplot_variables_list(bpy.types.Operator):
    """ Plot all the variables in the Variables List with bokeh"""
    bl_idname = "blendyn.bplot_variables_list"
    bl_label = "Plot all the variables in Variables List with bokeh"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_variables_list::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        # set up bokeh
        if mbs.plot_group:
            p = figure(plot_width=800, plot_height=800, title=mbs.display_enum_group, background_fill_color="#fafafa")
        else:
            p = figure(plot_width=800, plot_height=800, title="TIME HISTORY", background_fill_color="#fafafa")

        for rvar in mbs.render_vars:
            # get the corresponding plot_var
            pvar = mbs.plot_vars[rvar.idx]

            # get requested netCDF variable
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                                  mbs.file_basename + '.nc')
            nc = Dataset(ncfile, 'r')
            ncvar = nc.variables[pvar.name]

            # get its dimensions
            dim = len(ncvar.shape)

            # get time vector
            time = nc.variables["time"]

            units = '[{}]'.format(ncvar.units) if 'units' in dir(ncvar) else ''

            # create plot
            if dim == 2:
                n, m = ncvar.shape
                for mdx in range(m):
                    if pvar.plot_comps[mdx]:
                        ptime_data = [time[idx] for idx in range(0, n, pvar.plot_frequency)]
                        pvar_data = [ncvar[idx, mdx] for idx in range(0, n, pvar.plot_frequency)]
                        p.line(ptime_data, pvar_data, legend_label = '{0}.{1} {2}'.format(pvar.name, mdx + 1, units),
                               line_width = 2, color = colors[mdx])

            elif dim == 3:
                n, m, k = ncvar.shape
                if pvar.name[-1] == 'R':
                    dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]
                    dims1 = [0, 0, 0, 1, 1, 2]
                    dims2 = [0, 1, 2, 1, 2, 2]
                else:
                    dims_names = ["(1,1)", "(1,2)", "(1,3)", \
                                  "(2,1)", "(2,2)", "(2,3)", \
                                  "(3,1)", "(3,2)", "(3,3)"]
                    dims1 = [0, 0, 0, 1, 1, 1, 2, 2, 2]
                    dims2 = [0, 1, 2, 0, 1, 2, 0, 1, 2]
                for mdx in range(len(dims_names)):
                    if pvar.plot_comps[mdx]:
                        ptime_data = [time[idx] for idx in range(0, n, pvar.plot_frequency)]
                        pvar_data = [ncvar[idx, dims1[mdx], dims2[mdx]] for idx in range(0, n, pvar.plot_frequency)]
                        p.line(ptime_data, pvar_data, legend_label='{0}.{1} {2}'.format(pvar.name, dims_names[mdx], units),
                               line_width=2, color=colors[mdx])
            else:
                ptime_data = [time[idx] for idx in range(0, len(time), pvar.plot_frequency)]
                pvar_data = [ncvar[idx] for idx in range(0, len(time), pvar.plot_frequency)]
                p.line(ptime_data, pvar_data, legend_label='{0} {1}'.format(pvar.name, units),
                       line_width=2, color=colors[0])

        p.xaxis.axis_label = "time [s]"

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_variables_list::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        basename = mbs.file_basename

        if mbs.plot_group:
            basename += '..' + mbs.display_enum_group

        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)

        #Save graph as .html and .png file
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        output_file(filename = rel_path+".html")
        save(p)
        if mbs.show_in_localhost:
            show(p)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (820,820))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_variables_list::execute() " \
                  + "Variable " + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_bplot_variables_list class


class BLENDYN_OT_bplot_trajectory_object(bpy.types.Operator):
    """Plot trajectory graph of (Vec3) matrix variable using bokeh"""
    bl_idname = "blendyn.bplot_traj_object"
    bl_label = "Plot trajectory of the selected MBDyn var with bokeh"

    def execute(self, context):
        mbs = context.scene.mbdyn
        mbo = context.object.mbdyn

        # get requested netCDF variable
        pvar = mbs.plot_vars[mbo.plot_var_index]
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')
        ncvar = nc.variables[pvar.name]
        dim = len(ncvar.shape)
        units = '[{}]'.format(ncvar.units) if 'units' in dir(ncvar) else ''

        # set up bokeh
        p1 = figure(plot_width=400, plot_height=400, background_fill_color="#fafafa",
                    title = "TRAJECTORY OF " + pvar.name.upper())
        p1.xaxis.axis_label = "X {0}".format(units)
        p1.yaxis.axis_label = "Y {0}".format(units)
        p2 = figure(plot_width=400, plot_height=400, background_fill_color="#fafafa")
        p2.xaxis.axis_label = "Y {0}".format(units)
        p2.yaxis.axis_label = "Z {0}".format(units)
        p3 = figure(plot_width=400, plot_height=400, background_fill_color="#fafafa")
        p3.xaxis.axis_label = "Z {0}".format(units)
        p3.yaxis.axis_label = "X {0}".format(units)


        # create plot
        if dim == 2:
            n, m = ncvar.shape
            pvar_data_1 = [ncvar[idx, 0] for idx in range(0, n, pvar.plot_frequency)]
            pvar_data_2 = [ncvar[idx, 1] for idx in range(0, n, pvar.plot_frequency)]
            pvar_data_3 = [ncvar[idx, 2] for idx in range(0, n, pvar.plot_frequency)]
            p1.line(pvar_data_1, pvar_data_2, line_width=2, color=colors[0])
            p2.line(pvar_data_2, pvar_data_3, line_width=2, color=colors[1])
            p3.line(pvar_data_3, pvar_data_1, line_width=2, color=colors[2])
            fig = row(p1, p2, p3)
        else:
            message = "BLENDYN_OT_bplot_bplot_trajectory_object::execute() " \
                      + "Plotting variable should be (Vec3) matrix"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_trajectory_object::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        ## Create directory for saving file
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        basename = mbs.file_basename + ".Traj." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)

        ## Save image in .html and .png format
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        output_file(filename = rel_path+".html")
        save(fig)
        if mbs.show_in_localhost:
            show(fig)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (1220,430))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_trajectory_object::execute() " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
#--------------------------------------------------------------------------
# end of BLENDYN_OT_bplot_trajectory_object class


class BLENDYN_OT_bplot_trajectory_scene(bpy.types.Operator):
    """Plot trajectory graph of (Vec3) matrix variable using matplotlib"""
    bl_idname = "blendyn.bplot_traj_scene"
    bl_label = "Plot trajectory of the selected MBDyn var scene with bokeh"

    def execute(self, context):
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        pvar = mbs.plot_vars[mbs.plot_var_index]
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')
        ncvar = nc.variables[pvar.name]
        dim = len(ncvar.shape)
        units = '[{}]'.format(ncvar.units) if 'units' in dir(ncvar) else ''


        # set up bokeh
        p1 = figure(plot_width = 400, plot_height = 400, background_fill_color="#fafafa",
                    title = "TRAJECTORY OF " + pvar.name.upper())
        p1.xaxis.axis_label = "X {0}".format(units)
        p1.yaxis.axis_label = "Y {0}".format(units)
        p2 = figure(plot_width = 400, plot_height = 400, background_fill_color="#fafafa")
        p2.xaxis.axis_label = "Y {0}".format(units)
        p2.yaxis.axis_label = "Z {0}".format(units)
        p3 = figure(plot_width = 400, plot_height = 400, background_fill_color="#fafafa")
        p3.xaxis.axis_label = "Z {0}".format(units)
        p3.yaxis.axis_label = "X {0}".format(units)

        # create plot
        if dim == 2:
            n, m = ncvar.shape
            pvar_data_1 = [ncvar[idx, 0] for idx in range(0, n, pvar.plot_frequency)]
            pvar_data_2 = [ncvar[idx, 1] for idx in range(0, n, pvar.plot_frequency)]
            pvar_data_3 = [ncvar[idx, 2] for idx in range(0, n, pvar.plot_frequency)]
            p1.line(pvar_data_1, pvar_data_2, line_width=2, color=colors[4])
            p2.line(pvar_data_2, pvar_data_3, line_width=2, color=colors[1])
            p3.line(pvar_data_3, pvar_data_1, line_width=2, color=colors[2])
            fig = row(p1, p2, p3)
        else:
            message = "BLENDYN_OT_bplot_mplot_trajectory_scene::execute() " \
                      + "Plotting variable should be (Vec3) matrix"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}


        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_bplot_trajectory_scene::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        ## Create directory for saving file
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        basename = mbs.file_basename + ".Traj." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".png"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".png"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)
        outfname = os.path.join(plot_dir, basename)
        ## Save image in .html and .png format
        rel_path = os.path.relpath(outfname, start=os.getcwd())
        output_file(filename = rel_path+".html")
        save(fig)
        if mbs.show_in_localhost:
            show(fig)
        if mbs.save_as_png:
            hti = Html2Image()
            hti.screenshot(html_file = outfname+".html", save_as = basename+".png", size = (1220,430))
            Path(os.getcwd() + "/" + basename + ".png").rename(outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_bplot_trajectory_scene::execute() " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
#---------------------------------------------------------------------------
# End of BLENDYN_OT_bplot_trajectory_scene class

