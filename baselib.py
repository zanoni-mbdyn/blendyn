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
from mathutils import *
from math import *

import bpy
from bpy.types import Operator, Panel
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import numpy as np
import ntpath, os, csv, math
from collections import namedtuple

from .nodelib import *
from .elementlib import *

import pdb

try: 
    from netCDF4 import Dataset
except ImportError:
    print("blendyn: could not find netCDF4 module. NetCDF import "\
        + "will be disabled.")

## Function that parses the .log file and calls parse_elements() to add elements
# to the elements dictionary and parse_node() to add nodes to the nodes dictionary
# TODO: support more joint types
def parse_log_file(context):

    # utility rename
    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    is_init_nd = len(nd) == 0
    is_init_ed = len(ed) == 0

    for node_name in nd.keys():
        nd[node_name].is_imported = False

    for elem_name in ed.keys():
        ed[elem_name].is_imported = False

    log_file = mbs.file_path + mbs.file_basename + '.log'

    # Debug message to console
    print("parse_log_file(): Trying to read nodes and elements from file: "\
            + log_file)

    ret_val = {''}

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
                    b_elems_consistent = b_elems_consistent * parse_elements(context, entry[:-1], rw)

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

    del_nodes = [var for var in nd.keys() if nd[var].is_imported == False]
    del_elems = [var for var in ed.keys() if ed[var].is_imported == False]

    obj_names = [nd[var].blender_object for var in del_nodes]
    obj_names += [ed[var].blender_object for var in del_elems]

    obj_names = list(filter(None, obj_names))

    nn = len(nd)
    if nn:
        mbs.num_nodes = nn
        mbs.min_node_import = nd[0].int_label
        mbs.max_node_import = nd[0].int_label
        for ndx in range(1, len(nd)):
            if nd[ndx].int_label < mbs.min_node_import:
                mbs.min_node_import = nd[ndx].int_label
            elif nd[ndx].int_label > mbs.max_node_import:
                mbs.max_node_import = nd[ndx].int_label
        if mbs.use_netcdf:
            ncfile = mbs.file_path + mbs.file_basename + ".nc"
            nc = Dataset(ncfile, "r", format="NETCDF3")
            mbs.num_timesteps = len(nc.variables["time"])
        else:
            mbs.num_timesteps = mbs.num_rows/nn 
        mbs.is_ready = True
        ret_val = {'FINISHED'}
    else:
        ret_val = {'NODES_NOT_FOUND'}
    pass 
    
    out_file = mbs.file_path + mbs.file_basename + '.out'

    with open(out_file) as of:
        reader = csv.reader(of, delimiter=' ', skipinitialspace=True)
        for ii in range(4):
            next(reader)
        mbs.time_step = float(next(reader)[3])

    mbs.end_time = (mbs.num_timesteps - 1) * mbs.time_step

    return ret_val, obj_names
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
    try:
        with open(filepath) as f:
            for kk, ll in enumerate(f):
                pass
        return kk + 1
    except UnboundLocalError:
        return 0
# -----------------------------------------------------------
# end of file_len() function 

def assign_labels(context):
    """ Function that parses the (optional) labels file and assigns \
        the string labels it can find to the respective MBDyn objects """

    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    labels_changed = False
    
    log_file = mbs.file_path + mbs.file_basename + ".log"

    set_strings_node = ["  const integer Node_", \
                        "  integer Node_", \
                        "  const integer node_", \
                        "  integer node_", \
                        "  const integer NODE_", \
                        "  integer NODE_"]

    set_strings_joint = ["  const integer Joint_", \
                         "  integer Joint_"
                         "  const integer joint_", \
                         "  integer joint_", \
                         "  const integer JOINT_", \
                         "  integer JOINT_"]

    set_strings_beam = ["  const integer Beam_", \
                       "  integer Beam_", \
                       "  const integer beam_", \
                       "  integer beam_", \
                       "  const integer BEAM_", \
                       "  integer BEAM_"]

    def assign_label(line, type, set_string, dict):
        line_str = line.rstrip()
        eq_idx = line_str.find('=') + 1
        label_int = int(line_str[eq_idx:].strip())
        label_str = line_str[(len(set_string) - len(type) - 1):(eq_idx -1)].strip()
        for item in dict:
            if item.int_label == label_int:
                if item.string_label != label_str:
                    item.string_label = label_str
                    return True
                break
        return False

    try:
        with open(log_file) as lf:
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
        print("assign_labels(): can't read from file {}, \
                sticking with default labeling...".format(log_file))
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
    nd = context.scene.mbdyn.nodes 
 
    # Search for int label and assign corresponding string label, if found.
    # If not, signal it by assign the "not found" label
    node_string_label = "not_found"
    obj.mbdyn.is_assigned = False
    if obj.mbdyn.type == 'node.struct':
        try:
            key = 'node_' + str(obj.mbdyn.int_label)
            node_string_label = nd[key].string_label
            nd[key].blender_object = obj.name
            obj.mbdyn.is_assigned = True
            obj.mbdyn.string_label = node_string_label

            ret_val = {}
            if obj.mbdyn.is_assigned:
                ret_val = update_parametrization(obj)

            if ret_val == 'ROT_NOT_SUPPORTED':
                self.report({'ERROR'}, "Rotation parametrization not supported, node " \
                + obj.mbdyn.string_label)
            elif ret_val == 'LOG_NOT_FOUND':
                self.report({'ERROR'}, "MBDyn .log file not found")
        except KeyError:
            self.report({'ERROR'}, "Node not found")
            pass
    return
