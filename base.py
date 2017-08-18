# --------------------------------------------------------------------------
# Blendyn -- file base.py
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

# TODO: check for unnecessary stuff

import os

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

import ntpath, os, csv, math, time, shutil
import numpy as np

from collections import namedtuple
import subprocess
from multiprocessing import Process
import json

import pdb

try:
    from netCDF4 import Dataset
except ImportError:
    print("Blendyn: could not find the netCDF4 module. NetCDF import "\
        + "will be disabled.")

HAVE_PLOT = False

try:
    import pygal
    from .plotlib import *
    HAVE_PLOT = True
except ImportError:
    print("Blendyn: could not find the pygal module. Plotting  "\
        + "will be disabled.")

HAVE_PSUTIL = False
try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    print("Blendyn: could not find the psutil module. Stopping "\
            + "MBDyn from the Blender UI will be disabled.")

from .baselib import *
from .elements import *
from .eigenlib import *
from .rfmlib import *
from .logwatcher import *
from .liveanim import *
from .nodelib import set_obj_locrot_mov

from .driverlib import *
from .outputlib import *

import pdb

## Nodes Dictionary: contains nodes informations
class MBDynNodesDictionary(bpy.types.PropertyGroup):
    int_label = IntProperty(
            name = "node integer label",
            description = "Node integer label",
            )

    string_label = StringProperty(
            name = "node string label",
            description = "Node string label",
            default = "none"
            )

    blender_object = StringProperty(
            name = "blender object label",
            description = "Blender object",
            default = "none"
            )

    initial_pos = FloatVectorProperty(
            name = "node initial position",
            description = "Initial position",
            size = 3,
            precision = 6
            )

    initial_rot = FloatVectorProperty(
            name = "node initial orientation",
            description = "Node initial orientation (quaternion)",
            size = 4,
            precision = 6
            )

    parametrization = EnumProperty(
            items = [("EULER123", "euler123", "euler123", '', 1),\
                     ("EULER131", "euler313", "euler313", '', 2),\
                     ("EULER321", "euler321", "euler321", '', 3),\
                     ("PHI", "phi", "phi", '', 4),\
                     ("MATRIX", "mat", "mat", '', 5)],
            name = "rotation parametrization",
            default = "EULER123"
            )

    is_imported = BoolProperty(
        name = "Is imported flag",
        description = "Flag set to true at the end of the import process"
        )
# -----------------------------------------------------------
# end of MBDynNodesDictionary class
bpy.utils.register_class(MBDynNodesDictionary)

class MBDynRefsDictionary(bpy.types.PropertyGroup):
    int_label = IntProperty(
            name = "reference integer label",
            description = "Reference integer label"
            )

    string_label = StringProperty(
            name = "reference string label",
            description = "Reference string label",
            default = "none"
            )

    blender_object = StringProperty(
            name = "blender object label",
            description = "Blender Object",
            default = "none"
            )

    is_imported = BoolProperty(
            name = "Is imported flag",
            description = "Flag set to true at the end of the import process"
            )
    
    pos = FloatVectorProperty(
            name = "position",
            description = "Reference Position",
            size = 3,
            precision = 6
            )

    rot = FloatVectorProperty(
            name = "orientation",
            description = "Reference Orientation",
            size = 4,
            precision = 6
            )

    vel = FloatVectorProperty(
            name = "velocity",
            description = "Reference Velocity",
            size = 3,
            precision = 6
            )

    angvel = FloatVectorProperty(
            name = "angular velocity",
            description = "Reference Angular Velocity",
            size = 3,
            precision = 6
            )

# -----------------------------------------------------------
# end of MBDynRefsDictionary class
bpy.utils.register_class(MBDynRefsDictionary)

## Time PropertyGroup for animation
class MBDynTime(bpy.types.PropertyGroup):
    time = FloatProperty(
            name = "simulation time",
            description = "simulation time of animation frame"
            )
bpy.utils.register_class(MBDynTime)
# -----------------------------------------------------------
# end of MBDynTime class

## PropertyGroup of Render Variables
class MBDynRenderVarsDictionary(bpy.types.PropertyGroup):
    variable = StringProperty(
        name = "Render Variables",
        description = 'Variables to be set'
    )
    value = StringProperty(
        name = "Values of Render Variables",
        description = "Values of variables to be set"
    )
    components = BoolVectorProperty(
        name = "Components of the Variable",
        size = 9
    )
bpy.utils.register_class(MBDynRenderVarsDictionary)
# -----------------------------------------------------------
# end of MBDynRenderVarsDictionary class

class MBDynDisplayVarsDictionary(bpy.types.PropertyGroup):
	name = StringProperty(
		name = 'Group of Display Variables',
		description = 'Janga Reddy'
	)

	group = CollectionProperty(
		name = 'Actual collection group',
		type = MBDynRenderVarsDictionary
	)
bpy.utils.register_class(MBDynDisplayVarsDictionary)

## PropertyGroup of Environment Variables
class MBDynEnvVarsDictionary(bpy.types.PropertyGroup):
    variable = StringProperty(
            name = "Environment variables",
            description = 'Variables to be set'
            )
    value = StringProperty(
            name = "Values of Environment variables",
            description = "Values of variables to be set"
            )
bpy.utils.register_class(MBDynEnvVarsDictionary)
# -----------------------------------------------------------
# end of MBDynEnvVarsDictionary class

## PropertyGroup of MBDyn plottable variables
class MBDynPlotVars(bpy.types.PropertyGroup):
    name = StringProperty(
            name = "plottable variable"
            )
bpy.utils.register_class(MBDynPlotVars)

