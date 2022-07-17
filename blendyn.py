# --------------------------------------------------------------------------
# Blendyn -- file blendyn.py
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

import os, atexit

import bpy
import bmesh
from bpy.props import *
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper

import logging
baseLogger = logging.getLogger()
baseLogger.setLevel(logging.DEBUG)

from mathutils import *
from math import *

import shutil
import numpy as np

import subprocess
import json

try:
    from netCDF4 import Dataset
except ImportError as ierr:
    print("BLENDYN::base.py: could not enable the netCDF module. NetCDF import "\
            + "will be disabled. The reported error was:")
    print("{0}".format(ierr))

HAVE_PSUTIL = False
try:
    import psutil
    HAVE_PSUTIL = True
except ImportError as ierr:
    print("BLENDYN::base.py: could not enable the MBDyn control module. "\
            + "Stopping MBDyn from the Blender UI will be disabled.")
    print("{0}".format(ierr))

from . baselib import *
from . elements import *
from . components import *
from . eigenlib import *
from . rfmlib import *
from . logwatcher import *
from . utilslib import set_active_collection

HAVE_PLOT = True

try:
    from .plotlib import *
except (ImportError, OSError, ModuleNotFoundError) as ierr:
    print("BLENDYN::base.py: could not enable the plotting module. Plotting  "\
            + "will be disabled. The reported error was:")
    print("{0}".format(ierr))
    HAVE_PLOT = False