# -----------------------------------------------------------
# end of update_label() function 

## Function that clears the scene of keyframes of current simulation
def remove_oldframes(context):
    mbs = context.scene.mbdyn

    node_names = mbs.nodes.keys()
    obj_names = [bpy.context.scene.mbdyn.nodes[var].blender_object for var in node_names]

    obj_names = list(filter(lambda v: v != 'none', obj_names))
    obj_names = list(filter(lambda v: v in bpy.data.objects.keys(), obj_names))

    if len(obj_names) > 0:
       obj_list = [bpy.data.objects[var] for var in obj_names]
       for obj in obj_list:
           obj.animation_data_clear()
           obj.hide = False
# -----------------------------------------------------------
# end of remove_oldframes() function		

def hide_or_delete(obj_names, missing):

    obj_list = [bpy.data.objects[var] for var in obj_names]
    obj_list = [bpy.data.objects[var] for var in obj_names]

    if missing == "HIDE":
        obj_list = [bpy.data.objects[var] for var in obj_names]

        for obj in obj_list:
            obj.hide = True

    if missing == "DELETE":
        bpy.ops.object.select_all(action='DESELECT')
        for obj in obj_list:
            obj.select = True
            bpy.ops.object.delete()

## Function that parses the .mov file and sets the motion paths
def set_motion_paths_mov(context):

    # Debug message
    print("Setting Motion Paths using .mov output...")

    # utility renaming
    scene = context.scene
    mbs = scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    wm = context.window_manager

    if not(mbs.is_ready):
        return {'CANCELLED'}

    # .mov filename
    mov_file = mbs.file_path + mbs.file_basename + '.mov'
    
    # Debug message
    print("Reading from file:", mov_file)
   
    # total number of frames to be animated
    num_frames = int(mbs.num_rows/mbs.num_nodes)
    scene.frame_start = round(mbs.start_time/mbs.time_step)
    scene.frame_end = round(mbs.end_time/mbs.time_step) + 1

    # list of animatable Blender object types
    anim_types = ['MESH', 'ARMATURE', 'EMPTY']    

    # Cycle to establish which objects to animate
    anim_objs = dict()

    wm.progress_begin(scene.frame_start, scene.frame_end)
    try:
        with open(mov_file) as mf:
            reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
            # first loop: we establish which object to animate
            scene.frame_current = round(scene.frame_start / mbs.load_frequency)

            for ndx in range(scene.frame_start * mbs.num_nodes):
                next(reader)

            first = []
            for ndx in range(mbs.num_nodes):
                rw = np.array(next(reader)).astype(np.float)
                first = rw

                obj_name = nd['node_' + str(int(rw[0]))].blender_object
                if obj_name != 'none':
                    anim_objs[rw[0]] = obj_name
                    obj = bpy.data.objects[obj_name]
                    obj.select = True
                    set_obj_locrot_mov(obj, rw)

            # main for loop, from second frame to last
            freq = mbs.load_frequency
            Nskip = 0
            if freq > 1:
                Nskip = (np.ceil(freq) - 1)*mbs.num_nodes

            for idx, frame in enumerate(np.arange(scene.frame_start + freq, scene.frame_end, freq)):
                scene.frame_current += 1
                frac = np.ceil(frame) - frame

                print(frame, frac)

                # skip (freq - 1)*N lines
                for ii in range(int(Nskip) - idx%2):
                    first = np.array(next(reader)).astype(np.float)

                for ndx in range(mbs.num_nodes):
                    rw = np.array(next(reader)).astype(np.float)
                    second = rw
                    try:
                        answer = frac*first + (1-frac)*second
                        obj = bpy.data.objects[anim_objs[answer[0]]]
                        obj.select = True
                        set_obj_locrot_mov(obj, answer)

                    except KeyError:
                        pass

                    first = second
                wm.progress_update(scene.frame_current)
    except StopIteration:
        pass
    wm.progress_end()

    # Update deformable elements
    

    # Gets simulation time (FIXME: not the most clean and efficient way, for sure...)
    if mbs.simtime:
        mbs.simtime.clear()

    out_file = mbs.file_path + mbs.file_basename + '.out'
    try:
        with open(out_file) as of:
            reader = csv.reader(of, delimiter=' ', skipinitialspace=True)
            for ii in range(3):
                next(reader)

            for ii in range(scene.frame_start):
                next(reader)
                mbs.simtime.add()

            kk = scene.frame_start
            jj = scene.frame_start
            while kk < scene.frame_end:
                rw = next(reader)
                if int(rw[8]):
                    jj = jj + 1
                    if (jj - 1) == kk*mbs.load_frequency:
                        st = mbs.simtime.add()
                        st.time = float(rw[2])
                        kk = kk + 1
    except StopIteration:
        pass

    return {'FINISHED'}