## Set scene properties
class MBDynSettingsScene(bpy.types.PropertyGroup):

    # Base path of the module
    addon_path = StringProperty(
            name = "Addon path",
            description = "Base path of addon files",
            default = os.path.dirname(__file__)
            )

    # Boolean: is the .mov (or .nc) file loaded properly?
    is_loaded = BoolProperty(
            name = "MBDyn files loaded",
            description = "True if MBDyn files are loaded correctly"
            )

    # MBDyn's imported files path
    file_path = StringProperty(
            name = "MBDyn file path",
            description = "Path of MBDyn's imported files",
            default = "",
            subtype = 'DIR_PATH'
            )

    # Base name of MBDyn's imported files
    file_basename = StringProperty(
            name = "MBDyn base file name",
            description = "Base file name of MBDyn's imported files",
            default = "not yet loaded"
            )

    # Use text output even when NetCDF is available?
    # This property is used when a simulation is run from Blender
    force_text_import = BoolProperty(
            name = "Always use text output",
            description = "Use text output even when NetCDF output is available",
            default = False
            )

    # Path of MBDyn input file (to run simulation from Blender)
    input_path = StringProperty(
            name = "Input File Path",
            description = "Path of MBDyn input files",
            default = "not yet selected"
        )

    # MBDyn input file (to run simulation from Blender)
    input_basename = StringProperty(
            name = "Input File basename",
            description = "Base name of Input File",
            default = "not yet selected"
        )

    # String representing path of MBDyn Installation
    install_path = StringProperty(
            name = "Installation path of MBDyn",
            description = "Installation path of MBDyn",
            subtype = 'DIR_PATH',
            default = 'not yet set'
            )

    # Integer representing the current animation number
    sim_num = IntProperty(
            name = "Number of Simulation",
            default = 0
            )

    final_time = FloatProperty(
            name = "Previous State of Simulation",
            default = 0.0
        )

    ui_time = FloatProperty(
        name = "Final time from user",
        default = 0.0
        )

    mbdyn_running = BoolProperty(
            name = 'MBDyn running',
            default = False
        )

    sim_status = IntProperty(
            name = "Progress of Simulation",
            default = 0
            )

    # Command-line options to be specified in MBDyn simulation
    cmd_options = StringProperty(
            name = "Command-line Options",
            default = ''
            )
    # Boolean representing whether user wants to overwrite existing output files
    overwrite = BoolProperty(
            name = "Overwrite Property",
            description = "True if the user wants to overwrite the existing output files",
            default = False
            )

    del_log = BoolProperty(
            name = "Log property",
            description = "True if the user wants to delete log files on exit",
            default = False
            )

    render_nc_vars = EnumProperty(
        items = get_render_vars,
        name = 'Text overlay variables',
    )

    render_var_name = StringProperty(
        name = 'Name of variable',
        default = ''
    )

    render_vars = CollectionProperty(
        name = "MBDyn render variables collection",
        type = MBDynRenderVarsDictionary
    )

    display_vars_group = CollectionProperty(
        name = "MBDyn Display variables group collection",
        type = MBDynDisplayVarsDictionary
    )

    display_enum_group = EnumProperty(
        items = get_display_group,
        name = 'Display Enum Group'
    )

    group_name = StringProperty(
        name = "Name of Display Variables Group"
    )

    plot_group = BoolProperty(
        name = "Plot List of variables as group",
        default = False
        )

    # Collection of Environment variables and corresponding values
    env_vars = CollectionProperty(
            name = "MBDyn environment variables collection",
            type = MBDynEnvVarsDictionary
        )

    # Environment Variables index, holds the index for displaying the Envrionment variables in a list
    env_index = IntProperty(
            name = "MBDyn Environment variables collection index",
            default = 0
        )

    render_index = IntProperty(
        name = "MBDyn Render Variables collection index",
        default = 0
    )

    # Name of the Environment Variable
    env_variable = StringProperty(
            name = "MBDyn environment variables",
            description = "Environment variables used in MBDyn simulation"
            )

    # Value associated with the Environment Variable
    env_value = StringProperty(
            name = "Values of MBDyn environment values",
            description = "Values of the environment variables used in MBDyn simulation"
        )

    # Number of rows (output time steps * number of nodes) in MBDyn's .mov file
    num_rows = IntProperty(
            name = "MBDyn .mov file number of rows",
            description = "Total number of rows in MBDyn .mov file, corresponding (total time steps * number of nodes)"
            )

    # Load frequency: if different than 1, the .mov file is read every N time steps
    load_frequency = FloatProperty(
            name = "frequency",
            description = "If this value is X, different than 1, then the MBDyn output is loaded every X time steps",
            min = 1.0,
            default = 1.0
            )

    #Start time
    start_time = FloatProperty(
        name = "Start Time",
        description = "If this value is X, different than 0, the import starts at X seconds",
        min = 0.0,
        default = 0.0
        )

    end_time = FloatProperty(
        name = "End Time",
        description = "If this value is X, different than total simulation time, the import stops at X seconds",
        min = 0.0
        )

    time_step = FloatProperty(
        name = "Time Step",
        description = "Simulation time step"
        )

    # Reference dictionary -- holds the associations between MBDyn references and blender
    # objects
    references = CollectionProperty(
            name = "MBDyn references",
            type = MBDynRefsDictionary
            )

    # Reference dictionary index -- holds the index for displaying the Reference
    # Dictionary in a UI List
    ref_index = IntProperty(
            name = "References collection index",
            default = 0
            )

    disabled_output = StringProperty(
            name = "Nodes for which Output is disabled",
            default = ''
    )

    drivers = CollectionProperty(
        name = "MBDyn Drivers",
        type = MBDynFileDriversDictionary
        )

    dr_index = IntProperty(
        name = 'Index of driver',
        default = 0
        )

    output_elems = CollectionProperty(
        name = "MBDyn Output Elements",
        type = MBDynOutputElemsDictionary
        )

    # Nodes dictionary -- holds the association between MBDyn nodes and blender objects
    nodes = CollectionProperty(
            name = "MBDyn nodes",
            type = MBDynNodesDictionary
            )

    # Nodes dictionary index -- holds the index for displaying the Nodes Dictionary in a UI List
    nd_index = IntProperty(
            name = "MBDyn nodes collection index",
            default = 0
            )

    # Default object representing a node, when imported automatically
    node_object = EnumProperty(
            items = [("ARROWS", "Arrows", "Empty - arrows", 'OUTLINER_OB_EMPTY', 1),\
                     ("AXES", "Axes", "Empty - axes", 'EMPTY_DATA', 2),\
                     ("CUBE", "Cube", "", 'MESH_CUBE', 3),\
                     ("UVSPHERE", "UV Sphere", "", 'MESH_UVSPHERE', 4),\
                     ("NSPHERE", "Nurbs Sphere", "", 'SURFACE_NSPHERE', 5),\
                     ("CONE", "Cone", "", 'MESH_CONE', 6)],
            name = "Import nodes as",
            default = "ARROWS"
            )

    missing = EnumProperty(
            items = [("DO NOTHING", "Do Nothing","","" ,1),\
                     ("HIDE", "Hide", "","" ,2),\
                     ("DELETE", "Delete", "", "", 3)],
            name = "Handling of missing nodes/elements",
            default = "HIDE"
            )

    # Behavior for importing shells and beams: get a single mesh or separate mesh objects?
    mesh_import_mode = EnumProperty(
            items = [("SEPARATED OBJECTS", "Separated mesh objects", "", 'UNLINKED', 1),\
                     ("SINGLE MESH", "Joined in single mesh", "", 'LINKED', 2)],
            name = "Mesh objects",
            default = "SEPARATED OBJECTS"
            )

    # Elements dictionary -- holds the collection of the elements found in the .log file
    elems = CollectionProperty(
            name = "MBDyn elements collection",
            type = MBDynElemsDictionary
            )

    # Elements to be updated -- holds the keys to elements that need to update their configuration
    #                           when the scene changes
    elems_to_update = CollectionProperty(
            type = MBDynElemToBeUpdated,
            name = "Elements that require update",
            description = "Collection of indexes of the elements that need to be updated when \
                            the scene is changed"
        )

    # Current Simulation Time
    simtime = CollectionProperty(
            name = "MBDyn simulation time",
            type = MBDynTime
            )

    # Current simulation time
    time = FloatProperty(
            name = "time: ",
            description = "Current MBDyn simulation time",
            default = 0.0
            )

    # Elements dictionary index -- holds the index for displaying the Elements Dictionary in a
    # UI List
    ed_index = IntProperty(
            name = "MBDyn elements collection index",
            default = 0
            )

    # MBDyn's node count
    num_nodes = IntProperty(
            name = "MBDyn nodes number",
            description = "MBDyn node count"
            )

    # MBDyn's time steps count
    num_timesteps = IntProperty(
            name = "MBDyn time steps",
            description = "MBDyn time steps count"
            )

    # Flag that indicates if we are to use NETCDF results format
    use_netcdf = BoolProperty(
            name = "Use netCDF",
            description = "Import results in netCDF format",
            default = False
            )

    # Flag that indicates if the .mov (or .nc) file is loaded correctly and the
    # nodes dictionary is ready, used to indicate that all is ready for the object's
    # to be animated
    is_ready = BoolProperty(
            name = "ready to animate",
            description = "True if .mov (or .nc) file and nodes dictionary loaded correctly",
            )

    # If we want to hook vertices in creating mesh from nodes
    is_vertshook = BoolProperty(
            name = "Hook vertices",
            description = "Hook directly the vertices to the nodes in creating a mesh object?",
            default = False
            )

    # Lower limit of range import for nodes
    min_node_import = IntProperty(
            name = "first node to import",
            description = "Lower limit of integer labels for range import for nodes",
            default = 0
            )

    # Higher limit of range import for nodes
    max_node_import = IntProperty(
            name = "last node to import",
            description = "Higher limit of integer labels for range import for nodes",
            default = 0
            )

    node_scale_slider = FloatProperty(
            name = "Value of Scaling",
            default = 1.0
    )

    # Type filter for elements import
    elem_type_import = EnumProperty(
            items  = get_elems_types,
            name = "Elements to import",
            )

    elem_scale_slider = FloatProperty(
            name = 'Value of scaling',
            default = 1.0
    )

    elem_type_scale = EnumProperty(
            items = get_elems_types,
            name = "Elements to scale",
    )
    # Lower limit of range import for elemens
    min_elem_import = IntProperty(
            name = "first element to import",
            description = "Lower limit of integer labels for range import for elements",
            default = 0
            )

    # Higher limit of range import for elements
    max_elem_import = IntProperty(
            name = "last element to import",
            description = "Higher limit of integer labels for range import for elements",
            default = 2**31 - 1
            )
    # True if output contains at least one eigensolution
    eigensolutions = CollectionProperty(
            name = "Eigensolutions",
            description = "Parameters of the eigensolutions found in the MBDyn output",
            type = MBDynEigenanalysisProps
            )

    curr_eigsol = IntProperty(
            name = "current eigensolution",
            description = "Index of the currently selected eigensolution",
            default = 0,
            update = update_curr_eigsol
            )

    pause_live = BoolProperty(
        name = "Pause MBDyn Live Simulation",
        default = True
        )

    live_keyframes = BoolProperty(
        name = "Set Keyframes during live simulation",
        default = False
        )

    # Live Animation
    host_receiver = StringProperty(
        name = "Host Name of Receiver",
        description = "Host Name of Receiver Stream",
        default = "127.0.0.1"
    )

    port_receiver = IntProperty(
        name = "Port Receiver",
        description = "Port Address of MBDyn Stream",
        default = 9011
    )

    host_sender = StringProperty(
        name = "Host Name of Sender",
        description = "Host Name of Sender Stream",
        default = "127.0.0.1"
    )

    port_sender = IntProperty(
        name = "Port Sender",
        description = "",
        default = 9012
    )

    plot_vars = CollectionProperty(
            name = "MBDyn variables available for plotting",
            type = MBDynPlotVars
            )

    plot_var_index = IntProperty(
            name = "variable index",
            description = "index of the current variable to be plotted",
            default = 0
            )
    plot_comps = BoolVectorProperty(
        name = "components",
        description = "Components of property to plot",
        default = [True for i in range(9)],
        size = 9
        )

    if HAVE_PLOT:

        plot_sxy_varX = StringProperty(
                name = "Cross-spectrum X variable",
                description = "variable to be used as input in cross-spectrum",
                default = "none"
                )

        plot_sxy_varY = StringProperty(
                name = "Cross-spectrum Y variable",
                description = "variable to be used as output in cross-spectrum",
                default = "none"
                )

        plot_frequency = IntProperty(
                name = "frequency",
                description = "Frequency in plotting",
                default = 1
                )

        plot_type = EnumProperty(
                items = [("TIME HISTORY", "Time history", "Time history", '', 1),\
                        ("AUTOSPECTRUM", "Autospectrum", "Autospectrum", '', 2)], \
                name = "plot type",
                default = "TIME HISTORY"
                )

        fft_remove_mean = BoolProperty(
                name = "Subtract mean",
                description = "Subtract the mean value before calculating the FFT",
                default = False
                )

        plot_xrange_min = FloatProperty(
                name = "minimum X value",
                description = "Minimum value for abscissa",
                default = 0.0
                )

        plot_xrange_max = FloatProperty(
                name = "maximum X value",
                description = "Maximum value for abscissa",
                default = 0.0
                )