## Nodes Dictionary: contains nodes informations
class BLENDYN_PG_nodes_dictionary(bpy.types.PropertyGroup):
    mbclass: StringProperty(
            name = "Class of MBDyn element",
            description  = ""
    )
    int_label: IntProperty(
            name = "node integer label",
            description = "Node integer label",
    )
    string_label: StringProperty(
            name = "node string label",
            description = "Node string label",
            default = "none"
    )
    blender_object: StringProperty(
            name = "blender object label",
            description = "Blender object",
            default = "none"
    )
    initial_pos: FloatVectorProperty(
            name = "node initial position",
            description = "Initial position",
            size = 3,
            precision = 6
    )
    initial_rot: FloatVectorProperty(
            name = "node initial orientation",
            description = "Node initial orientation (quaternion)",
            size = 4,
            precision = 6
    )
    parametrization: EnumProperty(
            items = [("EULER123", "euler123", "euler123", '', 1),\
                     ("EULER321", "euler321", "euler321", '', 2),\
                     ("PHI", "phi", "phi", '', 3),\
                     ("MATRIX", "mat", "mat", '', 4)],
            name = "rotation parametrization",
            default = "EULER123"
    )
    is_imported: BoolProperty(
        name = "Is imported flag",
        description = "Flag set to true at the end of the import process"
    )
    output: BoolProperty(
            name = "node output state",
            description = "False if node output is disabled",
            default = False
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_nodes_dictionary class
bpy.utils.register_class(BLENDYN_PG_nodes_dictionary)


class BLENDYN_PG_reference_dictionary(bpy.types.PropertyGroup):
    int_label: IntProperty(
            name = "reference integer label",
            description = "Reference integer label"
    )
    string_label: StringProperty(
            name = "reference string label",
            description = "Reference string label",
            default = "none"
    )
    blender_object: StringProperty(
            name = "blender object label",
            description = "Blender Object",
            default = "none"
    )
    is_imported: BoolProperty(
            name = "Is imported flag",
            description = "Flag set to true at the end of the import process"
    )
    pos: FloatVectorProperty(
            name = "position",
            description = "Reference Position",
            size = 3,
            precision = 6
    )
    rot: FloatVectorProperty(
            name = "orientation",
            description = "Reference Orientation",
            size = 4,
            precision = 6
    )
    vel: FloatVectorProperty(
            name = "velocity",
            description = "Reference Velocity",
            size = 3,
            precision = 6
    )
    angvel: FloatVectorProperty(
            name = "angular velocity",
            description = "Reference Angular Velocity",
            size = 3,
            precision = 6
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_reference_dictionary class
bpy.utils.register_class(BLENDYN_PG_reference_dictionary)


## Time PropertyGroup for animation
class BLENDYN_PG_mbtime(bpy.types.PropertyGroup):
    time: FloatProperty(
            name = "simulation time",
            description = "simulation time of animation frame"
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_mbtime class
bpy.utils.register_class(BLENDYN_PG_mbtime)


## PropertyGroup of Render Variables
class BLENDYN_PG_render_vars_dictionary(bpy.types.PropertyGroup):
    idx: IntProperty(
        name = "Render Variable index",
        description = "Index of the NetCDF variable to be set for display in rendering"
    )
    varname: StringProperty(
        name = "Display name",
        description = "Display name of the rendered variable"
    )
    variable: StringProperty(
        name = "NetCDF variable",
        description = "NetCDF variable to be rendered"
    )
    components: BoolVectorProperty(
        name = "Components",
        description = "Components of the variable to be displayed",
        size = 9
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_render_vars_dictionary class
bpy.utils.register_class(BLENDYN_PG_render_vars_dictionary)


## PropertyGroup of Driver Variables
class BLENDYN_PG_driver_vars_dictionary(bpy.types.PropertyGroup):
    variable: StringProperty(
        name = "Variable",
        description = "NetCDF variable to be rendered"
    )
    components: BoolVectorProperty(
        name = "Components",
        description = "Components of the variable to be displayed",
        size = 9
    )
    values: FloatVectorProperty(
        name = "Values",
        description = "Values of the variable at current frame"
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_driver_vars_dictionary class
bpy.utils.register_class(BLENDYN_PG_driver_vars_dictionary)


class BLENDYN_PG_display_vars_dictionary(bpy.types.PropertyGroup):
    name: StringProperty(
        name = "Group of Display Variables",
        description = ""
    )
    group: CollectionProperty(
	name = "Actual collection group",
	type = BLENDYN_PG_render_vars_dictionary
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_display_vars_dictionary class
bpy.utils.register_class(BLENDYN_PG_display_vars_dictionary)

## PropertyGroup of Environment Variables
class BLENDYN_PG_environment_vars_dictionary(bpy.types.PropertyGroup):
    variable: StringProperty(
            name = "Environment variables",
            description = 'Variables to be set'
    )
    value: StringProperty(
            name = "Values of Environment variables",
            description = "Values of variables to be set"
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_environment_vars_dictionary class
bpy.utils.register_class(BLENDYN_PG_environment_vars_dictionary)

## PropertyGroup of MBDyn plottable variables
class BLENDYN_PG_plot_vars(bpy.types.PropertyGroup):
    name: StringProperty(
            name = "Plottable variable"
    )
    plot_comps: BoolVectorProperty(
            name = "components",
            description = "Components of property to plot",
            default = [True for i in range(9)],
            size = 9
    )
    as_driver: BoolProperty(
            name = "Use as driver variable",
            default = False,
            update = update_driver_variables
    )
    plot_frequency: IntProperty(
            name = "frequency",
            description = "Frequency in plotting",
            default = 1
    )

    fft_remove_mean: BoolProperty(
            name = "Subtract mean",
            description = "Subtract the mean value before calculating the FFT",
            default = False
            )
    plot_xrange_min: FloatProperty(
            name = "minimum X value",
            description = "Minimum value for abscissa",
            default = 0.0
    )
    plot_xrange_max: FloatProperty(
            name = "maximum X value",
            description = "Maximum value for abscissa",
            default = 0.0
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_plot_vars class
bpy.utils.register_class(BLENDYN_PG_plot_vars)

## Set scene properties
class BLENDYN_PG_settings_scene(bpy.types.PropertyGroup):
    # Base path of the module
    addon_path: StringProperty(
            name = "Addon path",
            description = "Base path of addon files",
            default = os.path.dirname(__file__)
    )
    # Boolean: is the .mov (or .nc) file loaded properly?
    is_loaded: BoolProperty(
            name = "MBDyn files loaded",
            description = "True if MBDyn files are loaded correctly"
    )
    # MBDyn's imported files path
    file_path: StringProperty(
            name = "MBDyn file path",
            description = "Path of MBDyn's imported files",
            default = "",
            subtype = 'DIR_PATH'
    )
    # Base name of MBDyn's imported files
    file_basename: StringProperty(
            name = "MBDyn base file name",
            description = "Base file name of MBDyn's imported files",
            default = "not yet loaded"
    )
    # Use text output even when NetCDF is available?
    # This property is used when a simulation is run from Blender
    force_text_import: BoolProperty(
            name = "Always use text output",
            description = "Use text output even when NetCDF output is available",
            default = False
    )
    # Path of MBDyn input file (to run simulation from Blender)
    input_path: StringProperty(
            name = "Input File Path",
            description = "Path of MBDyn input files",
            default = "not yet selected"
    )
    # MBDyn input file (to run simulation from Blender)
    input_basename: StringProperty(
            name = "Input File basename",
            description = "Base name of Input File",
            default = "not yet selected"
    )
    # String representing path of MBDyn Installation
    install_path: StringProperty(
            name = "Installation path of MBDyn",
            description = "Installation path of MBDyn",
            subtype = 'DIR_PATH',
            default = 'not yet set'
    )
    # Integer representing the current simulation
    sim_num: IntProperty(
            name = "Number of Simulation",
            default = 0
    )
    final_time: FloatProperty(
            name = "Previous State of Simulation",
            default = 0.0
    )
    ui_time: FloatProperty(
            name = "Final time from user",
            default = 0.0
    )
    mbdyn_running: BoolProperty(
            name = 'MBDyn running',
            default = False
    )
    sim_status: IntProperty(
            name = "Progress of Simulation",
            default = 0
    )
    # Command-line options to be specified in MBDyn simulation
    cmd_options: StringProperty(
            name = "Command-line Options",
            default = ''
    )
    # Boolean representing whether user wants to overwrite existing output files
    overwrite: BoolProperty(
            name = "Overwrite Property",
            description = "True if the user wants to overwrite the existing output files",
            default = False
    )
    del_log: BoolProperty(
            name = "Log property",
            description = "True if the user wants to delete log files on exit",
            default = False,
            update = update_del_log
    )
    render_nc_vars: EnumProperty(
            items = get_render_vars,
            name = "Text overlay variables",
    )
    render_var_name: StringProperty(
            name = "Name of variable",
            default = ''
    )
    render_vars: CollectionProperty(
            name = "RenderVars",
            description = "MBDyn render variables collection",
            type = BLENDYN_PG_render_vars_dictionary
    )
    driver_vars: CollectionProperty(
            name = "DriverVars",
            description = "Variables set to track NetCDF variables",
            type = BLENDYN_PG_driver_vars_dictionary
    )
    display_vars_group: CollectionProperty(
            name = "MBDyn Display variables group collection",
            type = BLENDYN_PG_display_vars_dictionary
    )
    display_enum_group: EnumProperty(
            items = get_display_group,
            name = 'Display Enum Group'
    )
    group_name: StringProperty(
            name = "Name of Display Variables Group"
    )
    plot_group: BoolProperty(
            name = "Plot List of variables as group",
            default = False
    )
    # Collection of Environment variables and corresponding values
    env_vars: CollectionProperty(
            name = "MBDyn environment variables collection",
                type = BLENDYN_PG_environment_vars_dictionary
    )
    # Environment Variables index, holds the index for displaying the Envrionment variables in a list
    env_index: IntProperty(
            name = "MBDyn Environment variables collection index",
            default = 0
    )
    render_index: IntProperty(
            name = "MBDyn Render Variables collection index",
            default = 0
    )
    # Name of the Environment Variable
    env_variable: StringProperty(
            name = "MBDyn environment variables",
            description = "Environment variables used in MBDyn simulation"
    )
    # Value associated with the Environment Variable
    env_value: StringProperty(
            name = "Values of MBDyn environment values",
            description = "Values of the environment variables used in MBDyn simulation"
    )
    # Number of rows (output time steps * number of nodes) in MBDyn's .mov file
    num_rows: IntProperty(
            name = "MBDyn .mov file number of rows",
            description = "Total number of rows in MBDyn .mov file, corresponding (total time steps * number of nodes)"
    )
    # Load frequency: if different than 1, the .mov file is read every N time steps
    load_frequency: FloatProperty(
            name = "frequency",
            description = "If this value is X, different than 1, then the MBDyn output is loaded every X time steps",
            min = 1.0,
            default = 1.0
    )
    #Start time
    start_time: FloatProperty(
            name = "Start Time",
            description = "If this value is X, different than 0, the import starts at X seconds",
            min = 0.0,
            default = 0.0,
            update = update_start_time
    )
    end_time: FloatProperty(
            name = "End Time",
            description = "If this value is X, different than total simulation time, the import stops at X seconds",
            min = 0.0,
            update = update_end_time
    )
    time_step: FloatProperty(
            name = "Time Step",
            description = "Simulation time step"
    )
    # Reference dictionary -- holds the associations between MBDyn references and blender
    # objects
    references: CollectionProperty(
            name = "MBDyn references",
            type = BLENDYN_PG_reference_dictionary
    )
    # Reference dictionary index -- holds the index for displaying the Reference
    # Dictionary in a UI List
    ref_index: IntProperty(
            name = "References collection index",
            default = 0
    )
    # Nodes dictionary -- holds the association between MBDyn nodes and blender objects
    nodes: CollectionProperty(
            name = "MBDyn nodes",
            type = BLENDYN_PG_nodes_dictionary
    )
    # Do we use 'free' or 'structured' labels?
    free_labels: BoolProperty(
            name = "Use free labels",
            description = "Do not check variable name when parsing labels"
            # update = bpy.ops.blendyn.free_labels_warning
    )       
    # Nodes dictionary index -- holds the index for displaying the Nodes Dictionary in a UI List
    nd_index: IntProperty(
            name = "MBDyn nodes collection index",
            default = 0
    )
    # Default object representing a node, when imported automatically
    node_object: EnumProperty(
            items = [("ARROWS", "Arrows", "Empty - arrows", 'OUTLINER_OB_EMPTY', 1),\
                     ("AXES", "Axes", "Empty - axes", 'EMPTY_DATA', 2),\
                     ("CUBE", "Cube", "", 'MESH_CUBE', 3),\
                     ("UVSPHERE", "UV Sphere", "", 'MESH_UVSPHERE', 4),\
                     ("NSPHERE", "Nurbs Sphere", "", 'SURFACE_NSPHERE', 5),\
                     ("CONE", "Cone", "", 'MESH_CONE', 6)],
            name = "Import nodes as",
            default = "ARROWS"
            )

    missing: EnumProperty(
            items = [("DO_NOTHING", "Do Nothing","","" ,1),\
                     ("HIDE", "Hide", "","" ,2),\
                     ("DELETE", "Delete", "", "", 3)],
            name = "Handling of missing nodes/elements",
            default = "HIDE"
    )
    # Behavior for importing shells and beams: get a single mesh or separate mesh objects?
    mesh_import_mode: EnumProperty(
            items = [("SEPARATED_OBJECTS", "Separated mesh objects", "", 'UNLINKED', 1),\
                     ("SINGLE_MESH", "Joined in single mesh", "", 'LINKED', 2)],
            name = "Mesh objects",
            default = "SEPARATED_OBJECTS"
    )
    # Elements dictionary -- holds the collection of the elements found in the .log file
    elems: CollectionProperty(
            name = "MBDyn elements collection",
            type = BLENDYN_PG_elems_dictionary
    )
    # Elements to be updated -- holds the keys to elements that need to update their configuration
    #                           when the scene changes
    elems_to_update: CollectionProperty(
            type = BLENDYN_PG_elem_to_be_updated,
            name = "Elements that require update",
            description = "Collection of indexes of the elements that need to be updated when \
                            the scene is changed"
    )
    # Current Simulation Time
    simtime: CollectionProperty(
            name = "MBDyn simulation time",
            type = BLENDYN_PG_mbtime
    )
    # Current simulation time
    time: FloatProperty(
            name = "time: ",
            description = "Current MBDyn simulation time",
            default = 0.0
    )
    # Elements dictionary index -- holds the index for displaying the Elements Dictionary in a
    # UI List
    ed_index: IntProperty(
            name = "MBDyn elements collection index",
            default = 0
    )

    # MBDyn's node count
    num_nodes: IntProperty(
            name = "MBDyn nodes number",
            description = "MBDyn node count"
    )
    # MBDyn's time steps count
    num_timesteps: IntProperty(
            name = "MBDyn time steps",
            description = "MBDyn time steps count"
    )
    # Flag that indicates if we are to use NETCDF results format
    use_netcdf: BoolProperty(
            name = "Use netCDF",
            description = "Import results in netCDF format",
            default = False
    )
    # Flag that indicates if the .mov (or .nc) file is loaded correctly and the
    # nodes dictionary is ready, used to indicate that all is ready for the object's
    # to be animated
    is_ready: BoolProperty(
            name = "ready to animate",
            description = "True if .mov (or .nc) file and nodes dictionary loaded correctly",
    )
    # If we want to hook vertices in creating mesh from nodes
    is_vertshook: BoolProperty(
            name = "Hook vertices",
            description = "Hook directly the vertices to the nodes in creating a mesh object?",
            default = False
    )
    # Lower limit of range import for nodes
    min_node_import: IntProperty(
            name = "first node to import",
            description = "Lower limit of integer labels for range import for nodes",
            default = 0
    )
    # Higher limit of range import for nodes
    max_node_import: IntProperty(
            name = "last node to import",
            description = "Higher limit of integer labels for range import for nodes",
            default = 0
    )
    node_scale_slider: FloatProperty(
            name = "Scaling factor",
            default = 1.0
    )
    # Type filter for elements import
    elem_type_import: EnumProperty(
            items  = get_elems_types,
            name = "Elements to import",
    )
    elem_scale_slider: FloatProperty(
            name = "Scaling Factor",
            default = 1.0
    )
    # Lower limit of range import for elements
    min_elem_import: IntProperty(
            name = "first element to import",
            description = "Lower limit of integer labels for range import for elements",
            default = 0
    )
    # Higher limit of range import for elements
    max_elem_import: IntProperty(
            name = "last element to import",
            description = "Higher limit of integer labels for range import for elements",
            default = 2**31 - 1
    )
    components: CollectionProperty(
            name = "Components",
            description = "Components structural and geometrical data",
            type = BLENDYN_PG_components_dictionary
    )
    adding_component: BoolProperty(
            description = "Are we adding a new component?",
            default = False
    )
    editing_component: BoolProperty(
            description = "Are we editing an existing component?",
            default = False
    )
    # Components dictionary index -- holds the index for displaying the 
    # Components Dictionary in a UI List
    cd_index: IntProperty(
            name = "MBDyn components collection index",
            default = 0,
            min = 0,
            update = update_cd_index,
    )
    comp_selected_elem: EnumProperty(
            items = get_deformable_elems,
            name = "Selected element",
            description = "Selected element in deformable elements list"
    )
    eigensolutions: CollectionProperty(
            name = "Eigensolutions",
            description = "Parameters of the eigensolutions found in the MBDyn output",
            type = BLENDYN_PG_eigenanalysis
    )
    curr_eigsol: IntProperty(
            name = "current eigensolution",
            description = "Index of the currently selected eigensolution",
            default = 0,
            update = update_curr_eigsol
    )
    plot_vars: CollectionProperty(
            name = "MBDyn variables available for plotting",
            type = BLENDYN_PG_plot_vars
    )
    plot_var_index: IntProperty(
            name = "Plot variable index",
            description = "index of the current variable to be plotted",
            default = 0
    )
    plot_engine: EnumProperty(
        items=[("PYGAL", "Pygal", "Pygal", '', 2), \
               ("MATPLOTLIB", "Matplotlib", "Matplotlib", '', 1), \
               ("BOKEH", "Bokeh", "bokeh", '', 3)], \
        name="plot engine",
        default="MATPLOTLIB"
    )
    plot_type: EnumProperty(
        items=[("TIME_HISTORY", "Time history", "Time history", '', 1), \
               ("AUTOSPECTRUM", "Autospectrum", "Autospectrum", '', 2), \
               ("TRAJECTORY", "Trajectory", "Trajectory", '', 3)], \
        name="plot type",
        default="TIME_HISTORY"
    )

    show_in_localhost: BoolProperty(
        description = "Are you want to show your plot in localhost?",
        default = False
    )

    save_as_png: BoolProperty(
        description = "Are you want to save your plot as png?",
        default = False
    )

    if HAVE_PLOT:
        plot_sxy_varX: StringProperty(
                name = "Cross-spectrum X variable",
                description = "variable to be used as input in cross-spectrum",
                default = "none"
        )
        plot_sxy_varY: StringProperty(
                name = "Cross-spectrum Y variable",
                description = "variable to be used as output in cross-spectrum",
                default = "none"
        )
# -----------------------------------------------------------
# end of BLENDYN_PG_settings_scene class


## MBDyn Settings for Blender Object
class BLENDYN_PG_settings_object(bpy.types.PropertyGroup):
    """ Properties of the current Blender Object related to MBDyn """
    # Type of MBDyn entity
    type: StringProperty(
        name = "MBDyn entity type",
        description = "Type of MBDyn entity associated with object",
        default = 'none'
    )
    # Dictionary key
    dkey: StringProperty(
        name = "MBDyn dictionary index",
        description = "Index of the entry of the MBDyn dictionary relative to the object",
        default = 'none'
    )
    # Specific for plotting
    if HAVE_PLOT:
        plot_var_index: IntProperty(
            name = "Plot variable index",
            description = "index of the current variable to be plotted",
            default = 0
        )

# -----------------------------------------------------------
# end of BLENDYN_PG_settings_object class

bpy.utils.register_class(BLENDYN_PG_settings_object)
bpy.utils.register_class(BLENDYN_PG_settings_scene)
bpy.types.Scene.mbdyn = PointerProperty(type=BLENDYN_PG_settings_scene)
bpy.types.Object.mbdyn = PointerProperty(type=BLENDYN_PG_settings_object)

# Handler to update the current time of simulation
@persistent
def update_time(scene):
    try:
        scene.mbdyn.time = scene.mbdyn.simtime[scene.frame_current].time
    except IndexError:
        pass
bpy.app.handlers.frame_change_pre.append(update_time)

@persistent
def render_variables(scene):
    mbs = scene.mbdyn
    if len(mbs.render_vars):
        try:
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, "r")
            string = [ '{0} : {1}'.format(var.variable, \
                parse_render_string(netcdf_helper(nc, scene, var.variable), var.components)) \
                for var in mbs.render_vars ]
            string = '\n'.join(string)
            if len(mbs.render_vars):
                bpy.data.scenes['Scene'].render.stamp_note_text = string
        except IndexError:
            pass

if HAVE_PLOT:
    bpy.app.handlers.frame_change_pre.append(render_variables)

@persistent
def update_driver_vars(scene):
    mbs = scene.mbdyn
    ncfile = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.nc')
    if (mbs.is_loaded and mbs.use_netcdf):
        nc = Dataset(ncfile, "r")
        for dvar in mbs.driver_vars:
            ncvar = netcdf_helper(nc, scene, dvar.variable)
            dim = len(ncvar.shape)
            if dim == 1:
                for ii in range(len(ncvar)):
                    dvar.values[ii] = ncvar[ii] if dvar.components[ii] else 0.0
            else:
                for ii in range(3):
                    for jj in range(3):
                        dvar.values[ii + jj] = ncvar[ii,jj] if dvar.components[ii+jj] else 0.0
bpy.app.handlers.frame_change_pre.append(update_driver_vars)

@persistent
def close_log(scene):
    baseLogger.handlers = []

bpy.app.handlers.load_pre.append(close_log)
bpy.app.handlers.save_pre.append(close_log)

@persistent
def set_mbdyn_path_startup(scene):
    mbs = bpy.context.scene.mbdyn
    try:
        with open(os.path.join(mbs.addon_path, 'config.json'), 'r') as f:
            mbs.install_path = json.load(f)['mbdyn_path']
    except FileNotFoundError:
        if shutil.which('mbdyn'):
            mbs.install_path = os.path.dirname(shutil.which('mbdyn'))
        pass

bpy.app.handlers.load_post.append(set_mbdyn_path_startup)

@persistent
def blend_log(scene):

    mbs = bpy.context.scene.mbdyn

    if mbs.file_path:
        log_messages(mbs, baseLogger, False)

bpy.app.handlers.load_post.append(blend_log)

@persistent
def rename_log(scene):
    mbs = bpy.context.scene.mbdyn
    logFile = ('{0}_{1}.bylog').format(mbs.file_path + 'untitled', mbs.file_basename)
    newBlend = path_leaf(bpy.data.filepath)[1]
    newLog = ('{0}_{1}.bylog').format(mbs.file_path + newBlend, mbs.file_basename)
    try:
        os.rename(logFile, newLog)
    except FileNotFoundError:
        pass

    if os.path.basename(logFile) != "untitled_not yet loaded.bylog":
        try:
            bpy.data.texts[os.path.basename(logFile)].name = os.path.basename(newLog)
            log_messages(mbs, baseLogger, True)
        except KeyError:
            pass

bpy.app.handlers.save_post.append(rename_log)

class BLENDYN_OT_standard_import(bpy.types.Operator):
    """ Automatically import nodes and elements at once """
    bl_idname = "blendyn.standard_import"
    bl_label = "MBDyn Standard Import"

    def execute(self, context):
        selftag = 'BLENDYN_OT_standard_import::execute(): ' 
        try:
            bpy.ops.blendyn.read_mbdyn_log_file('EXEC_DEFAULT') 
            bpy.ops.blendyn.node_import_all('EXEC_DEFAULT')
            bpy.ops.blendyn.elements_import_all('EXEC_DEFAULT')
        except RuntimeError as re:
            message = "BLENDYN_OT_standard_import::modal(): something went wrong during the automatic import. "\
                + " See the .bylog file for details"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}
        
        message = "BLENDYN_OT_standard_import::modal(): Done."
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)
        bpy.ops.object.select_all(action = 'DESELECT')
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of BLENDYN_OT_stardard_import class


class BLENDYN_OT_read_mbdyn_log_file(bpy.types.Operator):
    """ Imports MBDyn nodes and elements by parsing the .log file """
    bl_idname = "blendyn.read_mbdyn_log_file"
    bl_label = "MBDyn .log file parsing"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ret_val, obj_names = parse_log_file(context)

        missing = context.scene.mbdyn.missing
        selftag = 'BLENDYN_OT_read_mbdyn_log_file::execute(): '
        if len(obj_names) > 0:
            message = "Some of the nodes/elements are missing in the new .log file"
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            hide_or_delete(obj_names, missing)
            return {'FINISHED'}

        if ret_val == {'LOG_NOT_FOUND'}:
            message = ".log file not found"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}
        elif ret_val == {'NODES_NOT_FOUND'}:
            message = "The .log file selected does not contain node definitions"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}
        elif ret_val == {'MODEL_INCONSISTENT'}:
            message = "Contents of .log file are not onsistent with "\
                    + "current Blender scene."
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'FINISHED'}
        elif ret_val == {'NODES_INCONSISTENT'}:
            message = "Nodes in .log file are not consistent with "\
                    + "current Blender scene"
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'FINISHED'}
        elif ret_val == {'ELEMS_INCONSISTENT'}:
            message = "Elements in .log file are not consistent with "\
                    + "curren Blender scene"
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'FINISHED'}
        elif ret_val == {'OUT_NOT_FOUND'}:
            message = "Could not locate the .out file"
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'FINISHED'}
        elif ret_val == {'ROTATION_ERROR'}:
            message = "Output rotation parametrization is not supported by Blender"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}
        elif ret_val == {'FINISHED'}:
            message = "MBDyn model imported successfully"
            bpy.context.scene.render.use_stamp = True
            bpy.context.scene.render.use_stamp_note = True
            self.report({'INFO'}, message)
            baseLogger.info(selftag + message)
            return {'FINISHED'}
        else:
            # should not be reached
            message = "Unknown error in reading .log file."\
                    + "The return value of parse_log_file() was: {}".format(ret_val)
            self.report({'ERROR'}, message)
            baseLogger.info(selftag + message)
            return {'CANCELLED'} 

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of BLENDYN_OT_read_mbdyn_log_file class


