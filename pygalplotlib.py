# --------------------------------------------------------------------------
# Blendyn -- file pygalplotlib.py
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
    import pygal
    from netCDF4 import Dataset
except ModuleNotFoundError as ierr:
    print("BLENDYN::pygalplotlib.py: could not import dependencies. Pygal plotting " \
          + "will be disabled. The reported error was:")
    print("{0}".format(ierr))

HAVE_CAIROSVG = False
try:
    import cairosvg
    HAVE_CAIROSVG = True
except ModuleNotFoundError as ierr:
    print("BLENDYN::pygalplotlib.py: could not import cairosvg.  Pygal plots will only be saved" \
          + "in .svg format, and not displayed in Blender UI.")
except OSError as oserr:
    print("BLENDYN::pygalplotlib.py: could not import cairosvg, OSError raised (linking " \
          "error?). Plots will only be saved" \
          + "in .svg format, and not displayed in Blender UI.")
    print("The reported error was: {}".format(oserr))

import numpy as np
import logging
from .baselib import *
from .nodelib import *
from .elementlib import *
import os


class BLENDYN_OT_plot_var_sxx_scene(bpy.types.Operator):
    """ Plots the selected variable autospectrum (Sxx) in the image editor
        and optionally save it as .svg in the 'plots' directory.
        The user can choose among all the variables of all the
        MBDyn entitites found in the output NetCDF file."""
    bl_idname = "blendyn.plot_var_sxx_scene"
    bl_label = "Plot the selected MBDyn var autospectrum"

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

        # set up pygal
        config = pygal.Config()
        config.show_dots = False
        config.legend_at_bottom = True
        config.truncate_legend = -1
        if (pvar.plot_xrange_max != 0.0):
            if (pvar.plot_xrange_min >= 0) and (pvar.plot_xrange_max > pvar.plot_xrange_min):
                config.xrange = (pvar.plot_xrange_min, pvar.plot_xrange_max)
            else:
                message = 'Invalid range for abscissa'
                self.report({'ERROR'}, message)
                logging.error("BLENDYN_OT_plot_var_sxx_scene::execute(): " + message)
        chart = pygal.XY(config)

        # calculate autospectra and plot them
        if dim == 2:
            n, m = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))

            # FIXME: Check if this is still valid for a variable
            #        timestep simulation
            # ANSWER: No, it is not, but so are a lot of other
            #         assumptions we make inside of Blendyn.
            #         Fixed timestep output is needed everywhere.
            freq = np.arange(nfft) * 1. / time[-1];

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
                    chart.add(pvar.name + ".Sxx." + str(mdx + 1), \
                              [(freq[idx], Gxx[idx]) for idx in range(0, int(nfft / 2), pvar.plot_frequency)])
        elif dim == 3:
            n, m, k = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft) * 1. / time[-1];

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
                    chart.add(pvar.plot_var + ".Sxx." + dims_names[mdx], \
                              [(freq[idx], Gxx[idx]) \
                               for idx in range(0, int(nfft / 2), pvar.plot_frequency)])
        else:
            nfft = int(np.power(2, np.round(np.log2(len(time)) + .5)))
            freq = np.arange(nfft) * 1. / time[-1];
            if pvar.fft_remove_mean:
                ncvar_fft = np.fft.fft(ncvar - np.mean(ncvar))
            else:
                ncvar_fft = np.fft.fft(ncvar)
                Sxx = np.multiply(np.conj(ncvar_fft), ncvar_fft)
                Gxx = np.zeros(int(nfft / 2))
                Gxx[0] = Sxx[0]
                Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                chart.add(pvar.name + ".Sxx", [(freq[idx], Gxx[idx]) \
                                               for idx in range(0, int(nfft / 2), pvar.plot_frequency)])
        chart.x_title = "Frequency [Hz]"

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_var_sxx_scene::execute() : " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        basename = mbs.file_basename + ".Sxx." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        if HAVE_CAIROSVG:
            cairosvg.svg2png(file_obj=open(outfname + ".svg", "rb"), write_to=outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_plot_var_sxx_scene::execute(): " \
                  + "Variable " + pvar.name + " autospectrum plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_plot_var_sxx_scene class

class BLENDYN_OT_plot_var_sxx_object(bpy.types.Operator):
    """ Plots the object's selected variable autospectrum in the image editor
        and optionally save it as .svg in the 'plots' directory """
    bl_idname = "blendyn.plot_var_sxx_object"
    bl_label = "Plot the selected MBDyn var"

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

        # set up pygal
        config = pygal.Config()
        config.show_dots = False
        config.legend_at_bottom = True
        config.truncate_legend = -1
        if (pvar.plot_xrange_max != 0.0):
            if (pvar.plot_xrange_min >= 0) and (pvar.plot_xrange_max > pvar.plot_xrange_min):
                config.xrange = (pvar.plot_xrange_min, pvar.plot_xrange_max)
            else:
                message = "BLENDYN_OT_plot_var_sxx_object::execute(): " \
                          + "Invalid range for abscissa"
                self.report({'ERROR'}, message)
                logging.error(message)

        chart = pygal.XY(config)

        # calculate autospectra and plot them
        if dim == 2:
            n, m = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft) * 1. / time[-1];
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
                    chart.add(pvar.name + ".Sxx." + str(mdx + 1), \
                              [(freq[idx], Gxx[idx]) for idx in range(0, int(nfft / 2), pvar.plot_frequency)])
        elif dim == 3:
            n, m, k = ncvar.shape
            nfft = int(np.power(2, np.round(np.log2(n) + .5)))
            freq = np.arange(nfft) * 1. / time[-1];

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
                    if pvar.fft_remove_mean:
                        comp_fft = np.fft.fft(ncvar[:, dims1[mdx], dims2[mdx]] -
                                              np.mean(ncvar[:, dims2[mdx], dims2[mdx]]))
                    else:
                        comp_fft = np.fft.fft(ncvar[:, dims1[mdx], dims2[mdx]])
                    Sxx = np.multiply(np.conj(comp_fft), comp_fft)
                    Gxx = np.zeros(int(nfft / 2))
                    Gxx[0] = Sxx[0]
                    Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                    chart.add(pvar.name + ".Sxx." + dims_names[mdx], \
                              [(freq[idx], Gxx[idx]) \
                               for idx in range(0, int(nfft / 2), pvar.plot_frequency)])
        else:
            nfft = int(np.power(2, np.round(np.log2(len(time)) + .5)))
            freq = np.arange(nfft) * 1. / time[-1];
            if pvar.fft_remove_mean:
                ncvar_fft = np.fft.fft(ncvar - np.mean(ncvar))
            else:
                ncvar_fft = np.fft.fft(ncvar)
                Sxx = np.multiply(np.conj(ncvar_fft), ncvar_fft)
                Gxx = np.zeros(int(nfft / 2))
                Gxx[0] = Sxx[0]
                Gxx[1:int(nfft / 2 - 1)] = 2 * Sxx[1:int(nfft / 2 - 1)]
                chart.add(pvar.name + ".Sxx", [(freq[idx], Gxx[idx]) \
                                               for idx in range(0, int(nfft / 2), pvar.plot_frequency)])
            chart.add(pvar.name, [(time[idx], ncvar[idx]) \
                                  for idx in range(0, len(time), pvar.plot_frequency)])
        chart.x_title = "Frequency [Hz]"

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_var_sxx_object::execute(): " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        basename = mbs.file_basename + ".Sxx." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")
        if HAVE_CAIROSVG:
            cairosvg.svg2png(file_obj=open(outfname + ".svg", "rb"), write_to=outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_plot_var_sxx_object::execute(): " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}


# --------------------------------------------------
# end of BLENDYN_OT_plot_var_sxx_object class

class BLENDYN_OT_plot_variables_list(bpy.types.Operator):
    """ Plot all the variables in the Variables List """
    bl_idname = "blendyn.plot_variables_list"
    bl_label = "Plot all the variables in Variables List"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_variables_list::execute() " \
                      + "Please save current Blender file first"
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
                        chart.add('{0}.{1}  {2}'.format(pvar.name, mdx + 1, units), \
                                  [(time[idx], ncvar[idx, mdx]) for idx in range(0, n, pvar.plot_frequency)])
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
                        chart.add('{0}.{1}  {2}'.format(pvar.name, dims_names[mdx], units), \
                                  [(time[idx], ncvar[idx, dims1[mdx], dims2[mdx]]) \
                                   for idx in range(0, n, pvar.plot_frequency)])
            else:
                chart.add('{0}  {1}'.format(pvar.name, units), [(time[idx], ncvar[idx]) \
                                                                for idx in range(0, len(time), pvar.plot_frequency)])

        chart.x_title = "time [s]"
        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_variables_list::execute() " \
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
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")

        if HAVE_CAIROSVG:
            cairosvg.svg2png(file_obj=open(outfname + ".svg", "rb"), write_to=outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_plot_variables_list::execute() " \
                  + "Variable " + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}


# --------------------------------------------------
# end of BLENDYN_OT_plot_variables_list class


class BLENDYN_OT_plot_var_scene(bpy.types.Operator):
    """ Plots the selected variable in the image editor
        and optionally save it as .svg in the 'plots' directory.
        The user can choose among all the variables of all the
        MBDyn entitites found in the output NetCDF fila."""
    bl_idname = "blendyn.plot_var_scene"
    bl_label = "Plot the selected MBDyn var"

    var_index: bpy.props.IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_var_scene::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}

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

        # set up pygal
        config = pygal.Config()
        config.show_dots = False
        config.legend_at_bottom = True
        config.truncate_legend = -1
        chart = pygal.XY(config)

        # create plot
        if dim == 2:
            n, m = ncvar.shape
            for mdx in range(m):
                if pvar.plot_comps[mdx]:
                    chart.add('{0}.{1}  {2}'.format(pvar.name, mdx + 1, units), \
                              [(time[idx], ncvar[idx, mdx]) for idx in range(0, n, pvar.plot_frequency)])
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
                    chart.add('{0}.{1}  {2}'.format(pvar.name, dims_names[mdx], units), \
                              [(time[idx], ncvar[idx, dims1[mdx], dims2[mdx]]) \
                               for idx in range(0, n, pvar.plot_frequency)])
        else:
            chart.add('{0}  {1}'.format(pvar.name, units), [(time[idx], ncvar[idx]) \
                                                            for idx in range(0, len(time), pvar.plot_frequency)])

        chart.x_title = "time [s]"
        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_var_scene::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        basename = mbs.file_basename + "." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")

        if HAVE_CAIROSVG:
            cairosvg.svg2png(file_obj=open(outfname + ".svg", "rb"), write_to=outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_plot_var_scene::execute() " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}


# --------------------------------------------------
# end of BLENDYN_OT_plot_var_scene class

class BLENDYN_OT_plot_var_object(bpy.types.Operator):
    """ Plots the object's selected variable in the image editor
        and optionally save it as .svg in the 'plots' directory """
    bl_idname = "blendyn.plot_var_object"
    bl_label = "Plot the selected MBDyn var"

    def execute(self, context):
        mbo = context.object.mbdyn
        mbs = context.scene.mbdyn

        # get requested netCDF variable
        pvar = mbs.plot_vars[mbo.plot_var_index]
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                              mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r')
        ncvar = nc.variables[pvar.name]

        # get its dimensions
        dim = len(ncvar.shape)

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
            n, m = ncvar.shape
            for mdx in range(m):
                if pvar.plot_comps[mdx]:
                    chart.add(pvar.name + "." + str(mdx + 1), \
                              [(time[idx], ncvar[idx, mdx]) for idx in range(0, n, pvar.plot_frequency)])
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
                    chart.add(pvar.name + dims_names[mdx], \
                              [(time[idx], ncvar[idx, dims1[mdx], dims2[mdx]]) \
                               for idx in range(0, n, pvar.plot_frequency)])
        else:
            chart.add(pvar.name, [(time[idx], ncvar[idx]) \
                                  for idx in range(0, len(time), pvar.plot_frequency)])

        chart.x_title = "time [s]"

        if not (bpy.data.is_saved):
            message = "BLENDYN_OT_plot_var_object::execute() " \
                      + "Please save current Blender file first"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
        plot_dir = os.path.join(bpy.path.abspath('//'), "plots")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        basename = mbs.file_basename + "." + pvar.name
        outfname = os.path.join(plot_dir, basename)
        if os.path.exists(outfname + ".svg"):
            kk = 1
            while os.path.exists(outfname + ".00" + str(kk) + ".svg"):
                kk = kk + 1
            basename = basename + ".00" + str(kk)

        outfname = os.path.join(plot_dir, basename)
        chart.render_to_file(outfname + ".svg")

        if HAVE_CAIROSVG:
            cairosvg.svg2png(file_obj=open(outfname + ".svg", "rb"), write_to=outfname + ".png")
            bpy.ops.image.open(filepath=outfname + ".png")

        message = "BLENDYN_OT_plot_var_object::execute() " \
                  + "Variable " + pvar.name + " plotted"
        self.report({'INFO'}, message)
        logging.info(message)
        return {'FINISHED'}
# --------------------------------------------------
# end of BLENDYN_OT_plot_var_object class