bpy.utils.register_class(MBDynSettingsScene)
# -----------------------------------------------------------
# end of MBDynSettingsScene class

## MBDynSettings for Blender Object
class MBDynSettingsObject(bpy.types.PropertyGroup):
    """ Properties of the current Blender Object related to MBDyn """
    # Boolean: has the current object being assigned an MBDyn's entity?
    is_assigned = BoolProperty(
            name = "MBDyn entity assigned",
            description = "True if the object has been assigned an MBDyn node",
            )

    # Type of MBDyn entity
    type = StringProperty(
            name = "MBDyn entity type",
            description = "Type of MBDyn entity associated with object",
            default = 'none'
            )

    # Dictionary key
    dkey = StringProperty(
            name = "MBDyn dictionary key",
            description = "Key of the entry of the MBDyn dictionary relative to the object",
            default = 'none'
            )

    # Integer representing MBDyn's node label assigned to the object
    int_label = IntProperty(
            name = "MBDyn node",
            description = "Integer label of MBDyn's node assigned to the object",
            update = update_label
            )

    # String representing MBDyn's node string label assigned to the object.
    # Non-"not assigned" only if a .lab file with correct syntax is found
    string_label = StringProperty(
            name = "MBDyn's node or joint string label",
            description = "String label of MBDyn's node assigned to the object (if present)",
            default = "not assigned"
            )

    # Rotation parametrization of node
    parametrization = EnumProperty(
            items = [("EULER123", "euler123", "euler123", '', 1),\
                     ("EULER131", "euler313", "euler313", '', 2),\
                     ("EULER321", "euler321", "euler321", '', 3),\
                     ("PHI", "phi", "phi", '', 4),\
                     ("MATRIX", "mat", "mat", '', 5)],
            name = "rotation parametrization",
            default = "EULER123"
            )

    # Specific for plotting
    if HAVE_PLOT:
        plot_var = EnumProperty(
                name = "Variables",
                items = get_plot_vars,
                description = ""
                )

        plot_comps = BoolVectorProperty(
                name = "components",
                description = "Components of property to plot",
                default = [True for i in range(9)],
                size = 9
                )
        
        plot_type = EnumProperty(
            items = [("TIME HISTORY", "Time history", "Time history", '', 1),\
                     ("AUTOSPECTRUM", "Autospectrum", "Autospectrum", '', 2)],
            name = "plot type",
            default = "TIME HISTORY"
            )

        fft_remove_mean = BoolProperty(
                name = "Subtract mean",
                description = "Subtract the mean value before calculating the FFT",
                default = False
                )
        plot_xrange_min = FloatProperty(
                name = "minimum X value",
                description = "Minimum value for abscissa",
                default = 0.0
                )

        plot_xrange_max = FloatProperty(
                name = "maximum X value",
                description = "Maximum value for abscissa",
                default = 0.0
                )

bpy.utils.register_class(MBDynSettingsObject)
# -----------------------------------------------------------
# end of MBDynSettingsObject class

bpy.types.Scene.mbdyn = PointerProperty(type=MBDynSettingsScene)
bpy.types.Object.mbdyn = PointerProperty(type=MBDynSettingsObject)

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
    try:
        mbs = scene.mbdyn
        if mbs.use_netcdf:
            print('This might be working')
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, "r", format="NETCDF3")
            string = [ '{0} : {1}'.format(var.variable, \
            parse_render_string(netcdf_helper(nc, scene, var.value), var.components)) \
            for var in mbs.render_vars ]
            string = '\n'.join(string)
            if len(mbs.render_vars):
                bpy.data.scenes['Scene'].render.stamp_note_text = string
    except IndexError:
        pass
bpy.app.handlers.frame_change_pre.append(render_variables)

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
    os.rename(logFile, newLog)

    bpy.data.texts[os.path.basename(logFile)].name = os.path.basename(newLog)

    log_messages(mbs, baseLogger, True)

bpy.app.handlers.save_post.append(rename_log)

class MBDynStandardImport(bpy.types.Operator):
    """ Standard Import Process """
    bl_idname = "animate.standard_import"
    bl_label = "MBDyn Standard Import"

    def execute(self, context):
        try:
            bpy.ops.animate.read_mbdyn_log_file('EXEC_DEFAULT')
            bpy.ops.add.mbdynnode_all('EXEC_DEFAULT')
            bpy.ops.add.mbdyn_elems_all('EXEC_DEFAULT')
        except RuntimeError as re:
            message = "StandardImport: something went wrong during the automatic import. "\
                + " See the .bylog file for details"
            self.report({'ERROR'}, message)
            baseLogger.error(message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynStandardImport)
# -----------------------------------------------------------
# end of MBDynStandardImport class


class MBDynReadLog(bpy.types.Operator):
    """ Imports MBDyn nodes and elements by parsing the .log file """
    bl_idname = "animate.read_mbdyn_log_file"
    bl_label = "MBDyn .log file parsing"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ret_val, obj_names = parse_log_file(context)

        missing = context.scene.mbdyn.missing
        if len(obj_names) > 0:
            message = "Some of the nodes/elements are missing in the new .log file"
            baseLogger.warning(message)
            hide_or_delete(obj_names, missing)

        if len(mbs.disabled_output) > 0:
            message = "No output for nodes " + mbs.disabled_output
            baseLogger.warning(message)

        if ret_val == {'LOG_NOT_FOUND'}:
            message = "MBDyn .log file not found"
            self.report({'ERROR'}, message)
            baseLogger.error(message)
            return {'CANCELLED'}

        elif ret_val == {'NODES_NOT_FOUND'}:
            message = "The .log file selected does not contain MBDyn nodes definitions"
            self.report({'ERROR'}, message)
            baseLogger.error(message)
            return {'CANCELLED'}

        elif ret_val == {'MODEL_INCONSISTENT'}:
            message = "Contents of MBDyn .log file inconsistent with the scene"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'FINISHED'}

        elif ret_val == {'NODES_INCONSISTENT'}:
            message = "Nodes in MBDyn .log file inconsistent with the scene"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'FINISHED'}

        elif ret_val == {'ELEMS_INCONSISTENT'}:
            message = "Elements in MBDyn .log file inconsistent with the scene"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'FINISHED'}

        elif ret_val == {'OUT_NOT_FOUND'}:
            message = "Could not locate the .out file"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'FINISHED'}

        elif ret_val == {'FINISHED'}:
            message = "MBDyn entities imported successfully"
            bpy.data.scenes['Scene'].render.use_stamp = True
            bpy.data.scenes['Scene'].render.use_stamp_note = True
            self.report({'INFO'}, message) 
            baseLogger.info(message)

            return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynReadLog)
# -----------------------------------------------------------
# end of MBDynReadLog class

class MBDynSelectOutputFile(bpy.types.Operator, ImportHelper):
    """ Sets MBDyn's output files path and basename """

    bl_idname = "sel.mbdyn_mov_file"
    bl_label = "Select MBDyn results file"

    filter_glob = StringProperty(
            default = "*.mov;*.nc",
            options = {'HIDDEN'},
            )

    def execute(self, context):
        mbs = context.scene.mbdyn

        # removes keyframes before importing a new file
        remove_oldframes(context)

        si_retval = setup_import(self.filepath, context)

        mbs.file_path, mbs.file_basename = path_leaf(self.filepath)

        baseLogger.handlers = []
        log_messages(mbs, baseLogger, False)

        if si_retval == {'NETCDF_ERROR'}:
            self.report({'ERROR'}, "NetCDF module not imported correctly")
            return {'CANCELLED'}
        elif si_retval == {'FINISHED'}:
            return si_retval

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
bpy.utils.register_class(MBDynSelectOutputFile)
# -----------------------------------------------------------
# end of MBDynSelectLabFile class

