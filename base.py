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

import os.path

import bpy
import bmesh
from bpy.props import *
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ImportHelper

from mathutils import *
from math import *

import ntpath, os, csv, math
from collections import namedtuple
import subprocess
import os
import json

import pdb

try:
    from netCDF4 import Dataset
except ImportError:
    print("blendyn: could not find netCDF4 module. NetCDF import "\
        + "will be disabled.")

HAVE_PLOT = False
try:
    import pygal
    from .plotlib import *
    HAVE_PLOT = True
except ImportError:
    print("blendyn: could not find pygal module. Plotting  "\
        + "will be disabled.")

from .baselib import *
from .elements import *
from .eigenlib import *

import pdb

## Nodes Dictionary: contains integer/string labels associations
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

bpy.utils.register_class(MBDynNodesDictionary)
# -----------------------------------------------------------
# end of MBDynNodesDictionary class

## Time PropertyGroup for animation
class MBDynTime(bpy.types.PropertyGroup):
    time = FloatProperty(
            name = "simulation time",
            description = "simulation time of animation frame"
            )
bpy.utils.register_class(MBDynTime)
# -----------------------------------------------------------
# end of MBDynTime class

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

    input_path = StringProperty(
            name = "Input File Path",
            description = "Path of Input files for MBDyn",
            default = ""
        )

    input_basename = StringProperty(
            name = "Input File basename",
            description = "Base name of Input File",
            default = "not yet loaded"
        )

    # String representing path of MBDyn Installation
    install_path = StringProperty(
            name = "Installation path of MBDyn",
            description = "Installation path of MBDyn",
            subtype = 'DIR_PATH'
            )

    # Integer representing the current animation number
    sim_num = IntProperty(
            name = "Number of Simulation",
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

    # Nodes dictionary -- holds the association between MBDyn nodes and blender objects
    nodes = CollectionProperty(
            name = "MBDyn nodes collection",
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

    # Type filter for elements import
    elem_type_import = EnumProperty(
            items  = get_elems_types,
            name = "Elements to import",
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
            default = 0
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

    if HAVE_PLOT:
        plot_vars = CollectionProperty(
                name = "MBDyn variables available for plotting",
                type = MBDynPlotVars
                )

        plot_var_index = IntProperty(
                name = "variable index",
                description = "index of the current variable to be plotted",
                default = 0
                )

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

        plot_comps = BoolVectorProperty(
                name = "components",
                description = "Components of property to plot",
                default = [True for i in range(9)],
                size = 9
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
        plot_frequency = IntProperty(
                name = "frequency",
                description = "Frequency in plotting",
                default = 1
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

class MBDynReadLog(bpy.types.Operator):
    """ Imports MBDyn nodes and elements by parsing the .log file """
    bl_idname = "animate.read_mbdyn_log_file"
    bl_label = "MBDyn .log file parsing"

    def execute(self, context):
        ret_val, obj_names = parse_log_file(context)

        missing = context.scene.mbdyn.missing
        if len(obj_names) > 0:
            self.report({'WARNING'}, "Some of the nodes/elements are missing in the new .log file")
            hide_or_delete(obj_names, missing)
            return {'FINISHED'}
        if ret_val == {'LOG_NOT_FOUND'}:
            self.report({'ERROR'}, "MBDyn .log file not found")
            return {'CANCELLED'}
        elif ret_val == {'NODES_NOT_FOUND'}:
            self.report({'ERROR'}, "The .log file selected does not contain MBDyn nodes definitions")
            return {'CANCELLED'}
        elif ret_val == {'MODEL_INCONSISTENT'}:
            self.report({'WARNING'}, "Contents of MBDyn .log file inconsistent with the scene")
            return {'FINISHED'}
        elif ret_val == {'NODES_INCONSISTENT'}:
            self.report({'WARNING'}, "Nodes in MBDyn .log file inconsistent with the scene")
            return {'FINISHED'}
        elif ret_val == {'ELEMS_INCONSISTENT'}:
            self.report({'WARNING'}, "Elements in MBDyn .log file inconsistent with the scene")
            return {'FINISHED'}
        elif ret_val == {'FINISHED'}:
            self.report({'INFO'}, "MBDyn entities imported successfully")
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

        remove_oldframes(context)

        mbs.file_path, mbs.file_basename = path_leaf(self.filepath)
        if self.filepath[-2:] == 'nc':
            try:
                nc = Dataset(self.filepath, "r", format="NETCDF3")
                mbs.use_netcdf = True
                mbs.num_rows = 0
                try:
                    eig_step = nc.variables['eig.step']
                    eig_time = nc.variables['eig.time']
                    eig_dCoef = nc.variables['eig.dCoef']
                    for ii in range(0, len(eig_step)):
                        eigsol = mbs.eigensolutions.add()
                        eigsol.step = eig_step[ii]
                        eigsol.time = eig_time[ii]
                        eigsol.dCoef = eig_dCoef[ii]
                        eigsol.iNVec = nc.dimensions['eig_' + str(ii) + '_iNVec_out'].size
                        eigsol.curr_eigmode = 1
                except KeyError:
                    print('MBDynSelectOutputFile: no eigenanalysis results found')
                    pass
                if HAVE_PLOT:
                    get_plot_vars_glob(self, context)
            except NameError:
                self.report({'ERROR'}, "NetCDF module not imported correctly")
                return {'CANCELLED'}
        else:
            mbs.num_rows = file_len(self.filepath)
        return {'FINISHED'}

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
            self.report({'WARNING'}, "MBDyn labels file provided appears to not contain \
                    correct labels.")
            return {'CANCELLED'}
        elif ret_val == {'LABELS_UPDATED'}:
            self.report({'INFO'}, "MBDyn labels imported")
            return {'FINISHED'}
        elif ret_val == {'FILE_NOT_FOUND'}:
            self.report({'ERROR'}, "MBDyn labels file not found...")
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
        context.scene.mbdyn.nodes.clear()
        context.scene.mbdyn.elems.clear()
        self.report({'INFO'}, "Scene MBDyn data cleared.")
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
        blendyn_path = context.scene.mbdyn.addon_path
        mbdyn_path = context.scene.mbdyn.install_path

        config = {'mbdyn_path': mbdyn_path}
        with open(os.path.join(os.path.dirname(blendyn_path), 'config.json'), 'w') as f:
            json.dump(config, f)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetInstallPath)
# -----------------------------------------------------------
# end of MBDynSetInstallPath class

class MBDynSelectInputFile(bpy.types.Operator, ImportHelper):
    """Set input file's path and basename\
        to be used in MBDyn simulation"""

    bl_idname = "sel.mbdyn_input_file"
    bl_label = "MBDyn input file"

    def execute(self, context):
        mbs = context.scene.mbdyn

        mbs.sim_num = 0

        mbs.input_path = os.path.relpath(self.filepath)
        mbs.input_basename = os.path.splitext(os.path.basename(self.filepath))[0]

        mbs.file_basename = mbs.input_basename

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

    def execute(self, context):
        mbs = context.scene.mbdyn

        for idx in range(len(mbs.env_vars)):
            variable = mbs.env_vars[idx].variable
            value = mbs.env_vars[idx].value

            os.environ[variable] = value

        mbdyn_env = os.environ.copy()

        with open(os.path.join(os.path.dirname(mbs.addon_path), 'config.json'), 'r') as f:
            mbdyn_path = json.load(f)['mbdyn_path']

        mbdyn_env['PATH'] = mbdyn_path + ":" + mbdyn_env['PATH']

        command_line_options = mbs.cmd_options

        command = ('mbdyn {0} {1}').format(command_line_options, mbs.input_path)

        if not mbs.overwrite:
            mbs.sim_num += 1

        if len(mbs.file_basename.split('_')) > 1:
            filename = mbs.file_basename.split('_')
            filename[-1] = str(mbs.sim_num)
            mbs.file_basename = "_".join(filename)

        else:
            mbs.file_basename = ('{0}_{1}').format(mbs.file_basename, mbs.sim_num)

        if mbs.file_path:
            command += (' -o {}').format(mbs.file_path + mbs.file_basename)

        subprocess.call(command + ' &', shell = True, env = mbdyn_env)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynRunSimulation)
# -----------------------------------------------------------
# end of MBDynRunSimulation class

class MBDynStopSimulation(bpy.types.Operator):
    """Stops the MBDyn simulation"""
    bl_idname = "sel.mbdyn_stop_simulation"
    bl_label = "Stop MBDyn Simulation"

    def execute(self, context):
        subprocess.call('kill $(pidof mbdyn)', shell = True)

        self.report({'INFO'}, "The MBDyn simulation was interrupted")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynStopSimulation)
# -----------------------------------------------------------
# end of MBDynStopSimulation class

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
            self.report({'WARNING'}, "MBDyn results file not loaded")
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
        col.prop(mbs, "install_path", text="Path:")
        col.operator(MBDynSetInstallPath.bl_idname, text = 'Set Installation Path')

        row = layout.row()
        row.label(text='Run MBDyn simulation')

        col = layout.column(align = True)
        col.operator(MBDynSelectInputFile.bl_idname, text = 'Select input file')

        col = layout.column(align = True)
        col.prop(mbs, "overwrite", text = "Overwrite Previous Files")

        col = layout.column(align = True)
        col.prop(mbs, "file_path", text = "Output Directory:")

        col = layout.column(align = True)
        col.prop(mbs, "file_basename", text = "Output Filename:")

        col = layout.column(align = True)
        col.prop(mbs, "cmd_options", text = "Command-line options")

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
        col.operator(MBDynRunSimulation.bl_idname, text = 'Run Simulation')

        col = layout.column(align = True)
        col.operator(MBDynStopSimulation.bl_idname, text = 'Stop Simulaton')

# -----------------------------------------------------------
# end of MBDynSimulationPanel class

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

        # Display the active object
        if bpy.context.active_object:
            col = layout.column()
            row = col.row()
            row.label(text="Active Object")
            row = col.row()

            try:
                row.prop(obj, "name")

                if any(item.blender_object == obj.name for item in nd):

                    # Display MBDyn node info
                    row = col.row()

                    # Select MBDyn node
                    col = layout.column(align=True)
                    col.prop(obj.mbdyn, "int_label")
                    col = layout.column(align=True)
                    col.prop(obj.mbdyn, "string_label", text="")
                    col.prop(obj.mbdyn, "parametrization", text="")
                    col.enabled = False

                else:
                    for elem in ed:
                        if elem.blender_object == obj.name:
                            # Display MBDyn elements info
                            row = layout.row()
                            row.label(text = "MBDyn's element info:")

                            eval(elem.info_draw + "(elem, layout)")

                            if elem.update_info_operator != 'none' and elem.is_imported == True:
                                row = layout.row()
                                row.operator(elem.update_info_operator, \
                                        text = "Update element info").elem_key = elem.name
                            if elem.write_operator != 'none' and elem.is_imported == True:
                                row = layout.row()
                                row.operator(elem.write_operator, \
                                        text = "Write element input").elem_key = elem.name
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
            layout.label("", icon = custom_icon)
# -----------------------------------------------------------
# end of MBDynNodes_UL_List class

class MBDynElems_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'CONSTRAINT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)
# -----------------------------------------------------------
# end of MBDynElems_UL_List class

class MBDynPlotVar_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)
# -----------------------------------------------------------
# end of MBDynPLotVar_UL_List class

class MBDynEnvVar_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.variable)
        layout.label(item.value)