class BLENDYN_OT_select_output_file(bpy.types.Operator, ImportHelper):
    """ Sets MBDyn's output files path and basename """
    bl_idname = "blendyn.select_output_file"
    bl_label = "Select MBDyn results file"

    filter_glob: StringProperty(
            default = "*.mov;*.nc",
            options = {'HIDDEN'},
            )

    def execute(self, context):
        mbs = context.scene.mbdyn

        # removes keyframes before importing a new file
        remove_oldframes(context)

        si_retval = setup_import(self.filepath, context)

        selftag =  "BLENDYN_OT_select_output_file::execute(): "
        if si_retval == {'NETCDF_ERROR'}:
            message = "NetCDF module not imported correctly"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}
        elif si_retval == {'FILE_ERROR'}:
            message = "Output file not set correctly (no file selected?)"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
        elif si_retval == {'FINISHED'}:
            mbs.file_path, mbs.file_basename = path_leaf(self.filepath)
            baseLogger.handlers = []
            log_messages(mbs, baseLogger, False)
            return si_retval

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
# -----------------------------------------------------------
# end of BLENDYN_OT_select_output_file class


class BLENDYN_OT_assign_labels(bpy.types.Operator):
    """ Assigns 'recognisable' labels to MBDyn nodes and elements by
        parsing the .log file """
    bl_idname = "blendyn.assign_labels"
    bl_label = "Import labels of MBDyn objects"

    def execute(self, context):
        selftag =  "BLENDYN_OT_assign_labels::execute(): "
        ret_val = assign_labels(context)
        if ret_val == {'NOTHING_DONE'}:
            message = "MBDyn labels file provided appears to not contain " \
                    + "correctly defined labels."
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'CANCELLED'}

        elif ret_val == {'LABELS_UPDATED'}:
            message = "MBDyn labels imported correctly."
            self.report({'INFO'}, message)
            baseLogger.info(selftag + message)
            return {'FINISHED'}

        elif ret_val == {'FILE_NOT_FOUND'}:
            message = "MBDyn labels file not found."
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_assign_labels class