class MBDynAssignLabels(bpy.types.Operator):
    """ Assigns 'recognisable' labels to MBDyn nodes and elements by
        parsing the .log file """
    bl_idname = "import.mdbyn_labels"
    bl_label = "Import labels of MBDyn objects"

    def execute(self, context):
        ret_val = assign_labels(context)
        if ret_val == {'NOTHING_DONE'}:
            message = 'MBDyn labels file provided appears to not contain ' +\
            'correct labels.'
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'CANCELLED'}

        elif ret_val == {'LABELS_UPDATED'}:
            message = "MBDyn labels imported"
            self.report({'INFO'}, message)
            baseLogger.info(message)
            return {'FINISHED'}

        elif ret_val == {'FILE_NOT_FOUND'}:
            message = "MBDyn labels file not found..."
            self.report({'ERROR'}, message)
            baseLogger.error(message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynAssignLabels)
# -----------------------------------------------------------
# end of MBDynAssignLabels class

class MBDynClearData(bpy.types.Operator):
    """ Clears MBDyn elements and nodes dictionaries, essentially\
    'cleaning' the scene of all MBDyn related data"""
    bl_idname = "mbdyn.cleardata"
    bl_label = "Clear MBDyn Data"

    def execute(self, context):
        mbs = context.scene.mbdyn

        for var in dir(mbs):
            try:
                dummy = getattr(mbs, var)

            except AttributeError:
                continue

            if isinstance(dummy, bpy.types.bpy_prop_collection):
                print(dummy)
                dummy.clear()

        message = "Scene MBDyn data cleared."
        self.report({'INFO'}, message)
        baseLogger.info(message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynClearData)
# -----------------------------------------------------------
# end of MBDynClearData class

class MBDynSetInstallPath(bpy.types.Operator):
    """Sets the Installation Path of MBDyn to be used\
        in running simulation"""
    bl_idname = "sel.mbdyn_install_path"
    bl_label = "Set installation path of MBDyn"

    def execute(self, context):
        mbs = context.scene.mbdyn
        mbdyn_path = mbs.install_path
        config = {'mbdyn_path': mbdyn_path}

        with open(os.path.join(mbs.addon_path, 'config.json'), 'w') as f:
            json.dump(config, f)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetInstallPath)
# -----------------------------------------------------------
# end of MBDynSetInstallPath class

class MBDynDefaultInstallPath(bpy.types.Operator):
    """Sets the Installation path of MBDyn to the value\
        found in the system $PATH variable"""

    bl_idname = "sel.mbdyn_default_path"
    bl_label = "Set Default Path for MBDyn"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if shutil.which('mbdyn'):
            mbs.install_path = os.path.dirname(shutil.which('mbdyn'))

        else:
            message = 'MBDyn path is not set in the system $PATH variable'
            self.report({'ERROR'}, message)
            baseLogger.error(message)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynDefaultInstallPath)

class MBDynConfigInstallPath(bpy.types.Operator):
    """Sets the Installation path of MBDyn to the value\
        found in config.json"""

    bl_idname = "sel.mbdyn_config_path"
    bl_label = "Set config.json Path for MBDyn"

    def execute(self, context):
        mbs = bpy.context.scene.mbdyn

        try:
            with open(os.path.join(mbs.addon_path, 'config.json'), 'r') as f:
                mbs.install_path = json.load(f)['mbdyn_path']
        except FileNotFoundError:
            message = 'No config.json file found. Set value above'
            self.report({'ERROR'}, message)
            baseLogger.error(message)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynConfigInstallPath)

class MBDynSelectInputFile(bpy.types.Operator, ImportHelper):
    """Set input file's path and basename\
        to be used in MBDyn simulation"""

    bl_idname = "sel.mbdyn_input_file"
    bl_label = "MBDyn input file"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.sim_num = 0

        mbs.input_path = os.path.abspath(self.filepath)
        mbs.input_basename = os.path.splitext(os.path.basename(self.filepath))[0]

        mbs.file_basename = mbs.input_basename
        mbs.file_path = os.path.dirname(mbs.input_path)

        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
bpy.utils.register_class(MBDynSelectInputFile)
# -----------------------------------------------------------
# end of MBDynSelectInputFile class

class MBDynSetEnvVariables(bpy.types.Operator):
    """Sets the Environment variables to be\
        used in MBDyn simulation"""

    bl_idname = "sel.set_env_variable"
    bl_label = "Set Environment Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        exist_env_vars = [mbs.env_vars[var].variable for var in range(len(mbs.env_vars))]

        try:
            index = exist_env_vars.index(mbs.env_variable)
            mbs.env_vars[index].value = mbs.env_value

        except ValueError:
            env = mbs.env_vars.add()
            env.variable = mbs.env_variable
            env.value = mbs.env_value

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetEnvVariables)
# -----------------------------------------------------------
# end of MBDynSetEnvVariables class

class MBDynDeleteEnvVariables(bpy.types.Operator):
    """Delete Environment variables"""
    bl_idname = "sel.delete_env_variable"
    bl_label = "Delete Environment Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.env_vars.remove(mbs.env_index)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynDeleteEnvVariables)
# -----------------------------------------------------------
# end of MBDynDeleteEnvVariables class

class MBDynRunSimulation(bpy.types.Operator):
    """Runs the MBDyn Simulation in background"""
    bl_idname = "sel.mbdyn_run_simulation"
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

        if percent >= 100:
            context.window_manager.event_timer_remove(self.timer)

            mbs.mbdyn_running = False

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


        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        mbs = context.scene.mbdyn
        parse_input_file(context)

        mbs.mbdyn_running = True

        if not mbs.final_time:
            self.report({'ERROR'}, "Enter Final Time for the simulation to proceed")
            return {'CANCELLED'}

        return self.execute(context)

bpy.utils.register_class(MBDynRunSimulation)
# -----------------------------------------------------------
# end of MBDynRunSimulation class

class MBDynStopSimulation(bpy.types.Operator):
    """Stops the MBDyn simulation"""
    bl_idname = "sel.mbdyn_stop_simulation"
    bl_label = "Stop MBDyn Simulation"

    def execute(self, context):
        mbs = context.scene.mbdyn
        kill_mbdyn()

        mbs.mbdyn_running = False

        self.report({'INFO'}, "The MBDyn simulation was interrupted")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynStopSimulation)
# -----------------------------------------------------------
# end of MBDynStopSimulation class

class MBDynLiveAnimation(bpy.types.Operator):
    bl_idname = "animation.start_sockets"
    bl_label = "MBDyn Start sockets"

    def modal(self, context, event):
        mbs = context.scene.mbdyn

        if not mbs.mbdyn_running:
            return self.close(context)

        allowed_keys = ['ESC', 'P','TIMER', 'J', 'K', 'LEFT_ARROW', 'RIGHT_ARROW', 'UP_ARROW', 'DOWN_ARROW']

        if not (event.type in allowed_keys or (hasattr(self, "channels") and event.type in self.channels)):
            return {'PASS_THROUGH'}

        if event.type == 'P' and event.value == 'PRESS':
            mbs.pause_live = not mbs.pause_live
            print(mbs.pause_live)

        elif event.type == 'K' and event.value == 'PRESS':
            mbs.load_frequency += 1

        elif event.type == 'J' and event.value == 'PRESS':
            mbs.load_frequency -= 1
            mbs.load_frequency = max(1, mbs.load_frequency)

        elif event.type == 'UP_ARROW' and event.value == 'PRESS':
            mbs.dr_index += 1
            mbs.dr_index %= len(mbs.drivers)
            print(mbs.dr_index)

        elif event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            mbs.dr_index -= 1
            mbs.dr_index = mbs.dr_index + len(mbs.drivers) if mbs.dr_index < 0 else mbs.dr_index
            print(mbs.dr_index)

        elif event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            mbs.drivers[mbs.dr_index].value += 1

        elif event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            mbs.drivers[mbs.dr_index].value -= 1

        elif event.type == 'ESC':

            kill_mbdyn()

            mbs.mbdyn_running = False

            self.report({'INFO'}, "The MBDyn simulation was interrupted")

            return self.close(context)

        if hasattr(self, "senders") and (not mbs.pause_live):
            try:
                for ii in range(int(mbs.load_frequency)):
                    for driver in mbs.drivers:
                        self.senders[driver.name].send([driver.value])
                self.running += 1
            except BrokenPipeError:
                return self.close(context)

        if hasattr(self, "receiver") and (not mbs.pause_live):
            data = self.receiver.get_data()
            for i, node in enumerate(self.nodes):
                self.frame += 1

                node = mbs.nodes['node_' + node]
                node_obj = bpy.data.objects[node.blender_object]

                # set_obj_locrot_mov(node_obj, [node.int_label] + list(data[12*i: 12 + 12*i]))
                node_obj.location = Vector(data[12*i : 12*i+3])
                node_obj.rotation_euler = Matrix([data[12*i+3 : 12*i+6], data[12*i+6 : 12*i+9], data[12*i+9 : 12*i+12]]).to_euler(node_obj.rotation_euler.order)

        return {'PASS_THROUGH'}

    def close(self, context):
        context.scene.frame_end = context.scene.frame_current
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

        if hasattr(self, "receiver"):
            self.receiver.close()

        if hasattr(self, "sender"):
            self.sender.close()

        wm.progress_end()
        return {'FINISHED'}
    def execute(self, context):
        mbs = context.scene.mbdyn

        self.running = 0
        self.frame = context.scene.frame_start = context.scene.frame_current = 0

        mbs.pause_live = True

        host_name, port_number = mbs.host_sender, mbs.port_sender
        self.senders = [(driver.name, StreamSender(driver, context)) for driver in mbs.drivers]
        self.senders = dict(self.senders)

        for driver in mbs.drivers:
            self.senders[driver.name].send([driver.value])

        self.nodes = mbs.output_elems[0].nodes.split(' ')
        self.receiver = StreamReceiver(mbs.output_elems[0], context)

        if self.receiver.socket:
            self.receiver.start()
        else:
            self.report({'INFO'}, "Animation stream socket failed to connect")
            del self.receiver

        self.out_file = os.path.join(mbs.file_path, mbs.file_basename + '.out')

        wm = context.window_manager
        wm.progress_begin(0., 100.)
        self.timer = wm.event_timer_add(0.0001, context.window)
        wm.modal_handler_add(self)

        return{'RUNNING_MODAL'}