# -----------------------------------------------------------
# end of MBDynEnvVar_UL_List class

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

        if mbs.nd_index >= 0 and len(nd):
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
                    text="Add nodes to scene")

            row = layout.row()
            row.operator("add.vertsfromnodes", text="Create vertex grid from nodes")

            row = layout.row()
            row.prop(mbs, "is_vertshook", text="Hook vertices to nodes")
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

        if mbs.ed_index >= 0 and len(mbs.elems):
            item = mbs.elems[mbs.ed_index]

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
# -----------------------------------------------------------
# end of MBDynNodesScenePanel class

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
                    self.report({'ERROR'}, "Could not spawn the Blender object assigned to node " \
                            + str(node.int_label))
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
                print("MBDynNodeImportAllButton: added node " + str(node.int_label) + " to scene and associated with object " + obj.name)
                added_nodes += 1

        if added_nodes:
            self.report({'INFO'}, "All MBDyn nodes imported successfully")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No MBDyn nodes imported")
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
                    self.report({'ERROR'}, "Could not spawn the Blender object assigned to node " \
                            + str(node.int_label))
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
            self.report({'INFO'}, "MBDyn node " + node.string_label + " imported to scene.")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Cannot import MBDyn node " + node.string_label + ".")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Node_Import_Single class

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
                    self.report({'ERROR'}, "Couldn't find the element import function")
                    return {'CANCELLED'}
        return {'FINISHED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Elements_by_Type class

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
                self.report({'ERROR'}, "Rotation parametrization not supported, node " \
                            + obj.mbdyn.string_label)
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
            self.report({'WARNING'}, "No MBDyn nodes associated with selected objects.")
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