class BLENDYN_OT_clear_data(bpy.types.Operator):
    """ Clears MBDyn elements and nodes dictionaries, essentially\
    'cleaning' the scene of all MBDyn related data"""
    bl_idname = "blendyn.clear_data"
    bl_label = "Clear MBDyn Data"

    def execute(self, context):
        mbs = context.scene.mbdyn

        for var in mbs.keys():
            dummy = getattr(mbs, var)
            if isinstance(dummy, bpy.types.bpy_prop_collection):
                dummy.clear()

        selftag = "BLENDYN_OT_clear_data::execute(): "
        message = "Cleared MBDyn data."
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_clear_data class


class BLENDYN_OT_set_mbdyn_install_path(bpy.types.Operator):
    """Sets the Installation Path of MBDyn to be used\
        in running simulation"""
    bl_idname = "blendyn.set_mbdyn_install_path"
    bl_label = "Set installation path of MBDyn"

    def execute(self, context):
        mbs = context.scene.mbdyn
        mbdyn_path = mbs.install_path
        config = {'mbdyn_path': mbdyn_path}

        selftag = "BLENDYN_OT_set_mbdyn_install_path::execute(): "
        message = "MBDyn install path set to "\
                + mbdyn_path
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)

        with open(os.path.join(mbs.addon_path, 'config.json'), 'w') as f:
            json.dump(config, f)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_mbdyn_install_path class


class BLENDYN_OT_mbdyn_default_install_path(bpy.types.Operator):
    """Sets the Installation path of MBDyn to the value\
        found in the system $PATH variable"""
    bl_idname = "blendyn.mbdyn_default_install_path"
    bl_label = "Set Default Path for MBDyn"

    def execute(self, context):
        mbs = context.scene.mbdyn

        selftag = "BLENDYN_OT_mbdyn_default_install_path::execute(): "
        if shutil.which('mbdyn'):
            mbs.install_path = os.path.dirname(shutil.which('mbdyn'))
            message = "MBDyn found in system's PATH at "\
                    + mbs.install_path
            self.report({'INFO'}, message)
            baseLogger.info(selftag + message)
        else:
            message = "MBDyn path is not set in the system $PATH variable"
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_mbdyn_default_install_path class


class BLENDYN_OT_config_mbdyn_install_path(bpy.types.Operator):
    """Sets the Installation path of MBDyn to the value\
        found in config.json"""
    bl_idname = "blendyn.config_mbdyn_install_path"
    bl_label = "Set config.json Path for MBDyn"

    def execute(self, context):
        mbs = bpy.context.scene.mbdyn
        selftag = "BLENDYN_OT_config_mbdyn_install_path::execute(): "

        try:
            with open(os.path.join(mbs.addon_path, 'config.json'), 'r') as f:
                mbs.install_path = json.load(f)['mbdyn_path']
                message = "Loaded MBDyn installation path "\
                        + mbs.install_path + " from config.json file"
                self.report({'INFO'}, message)
                baseLogger.info(selftag + message)
        except FileNotFoundError:
            message = "No config.json file found. Please set the path manually."
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_config_mbdyn_install_path class


class BLENDYN_OT_select_mbdyn_input_file(bpy.types.Operator, ImportHelper):
    """Set input file's path and basename\
        to be used in MBDyn simulation"""
    bl_idname = "blendyn.select_mbdyn_input_file"
    bl_label = "MBDyn input file"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.sim_num = 0

        mbs.input_path = os.path.abspath(self.filepath)
        mbs.input_basename = os.path.splitext(os.path.basename(self.filepath))[0]

        mbs.file_basename = mbs.input_basename
        mbs.file_path = os.path.dirname(mbs.input_path)

        selftag = "BLENDYN_OT_select_mbdyn_input_file::execute(): "
        message = "Set input file to " \
                + mbs.input_path + mbs.input_basename

        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
# -----------------------------------------------------------
# end of BLENDYN_OT_select_mbdyn_input_file class


class BLENDYN_OT_set_env_variable(bpy.types.Operator):
    """Sets an environment variable to be\
        used in MBDyn simulation"""
    bl_idname = "blendyn.set_env_variable"
    bl_label = "Set Environment Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn
        selftag =  "BLENDYN_OT_set_env_variable::execute(): "

        exist_env_vars = [mbs.env_vars[var].variable for var in range(len(mbs.env_vars))]

        try:
            index = exist_env_vars.index(mbs.env_variable)
            mbs.env_vars[index].value = mbs.env_value

        except ValueError:
            env = mbs.env_vars.add()
            env.variable = mbs.env_variable
            env.value = mbs.env_value

        message = "Set environment variable "\
                + env.variable + " = " + env.value
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_env_variable class