bpy.utils.register_class(MBDynLiveAnimation)

class MBDynSetMotionPaths(bpy.types.Operator):
    """ Sets the motion path for all the objects that have an assigned MBDyn's node """
    bl_idname = "animate.set_mbdyn_motion_path"
    bl_label = "MBDyn Motion Path setter"

    def execute(self, context):
        mbs = context.scene.mbdyn

        if mbs.end_time > (mbs.num_timesteps) * mbs.time_step:
            self.report({'ERROR'}, "End time greater than total simulation time")
            return {'CANCELLED'}

        if mbs.start_time > (mbs.num_timesteps) * mbs.time_step:
            self.report({'ERROR'}, "Start time greater than total simulation time")
            return {'CANCELLED'}

        remove_oldframes(context)

        if not(context.scene.mbdyn.use_netcdf):
            ret_val = set_motion_paths_mov(context)
        else:
            ret_val = set_motion_paths_netcdf(context)
        if ret_val == 'CANCELLED':
            message = "MBDyn results file not loaded"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            
        return ret_val

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetMotionPaths)
# -----------------------------------------------------------
# end of MBDynSetMotionPaths class

class MBDynSetImportFreqAuto(bpy.types.Operator):
    """ Sets the import frequency automatically in order to match the Blender
        time and the simulation time, based on the current render fps """
    bl_idname = "set.mbdyn_loadfreq_auto"
    bl_label = "Import frequency: auto"

    def execute(self, context):
        mbs = context.scene.mbdyn
        mbs.load_frequency = 1./(context.scene.render.fps*mbs.time_step)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class MBDynSetRenderVariables(bpy.types.Operator):
    """Sets the Render variables to be\
        used in a Blender Render"""

    bl_idname = "sel.set_render_variable"
    bl_label = "Set Render Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        exist_render_vars = [mbs.render_vars[var].value for var in range(len(mbs.render_vars))]

        try:
            index = exist_render_vars.index(mbs.plot_vars[mbs.plot_var_index].name)
            mbs.render_vars[index].variable = mbs.render_var_name
            mbs.render_vars[index].components = mbs.plot_comps

        except ValueError:
            rend = mbs.render_vars.add()
            rend.variable = mbs.render_var_name
            rend.value = mbs.plot_vars[mbs.plot_var_index].name
            rend.components = mbs.plot_comps

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetRenderVariables)
# -----------------------------------------------------------
# end of MBDynSetRenderVariables class

class MBDynDeleteRenderVariables(bpy.types.Operator):
    """Delete Render variables"""
    bl_idname = "sel.delete_render_variable"
    bl_label = "Delete Render Variable"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.render_vars.remove(mbs.render_index)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynDeleteRenderVariables)
# -----------------------------------------------------------
# end of MBDynDeleteRenderVariables class

class MBDynDeleteAllRenderVariables(bpy.types.Operator):
    bl_idname = "sel.delete_all_render_variables"
    bl_label = "Delete all Render variables"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.render_vars.clear()

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynDeleteAllRenderVariables)


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

bpy.utils.register_class(MBDynShowDisplayGroup)


class MBDynSetDisplayGroup(bpy.types.Operator):
    """Delete Render variables"""
    bl_idname = "sel.set_display_group"
    bl_label = "Set Display Group"

    def execute(self, context):
        mbs = context.scene.mbdyn

        exist_display_groups = [mbs.display_vars_group[var].name for var in range(len(mbs.display_vars_group))]

        try:
            index = exist_display_groups.index(mbs.group_name)
            mbs.display_vars_group[index].group.clear()

            janga = mbs.display_vars_group[mbs.group_name]

            for ii in list(range(len(mbs.render_vars))):
                rend = janga.group.add()
                rend.variable = mbs.render_vars[ii].variable
                rend.value = mbs.render_vars[ii].value
                rend.components = mbs.render_vars[ii].components


        except ValueError:
            janga = mbs.display_vars_group.add()
            janga.name = mbs.group_name

            for ii in list(range(len(mbs.render_vars))):
                rend = janga.group.add()
                rend.variable = mbs.render_vars[ii].variable
                rend.value = mbs.render_vars[ii].value
                rend.components = mbs.render_vars[ii].components

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetDisplayGroup)
# -----------------------------------------------------------
# end of MBDynDeleteRenderVariables class