# -----------------------------------------------------------
# end of set_motion_paths_mov() function 

def set_motion_paths_netcdf(context):

    scene = context.scene
    mbs = scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems 
    wm = context.window_manager

    ncfile = mbs.file_path + mbs.file_basename + '.nc'
    nc = Dataset(ncfile, "r", format="NETCDF3")
    nctime = nc.variables["time"]

    mbs.time_step = nctime[1]

    freq = mbs.load_frequency
    # scene.frame_end = len(nctime)/freq - 1

    scene.frame_start = round(mbs.start_time/(freq*mbs.time_step))
    scene.frame_end = round(mbs.end_time/(freq*mbs.time_step)) + 1

    anim_nodes = list()
    for node in nd:
        if node.blender_object != 'none':
            anim_nodes.append(node.name)

    scene.frame_current = scene.frame_start
    if mbs.simtime:
        mbs.simtime.clear()

    # set time
    for frame in range(scene.frame_start):
        mbs.simtime.add()

    for frame in range(scene.frame_start, scene.frame_end):
        tdx = frame*freq
        st = mbs.simtime.add()
        st.time = nctime[tdx]
    
    # set objects location and rotation
    wm.progress_begin(1, len(anim_nodes))

    kk = 0
    for ndx in anim_nodes:
        obj = bpy.data.objects[nd[ndx].blender_object]
        obj.select = True
        node_var = 'node.struct.' + str(nd[ndx].int_label) + '.'
        if obj.mbdyn.parametrization[0:5] == 'EULER':
            for frame in range(scene.frame_start, scene.frame_end):
                scene.frame_current = frame
                tdx = frame*freq
                
                obj.location = Vector(( nc.variables[node_var + 'X'][tdx, :] ))
                obj.keyframe_insert(data_path = "location")
            
                obj.rotation_euler = \
                        Euler( Vector(( math.radians(1.0)*(nc.variables[node_var + 'E'][tdx, :]) )),
                                axes[obj.mbdyn.parametrization[7]] +\
                                axes[obj.mbdyn.parametrization[6]] +\
                                axes[obj.mbdyn.parametrization[5]] )
                obj.keyframe_insert(data_path = "rotation_euler")
        elif obj.mbdyn.parametrization == 'PHI':
            for frame in range(scene.frame_start, scene.frame_end):
                scene.frame_current = frame
                tdx = frame*freq

                obj.location = Vector(( nc.variables[node_var + 'X'][tdx, :] ))
                obj.keyframe_insert(data_path = "location")

                rotvec = Vector(( nc.variables[node_var + 'Phi'][tdx, :] ))
                rotvec_norm = rotvec.normalized()
                obj.rotation_axis_angle = Vector (( rotvec.magnitude, \
                        rotvec_norm[0], rotvec_norm[1], rotvec_norm[2] ))
                obj.keyframe_insert(data_path = "rotation_axis_angle")
        elif obj.mbdyn.parametrization == 'MATRIX':
            for frame in range(scene.frame_start, scene.frame_end):
                scene.frame_current = frame
                tdx = frame*freq

                obj.location = Vector(( nc.variables[node_var + 'X'][tdx, :] ))
                obj.keyframe_insert(data_path = "location")

                R = Matrix(( nc.variables[node_var + 'R'][tdx, :] ))
                obj.rotation_quaternion = R.to_quaternion()
                obj.keyframe_insert(data_path = "rotation_quaternion")
        else:
            # Should not be reached
            print("set_motion_paths_netcdf() Error: unrecognised rotation parametrization")
            return {'CANCELLED'}
        obj.select = False
        kk = kk + 1
        wm.progress_update(kk)
    wm.progress_end()

    return {'FINISHED'}

# -----------------------------------------------------------
# end of set_motion_paths_netcdf() function 