class BLENDYN_OT_delete_env_variable(bpy.types.Operator):
    """Delete Environment variable"""
    bl_idname = "blendyn.delete_env_variable"
    bl_label = "Delete Environment Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn
        selftag =  "BLENDYN_OT_delete_env_variable::execute(): "

        message = "Removing environment variable "\
                + mbs.env_vars[mbs.env_index]
        mbs.env_vars.remove(mbs.env_index)
        self.report({'INFO'}, message)
        baseLogger.info(selftag, message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_delete_env_variable class

class BLENDYN_OT_run_mbdyn_simulation(bpy.types.Operator):
    """Runs the MBDyn Simulation in background"""
    bl_idname = "blendyn.run_mbdyn_simulation"
    bl_label = "Run MBDyn Simulation"

    timer = None

    def execute(self, context):
        mbs = context.scene.mbdyn

        for idx in range(len(mbs.env_vars)):
            variable = mbs.env_vars[idx].variable
            value = mbs.env_vars[idx].value

            os.environ[variable] = value

        mbdyn_env = os.environ.copy()

        mbdyn_env['PATH'] = mbs.install_path + ":" + mbdyn_env['PATH']

        command_line_options = mbs.cmd_options

        command = ('mbdyn {0} {1}').format(command_line_options, mbs.input_path)

        if not mbs.overwrite:
            mbs.sim_num += 1

        basename_list = mbs.file_basename.split('_')

        if len(basename_list) > 1:
            try:
                if int(basename_list[-1]) == mbs.sim_num - 1:
                    filename = basename_list
                    filename[-1] = str(mbs.sim_num)
                    mbs.file_basename = "_".join(filename)
            except ValueError:
                pass

        else:
            mbs.file_basename = ('{0}_{1}').format(mbs.file_basename, mbs.sim_num)

        if mbs.file_path:
            command += (' -o {}').format(os.path.join(mbs.file_path, mbs.file_basename))

        mbdyn_retcode = subprocess.call(command + ' &', shell = True, env = mbdyn_env)

        self.timer = context.window_manager.event_timer_add(0.5, context.window)
        context.window_manager.modal_handler_add(self)

        selftag = "BLENDYN_OT_run_mbdyn_simulation::execute() "
        message = "Started MBDyn simulation... "
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        mbs = context.scene.mbdyn

        file = os.path.join(mbs.file_path, mbs.file_basename)

        if not mbs.mbdyn_running:
            context.window_manager.event_timer_remove(self.timer)
            return {'CANCELLED'}

        status = ''
        percent = 0

        if event.type == 'TIMER':
            context.area.tag_redraw()
            if os.path.exists(file + '.out'):
                try:
                    status = LogWatcher.tail(file + '.out', 1)[0].decode('utf-8')
                    status = status.split(' ')[2]
                    percent = (float(status)/mbs.final_time)*100
                except IndexError:
                    pass
                except ValueError:
                    pass
            mbs.sim_status = percent
            print(str(round(percent)) + '% completed')

        if percent >= 100:
            context.window_manager.event_timer_remove(self.timer)

            si_retval = {'FINISHED'}

            if ( os.path.isfile(os.path.join(mbs.file_path, \
                    mbs.file_basename + '.nc') ) and not( mbs.force_text_import) ):
                si_retval = setup_import(os.path.join(mbs.file_path, \
                        mbs.file_basename + '.nc'), context)
            else:
                mbs.use_netcdf = False
                si_retval = setup_import(os.path.join(mbs.file_path, \
                        mbs.file_basename + '.mov'), context)

            si_retval = setup_import(os.path.join(mbs.file_path, \
                        mbs.file_basename + '.mov'), context)
            return si_retval

        selftag = "BLENDYN_OT_run_mbdyn_simulation::execute() "
        message = "MBDyn simulation completed."
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        mbs = context.scene.mbdyn
        parse_input_file(context)

        mbs.mbdyn_running = True

        if not mbs.final_time:
            selftag = "BLENDYN_OT_run_mbdyn_simulation::execute() "
            message = "Enter final time to start the simulation. Aborting..."
            self.report({'ERROR'}, message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}

        return self.execute(context)

# -----------------------------------------------------------
# end of BLENDYN_OT_run_mbdyn_simulation class


class BLENDYN_OT_stop_mbdyn_simulation(bpy.types.Operator):
    """Stops the MBDyn simulation"""
    bl_idname = "blendyn.stop_mbdyn_simulation"
    bl_label = "Stop MBDyn Simulation"

    def execute(self, context):
        selftag =  "BLENDYN_OT_stop_mbdyn_simulation::execute(): "
        mbs = context.scene.mbdyn
        kill_mbdyn()

        mbs.mbdyn_running = False

        message = "MBDyn simulation halted."
        self.report({'INFO'}, message)
        baseLogger.info(selftag + message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of BLENDYN_OT_stop_mbdyn_simulation class


class BLENDYN_OT_set_motion_paths(bpy.types.Operator):
    """ Sets the motion path for all the objects that have an assigned MBDyn's node """
    bl_idname = "blendyn.set_motion_paths"
    bl_label = "MBDyn Motion Path setter"

    def execute(self, context):
        mbs = context.scene.mbdyn

        remove_oldframes(context)

        if not(context.scene.mbdyn.use_netcdf):
            ret_val = set_motion_paths_mov(context)
        else:
            ret_val = set_motion_paths_netcdf(context)
        if ret_val == 'CANCELLED':
            selftag =  "BLENDYN_OT_set_motion_paths::execute()"
            message = "MBDyn results file not loaded"
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
        return ret_val

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_motion_paths class


class BLENDYN_OT_set_import_freq_auto(bpy.types.Operator):
    """ Sets the import frequency automatically in order to match the Blender
        time and the simulation time, based on the current render fps """
    bl_idname = "blendyn.set_import_freq_auto"
    bl_label = "Import frequency: auto"

    def execute(self, context):
        mbs = context.scene.mbdyn
        mbs.load_frequency = 1./(context.scene.render.fps*mbs.time_step)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_set_import_freq_auto class

class BLENDYN_OT_outline_collapse(bpy.types.Operator):
    """ Collapses all the elements in the scene outline """
    bl_idname = "blendyn.outline_collapse"
    bl_label = "Collapse scene outline"

    def execute(self, context):
        outline_toggle(context, 'collapse')
        return{'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_outline_collapse class

class BLENDYN_OT_outline_expand(bpy.types.Operator):
    """ Collapses all the elements in the scene outline """
    bl_idname = "blendyn.outline_expand"
    bl_label = "Expand scene outline"

    def execute(self, context):
        outline_toggle(context, 'expand')
        return{'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_outline_expand class

class BLENDYN_PT_tool_bar:
    bl_category = 'Blendyn'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

class BLENDYN_PT_import(BLENDYN_PT_tool_bar, bpy.types.Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    bl_idname = "BLENDYN_PT_import"
    bl_label = "Load results"

    def draw(self, context):

        # utility renaming
        layout = self.layout
        obj = context.object
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        ed = mbs.elems

        # MBDyn output file selection
        col = layout.column(align = True)
        col.label(text = "MBDyn simulation results")
        col.operator(BLENDYN_OT_select_output_file.bl_idname, \
                text = "Select results file")

        row = layout.row()

        col = layout.column(align = True)
        col.operator(BLENDYN_OT_standard_import.bl_idname,\
                text = "Standard Import")

        # Display MBDyn file basename and info
        row = layout.row()
        col = layout.column(align = True)
        col.label(text = "Loaded results file") 
        col.prop(mbs, "file_basename", text = "")
        col.prop(mbs, "num_nodes", text = "nodes total")

        if not(mbs.use_netcdf):
            col.prop(mbs, "num_rows", text = "rows total")
        col.prop(mbs, "num_timesteps", text = "time steps")

        row = layout.row()
        fpath = mbs.file_path + mbs.file_basename
        if mbs.use_netcdf:
            fpath += '.nc'
        else:
            fpath += '.mov'
        if mbs.file_path:
            row.label(text = "Full file path:")
            row = layout.row()
            row.label(text = fpath)
        col.enabled = False

        # Import MBDyn data
        row = layout.row()
        # row.label(text = "Load MBDyn data")
        col = layout.column(align = True)
        col.operator(BLENDYN_OT_read_mbdyn_log_file.bl_idname, \
                text = "Load .log file")

        # Assign MBDyn labels to elements in dictionaries
        col.operator(BLENDYN_OT_assign_labels.bl_idname, \
                text = "Load MBDyn labels")
        col.prop(mbs, "free_labels", text = "Free labels")
        if mbs.free_labels:
            box = layout.box()
            box.label(text = "WARNING: with free labels, no checks are made on labels names. See docs for details")
        
        # Set action to be taken for missing nodes/elements
        row = layout.row()
        col = layout.column(align = True)
        col.label(text = "Missing nodes/elements")
        col.prop(mbs, "missing", text = "")

        row = layout.row()
        col = layout.column(align = True)
        col.prop(mbs, "del_log", text = "Delete Log Files on Exit")

        # Clear MBDyn data for scene
        col = layout.column(align = True)
        col.label(text = "Erase MBDyn data in scene")
        col.operator(BLENDYN_OT_clear_data.bl_idname, \
                text = "CLEAR MBDYN DATA")

# -----------------------------------------------------------
# end of BLENDYN_PT_import class


class BLENDYN_PT_animate(BLENDYN_PT_tool_bar, bpy.types.Panel):
    """ Create animation of simulation results - Toolbar Panel """
    bl_idname = "BLENDYN_PT_animate"
    bl_label = "Create animation"

    def draw(self, context):

        # utility renaming
        layout = self.layout
        mbs = context.scene.mbdyn

        # Insert keyframes for animation
        col = layout.column(align = True)
        col.label(text = "Start animating")
        col.operator(BLENDYN_OT_set_motion_paths.bl_idname, \
                text = "Animate scene")
        col.operator(BLENDYN_OT_set_import_freq_auto.bl_idname, \
                text = "Auto set frequency")
        col.prop(mbs, "load_frequency")

        # time_step > 0 only if .log file had been loaded
        col.enabled = bool(mbs.time_step)


        col = layout.column(align = True)

        col.label(text = "Time Range of import")
        col.prop(mbs, "start_time")
        col.prop(mbs, "end_time")


        col = layout.column(align = True)
        col.label(text = "Current Simulation Time")
        col.prop(mbs, "time")
# -----------------------------------------------------------
# end of BLENDYN_PT_animate class


class BLENDYN_PT_simulation(BLENDYN_PT_tool_bar, bpy.types.Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    bl_idname = "BLENDYN_PT_simulation"
    bl_label = "Run simulation"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

     # utility renaming
        layout = self.layout
        obj = context.object
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        ed = mbs.elems

        #Running MBDyn from Blender interface
        # if not os.path.exists(os.path.join(os.path.dirname(mbs.addon_path), 'config.json')):

        row = layout.row()
        row.label(text = 'Path of MBDyn')
        col = layout.column(align = True)
        col.prop(mbs, "install_path", text = "Path")
        col.operator(BLENDYN_OT_set_mbdyn_install_path.bl_idname, \
                text = 'Set Installation Path')
        col.operator(BLENDYN_OT_mbdyn_default_install_path.bl_idname, \
                text = 'Use default MBDyn')
        col.operator(BLENDYN_OT_config_mbdyn_install_path.bl_idname, \
                text = 'Use config MBDyn Path')

        col = layout.column(align = True)
        col.label(text = "Selected input file")
        col.prop(mbs, "input_path", text = '')
        col.operator(BLENDYN_OT_select_mbdyn_input_file.bl_idname, \
                text = 'Select input file')

        col = layout.column(align = True)
        col.label(text = "Output Directory")
        col.prop(mbs, "file_path", text = '')

        col = layout.column(align = True)
        col.label(text = "Output Filename")
        col.prop(mbs, "file_basename", text = '')

        col = layout.column(align = True)
        col.prop(mbs, "overwrite", text = "Overwrite Previous Files")
        col.prop(mbs, "force_text_import", text = "Always load text output")

        col = layout.column(align = True)
        col.label(text = "Command-line options")
        col.prop(mbs, "cmd_options", text = '')

        row = layout.row()
        row.label(text = "Set Environment Variables")

        row = layout.row()
        row.template_list('BLENDYN_UL_env_vars_list', \
                "MBDyn Environment variables list", \
                mbs, "env_vars",\
                mbs, "env_index")

        col = layout.column(align = True)
        col.prop(mbs, "env_variable", text = "Variable")
        col.prop(mbs, "env_value", text = "Value")
        col.operator(BLENDYN_OT_set_env_variable.bl_idname, \
                text = 'Set Variable')
        col.operator(BLENDYN_OT_delete_env_variable.bl_idname, \
                text = 'Delete Variable')

        col = layout.column(align = True)
        col.prop(mbs, "ui_time", text = 'Final Time')

        col = layout.column(align = True)
        col.prop(mbs, "sim_status", text = 'Simulation Status [compl. %]')
        col.operator(BLENDYN_OT_run_mbdyn_simulation.bl_idname, \
                text = 'Run Simulation')

        if HAVE_PSUTIL:
            col.operator(BLENDYN_OT_stop_mbdyn_simulation.bl_idname, \
                    text = 'Stop Simulaton')

# -----------------------------------------------------------
# end of BLENDYN_PT_simulation class


class BLENDYN_PT_eigenanalysis(BLENDYN_PT_tool_bar, bpy.types.Panel):
    """ Visualizes the results of an eigenanalysis - Toolbar Panel """
    bl_idname = "BLENDYN_PT_eigenanalysis"
    bl_label = "Eigenanalysis"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        # utility renaming
        layout = self.layout
        mbs = context.scene.mbdyn

        # Eigenanalysis output visualization (if eigensolution is found in output)
        if mbs.eigensolutions:
            row = layout.row()
            row.label(text = "Eigenanalysis")
            row = layout.row()
            row.prop(mbs, "curr_eigsol")
            col = layout.column(align = True)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "index", slider = False)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "step", slider = False)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "time", slider = False)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "iNVec", slider = False)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "dCoef", slider = False)
            col.enabled = False
            row = layout.row()
            row.operator(BLENDYN_OT_eigen_geometry.bl_idname, \
                    text = "Reference configuration")

            row = layout.row()
            row.separator()

            col = layout.column(align = True)
            col.label(text = "Selected Eigenmode")
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "curr_eigmode", text = "")
            col.enabled = True
            col = layout.column(align = True)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "lambda_damp", slider = False)
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "lambda_freq", slider = False)
            col.enabled = False

            row = layout.row()
            row.separator()

            col = layout.column(align = True)
            col.label(text = "Animation parameters")
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "anim_scale")
            col.prop(mbs.eigensolutions[mbs.curr_eigsol], "anim_frames")
            col.operator(BLENDYN_OT_animate_eigenmode.bl_idname, \
                    text = "Visualize mode")

# -----------------------------------------------------------
# end of BLENDYN_PT_eigenanalysis class


