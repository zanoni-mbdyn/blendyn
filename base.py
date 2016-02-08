# --------------------------------------------------------------------------
# MBDynImporter -- file base.py
# Copyright (C) 2015 Andrea Zanoni -- andrea.zanoni@polimi.it
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
import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import ntpath, os, csv, math
from collections import namedtuple

from .baselib import *
from .elements import *

## Nodes Dictionary: contains integer/string labels associations
class MBDynNodesDictionary(bpy.types.PropertyGroup):
    int_label = IntProperty(
            name = "node int label",
            description = "",
            )

    string_label = StringProperty(
            name = "node string label",
            description = "",
            default = "none"
            )

    blender_object = StringProperty(
            name = "blender object label",
            description = "",
            default = "none"
            )

    initial_pos = FloatVectorProperty(
            name = "node initial position",
            description = "",
            size = 3,
            precision = 6
            )

    initial_rot = FloatVectorProperty(
            name = "node initial orientation",
            description = "Quaternion holding the node initial orientation",
            size = 4,
            precision = 6
            )

    parametrization = StringProperty(
            name = "Rotation parametrization",
            description = "Rotation parametrization of node.",
            default = "euler123"
            )
bpy.utils.register_class(MBDynNodesDictionary)
# -----------------------------------------------------------
# end of MBDynNodesDictionary class

