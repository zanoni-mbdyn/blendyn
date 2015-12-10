#lr --------------------------------------------------------------------------
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
from bpy.props import BoolProperty, IntProperty, IntVectorProperty, FloatVectorProperty
from bpy.props import StringProperty, BoolVectorProperty, PointerProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper

import ntpath, os, csv, math
from collections import namedtuple

from .nodelib import *
from .elementlib import *

## Function that parses the .log file and calls parse_joints() to add elements
# to the elements dictionary and parse_node() to add nodes to the nodes dictionary
# TODO: support more joint types
def parse_log_file(context):

    # utility rename
    mbs = context.scene.mbdyn_settings
    nd = mbs.nodes_dictionary
    ed = mbs.elems_dictionary

    is_init_nd = len(nd) == 0
    is_init_ed = len(ed) == 0

    log_file = mbs.file_path + mbs.file_basename + '.log'

    # Debug message to console
    print("parse_log_file(): Trying to read nodes and elements from file: "\
            + log_file)
    try:
        with open(log_file) as lf:
            # open the reader, skipping initial whitespaces
            b_nodes_consistent = True
            b_elems_consistent = True
            reader = csv.reader(lf, delimiter=' ', skipinitialspace=True)
        
            entry = ""
            while entry[:-1] != "Symbol table":
                # get the next row
                rw = next(reader)
            
                entry = rw[0]
                ii = 0
            
                while (rw[ii][-1] != ':') and (ii < min(3, (len(rw) - 1))):
                    ii = ii + 1
                    entry = entry + " " + rw[ii]
            
                if ii == min(3, (len(rw) - 1)):
                    print("parse_log_file(): row does not contain an element definition. Skipping...")
                elif entry == "structural node:":
                    print("parse_log_file(): Found a structural node.")
                    b_nodes_consistent = b_nodes_consistent * (parse_node(context, rw))
                else:
                    print("parse_log_file(): Found " + entry[:-1] + " element.")
                    b_elems_consistent = b_elems_consistent * parse_joint(context, entry[:-1], rw)

            if (is_init_nd and is_init_ed) or (b_nodes_consistent*b_elems_consistent):
                ret_val = {'FINISHED'}
            elif (not(b_nodes_consistent) and not(is_init_nd)) and (not(b_elems_consistent) and not(is_init_ed)):
                ret_val = {'MODEL_INCONSISTENT'}
            elif (not(b_nodes_consistent) and not(is_init_nd)) and (b_elems_consistent):
                ret_val = {'NODES_INCONSISTENT'}
            elif (b_nodes_consistent) and (not(b_elems_consistent) and not(is_init_ed)):
                ret_val = {'ELEMS_INCONSISTENT'}
            else:
                ret_val = {'FINISHED'}
    except IOError:
        print("Could not locate the file " + log_file + ".")
        ret_val = {'LOG_NOT_FOUND'}
        pass
    except StopIteration:
        print("Reached the end of .log file")

    nn = len(nd)
    if nn:
        mbs.num_nodes = nn
        mbs.num_timesteps = mbs.num_rows/nn 
        mbs.is_ready = True
    else:
        ret_val = {'NODES_NOT_FOUND'}
    pass 
    
    return ret_val
# -----------------------------------------------------------
# end of parse_log_file() function 

def path_leaf(path, keep_extension = False):
    """ Helper function to strip filename of path """
    head, tail = ntpath.split(path)
    tail1 = (tail or ntpath.basename(head))
    if keep_extension:
        return path.replace(tail1, ''), tail1
    else:
        return path.replace(tail1, ''), os.path.splitext(tail1)[0]
# -----------------------------------------------------------
# end of path_leaf() function 

def file_len(filepath):
    """ Function to count the number of rows in a file """
    with open(filepath) as f:
        for kk, ll in enumerate(f):
            pass
    return kk + 1
# -----------------------------------------------------------
# end of file_len() function 

def assign_labels(context):
    """ Function that parses the (optional) labels file and assigns \
        the string labels it can find to the respective MBDyn objects """

    mbs = context.scene.mbdyn_settings
    nd = mbs.nodes_dictionary
    ed = mbs.elems_dictionary

    labels_changed = False

    labels_file = mbs.lab_file_path + mbs.lab_file_name
    
    set_strings_node = ["set: const integer Node_", \
                        "set: integer Node_", \
                        "set: const integer node_", \
                        "set: integer node_", \
                        "set: const integer NODE_", \
                        "set: integer NODE_"]

    set_strings_joint = ["set: const integer Joint_", \
                         "set: integer Joint_"
                         "set: const integer joint_", \
                         "set: integer joint_", \
                         "set: const integer JOINT_", \
                         "set: integer JOINT_"]

    set_strings_beam = ["set: const integer Beam_", \
                       "set: integer Beam_", \
                       "set: const integer beam_", \
                       "set: integer beam_", \
                       "set: const integer BEAM_", \
                       "set: integer BEAM_"]

    def assign_label(line, type, set_string, dict):
        line_str = line.rstrip()
        eq_idx = line_str.find('=') + 1
        label_int = int(line_str[eq_idx:-1].strip())
        label_str = line_str[(len(set_string) - len(type) - 1):(eq_idx -1)].strip()
        for item in dict:
            if item.int_label == label_int:
                if item.string_label != label_str:
                    item.string_label = label_str
                    return True
                break
        return False

    try:
        with open(labels_file) as lf:
            for line in lf:
                found = False
                for set_string in set_strings_node:
                    if set_string in line:
                        labels_changed += (assign_label(line, 'node', set_string, nd))
                        found = True
                        break
                if not(found):
                    for set_string in set_strings_joint:
                        if set_string in line:
                            labels_changed += (assign_label(line, 'joint', set_string, ed))
                            found = True
                            break
                if not(found):
                    for set_string in set_strings_beam:
                        if set_string in line:
                            labels_changed += (assign_label(line, 'beam', set_string, ed))
                            found = True
                            break
    except IOError:
        print("assign_labels(): can't find the specified labels file {}, \
                sticking with default labeling...".format(labels_file))
        return {'FILE_NOT_FOUND'}
    
    if labels_changed:
        return {'LABELS_UPDATED'}
    else:
        return {'NOTHING_DONE'}