class BLENDYN_PT_active_object(BLENDYN_PT_tool_bar, bpy.types.Panel):
    """ Visualizes MBDyn data relative to the current active object - Toolbar Panel """
    bl_idname = "BLENDYN_PT_active_object"
    bl_label = "Active Object info"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        # utility renaming
        layout = self.layout
        obj = context.object
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        ed = mbs.elems
        rd = mbs.references

        # Display the active object
        if bpy.context.active_object:
            col = layout.column()
            row = col.row()
            row.label(text = "Active Object")
            row = col.row()

            try:
                row.prop(obj, "name")
                node = [node for node in nd if node.blender_object == obj.name]

                if node:
                    # Display MBDyn node info
                    row = col.row()

                    # Select MBDyn node
                    col = layout.column(align=True)
                    col.prop(node[0], "int_label")
                    col = layout.column(align=True)
                    col.prop(node[0], "string_label", text="")
                    col.prop(node[0], "parametrization", text="")
                    col.enabled = False
                    return

                elem = [elem for elem in ed if elem.blender_object == obj.name]
                if elem:
                    # Display MBDyn elements info
                    row = layout.row()
                    row.label(text = "MBDyn's element info:")

                    eval(elem[0].info_draw + "(elem[0], layout)")

                    if elem[0].update_info_operator != 'none' and elem[0].is_imported == True:
                        row = layout.row()
                        row.operator(elem[0].update_info_operator, \
                                text = "Update element info").elem_key = elem[0].name
                    if elem[0].write_operator != 'none' and elem[0].is_imported == True:
                        row = layout.row()
                        row.operator(elem[0].write_operator, \
                                text = "Write element input").elem_key = elem[0].name
                    return

                ref  = [ref for ref in rd if node.blender_object == obj.name]
                if ref:
                    reference_info_draw(ref[0], layout)
                    return
                else:
                    pass

            except AttributeError:
                row.label(text = "No active objects")
                pass
            except TypeError:
                pass
# -----------------------------------------------------------
# end of BLENDYN_PT_active_object class

class BLENDYN_PT_utilities(BLENDYN_PT_tool_bar, bpy.types.Panel):
    """ Simple utilities - Toolbar Panel """
    bl_idname = "BLENDYN_PT_utilities"
    bl_label = "Utilities"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):

        # utility renaming
        layout = self.layout
        col = layout.column()
        col.operator(BLENDYN_OT_outline_collapse.bl_idname, text = "Collapse outline")
        col.operator(BLENDYN_OT_outline_expand.bl_idname, text = "Expand outline")
# -----------------------------------------------------------
# end of BLENDYN_PT_utilities class

class BLENDYN_UL_mbdyn_nodes_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OUTLINER_OB_EMPTY'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_mbdyn_nodes_list class
bpy.utils.register_class(BLENDYN_UL_mbdyn_nodes_list)


class BLENDYN_UL_elements_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'CONSTRAINT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_elements_list class
bpy.utils.register_class(BLENDYN_UL_elements_list)


class BLENDYN_UL_env_vars_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text = item.varname)
        layout.label(text = item.variable)
# -----------------------------------------------------------
# end of BLENDYN_UL_env_vars_list class
bpy.utils.register_class(BLENDYN_UL_env_vars_list)

class BLENDYN_UL_refs_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OUTLINER_DATA_EMPTY'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text = item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.aligment = 'CENTER'
            layout.label(text = '', icon = custom_icon)
# -----------------------------------------------------------
# end of BLENDYN_UL_refs_list
bpy.utils.register_class(BLENDYN_UL_refs_list)

## Panel in scene properties toolbar that shows the MBDyn
#  nodes found in the .log file and links to an operator
#  that imports all of them automatically
class BLENDYN_PT_nodes_scene(bpy.types.Panel):
    """ List of MBDyn nodes: use import all button to add \
            them all to the scene at once """
    bl_label = "MBDyn nodes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        layout = self.layout
        row = layout.row()
        row.template_list('BLENDYN_UL_mbdyn_nodes_list', \
                "MBDyn nodes list", \
                mbs, "nodes",\
                mbs, "nd_index")

        if len(nd):
            item = mbs.nodes[mbs.nd_index]

            box = layout.box()
            col = box.column()
            col.prop(item, "int_label")
            col.prop(item, "string_label")
            col.prop(item, "blender_object")
            col.enabled = False

            box = layout.box()
            col = box.column()
            col.prop(mbs, "node_object")
            col.prop(mbs, "min_node_import")
            col.prop(mbs, "max_node_import")
            col.operator(BLENDYN_OT_node_import_all.bl_idname,\
                    text = "Add nodes to scene")

            box = layout.box()
            col = box.column()
            col.operator(BLENDYN_OT_select_all_nodes.bl_idname, \
                    text = "Select All Nodes")

            box = layout.box()
            col = box.column(align = True)
            col.prop(mbs, "node_scale_slider")
            col.operator(BLENDYN_OT_scale_node.bl_idname, \
                    text = "Scale Selected Node")
            col.operator(BLENDYN_OT_scale_sel_nodes.bl_idname, \
                    text = "Scale All Nodes")

            box = layout.box()
            col = box.column()
            col.operator(BLENDYN_OT_create_vertices_from_nodes.bl_idname,\
                    text = "Create vertex grid from nodes")
            col.prop(mbs, "is_vertshook", text = "Hook vertices to nodes")
# -----------------------------------------------------------
# end of BLENDYN_PT_nodes_scene class


## Panel in scene properties toolbar that shows the MBDyn
#  elements found in the .log file
class BLENDYN_PT_elems_scene(bpy.types.Panel):
    """ List of MBDyn elements: use import button to add \
            them to the scene  """
    bl_label = "MBDyn elements"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mbs = context.scene.mbdyn
        layout = self.layout
        row = layout.row()
        row.template_list("BLENDYN_UL_elements_list", \
                "MBDyn elements", \
                mbs, "elems",\
                mbs, "ed_index")

        if len(mbs.elems):
            item = mbs.elems[mbs.ed_index]

            box = layout.box()
            col = box.column()
            col.prop(item, "int_label")
            col.prop(item, "string_label")
            col.prop(item, "blender_object")
            col.enabled = False

            row = layout.row()
            row.operator(item.import_function, \
                    text="Add element to the scene").int_label = item.int_label


            box = layout.box()
            col = box.column()
            col.label(text = "Selected element type")
            col.prop(mbs, "elem_type_import", text = "")

            box = layout.box()
            col = box.column()
            col.prop(mbs, "min_elem_import")
            col.prop(mbs, "max_elem_import")
            if mbs.elem_type_import in ('shell4', 'membrane4'):
                col.prop(mbs, "mesh_import_mode")
            if mbs.mesh_import_mode == 'SEPARATED_OBJECTS':
                col.operator(BLENDYN_OT_import_elements_by_type.bl_idname, \
                        text="Import elements by type")
            elif mbs.mesh_import_mode == 'SINGLE_MESH':
                col.operator(BLENDYN_OT_import_elements_as_mesh.bl_idname, \
                        text="Import elements by type")
            col.operator(BLENDYN_OT_elements_import_all.bl_idname)

            box = layout.box()
            col = box.column(align = True)
            col.operator(BLENDYN_OT_select_elements_by_type.bl_idname, \
                    text = "Select Elements")

            box = layout.box()
            col = box.column()
            col.prop(mbs, "elem_scale_slider")
            col.operator(BLENDYN_OT_scale_elements_by_type.bl_idname, \
                    text = "Scale Elements")

# -----------------------------------------------------------
# end of BLENDYN_PT_elems_scene class


class BLENDYN_PT_reference_scene(bpy.types.Panel):
    """ List of MBDyn references, found in the .rfm file:
        adds them to the scene as empty axes objects """
    bl_label = "MBDyn References"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mbs = context.scene.mbdyn
        rd = mbs.references
        layout = self.layout

        row = layout.row()
        row.template_list('BLENDYN_UL_refs_list', "MBDyn references list", \
                mbs, "references", mbs, "ref_index")

        try:
            item = mbs.references[mbs.ref_index]

            col = layout.column()
            col.prop(item, "int_label")
            col.prop(item, "string_label")
            col.prop(item, "blender_object")
            col.enabled = False

            col = layout.column()
            col.operator(BLENDYN_OT_references_import_single.bl_idname, \
                    text = "Add reference to the scene").int_label = item.int_label
            col.operator(BLENDYN_OT_references_import_all.bl_idname, \
                   text = "Add all references to the scene")
        except KeyError:
            pass
        except IndexError:
            pass
# -----------------------------------------------------------
# end of BLENDYN_PT_reference_scene class


## Panel in object properties toolbar that helps associate
#  MBDyn nodes to Blender objects
class BLENDYN_PT_obj_select(bpy.types.Panel):
    """ Associate MBDyn node with current object """
    bl_label = "MBDyn nodes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        obj = context.object
        mbs = context.scene.mbdyn
        nd = mbs.nodes

        layout = self.layout
        layout.alignment = 'LEFT'

        row = layout.row()
        row.label(text = "Node #")
        row.label(text = "Node label")
        row.label(text = "Blender Object")
        row.label(text = "")
        row.label(text = "")
        for nd_entry in nd:
            row = layout.row()
            row.label(text = str(nd_entry.int_label))
            row.label(text = nd_entry.string_label)
            if nd_entry.blender_object == obj.name:
                row.label(text = nd_entry.blender_object, icon = 'OBJECT_DATA')
                row.operator(BLENDYN_OT_obj_select_node.bl_idname, \
                        text = "UNASSIGN").ndx = nd_entry.name
            else:
                row.label(text = nd_entry.blender_object)
                row.operator(BLENDYN_OT_obj_select_node.bl_idname, \
                        text = "ASSIGN").ndx = nd_entry.name
                if bpy.data.objects.get(nd_entry.blender_object) == 'none':
                    row.operator(BLENDYN_OT_node_import_single.bl_idname, \
                            text = "ADD").int_label = nd_entry.int_label
# -----------------------------------------------------------
# end of BLENDYN_PT_obj_select class