class MBDynImportPanel(bpy.types.Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_ImportPath"
    bl_label = "Load results"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'MBDyn'

    def draw(self, context):

        # utility renaming
        layout = self.layout
        obj = context.object
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        ed = mbs.elems

        # MBDyn output file selection
        row = layout.row()
        row.label(text = "MBDyn simulation results")

        col = layout.column(align = True)
        col.operator(MBDynSelectOutputFile.bl_idname, text = "Select results file")

        # Display MBDyn file basename and info
        row = layout.row()

        row.label(text = "Loaded results file")

        col = layout.column(align = True)
        col.prop(mbs, "file_basename", text = "")
        col.prop(mbs, "num_nodes", text = "nodes total")

        if not(mbs.use_netcdf):
            col.prop(mbs, "num_rows", text = "rows total")
        col.prop(mbs, "num_timesteps", text = "time steps")
        
        row = layout.row()
        if mbs.file_path:
            row.label(text = "Full file path:")
            row = layout.row()
            row.label(text = mbs.file_path)
        col.enabled = False

        row = layout.row()
        row.operator(MBDynStandardImport.bl_idname, text = "Standard Import")

        # Import MBDyn data
        row = layout.row()
        # row.label(text="Load MBDyn data")
        col = layout.column(align = True)
        col.operator(MBDynReadLog.bl_idname, text = "Load .log file")

        # Assign MBDyn labels to elements in dictionaries
        col = layout.column(align = True)
        col.operator(MBDynAssignLabels.bl_idname, text = "Load MBDyn labels")

        # Set action to be taken for missing nodes/elements
        row = layout.row()
        row.label(text = "Missing nodes/elements")
        row = layout.row()
        row.prop(mbs, "missing", text = "")

        row = layout.row()
        col = layout.column(align = True)
        col.prop(mbs, "del_log", text = "Delete Log Files on Exit")

        # Clear MBDyn data for scene
        row = layout.row()
        row.label(text="Erase all MBDyn data in scene")
        col = layout.column(align = True)
        col.operator(MBDynClearData.bl_idname, text = "CLEAR MBDYN DATA")

# -----------------------------------------------------------
# end of MBDynImportPanel class

class MBDynAnimatePanel(bpy.types.Panel):
    """ Create animation of simulation results - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_Animate"
    bl_label = "Create animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'MBDyn'

    def draw(self, context):

        # utility renaming
        layout = self.layout
        mbs = context.scene.mbdyn

        # Insert keyframes for animation
        col = layout.column(align=True)
        col.label(text = "Start animating")
        col.operator(MBDynSetMotionPaths.bl_idname, text = "Animate scene")
        col.operator(MBDynSetImportFreqAuto.bl_idname, text = "Auto set frequency")
        col.prop(mbs, "load_frequency")
        
        # time_step > 0 only if .log file had been loaded
        col.enabled = bool(mbs.time_step)   


        col = layout.column(align=True)

        col.label(text = "Time Range of import")
        col.prop(mbs, "start_time")
        col.prop(mbs, "end_time")


        col = layout.column(align=True)
        col.label(text = "Current Simulation Time")
        col.prop(mbs, "time")
# -----------------------------------------------------------
# end of MBDynAnimatePanel class

class MBDynSimulationPanel(bpy.types.Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_RunSim"
    bl_label = "Run Simulation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'MBDyn'

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
        row.label(text='Path of MBDyn')
        col = layout.column(align=True)
        col.prop(mbs, "install_path", text="Path")
        col.operator(MBDynSetInstallPath.bl_idname, text = 'Set Installation Path')
        col.operator(MBDynDefaultInstallPath.bl_idname, text = 'Use default MBDyn')
        col.operator(MBDynConfigInstallPath.bl_idname, text = 'Use config MBDyn Path')

        col = layout.column(align = True)
        col.label(text = "Selected input file")
        col.prop(mbs, "input_path", text = '')
        col.enabled = False

        col = layout.column(align = True)
        col.operator(MBDynSelectInputFile.bl_idname, text = 'Select input file')
        
        col = layout.column(align = True)
        col.label(text = "Output Directory")
        col.prop(mbs, "file_path", text = '')

        col = layout.column(align = True)
        col.label(text = "Output Filename")
        col.prop(mbs, "file_basename", text = '')

        col = layout.column(align = True)
        col.prop(mbs, "overwrite", text = "Overwrite Previous Files")

        col = layout.column(align = True)
        col.prop(mbs, "force_text_import", text = "Always load text output")

        col = layout.column(align = True)
        col.label(text = "Command-line options")
        col.prop(mbs, "cmd_options", text = '')

        row = layout.row()
        row.label(text='Set Environment Variables')

        row = layout.row()
        row.template_list('MBDynEnvVar_UL_List', "MBDyn Environment variables list", mbs, "env_vars",\
                mbs, "env_index")

        col = layout.column(align = True)
        col.prop(mbs, "env_variable", text = "Variable")
        col.prop(mbs, "env_value", text = "Value")
        col.operator(MBDynSetEnvVariables.bl_idname, text = 'Set Variable')
        col.operator(MBDynDeleteEnvVariables.bl_idname, text = 'Delete Variable')

        col = layout.column(align = True)
        col.prop(mbs, "ui_time", text = 'Final Time')

        col = layout.column(align = True)
        col.prop(mbs, "sim_status", text = 'Simulation Status [compl. %]')


        col = layout.column(align = True)
        col.operator(MBDynRunSimulation.bl_idname, text = 'Run Simulation')

        if HAVE_PSUTIL:
            col = layout.column(align = True)
            col.operator(MBDynStopSimulation.bl_idname, text = 'Stop Simulaton')

# -----------------------------------------------------------
# end of MBDynSimulationPanel class

class MBDynLiveAnimPanel(bpy.types.Panel):
    """Live Animation Panel"""
    bl_idname = "VIEW3D_TL_MBDyn_Live"
    bl_label = "LiveAnimation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'MBDyn'

    def draw(self, context):

     # utility renaming
        layout = self.layout
        obj = context.object
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        ed = mbs.elems

        row = layout.row()
        row.label(text = "MBDyn Standard Import")
        col = layout.column(align = True)
        col.operator(MBDynStandardImport.bl_idname, text = "Standard Import")

        layout.separator()

        row = layout.row()
        row.operator(MBDynReadLog.bl_idname, text = "Load .log file")

        layout.separator()

        row = layout.row()
        row.prop(mbs, "load_frequency")

        row = layout.row()
        row.operator(MBDynLiveAnimation.bl_idname, text = "Start Sockets")

        row = layout.row()
        row.template_list('MBDynDriver_UL_List', "MBDyn drivers list", mbs, "drivers",\
                mbs, "dr_index")

class MBDynEigenanalysisPanel(bpy.types.Panel):
    """ Visualizes the results of an eigenanalysis - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_Eigen"
    bl_label = "Eigenanalysis"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'MBDyn'

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
            row = layout.row()
            row.prop(mbs.eigensolutions[mbs.curr_eigsol], "iNVec")
            row.enabled = False
            row = layout.row()
            row.operator(Tools_OT_MBDyn_Eigen_Geometry.bl_idname, text = "Reference configuration")

            row = layout.row()
            row.separator()

            row = layout.row()
            row.label(text = "Selected Eigenmode")
            row.prop(mbs.eigensolutions[mbs.curr_eigsol], "curr_eigmode", text = "")
            row = layout.row()
            row.prop(mbs.eigensolutions[mbs.curr_eigsol], "lambda_real")
            row.enabled = False
            row = layout.row()
            row.prop(mbs.eigensolutions[mbs.curr_eigsol], "lambda_freq")
            row.enabled = False

            row.separator()
            row = layout.row()
            row.label(text = "Animation parameters")
            row.prop(mbs.eigensolutions[mbs.curr_eigsol], "anim_scale")
            row = layout.row()
            row.prop(mbs.eigensolutions[mbs.curr_eigsol], "anim_frames")
            row = layout.row()
            row.operator(Tools_OT_MBDyn_Animate_Eigenmode.bl_idname, text = "Visualize mode")

# -----------------------------------------------------------
# end of MBDynEigenanalysisPanel class

class MBDynActiveObjectPanel(bpy.types.Panel):
    """ Visualizes MBDyn data relative to the current active object - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_ActiveObject"
    bl_label = "Active Object info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'MBDyn'

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
            row.label(text="Active Object")
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
                row.label(text="No active objects")
                pass
            except TypeError:
                pass
# -----------------------------------------------------------
# end of MBDynActiveObjectPanel class

class MBDynNodes_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OUTLINER_OB_EMPTY'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label('', icon = custom_icon)
# -----------------------------------------------------------
# end of MBDynNodes_UL_List class

class MBDynElems_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'CONSTRAINT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label('', icon = custom_icon)
# -----------------------------------------------------------
# end of MBDynElems_UL_List class

class MBDynDriver_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)
        layout.label(str(item.value))
# -----------------------------------------------------------
# end of MBDynDriver_UL_List class

class MBDynPlotVar_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)
# -----------------------------------------------------------
# end of MBDynPLotVar_UL_List class

class MBDynRenderVar_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.variable)
        layout.label(item.value + comp_repr(item.components, item.value, context))
# -----------------------------------------------------------
# end of MBDynRenderVar_UL_List class

class MBDynEnvVar_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.variable)
        layout.label(item.value)
# -----------------------------------------------------------
# end of MBDynEnvVar_UL_List class

class MBDynReferences_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OUTLINER_DATA_EMPTY'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.aligment = 'CENTER'
            layout.label('', icon = custom_icon) 
# -----------------------------------------------------------
# end of MBDynReferences_UL_List class

## Panel in scene properties toolbar that shows the MBDyn
#  nodes found in the .log file and links to an operator
#  that imports all of them automatically
class MBDynNodesScenePanel(bpy.types.Panel):
    """ List of MBDyn nodes: use import all button to add \
            them all to the scene at once """
    bl_label = "MBDyn nodes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        layout = self.layout
        row = layout.row()
        row.template_list('MBDynNodes_UL_List', "MBDyn nodes list", mbs, "nodes",\
                mbs, "nd_index")

        if len(nd):
            item = mbs.nodes[mbs.nd_index]

            col = layout.column()

            col.prop(item, "int_label")
            col.prop(item, "string_label")
            col.prop(item, "blender_object")
            col.enabled = False

            row = layout.row()
            row.prop(mbs, "node_object")

            col = layout.column()
            col.prop(mbs, "min_node_import")
            col.prop(mbs, "max_node_import")
            row = layout.row()
            row.operator(Scene_OT_MBDyn_Node_Import_All.bl_idname,\
                    text = "Add nodes to scene")

            row = layout.row()
            row.operator(MBDynCreateVerticesFromNodesButton.bl_idname,\
                    text = "Create vertex grid from nodes")

            row = layout.row()
            row.prop(mbs, "is_vertshook", text = "Hook vertices to nodes")
# -----------------------------------------------------------
# end of MBDynNodesScenePanel class

## Panel in scene properties toolbar that shows the MBDyn
#  elements found in the .log file
class MBDynElemsScenePanel(bpy.types.Panel):
    """ List of MBDyn elements: use import button to add \
            them to the scene  """
    bl_label = "MBDyn elements"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        mbs = context.scene.mbdyn
        layout = self.layout
        row = layout.row()
        row.template_list("MBDynElems_UL_List", "MBDyn elements", mbs, "elems",\
                mbs, "ed_index")

        if len(mbs.elems):
            item = mbs.elems[mbs.ed_index]

            row = layout.row()
            row.separator()

            col = layout.column()
            col.prop(item, "int_label")
            col.prop(item, "string_label")
            col.prop(item, "blender_object")
            col.enabled = False

            row = layout.row()
            row.operator(item.import_function, \
                    text="Add element to the scene").int_label = item.int_label

            col = layout.column()

            row = col.row()
            row.prop(mbs, "elem_type_import")
            row = col.row()
            col.prop(mbs, "min_elem_import")
            col.prop(mbs, "max_elem_import")
            if mbs.elem_type_import in ['shell4']:
                col.prop(mbs, "mesh_import_mode")
            if mbs.mesh_import_mode == 'SEPARATED OBJECTS':
                col.operator(Scene_OT_MBDyn_Import_Elements_by_Type.bl_idname, \
                        text="Import elements by type")
            elif mbs.mesh_import_mode == 'SINGLE MESH':
                col.operator(Scene_OT_MBDyn_Import_Elements_as_Mesh.bl_idname, \
                        text="Import elements by type")

            col = layout.column()
            col.operator(Scene_OT_MBDyn_Elements_Import_All.bl_idname)
# -----------------------------------------------------------
# end of MBDynNodesScenePanel class

class MBDynScalingPanel(bpy.types.Panel):
    """ List of MBDyn elements: use import button to add \
            them to the scene  """
    bl_label = "Scale MBDyn Entities"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        mbs = context.scene.mbdyn
        layout = self.layout
        
        box = layout.box()
        row = box.row()
        row.template_list('MBDynNodes_UL_List', "MBDyn nodes list", mbs, "nodes",\
                mbs, "nd_index")
        row = box.row()
        row.prop(mbs, "node_scale_slider")
        row = box.row()
        row.operator(Scene_OT_MBDyn_Select_all_Nodes.bl_idname, text = 'Select all Nodes')
        row.operator(Scene_OT_MBDyn_Scale_Node.bl_idname, text = 'Scale Node')

        box = layout.box()
        row = box.row()
        row.prop(mbs, "elem_type_scale")
        row = box.row()
        row.prop(mbs, "elem_scale_slider")
        row = box.row()
        row.operator(Scene_OT_MBDyn_Select_Elements_by_Type.bl_idname, text = 'Select Elements')
        row.operator(Scene_OT_MBDyn_Scale_Elements_by_Type.bl_idname, text = "Scale Elements")

## Panel in Scene toolbar
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
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
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
                if HAVE_PLOT:
                    row = layout.row()
                    col = layout.column()
                    col.prop(mbs, "plot_frequency")
                    col.operator(Scene_OT_MBDyn_plot_freq.bl_idname, text="Use Import freq")
                    row = layout.row()
                    row.prop(mbs, "plot_type")
                    row = layout.row()
                    row.prop(mbs, "plot_xrange_min")
                    row = layout.row()
                    row.prop(mbs, "plot_xrange_max")
                    row = layout.row()
                    if mbs.plot_type == "TIME HISTORY":
                        row.operator(Scene_OT_MBDyn_plot_var.bl_idname, 
                                text="Plot variable")
                    elif mbs.plot_type == "AUTOSPECTRUM":
                        row = layout.row()
                        row.prop(mbs, "fft_remove_mean")
                        row = layout.row()
                        row.operator(Scene_OT_MBDyn_plot_var_Sxx.bl_idname,
                                text="Plot variable Autospectrum")
            except IndexError:
                pass

            layout.separator()
            layout.separator()

            row = layout.row()
            row.template_list('MBDynRenderVar_UL_List', "MBDyn Render Variables list", mbs, "render_vars",\
                    mbs, "render_index")
            row = layout.row()
            row.prop(mbs, "render_var_name")

            row = layout.row()
            row.operator(MBDynSetRenderVariables.bl_idname, text = 'Set Display Variable')

            row = layout.row()
            row.operator(MBDynDeleteRenderVariables.bl_idname, text = 'Delete Display Variable')
            row.operator(MBDynDeleteAllRenderVariables.bl_idname, text = 'Clear')

            if HAVE_PLOT:
                row = layout.row()
                row.operator(Scene_OT_MBDyn_plot_variables_list.bl_idname, text="Plot variables in List")

                row.prop(mbs, "plot_group", text = "Plot Group")
                layout.separator()
                layout.separator()

                row = layout.row()
                row.prop(mbs, "group_name")
                row.operator(MBDynSetDisplayGroup.bl_idname, text="Set Display Group")

                row = layout.row()
                row.prop(mbs, "display_enum_group")
                row.operator(MBDynShowDisplayGroup.bl_idname, text = "Show Display Group")

        else:
            row = layout.row()
            row.label(text="Plotting from text output")
            row.label(text="is not supported yet.")

## Panel in scene properties toolbar that shows the MBDyn reference found in the .rfm file
class MBDynReferenceScenePanel(bpy.types.Panel):
    """ List of MBDyn references: use import button to add them to the scene as empty
        axes objects """
    bl_label = "MBDyn References"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        mbs = context.scene.mbdyn
        rd = mbs.references
        layout = self.layout

        row = layout.row()
        row.template_list('MBDynReferences_UL_List', "MBDyn references list", \
                mbs, "references", mbs, "ref_index")

        try:
            item = mbs.references[mbs.ref_index]

            col = layout.column()
            col.prop(item, "int_label")
            col.prop(item, "string_label")
            col.prop(item, "blender_object")
            col.enabled = False

            col = layout.column()
            col.operator(Scene_OT_MBDyn_References_Import_Single.bl_idname, \
                    text = "Add reference to the scene").int_label = item.int_label
            col.operator(Scene_OT_MBDyn_References_Import_All.bl_idname, \
                   text = "Add all references to the scene")
        except KeyError:
            pass
        except IndexError:
            pass

## Panel in object properties toolbar that helps associate
#  MBDyn nodes to Blender objects
class MBDynOBJNodeSelect(bpy.types.Panel):
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
        row.label("Node #")
        row.label("Node label")
        row.label("Blender Object")
        row.label("")
        row.label("")
        for nd_entry in nd:
            row = layout.row()
            row.label(str(nd_entry.int_label))
            row.label(nd_entry.string_label)
            if nd_entry.blender_object == obj.name:
                row.label(nd_entry.blender_object, icon = 'OBJECT_DATA')
                row.operator("sel.mbdynnode", text="ASSIGN").int_label = nd_entry.int_label
            else:
                row.label(nd_entry.blender_object)
                row.operator("sel.mbdynnode", text="ASSIGN").int_label = nd_entry.int_label
                if bpy.data.objects.get(nd_entry.blender_object) == None:
                    row.operator(Scene_OT_MBDyn_Node_Import_Single.bl_idname, \
                            text="ADD").int_label = nd_entry.int_label
# -----------------------------------------------------------
# end of MBDynOBJNodeSelect class

class Scene_OT_MBDyn_Node_Import_All(bpy.types.Operator):
    bl_idname = "add.mbdynnode_all"
    bl_label = "Add MBDyn nodes to scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        added_nodes = 0

        for node in nd:
            if (mbs.min_node_import <= node.int_label) & (mbs.max_node_import >= node.int_label):
                if not(spawn_node_obj(context, node)):
                    message = "Could not spawn the Blender object assigned to node {}"\
                            .format(node.int_label)

                    self.report({'ERROR'}, message)
                    baseLogger.error(message)
                    return {'CANCELLED'}

                obj = context.scene.objects.active
                obj.mbdyn.type = 'node.struct'
                obj.mbdyn.int_label = node.int_label
                obj.mbdyn.string_label = node.string_label
                obj.mbdyn.parametrization = node.parametrization
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = node.initial_rot
                update_parametrization(obj)
                if obj.mbdyn.string_label != "none":
                    obj.name = node.string_label
                else:
                    obj.name = node.name
                node.blender_object = obj.name
                obj.mbdyn.is_assigned = True
                print("MBDynNodeImportAllButton: added node " \
                        + str(node.int_label) \
                        + " to scene and associated with object " + obj.name)
                added_nodes += 1

        if added_nodes:
            message = "All MBDyn nodes imported successfully"
            self.report({'INFO'}, message)
            baseLogger.info(message)
            return {'FINISHED'}
        else:
            message = "No MBDyn nodes imported"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Node_Import_All class

class Scene_OT_MBDyn_Node_Import_Single(bpy.types.Operator):
    bl_idname = "add.mbdynnode"
    bl_label = "Add selected MBDyn node to scene"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        for node in context.scene.mbdyn.nodes:
            if node.int_label == self.int_label:
                node.blender_object = "none"

    def execute(self, context):
        added_node = False
        for node in context.scene.mbdyn.nodes:
            if node.int_label == self.int_label:
                if not(spawn_node_obj(context, node)):
                    message = "Could not spawn the Blender object assigned to node {}"\
                            .format(node.int_label)

                    self.report({'ERROR'}, message)
                    baseLogger.error(message)
                    return {'CANCELLED'}
                obj = context.scene.objects.active
                obj.mbdyn.type = 'node.struct'
                obj.mbdyn.int_label = node.int_label
                obj.mbdyn.string_label = node.string_label
                obj.mbdyn.parametrization = node.parametrization
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = node.initial_rot
                update_parametrization(obj)
                if obj.mbdyn.string_label != "none":
                    obj.name = node.string_label
                else:
                    obj.name = node.name
                node.blender_object = obj.name
                obj.mbdyn.is_assigned = True
                print("MBDynNodeAddButton: added node " + str(node.int_label) + " to scene and associated with object " + obj.name)
                added_node = True
        if added_node:
            message = "MBDyn node " + node.string_label + " imported to scene."
            self.report({'INFO'}, message)
            baseLogger.info(message)
            return {'FINISHED'}
        else:
            message = "Cannot import MBDyn node " + node.string_label + "."
            self.report({'WARNING'}, message) 
            baseLogger.warning(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Node_Import_Single class

class Scene_OT_MBDyn_References_Import_All(bpy.types.Operator):
    bl_idname = "add.mbdyn_reference_all"
    bl_label = "Add MBDyn references to scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        rd = mbs.references

        for ref in rd:
            retval = spawn_reference_frame(ref, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "Found the Object " + ref.blender_object + \
                    " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
        return {'FINISHED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_References_Import_All class

class Scene_OT_MBDyn_References_Import_Single(bpy.types.Operator):
    bl_idname = "add.mbdyn_reference_single"
    bl_label = "Add MBDyn reference to scene"

    int_label = IntProperty()

    def execute(self, context):
        mbs = context.scene.mbdyn
        rd = mbs.references

        for ref in rd:
            if ref.int_label == self.int_label:
                retval = spawn_reference_frame(ref, context)
                if retval == {'OBJECT_EXISTS'}:
                    message = "Found the Object " + ref.blender_object + \
                        " remove or rename it to re-import the element!"
                    self.report({'WARNING'}, message)
                    logging.warning(message)
                    return {'CANCELLED'}
        return {'FINISHED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_References_Import_Single class

class Scene_OT_MBDyn_Select_all_Nodes(bpy.types.Operator):
    bl_idname = "sel.select_all_nodes"
    bl_label = "Select all MBDyn Node Objects"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        bpy.ops.object.select_all(action = 'DESELECT')
        for var in nd.keys():
            obj = bpy.data.objects[var]
            obj.select = True
        return {'FINISHED'}

class Scene_OT_MBDyn_Select_Elements_by_Type(bpy.types.Operator):
    bl_idname = "sel.select_all_elements"
    bl_label = "Select all MBDyn objects"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        bpy.ops.object.select_all(action = 'DESELECT')
        for var in ed.keys():
            if mbs.elem_type_scale in var:
                obj = bpy.data.objects[var]
                obj.select = True
        return {'FINISHED'}

class Scene_OT_MBDyn_Scale_Node(bpy.types.Operator):
    bl_idname = "add.mbdyn_scale_node"
    bl_label = "Scale selected node"

    def execute(self, context):
        mbs = context.scene.mbdyn
        nd = mbs.nodes
        s = mbs.node_scale_slider
        scaleOBJ = bpy.data.objects[nd[mbs.nd_index].blender_object]
        scaleOBJ.scale = Vector((s, s, s))

        return {'FINISHED'}

class Scene_OT_MBDyn_Scale_Elements_by_Type(bpy.types.Operator):
    bl_idname = "add.mbdyn_scale_elems"
    bl_label = "Scale all elements of selected type"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        s = mbs.elem_scale_slider
        for elem in ed:
            if elem.type == mbs.elem_type_scale:
                scaleOBJ = bpy.data.objects[elem.name]
                scaleOBJ.scale = Vector((s, s, s))

        return {'FINISHED'}

class Scene_OT_MBDyn_Import_Elements_by_Type(bpy.types.Operator):
    bl_idname = "add.mbdyn_elems_type"
    bl_label = "Add all elements of selected type to scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        for elem in ed:
            if (elem.type == mbs.elem_type_import) \
                    and (elem.int_label >= mbs.min_elem_import) \
                    and (elem.int_label <= mbs.max_elem_import):
                try:
                    eval("spawn_" + elem.type + "_element(elem, context)")
                except NameError:
                    if ( elem.type == 'structural_absolute_force' ) \
                            or ( elem.type == 'structural_follower_force' ):
                        eval("spawn_structural_force_element(elem, context)")
                    elif ( elem.type == 'structural_absolute_couple' ) \
                            or ( elem.type == 'structural_follower_couple' ):
                        eval("spawn_structural_couple_element(elem, context)")
                    else:
                        message = "Could not find the import function for element of type " + \
                                elem.type + ". Element " + elem.name + " not imported."
                        self.report({'ERROR'}, message)
                        baseLogger.error(message)
                        return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Elements_by_Type class

class Scene_OT_MBDyn_Elements_Import_All(bpy.types.Operator):
    bl_idname = "add.mbdyn_elems_all"
    bl_label = "Add all the elements to the scene"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems

        ELEMS_MISSING = False
        for elem in ed:
            if (elem.int_label >= mbs.min_elem_import) \
                    and (elem.int_label <= mbs.max_elem_import):
                try:
                    eval("spawn_" + elem.type + "_element(elem, context)")
                except NameError:
                    if ( elem.type == 'structural_absolute_force' ) \
                            or ( elem.type == 'structural_follower_force' ):
                        eval("spawn_structural_force_element(elem, context)")
                    elif ( elem.type == 'structural_absolute_couple' ) \
                            or ( elem.type == 'structural_follower_couple' ):
                        eval("spawn_structural_couple_element(elem, context)")
                    else:
                        message = "Could not find the import function for element of type " + \
                            elem.type + ". Element " + elem.name + " not imported."
                        baseLogger.warning(message)
                        if not(ELEMS_MISSING):
                            ELEMS_MISSING = True
                        pass

        if ELEMS_MISSING:
            message = "Some elements were not imported. See log file for details"
            baseLogger.warning(message)
            self.report({'WARNING'}, message)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Elements_Import_All class

class MBDynOBJNodeSelectButton(bpy.types.Operator):
    bl_idname = "sel.mbdynnode"
    bl_label = "MBDyn Node Sel Button"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        axes = {'1': 'X', '2': 'Y', '3': 'Z'}
        context.object.mbdyn.int_label = self.int_label
        context.object.mbdyn.type = 'node.struct'
        ret_val = ''
        for item in context.scene.mbdyn.nodes:
            if self.int_label == item.int_label:
                item.blender_object = context.object.name
                ret_val = update_parametrization(context.object)

            if ret_val == 'ROT_NOT_SUPPORTED':
                message = "Rotation parametrization not supported, node " \
                + obj.mbdyn.string_label

                self.report({'ERROR'}, message)
                baseLogger.error(message)

            else:
                # DEBUG message to console
                print("Object " + context.object.name + \
                      " MBDyn node association updated to node " + \
                str(context.object.mbdyn.int_label))
        return{'FINISHED'}
# -----------------------------------------------------------
# end of MBDynOBJNodeSelectButton class

class MBDynCreateVerticesFromNodesButton(bpy.types.Operator):
    bl_idname = "add.vertsfromnodes"
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
                    obj.select = False
                    sel_obj.append(obj.name)

        if vidx:

            if len(bpy.context.selected_objects):
                # deselect all objects
                bpy.ops.object.select_all()

            vert_obj = bpy.data.objects.new("VertsFromNodes", me)
            bpy.context.scene.objects.link(vert_obj)

            vert_obj.select=True
            bpy.context.scene.objects.active = vert_obj
            bpy.context.scene.update()


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
            message = "No MBDyn nodes associated with selected objects."
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return{'CANCELLED'}

        return{'FINISHED'}
# -----------------------------------------------------------
# end of MBDynCreateVerticesFromNodesButton class

class Object_OT_Delete_Override(bpy.types.Operator):
    """ Overrides the delete function of Blender Objects to remove
        the related elements in MBDyn dictionaries """
    bl_idname = "object.delete"
    bl_label = "Object Delete Operator"
    use_global = BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    @classmethod
    def remove_from_dict(self, obj, context):
        if obj.mbdyn.type == 'node.struct':
            node = bpy.context.scene.mbdyn.nodes[obj.mbdyn.dkey]
            node.blender_object = 'none'
            node.is_imported = False
        elif obj.mbdyn.type == 'reference':
            ref = bpy.context.scene.mbdyn.references[obj.mbdyn.dkey]
            ref.blender_object = 'none'
            ref.is_imported = False
        else:
            elem = bpy.context.scene.mbdyn.elems[obj.mbdyn.dkey]
            elem.blender_object = 'none'
            elem.is_imported = False
            for idx, ude in enumerate(bpy.context.scene.mbdyn.elems_to_update):
                if ude.dkey == elem.name:
                    bpy.context.scene.mbdyn.elems_to_update.remove(idx)
                    break

    def execute(self, context):
        for obj in context.selected_objects:
            try:
                self.remove_from_dict(obj, context)
            except KeyError:
                print("remove_from_dict(): key not found")
                pass
            bpy.context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)
            return {'FINISHED'}