# -----------------------------------------------------------
# end of assign_labels() function 

                    
def update_label(self, context):
    
    # utility renaming
    obj = context.scene.objects.active
    nd = context.scene.mbdyn_settings.nodes_dictionary 
 
    # Search for int label and assign corresponding string label, if found.
    # If not, signal it by assign the "not found" label
    node_string_label = "not_found"
    obj.mbdyn_settings.is_assigned = False
    for item in nd:
        if item.int_label == obj.mbdyn_settings.int_label:
            node_string_label = item.string_label
            item.blender_object = obj.name
            obj.mbdyn_settings.is_assigned = True
    
    obj.mbdyn_settings.string_label = node_string_label
    if obj.mbdyn_settings.is_assigned:
        ret_val = update_parametrization(obj)

    if ret_val == 'ROT_NOT_SUPPORTED':
        self.report({'ERROR'}, "Rotation parametrization not supported, node " \
            + obj.mbdyn_settings.string_label)
    elif ret_val == 'LOG_NOT_FOUND':
        self.report({'ERROR'}, "MBDyn .log file not found")
    
    return
# -----------------------------------------------------------
# end of update_label() function 

def set_obj_locrot(obj, rw):
   
    axes = {'1': 'X', '2': 'Y', '3': 'Z'}

    # Position
    obj.location[0] = float(rw[1])
    obj.location[1] = float(rw[2])
    obj.location[2] = float(rw[3])
    
    # Orientation
    parametrization = obj.mbdyn_settings.parametrization
    
    if parametrization[0:5] == 'euler':
        euler_seq = axes[parametrization[7]] + axes[parametrization[6]] + axes[parametrization[5]]
        obj.rotation_euler = Euler((math.radians(float(rw[4])), math.radians(float(rw[5])), math.radians(float(rw[6]))), euler_seq)
    elif parametrization == 'phi':
        rotvec = Vector((float(rw[4]), float(rw[5]), float(rw[6])))
        rotvec_norm = rotvec.normalized()
        print(str(rotvec.magnitude), str(rotvec_norm[0]), str(rotvec_norm[1]), str(rotvec_norm[2]))
        obj.rotation_axis_angle = Vector((rotvec.magnitude, rotvec_norm[0], rotvec_norm[1], rotvec_norm[2]))
        pass
    elif parametrization == 'mat':
        R = Matrix((( float(rw[4]), float(rw[5]), float(rw[6]), 0.0),\
                    (float(rw[7]), float(rw[8]), float(rw[9]), 0.0),\
                    (float(rw[10]), float(rw[11]), float(rw[12]), 0.0),\
                    (0.0, 0.0, 0.0, 1.0)))
        obj.rotation_quaternion = R.to_quaternion()
    else:
        print("Error: rotation parametrization not supported (yet...)")
    
    bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot')
    
    return
# -----------------------------------------------------------
# end of set_obj_locrot() function 

## Function that parses the .mov file and sets the motion paths
def set_motion_paths(context):
    # Debug message
    print("Setting Motion Paths...")
    
    # utility renaming
    scene = context.scene
    mbs = scene.mbdyn_settings
    
    # .mov filename
    mov_file = mbs.file_path + mbs.file_basename + '.mov'
    
    # Debug message
    print("Reading from file:", mov_file)
   
    # total number of frames to be animated
    num_frames = int(mbs.num_rows/mbs.num_nodes)
    scene.frame_end = int(num_frames/mbs.load_frequency)

    # list of animatable Blender object types
    anim_types = ['MESH', 'ARMATURE', 'EMPTY']    

    # main loop
    if  mbs.is_ready:
        with open(mov_file) as mf:
            
            # open the reader, skipping initial whitespaces
            reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
            
            # main for loop, from start frame to last 
            for frame in range(scene.frame_end):
                scene.frame_current = (frame + 1)
                for node in range(mbs.num_nodes):
                    rw = next(reader)
                    # cycle animatable objects and set their location and rotation parameters
                    for obj in bpy.data.objects:
                        if (obj.type in anim_types) and obj.mbdyn_settings.is_assigned and int(rw[0]) == obj.mbdyn_settings.int_label:
                            # make sure that the object is selected
                            obj.select = True
                            # set object location and orientation and insert keyframe
                            set_obj_locrot(obj, rw)
                        else:
                            pass
                        for elem in mbs.elems_dictionary:
                            if elem.is_imported:
                                elem.is_updated = False
                if mbs.load_frequency > 1:
                    for ii in range(1, (mbs.load_frequency - 1)*mbs.num_nodes):
                        rw = next(reader)
                
    else:
        return{'CANCELLED'}
    
    return {'FINISHED'}
# -----------------------------------------------------------
# end of set_motion_paths() function 