class BLENDYN_PT_components(bpy.types.Panel):
    """ List of Blendyn components: add/modify them,
        generate armatures and geometry """
    bl_label = "MBDyn components"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mbs = context.scene.mbdyn
        comps = mbs.components
        layout = self.layout
        layout.alignment = 'LEFT'
        col = layout.column()
        col.label(text = "Components:")
        row = col.row()
        row.template_list("BLENDYN_UL_components_list", \
                "MBDyn components", \
                mbs, "components", \
                mbs, "cd_index")
        row = col.row()
        if not mbs.adding_component:
            row.operator(BLENDYN_OT_component_add.bl_idname, \
                    text = "Add New Component")
            row = col.row()
            row.operator(BLENDYN_OT_component_edit.bl_idname, \
                    text = "Edit Selected Component")
            row = col.row()
            row.operator(BLENDYN_OT_component_remove.bl_idname, \
                    text = "Remove Component")
            if len(comps):
                comp = comps[mbs.cd_index]
        else:
            comp = comps[-1]

        if len(comps) and (mbs.adding_component or mbs.editing_component) :
            col = layout.column()
            col.label(text = "Component Elements:")
            row = col.row()
            split = row.split(factor = 0.2)
            col = split.column()
            col.label(text = "#")
            col = split.column()
            split = col.split(factor = .67)
            col = split.column()
            col.label(text = "element")
            col = split.column()
            col.label(text = "subs")
            col = layout.column()
            row = col.row()
            row.template_list("BLENDYN_UL_component_elements_list", \
                "Component elements", \
                comp, "elements", \
                comp, "el_index")
            col.prop(mbs, "comp_selected_elem", text = "Add")
            if mbs.comp_selected_elem[:5] == "modal":
                col = layout.column()
                col.label(text="Modal node:")
                row = col.row()
                row.template_list("BLENDYN_UL_modal_nodes_list", \
                                  "Modal nodes", \
                                  mbs.elems[mbs.comp_selected_elem], "nodes", \
                                  mbs.elems[mbs.comp_selected_elem], "node_index")
                row = col.row()
                row.prop(mbs.elems[mbs.comp_selected_elem], "selected_node", text = "Add:")
                row = col.row()
                split = row.split(factor = 0.5)
                col1 = split.column()
                col1.operator(BLENDYN_OT_element_add_node.bl_idname,
                             text="Add node")
                col2 = split.column()
                col2.operator(BLENDYN_OT_element_remove_node.bl_idname,
                              text="Remove node")
                row = col.row()
                row.operator(BLENDYN_OT_element_add_all_selected_nodes.bl_idname,
                             text = "Add all selected node")
                row.operator(BLENDYN_OT_element_remove_all_nodes.bl_idname,
                             text = "Remove all nodes")

                ## FEM Connection panel
                col = layout.column()
                col.label(text="Modal FEM Connect:")
                row = col.row()
                split = row.split(factor = 0.4)
                col = split.column()
                col.label(text="Name")
                col = split.column()
                split = col.split(factor = 0.5)
                col = split.column()
                col.label(text="Node 1")
                col = split.column()
                col.label(text="Node 2")
                col = layout.column()
                row = col.row()
                row.template_list("BLENDYN_UL_fem_connections_list", \
                                  "Modal FEM connections", \
                                  mbs.elems[mbs.comp_selected_elem], "fem_connects", \
                                  mbs.elems[mbs.comp_selected_elem], "connect_index")
                row = col.row()
                row.operator(BLENDYN_OT_element_add_new_connect.bl_idname,
                             text = "Add new connect")
                row.operator(BLENDYN_OT_element_remove_connect.bl_idname,
                             text = "Remove connect")
                row.operator(BLENDYN_OT_element_remove_all_connects.bl_idname,
                             text = "Remove all connect")


            col = layout.column()
            col.operator(BLENDYN_OT_component_add_elem.bl_idname, \
                    text = "Add Element")
            col.operator(BLENDYN_OT_component_remove_elem.bl_idname, \
                    text = "Remove Element")
    
            col = layout.column()
            col.operator(BLENDYN_OT_component_remove_all_elems.bl_idname, \
                    text = "Remove All Elements")
            col.operator(BLENDYN_OT_component_add_selected_elems.bl_idname, \
                    text = "Add Selected Elements")
            if mbs.adding_component:
                col.prop(comp, "remove_from_etu", text = "Disable elements update")

            col = layout.column()
            col.alignment = 'LEFT' 
            col.prop(comp, "object")
            
            if mbs.adding_component:
                col.operator(BLENDYN_OT_component_add_confirm.bl_idname, \
                    text = "Confirm")
                col.operator(BLENDYN_OT_component_add_cancel.bl_idname, \
                    text = "Cancel")
            elif mbs.editing_component:
                col.operator(BLENDYN_OT_component_edit_confirm.bl_idname, \
                    text = "Confirm")
                col.operator(BLENDYN_OT_component_edit_cancel.bl_idname, \
                    text = "Cancel")
# -----------------------------------------------------------
# end of BLENDYN_PT_components_scene

class BLENDYN_OT_node_import_all(bpy.types.Operator):
    """ Imports all the MBDyn nodes into the Blender scene """
    bl_idname = "blendyn.node_import_all"
    bl_label = "Add MBDyn nodes to scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        added_nodes = 0
        selftag = "BLENDYN_OT_node_import_all::execute(): "

        try:
            ncol = bpy.data.collections['mbdyn.nodes']
            set_active_collection('mbdyn.nodes')
        except KeyError:
            message =  "could not find the 'mbdyn.nodes' collection"
            print(message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}

        wm = bpy.context.window_manager
        Nnodes = len(nd)
        wm.progress_begin(0, Nnodes)
        for node in nd:
            if (mbs.min_node_import <= node.int_label) & (mbs.max_node_import >= node.int_label):

                if not(spawn_node_obj(context, node)):
                    message = "Could not spawn the Blender object assigned to node " \
                              + str(node.int_label) \
                              + ". Object already present?"
                    self.report({'ERROR'}, message)
                    baseLogger.error(selftag + message)
                    return {'CANCELLED'}

                obj = context.active_object
                obj.mbdyn.type = 'node'
                obj.mbdyn.dkey = node.name
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = node.initial_rot
                update_parametrization(obj)
                if node.string_label != "none":
                    obj.name = node.string_label
                else:
                    obj.name = node.name
                node.blender_object = obj.name

                message = "added node " \
                        + str(node.int_label) \
                        + " to scene and associated with object " + obj.name
                added_nodes += 1
                baseLogger.info(selftag + message)
                wm.progress_update(added_nodes)

        set_active_collection('Master Collection')
        if (added_nodes == Nnodes):
            message =  "All MBDyn nodes imported successfully"
            self.report({'INFO'}, message)
            baseLogger.info(selftag + message)
            return {'FINISHED'}
        elif added_nodes == 0:
            message = "No MBDyn nodes imported"
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'CANCELLED'}
        else:
            message = "Not every MBDyn node was imported."
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
# -----------------------------------------------------------
# end of BLENDYN_OT_node_import_all class