## Set scene properties
class MBDynSettingsScene(bpy.types.PropertyGroup):
    # Boolean: is the .mov file loaded properly?
    is_loaded = BoolProperty(
            name = "MBDyn files loaded",
            description = "True if MBDyn files are loaded correctly"
            )

    # MBDyn's imported files path
    file_path = StringProperty(
            name = "MBDyn file path",
            description = "Path of MBDyn's imported files",
            default = ""
            )

    # Base name of MBDyn's imported files
    file_basename = StringProperty(
            name = "MBDyn base file name",
            description = "Base file name of MBDyn's imported files",
            default = "not yet loaded"
            )

    # Filename of (optional) labels file
    lab_file_name = StringProperty(
            name = "",
            description = "Name of (optional) MBDyn's labels file",
            default = "not yet loaded"
            )

    lab_file_path = StringProperty(
            name = "MBDyn .lab file path",
            description = "Path of (optional) MBDyn's labels file",
            default = ""
            )

    # Number of rows (output time steps * number of nodes) in MBDyn's .mov file
    num_rows = IntProperty(
            name = "MBDyn .mov file number of rows",
            description = "Total number of rows in MBDyn .mov file, corresponding (total time steps * number of nodes)"
            )

    # Load frequency: if different than 1, the .mov file is read every N time steps
    load_frequency = IntProperty(
            name = "frequency",
            description = "If this value is X, different than 1, then the MBDyn output is loaded every X time steps",
            min = 1,
            default = 1
            )

    # Nodes dictionary -- holds the association between MBDyn nodes and blender objects
    nodes_dictionary = CollectionProperty(
            name = "MBDyn nodes collection",
	    type = MBDynNodesDictionary
            )

    # Nodes dictionary index -- holds the index for displaying the Nodes Dictionary in a UI List
    nd_index = IntProperty(
            name = "MBDyn nodes collection index",
            default = 0
            )

    # Elements dictionary -- holds the collection of the elements defined in the .log file
    elems_dictionary = CollectionProperty(
            name = "MBDyn elements collection",
            type = MBDynElemsDictionary
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

    # Boolean flag that indicates if the .mov file is loaded correctly and the nodes dictionary is ready,
    # used to indicate that all is ready for the object's to be animated        
    is_ready = BoolProperty(
            name = "ready to animate",
            description = "True if .mov file and nodes dictionary loaded correctly",
            )
bpy.utils.register_class(MBDynSettingsScene)
# -----------------------------------------------------------
# end of MBDynSettingsScene class

## MBDynSettings for Blender Object
class MBDynSettingsObject(bpy.types.PropertyGroup): 
    # Boolean: has the current object being assigned an MBDyn's node?
    is_assigned = BoolProperty(
            name = "MBdyn node ok",
            description = "True if the object has been assigned an MBDyn node",
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
    parametrization = StringProperty(
            name = "Rotation parametrization",
            description = "Rotation parametrization of node.",
            default = "euler123"
            )
bpy.utils.register_class(MBDynSettingsObject)
# -----------------------------------------------------------
# end of MBDynSettingsObject class

bpy.types.Scene.mbdyn_settings = PointerProperty(type=MBDynSettingsScene)
bpy.types.Object.mbdyn_settings = PointerProperty(type=MBDynSettingsObject)

class MBDynReadLog(Operator):
    """ Imports MBDyn nodes and elements by parsing the .log file """
    bl_idname = "animate.read_mbdyn_log_file"
    bl_label = "MBDyn .log file parsing"

    def execute(self, context):
        ret_val = parse_log_file(context)
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

class MBDynSelectLabFile(Operator, ImportHelper):
    """ Helper class to set MBDyn's (optional) labels file path """

    bl_idname = "sel.mbdyn_lab_file"
    bl_label = "Select MBDyn labels file"

    filter_glob = StringProperty(
            default = "*.*",
            options = {'HIDDEN'},
            )

    def execute(self, context):
        mbs = context.scene.mbdyn_settings
        mbs.lab_file_path, mbs.lab_file_name = path_leaf(self.filepath, True)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
bpy.utils.register_class(MBDynSelectLabFile)
# -----------------------------------------------------------
# end of MBDynSelectLabFile class

class MBDynSelectMovFile(Operator, ImportHelper):
    """ Helper class to set MBDyn's output files path and basename """

    bl_idname = "sel.mbdyn_mov_file"
    bl_label = "Select MBDyn .mov file"

    filter_glob = StringProperty(
            default = "*.mov",
            options = {'HIDDEN'},
            )

    def execute(self, context):
        mbs = context.scene.mbdyn_settings
        mbs.file_path, mbs.file_basename = path_leaf(self.filepath)
        mbs.num_rows = file_len(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
bpy.utils.register_class(MBDynSelectMovFile)
# -----------------------------------------------------------
# end of MBDynSelectLabFile class

class MBDynAssignLabels(Operator):
    """ Helper class to assign labels to MBDyn nodes and elements \
            provided that a properly formatted .lab file has been \
            selected by the user """
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

class MBDynClearData(Operator):
    """ Clears MBDyn elements and nodes dictionaries, essentially\
    'cleaning' the scene of all MBDyn related data"""
    bl_idname = "mbdyn.cleardata"
    bl_label = "Clear MBDyn Data"

    def execute(self, context):
        context.scene.mbdyn_settings.nodes_dictionary.clear()
        context.scene.mbdyn_settings.elems_dictionary.clear()
        self.report({'INFO'}, "Scene MBDyn data cleared.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynClearData)
# -----------------------------------------------------------
# end of MBDynClearData class

class MBDynSetMotionPaths(Operator):
    """ Sets the motion path for all the objects that have an assigned MBDyn's node """
    bl_idname = "animate.set_mbdyn_motion_path"
    bl_label = "MBDyn Motion Path setter"
    
    def execute(self, context):
        ret_val = set_motion_paths(context)
        if ret_val == 'CANCELLED':
            self.report({'WARNING'}, "MBDyn. mov file not loaded")
        return ret_val

    
    def invoke(self, context, event):
        return self.execute(context)
bpy.utils.register_class(MBDynSetMotionPaths)
# -----------------------------------------------------------
# end of MBDynSetMotionPaths class

class MBDynImportPanel(Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_ImportPath" 
    bl_label = "MBDyn Importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'Animation'
    
    def draw(self, context):
        
        # utility renaming        
        layout = self.layout
        obj = context.object
        sce = context.scene
        nd = sce.mbdyn_settings.nodes_dictionary
        ed = sce.mbdyn_settings.elems_dictionary

        # MBDyn .mov file selection
        row = layout.row()
        row.label(text="MBDyn simulation results")
        col = layout.column(align = True)
        col.operator(MBDynSelectMovFile.bl_idname, text="Select .mov file")

        # Display MBDyn file basename and info
        row = layout.row()
        row.label(text="Loaded .mov file")
        col = layout.column(align=True)
        col.prop(sce.mbdyn_settings, "file_basename", text="")
        col.prop(sce.mbdyn_settings, "num_nodes", text="# of nodes")
        col.prop(sce.mbdyn_settings, "num_rows", text="# of rows")
        col.prop(sce.mbdyn_settings, "num_timesteps", text="# of time steps")
        col.enabled = False

        # Import MBDyn data
        row = layout.row()
        # row.label(text="Load MBDyn data")
        col = layout.column(align = True)
        col.operator(MBDynReadLog.bl_idname, text = "Load .log file")
        
        # MBDyn labels file selection
        row = layout.row()
        row.label(text="MBDyn labels file (opt)")
        col = layout.column(align = True)
        col.operator(MBDynSelectLabFile.bl_idname, text="Select labels file")
        if not(sce.mbdyn_settings.lab_file_name == 'not yet loaded'):
            row = layout.row()
            row.label(text="Loaded labels file")
            col = layout.column(align = True)
            col.prop(sce.mbdyn_settings, "lab_file_name")
            col.enabled = False

        # Assign MBDyn labels to elements in dictionaries
        row = layout.row()
        # row.label(text="Load MBDyn labels")
        col = layout.column(align = True)
        col.operator(MBDynAssignLabels.bl_idname, text = "Load MBDyn labels")
        if sce.mbdyn_settings.lab_file_name == 'not yet loaded':
            col.enabled = False

        # Clear MBDyn data for scene
        row = layout.row()
        row.label(text="Erase all MBDyn data in scene")
        col = layout.column(align = True)
        col.operator(MBDynClearData.bl_idname, text = "CLEAR MBDYN DATA")
        
        # Display the active object 
        row = layout.row()
        try:
            row.label(text="Active object is: " + obj.name)

            if any(item.blender_object == obj.name for item in nd):

                # Display MBDyn node info
                row = layout.row()
                row.label(text = "MBDyn's node label:")
        
                # Select MBDyn node
                col = layout.column(align=True)
                col.prop(obj.mbdyn_settings, "string_label", text="")
                col.prop(obj.mbdyn_settings, "int_label")
                col.prop(obj.mbdyn_settings, "parametrization", text="")

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

        # Insert keyframes for animation
        col = layout.column(align=True)
        col.label(text = "Start animating")
        col.operator(MBDynSetMotionPaths.bl_idname, text = "Animate scene")
        col.prop(sce.mbdyn_settings, "load_frequency")
# -----------------------------------------------------------
# end of MBDynImportPanel class

class MBDynNodes_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # just to test
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
        # just to test
        custom_icon = 'CONSTRAINT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)
# -----------------------------------------------------------
# end of MBDynElems_UL_List class

## Panel in scene properties toolbar that shows the MBDyn 
#  nodes found in the .log file and links to an operator
#  that imports all of them automatically
class MBDynNodesScenePanel(bpy.types.Panel):
    """ List of MBDyn nodes: use import all button to add \
            them all to the scene at once """
    bl_label = "MBDyn node list"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        mbs = context.scene.mbdyn_settings
        layout = self.layout
        row = layout.row()
        row.template_list("MBDynNodes_UL_List", "MBDyn nodes list", mbs, "nodes_dictionary",\
                mbs, "nd_index") 

        if mbs.nd_index >= 0 and len(mbs.nodes_dictionary):
            item = mbs.nodes_dictionary[mbs.nd_index]
            col = layout.column()
            row = layout.row()
            row.prop(item, "int_label")
            row = layout.row()
            row.prop(item, "string_label")
            row = layout.row()
            row.prop(item, "blender_object")
            col.enabled = False
            row = layout.row()
            row.operator("add.mbdynnode_all", text="Add all nodes to scene")
# -----------------------------------------------------------
# end of MBDynNodesScenePanel class

## Panel in scene properties toolbar that shows the MBDyn 
#  elements found in the .log file
class MBDynElemsScenePanel(bpy.types.Panel):
    """ List of MBDyn elements: use import button to add \
            them to the scene  """
    bl_label = "MBDyn elements list"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        mbs = context.scene.mbdyn_settings
        layout = self.layout
        row = layout.row()
        row.template_list("MBDynElems_UL_List", "MBDyn elements list", mbs, "elems_dictionary",\
                mbs, "ed_index") 

        if mbs.ed_index >= 0 and len(mbs.elems_dictionary):
            item = mbs.elems_dictionary[mbs.ed_index]
            col = layout.column()
            row = layout.row()
            row.prop(item, "int_label")
            row = layout.row()
            row.prop(item, "string_label")
            row = layout.row()
            row.operator(item.import_function, text="Add element to the scene").int_label = item.int_label
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
        mbs = context.scene.mbdyn_settings
        nd = mbs.nodes_dictionary
        
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
                row.label(nd_entry.blender_object, icon = "OBJECT_DATA")
                row.operator("sel.mbdynnode", text="ASSIGN").int_label = nd_entry.int_label
            else:
                row.label(nd_entry.blender_object)
                row.operator("sel.mbdynnode", text="ASSIGN").int_label = nd_entry.int_label
                if bpy.data.objects.get(nd_entry.blender_object) == None:
                    row.operator("add.mbdynnode", text="ADD").int_label = nd_entry.int_label
# -----------------------------------------------------------
# end of MBDynOBJNodeSelect class

class MBDynNodeImportAllButton(bpy.types.Operator):
    bl_idname = "add.mbdynnode_all"
    bl_label = "MBDyn add all nodes to scene"

    def execute(self, context):
        nd = context.scene.mbdyn_settings.nodes_dictionary
        added_nodes = 0
        for node in nd:
            bpy.ops.object.empty_add(type = 'ARROWS', location = node.initial_pos)
            obj = context.scene.objects.active
            obj.mbdyn_settings.int_label = node.int_label
            obj.mbdyn_settings.string_label = node.string_label
            obj.mbdyn_settings.parametrization = node.parametrization
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = node.initial_rot
            update_parametrization(obj)
            if obj.mbdyn_settings.string_label != "none":
                obj.name = node.string_label
            else:
                obj.name = node.name
            node.blender_object = obj.name
            obj.mbdyn_settings.is_assigned = True
            print("MBDynNodeImportAllButton: added node " + str(node.int_label) + " to scene and associated with object " + obj.name)
            added_nodes += 1
        
        if added_nodes == len(nd):
            self.report({'INFO'}, "All MBDyn nodes imported successfully")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Some MBDyn nodes were not imported")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of MBDynNodeImportAllButton class

class MBDynNodeAddButton(bpy.types.Operator):
    bl_idname = "add.mbdynnode"
    bl_label = "MBDyn add selected node to scene"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        for node in context.scene.mbdyn_settings.nodes_dictionary:
            if node.int_label == self.int_label:
                node.blender_object = "none"

    def execute(self, context):
        added_node = False
        for node in context.scene.mbdyn_settings.nodes_dictionary:
            if node.int_label == self.int_label:
                bpy.ops.object.empty_add(type = 'ARROWS', location = node.initial_pos)
                obj = context.scene.objects.active
                obj.mbdyn_settings.int_label = node.int_label
                obj.mbdyn_settings.string_label = node.string_label
                obj.mbdyn_settings.parametrization = node.parametrization
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = node.initial_rot
                update_parametrization(obj)
                if obj.mbdyn_settings.string_label != "none":
                    obj.name = node.string_label
                else:
                    obj.name = node.name
                node.blender_object = obj.name
                obj.mbdyn_settings.is_assigned = True
                print("MBDynNodeAddButton: added node " + str(node.int_label) + " to scene and associated with object " + obj.name)
                added_node = True
        if added_node:
            self.report({'INFO'}, "MBDyn node " + node.string_label + " imported to scene.")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Cannot import MBDyn node " + node.string_label + ".") 
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of MBDynNodeAddButton class

class MBDynOBJNodeSelectButton(bpy.types.Operator):
    bl_idname = "sel.mbdynnode"
    bl_label = "MBDyn Node Sel Button"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        axes = {'1': 'X', '2': 'Y', '3': 'Z'}
        context.object.mbdyn_settings.int_label = self.int_label
        ret_val = ''
        for item in context.scene.mbdyn_settings.nodes_dictionary:
            if self.int_label == item.int_label:
                item.blender_object = context.object.name
                ret_val = update_parametrization(context.object)
            if ret_val == 'ROT_NOT_SUPPORTED':
                self.report({'ERROR'}, "Rotation parametrization not supported, node " \
                            + obj.mbdyn_settings.string_label)
            else:
                # DEBUG message to console
                print("Object " + context.object.name + \
                      " MBDyn node association updated to node " + \
                str(context.object.mbdyn_settings.int_label))
        return{'FINISHED'}
# -----------------------------------------------------------
# end of MBDynOBJNodeSelectButton class