class BLENDYN_OT_node_import_single(bpy.types.Operator):
    """ Imports a single MBDyn node, selected by the user in the UI,
        into the Blender scene """
    bl_idname = "blendyn.single_node_import"
    bl_label = "Add selected MBDyn node to scene"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        for node in context.scene.mbdyn.nodes:
            if node.int_label == self.int_label:
                node.blender_object = "none"

    def execute(self, context):
        selftag =  "BLENDYN_OT_node_import_single::execute(): "
        try:
            ncol = bpy.data.collections['mbdyn.nodes']
            set_active_collection('mbdyn.nodes')
        except KeyError:
            message = "could not find the 'mbdyn.nodes' collection"
            print(message)
            baseLogger.error(selftag + message)
            return {'CANCELLED'}

        added_node = False
        for node in context.scene.mbdyn.nodes:
            if node.int_label == self.int_label:
                if not(spawn_node_obj(context, node)):
                    message = "Could not spawn the Blender object assigned to node {}"\
                              .format(node.int_label)
                    self.report({'ERROR'}, message)
                    baseLogger.error(selftag + message)
                    return {'CANCELLED'}
                obj = context.active_object
                obj.mbdyn.type = 'node'
                obj.mbdyn.dkey = node.name
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = node.initial_rot
                update_parametrization(obj)
                if obj.mbdyn.string_label != "none":
                    obj.name = node.string_label
                else:
                    obj.name = node.name
                node.blender_object = obj.name
                message = "added node " + str(node.int_label)\
                          + " to scene and associated it with object " \
                          + obj.name
                self.report({'INFO'}, message)
                baseLogger.info(selftag + message)
                added_node = True
        if added_node:
            message = "node " + str(node.int_label)\
                      + " imported to scene "
            self.report({'INFO'}, message)
            baseLogger.info(selftag + message)
            return {'FINISHED'}
        else:
            message =  "Cannot import MBDyn node " + node.string_label
            self.report({'WARNING'}, message)
            baseLogger.warning(selftag + message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_node_import_single class


class BLENDYN_OT_references_import_all(bpy.types.Operator):
    """ Imports all the MBDyn references into the Blender scene """
    bl_idname = "blendyn.references_import_all"
    bl_label = "Add MBDyn references to scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        rd = mbs.references
        selftag = "BLENDYN_OT_references_import_all::execute(): "

        for ref in rd:
            retval = spawn_reference_frame(ref, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "Found the Object " + ref.blender_object \
                          + " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_references_import_all class


class BLENDYN_OT_references_import_single(bpy.types.Operator):
    """ Import a single reference frame, selected by
        the user in the UI, into the Blender scene """
    bl_idname = "blendyn.references_import_single"
    bl_label = "Add MBDyn reference to scene"

    int_label: IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn
        rd = mbs.references

        for ref in rd:
            if ref.int_label == self.int_label:
                retval = spawn_reference_frame(ref, context)
                if retval == {'OBJECT_EXISTS'}:
                    message = "BLENDYN_OT_references_import_single::execute(): "\
                              + "Found the Object " + ref.blender_object \
                              + " remove or rename it to re-import the element!"
                    self.report({'WARNING'}, message)
                    logging.warning(message)
                    return {'CANCELLED'}
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_references_import_single class


class BLENDYN_OT_select_all_nodes(bpy.types.Operator):
    """ Selects all the objects associated to  MBDyn nodes"""
    bl_idname = "blendyn.select_all_nodes"
    bl_label = "Select all MBDyn Node Objects"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        bpy.ops.object.select_all(action = 'DESELECT')
        for var in nd.keys():
                try:
                    obj = bpy.data.objects[var]
                    obj.select_set(state = True)
                except KeyError:
                    message = "BLENDYN_OT_select_all_nodes::execute() "\
                            + "Could not find object for node "\
                            + var
                    self.report({'WARNING'}, message)
                    logging.warning(message)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_select_all_nodes class


class BLENDYN_OT_select_elements_by_type(bpy.types.Operator):
    """ Select all the objects associated to MBDyn elements
        of a specified type """
    bl_idname = "blendyn.select_elements_by_type"
    bl_label = "Select objects related to selected element type"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        bpy.ops.object.select_all(action = 'DESELECT')
        for var in ed.keys():
            if mbs.elem_type_import in var:
                try:
                    obj = bpy.data.objects[var]
                    obj.select_set(state = True)
                except KeyError:
                    message = "BLENDYN_OT_select_elements_by_type::execute() "\
                            + "Could not find object for element "\
                            + var
                    self.report({'WARNING'}, message)
                    logging.warning(message)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_select_elements_by_type class


class BLENDYN_OT_scale_node(bpy.types.Operator):
    """ Scales the selected object, associated with
        an MBDyn node """
    bl_idname = "blendyn.scale_node"
    bl_label = "Scale active node"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        s = mbs.node_scale_slider
        actobj = bpy.context.active_object
        for node in nd:
            if node.blender_object == actobj.name:
                actobj.scale = Vector((s, s, s))
                # bpy.ops.object.transform_apply(location = False, \
                #        rotation = False, scale = True)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_scale_node class


class BLENDYN_OT_scale_sel_nodes(bpy.types.Operator):
    """ Scales the selected objects, associated with
        MBDyn nodes """
    bl_idname = "blendyn.scale_sel_nodes"
    bl_label = "Scale all sected nodes"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        s = mbs.node_scale_slider
        for node in nd:
            scaleOBJ = bpy.data.objects[node.blender_object]
            bpy.context.view_layer.objects.active = scaleOBJ
            scaleOBJ.scale = Vector((s, s, s))
            # bpy.ops.object.transform_apply(location = False, \
            #        rotation = False, scale = True)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_scale_sel_nodes class


class BLENDYN_OT_scale_elements_by_type(bpy.types.Operator):
    """ Scales the objects associated with MBDyn elements of
        the selected type """
    bl_idname = "blendyn.scale_elements_by_type"
    bl_label = "Scale all elements of selected type"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        s = mbs.elem_scale_slider
        for elem in ed:
            if elem.type == mbs.elem_type_import:
                scaleOBJ = bpy.data.objects[elem.blender_object]
                bpy.context.view_layer.objects.active = scaleOBJ
                scaleOBJ.scale = Vector((s, s, s))
             #   bpy.ops.object.transform_apply(location = False, \
             #           rotation = False, scale = True)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_scale_elements_by_type class

class BLENDYN_OT_import_elements_by_type(bpy.types.Operator):
    """ Imports the MBDyn elements of the selected type in the blender scene """
    bl_idname = "blendyn.import_elements_by_type"
    bl_label = "Add all elements of selected type to scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        for elem in ed:
            if (elem.type == mbs.elem_type_import) \
                    and (elem.int_label >= mbs.min_elem_import) \
                    and (elem.int_label <= mbs.max_elem_import):
                try:
                    # eval("spawn_" + elem.type + "_element(elem, context)")
                    eval("bpy.ops." + elem.import_function + "(int_label = " + \
                            str(elem.int_label) + ")")
                except NameError:
                        message = "BLENDYN_OT_import_elements_by_type::execute(): " \
                                  + "Could not find the import function for element of type " \
                                  + elem.type + ". Element " + elem.name + " not imported."
                        self.report({'ERROR'}, message)
                        baseLogger.error(message)
                        return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of BLENDYN_OT_import_elements_by_type class


class BLENDYN_OT_elements_import_all(bpy.types.Operator):
    """ Imports all the supported MBDyn elements into the Blender scene """
    bl_idname = "blendyn.elements_import_all"
    bl_label = "Add all the elements to the scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems

        Nelems = len(ed)
        wm = bpy.context.window_manager
        wm.progress_begin(0, Nelems)
        added_elems = 0
        missing_elems = 0
        for elem in ed:
            if (elem.int_label >= mbs.min_elem_import) \
                    and (elem.int_label <= mbs.max_elem_import):
                try:
                    eval("bpy.ops." + elem.import_function \
                            + "(int_label = " + str(elem.int_label) + ")")
                    added_elems += 1
                except NameError:
                        message = "BLENDYN_OT_elements_import_all::execute(): " \
                                  + "Could not find the import function for element of type " \
                                  + elem.type + ". Element " + elem.name + " not imported."
                        baseLogger.warning(message)
                        missing_elems += 1
                        pass
                wm.progress_update(added_elems + missing_elems)
        if missing_elems:
            message = "BLENDYN_OT_elements_import_all::execute(): " \
                      + "Some elements were not imported. See log file for details"
            baseLogger.warning(message)
            self.report({'WARNING'}, message)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of BLENDYN_OT_elements_import_all class


class BLENDYN_OT_obj_select_node(bpy.types.Operator):
    """ Selects the objects associated with an MBDyn node """
    bl_idname = "blendyn.obj_select_node"
    bl_label = "MBDyn Node Select Button"
    ndx: bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ret_val = ''
        node = context.scene.mbdyn.nodes[self.ndx]
        if node.blender_object == context.object.name:
            node.blender_object = 'none'
            context.object.mbdyn.type = 'none'
            context.object.mbdyn.dkey = 'none'
            ret_val = {'UNASSIGNED'}
        else:
            node.blender_object = context.object.name
            ret_val = assign_parametrization(context.object, node)
            if ret_val == {'FINISHED'}:
                obj = context.object
                obj.mbdyn.type = 'node'
                obj.mbdyn.dkey = node.name

        if ret_val == {'ROT_NOT_SUPPORTED'}:
            message = "BLENDYN_OT_obj_select_node::execute(): "\
                    + "Rotation parametrization not supported, node "\
                    + str(node.int_label)
            self.report({'ERROR'}, message)
            baseLogger.error(message)
            print(message)
            return {'CANCELLED'}
        elif ret_val == {'UNASSIGNED'}:
            # DEBUG message to console and log file
            message = "BLENDYN_OT_obj_select_node::execute(): "\
                    + "Node " + str(node.int_label) + " association with "\
                    + "Object " + context.object.name + " removed."
            baseLogger.info(message)
            print(message)
            return {'FINISHED'}
        else: # ret_val == {'FINISHED'}
            message = "BLENDYN_OT_obj_select_node::execute(): Object "\
                    + context.object.name \
                    + " MBDyn node association updated to node " \
                    + str(node.int_label)
            baseLogger.info(message)
            print(message)
            return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_obj_select_node class


class BLENDYN_OT_create_vertices_from_nodes(bpy.types.Operator):
    """ Creates a mesh in which the vertices are hooked to
        the motion of MBDyn nodes """
    bl_idname = "blendyn.create_vertices_from_nodes"
    bl_label = "Create vertices from nodes"

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        me = bpy.data.meshes.new("VertsFromNodes")
        vidx = 0
        mbs = bpy.context.scene.mbdyn
        nds = mbs.nodes

        obj_list = bpy.context.selected_objects
        sel_obj = []
        for obj in obj_list:
            for nd in nds:
                if nd.blender_object == obj.name:
                    me.vertices.add(1)
                    me.vertices[vidx].co = obj.location
                    vidx = vidx + 1
                    obj.select_set(state = False)
                    sel_obj.append(obj.name)

        if vidx:

            if len(bpy.context.selected_objects):
                # deselect all objects
                bpy.ops.object.select_all()

            vert_obj = bpy.data.objects.new("VertsFromNodes", me)
            bpy.context.scene.collection.objects.link(vert_obj)

            vert_obj.select_set(state = True)
            bpy.context.view_layer.objects.active = vert_obj
            dg = bpy.context.evaluated_depsgraph_get()
            dg.update()

            if mbs.is_vertshook:
                # We want to set an hook to all newly created vertices with
                # the corresponding node

                # get the mesh, create individual vertex groups and deselect
                # all vertices
                me = vert_obj.data
                vidx = 0
                for v in me.vertices:
                    vert_obj.vertex_groups.new(name = 'v' + sel_obj[vidx])
                    verts = []
                    verts.append(v.index)
                    vert_obj.vertex_groups['v' + sel_obj[vidx]].add(verts, 1.0, 'ADD')
                    v.select = False
                    vidx = vidx + 1

                # Add the modifiers in edit mode
                bpy.ops.object.mode_set(mode='EDIT')
                vidx = 0
                for obj in sel_obj:
                    bpy.ops.object.modifier_add(type='HOOK')
                    hname = 'hm' + obj
                    vert_obj.modifiers['Hook'].name = hname
                    vert_obj.modifiers[hname].object = bpy.data.objects[obj]
                    vert_obj.modifiers[hname].vertex_group = 'v' + obj
                    vidx = vidx + 1
                    bpy.ops.object.hook_reset(modifier=hname)

                # exit edit mode
                bpy.ops.object.mode_set(mode='OBJECT')

                # deselect all
                bpy.ops.object.select_all()

        else:
            message = "BLENDYN_OT_create_vertices_from_nodes::execute(): " \
                      + "No MBDyn nodes associated with selected objects."
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return{'CANCELLED'}

        return{'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_create_vertices_from_nodes class


class BLENDYN_OT_delete_override(bpy.types.Operator):
    """ Overrides the delete function of Blender Objects to remove
        the related elements in MBDyn dictionaries """
    bl_idname = "object.delete"
    bl_label = "Delete"
    use_global: BoolProperty()

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None)

    @classmethod
    def remove_from_dict(self, obj, context):
        try:
            dictitem = get_dict_item(context, obj)
            dictitem.blender_object = 'none'
            dictitem.is_imported = False
        except AttributeError:
            pass

        if obj.mbdyn.type == 'element':
            etu = context.scene.mbdyn.elems_to_update
            for idx, ude in enumerate(etu):
                if obj.mbdyn.dkey == ude.dkey:
                    etu.remove(idx)
                break

    def execute(self, context):
        for obj in context.selected_objects:
            if len(context.scene.mbdyn.nodes):
                try:
                    self.remove_from_dict(obj, context)
                except KeyError:
                    pass
            bpy.data.objects.remove(obj, do_unlink = True)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
# -----------------------------------------------------------
# end of BLENDYN_OT_delete_override class
