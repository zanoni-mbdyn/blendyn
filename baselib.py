# --------------------------------------------------------------------------
# Blendyn -- file baselib.py
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

from mathutils import *
from math import *

import bpy
from bpy.types import Operator, Panel
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import logging

import numpy as np

import ntpath, os, csv, math, atexit, re

from collections import namedtuple

from .nodelib import *
from .elementlib import *
from .rfmlib import *
from .logwatcher import *

HAVE_PSUTIL = False
try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    pass

import os, time
try:
    from netCDF4 import Dataset
except ImportError:
    print("Blendyn: could not find netCDF4 module. NetCDF import "\
        + "will be disabled.")
    pass

def parse_input_file(context):
    mbs = context.scene.mbdyn

    out_file = mbs.input_path

    with open(out_file) as of:
        reader = csv.reader(of, delimiter=' ', skipinitialspace=True)

        while True:
            rw = next(reader)
            print(rw)
            if rw:
                first = rw[0].strip()

            if first == 'final':
                time = rw[2]

                try:
                    time = float(time[:-1])

                except ValueError:
                    mbs.final_time = mbs.ui_time
                    break

                mbs.final_time = time
                mbs.ui_time = time

                break

if HAVE_PSUTIL:
    def kill_mbdyn():
        mbdynProc = [var for var in psutil.process_iter() if var.name() == 'mbdyn']

        if mbdynProc:
            mbdynProc[0].kill()

def get_plot_vars_glob(context):
    mbs = context.scene.mbdyn
    if mbs.use_netcdf:
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.nc')
        nc = Dataset(ncfile, 'r', format='NETCDF3')
        N = len(nc.variables["time"])

        var_list = list()
        for var in nc.variables:
            m = nc.variables[var].shape
            if (m[0] == N) and (var not in mbs.plot_vars.keys()):
                plotvar = mbs.plot_vars.add()
                plotvar.name = var

## Function that sets up the data for the import process
def setup_import(filepath, context):
    mbs = context.scene.mbdyn
    mbs.file_path, mbs.file_basename = path_leaf(filepath)
    if filepath[-2:] == 'nc':
        nc = Dataset(filepath, "r", format="NETCDF3")
        mbs.use_netcdf = True
        mbs.num_rows = 0
        try:
            eig_step = nc.variables['eig.step']
            eig_time = nc.variables['eig.time']
            eig_dCoef = nc.variables['eig.dCoef']
            NVecs = [dim for dim in nc.dimensions if 'iNVec_out' in dim]

            for ii in range(0, len(NVecs)):
                eigsol = mbs.eigensolutions.add()
                eigsol.index = float(NVecs[ii][4:-10])
                eigsol.step = eig_step[eigsol.index]
                eigsol.time = eig_time[eigsol.index]
                eigsol.dCoef = eig_dCoef[eigsol.index]
                eigsol.iNVec = nc.dimensions[NVecs[ii]].size
                eigsol.curr_eigmode = 1
        except KeyError:
            message = 'MBDynSelectOutputFile::setup_import() INFO: ' + \
                    'no valid eigenanalysis results found'
            print(message)
            logging.warning(message)
            pass

        get_plot_vars_glob(context)
    else:
        mbs.use_netcdf = False
        mbs.num_rows = file_len(filepath)
        if mbs.num_rows < 0:
            return {'FILE_ERROR'}
    return {'FINISHED'}

# -----------------------------------------------------------
# end of setup_import() function

def no_output(context):
    """Check for nodes with no output"""
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if mbs.use_netcdf:
        ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.nc')
        nc = Dataset(ncfile, "r", format="NETCDF3")
        list1 = nc.variables.keys()
        regex = re.compile(r'node.struct.*\.X$')
        list2 = list(filter(regex.search, list1))
        result_nodes = list(map(lambda x: x.split('.')[2], list2))
        log_nodes = list(map(lambda x: x[5:], nd.keys()))
        difference = set(result_nodes) ^ set(log_nodes)
        difference = ' '.join(difference)
        print(difference)
        mbs.disabled_output = difference

    else:
        # .mov filename
        mov_file = os.path.join(os.path.dirname(mbs.file_path), \
                mbs.file_basename + '.mov')
        try:
            with open(mov_file) as mf:
                reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
                list1 = []
                for ii in range(len(nd)):
                    rw = next(reader)
                    list1.append(rw[0])

                result_nodes = list1
                log_nodes = list(map(lambda x: x[5:], nd.keys()))
                difference = set(result_nodes) ^ set(log_nodes)
                difference = ' '.join(difference)
                print(difference)
                mbs.disabled_output = difference
        except FileNotFoundError:
            pass
        except StopIteration:
            pass
# -----------------------------------------------------------
# end of no_output() function

## Function that parses the .log file and calls parse_elements() to add elements
# to the elements dictionary and parse_node() to add nodes to the nodes dictionary
# TODO:support more joint types
def parse_log_file(context):

    # utility rename
    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems
    rd = mbs.references

    is_init_nd = len(nd) == 0
    is_init_ed = len(ed) == 0

    for node_name in nd.keys():
        nd[node_name].is_imported = False

    for elem_name in ed.keys():
        ed[elem_name].is_imported = False

    log_file = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.log')
    
    out_file = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.out')
    
    rfm_file = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.rfm')
    
    # Debug message to console
    print("Blendyn::parse_log_file(): Trying to read nodes and elements from file: "\
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
                    print("Blendyn::parse_log_file(): row does not contain an element definition. Skipping...")
                elif entry == "structural node:":
                    print("Blendyn::parse_log_file(): Found a structural node.")
                    b_nodes_consistent = b_nodes_consistent * (parse_node(context, rw))
                else:
                    print("Blendyn::parse_log_file(): Found " + entry[:-1] + " element.")
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
        print("Blendyn::parse_log_file(): Could not locate the file " + log_file + ".")
        ret_val = {'LOG_NOT_FOUND'}
        pass
    except StopIteration:
        print("Blendyn::parse_log_file() Reached the end of .log file")

    del_nodes = [var for var in nd.keys() if nd[var].is_imported == False]
    del_elems = [var for var in ed.keys() if ed[var].is_imported == False]

    obj_names = [nd[var].blender_object for var in del_nodes]
    obj_names += [ed[var].blender_object for var in del_elems]

    obj_names = list(filter(None, obj_names))

    nn = len(nd)

    # Account for nodes with no output

    if nn:
        no_output(context)

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
            ncfile = os.path.join(os.path.dirname(mbs.file_path), \
                    mbs.file_basename + '.nc')
            nc = Dataset(ncfile, "r", format="NETCDF3")
            mbs.num_timesteps = len(nc.variables["time"])
        else:
            disabled_nodes = 0 if len(mbs.disabled_output) == 0 else len(mbs.disabled_output.split(' '))
            mbs.num_timesteps = mbs.num_rows/(nn - disabled_nodes)
        mbs.is_ready = True
        ret_val = {'FINISHED'}
    else:
        ret_val = {'NODES_NOT_FOUND'}
    pass

    en = len(ed)
    if en:
        mbs.min_elem_import = ed[0].int_label
        mbs.max_elem_import = ed[0].int_label
        for edx in range(1, len(ed)):
            if ed[edx].int_label < mbs.min_elem_import:
                mbs.min_elem_import = ed[edx].int_label
            elif ed[edx].int_label > mbs.max_elem_import:
                mbs.max_elem_import = ed[edx].int_label

    try:
        with open(out_file) as of:
            reader = csv.reader(of, delimiter = ' ', skipinitialspace = True)
            while True:
                if next(reader)[0] == 'Step':
                  mbs.time_step = float(next(reader)[3])
                  break
    except FileNotFoundError:
        print("Blendyn::parse_log_file(): Could not locate the file " + out_file)
        ret_val = {'OUT_NOT_FOUND'}
        pass
    except StopIteration:
        print("Blendyn::parse_log_file(): Reached the end of .out file")
    except IOError:
        print("Blendyn::parse_log_file(): Could not read the file " + out_file)
        pass

    try:
        with open(rfm_file) as rfm:
            reader = csv.reader(rfm, delimiter = ' ', skipinitialspace = True)
            for rfm_row in reader:
                if len(rfm_row) and rfm_row[0].strip() != '#':
                        parse_reference_frame(rfm_row, rd)
    except StopIteration:
        pass
    except FileNotFoundError:
        print("Blendyn::parse_out_file(): Could not locate the file " + rfm_file)
        pass
    except IOError:
        print("Blendyn::parse_out_file(): Could not read the file " + rfm_file)
        pass 

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
    except IsADirectoryError:
        return 0
# -----------------------------------------------------------
# end of file_len() function

def assign_labels(context):
    """ Function that parses the (optional) labels file and assigns \
        the string labels it can find to the respective MBDyn objects """

    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems
    rd = mbs.references

    labels_changed = False

    log_file = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.log')

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

    set_strings_refs = ["  const integer Ref_", \
                        "  integer Ref_", \
                        "  const integer ref_", \
                        "  integer ref_", \
                        "  const integer REF_", \
                        "  integer REF_", \
                        "  const integer Reference_", \
                        "  integer Reference_", \
                        "  const integer reference_", \
                        "  integer reference_", \
                        "  const integer REFERENCE_", \
                        "  integer REFERENCE_"]

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
                if not (found):
                    for set_string in set_strings_refs:
                        if set_string in line:
                            labels_changed += (assign_label(line, 'ref', set_string, rd))
                            found = True
                            break
    except IOError:
        print("Blendyn::assign_labels(): can't read from file {}, \
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
                message = "Rotation parametrization not supported, node " \
                + obj.mbdyn.string_label
                self.report({'ERROR'}, message)
                logging.error(message)

            elif ret_val == 'LOG_NOT_FOUND':
                message = "MBDyn .log file not found"
                self.report({'ERROR'}, message)
                logging.error(message)

        except KeyError:
            message = "Node not found"
            self.report({'ERROR'}, message)
            logging.error(message)
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
# -----------------------------------------------------------
# end of remove_oldframes() function

def hide_or_delete(obj_names, missing):

    obj_names = list(filter(lambda v: v != 'none', obj_names))
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
    print("Blendyn::set_motion_paths_mov(): Setting Motion Paths using .mov output...")

    # utility renaming
    scene = context.scene
    mbs = scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    wm = context.window_manager

    if not(mbs.is_ready):
        return {'CANCELLED'}

    # .mov filename
    mov_file = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.mov')

    # Debug message
    print("Blendyn::set_motion_paths_mov(): Reading from file:", mov_file)

    # total number of frames to be animated
    scene.frame_start = int(mbs.start_time/(mbs.time_step * mbs.load_frequency))
    scene.frame_end = int(mbs.end_time/(mbs.time_step * mbs.load_frequency)) + 1

    loop_start = int(scene.frame_start * mbs.load_frequency)
    loop_end = int(scene.frame_end * mbs.load_frequency)

    # list of animatable Blender object types
    anim_types = ['MESH', 'ARMATURE', 'EMPTY']

    # Cycle to establish which objects to animate
    anim_objs = dict()

    wm.progress_begin(scene.frame_start, scene.frame_end)
    try:
        with open(mov_file) as mf:
            reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
            # first loop: we establish which object to animate
            scene.frame_current = scene.frame_start

            disabled_nodes = 0 if len(mbs.disabled_output) == 0 else len(mbs.disabled_output.split(' '))
            nodes_iterate = mbs.num_nodes - disabled_nodes

            for ndx in range(int(mbs.start_time * nodes_iterate / mbs.time_step)):
                next(reader)

            first = []
            second = []
            for ndx in range(nodes_iterate):
                rw = np.array(next(reader)).astype(np.float)
                first.append(rw)
                second.append(rw)

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
                Nskip = (np.ceil(freq) - 1)*nodes_iterate

            for idx, frame in enumerate(np.arange(loop_start + freq, loop_end, freq)):
                scene.frame_current += 1
                frac = np.ceil(frame) - frame

                # skip (freq - 1)*N lines
                for ii in range(int(Nskip) - (idx%2)*nodes_iterate):
                    first[ii % nodes_iterate] = np.array(next(reader)).astype(np.float)

                for ndx in range(nodes_iterate):
                    rw = np.array(next(reader)).astype(np.float)
                    second[ndx] = rw

                for ndx in range(nodes_iterate):
                    try:
                        answer = frac*first[ndx] + (1-frac)*second[ndx]
                        obj = bpy.data.objects[anim_objs[round(answer[0])]]
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

    for ii in np.arange(0, loop_start, mbs.load_frequency):
        mbs.simtime.add()

    for ii in np.arange(loop_start, loop_end, mbs.load_frequency):
        st = mbs.simtime.add()
        st.time = mbs.time_step * ii

    return {'FINISHED'}
# -----------------------------------------------------------
# end of set_motion_paths_mov() function

def active_object_rel(bool1, bool2):
    if not bool1:
        return True
    if bool1:
        if bool2:
            return True
        else:
            return False

def get_render_vars(self, context):
    mbs = context.scene.mbdyn
    ed = mbs.elems
    ncfile = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.nc')
    nc = Dataset(ncfile, "r", format="NETCDF3")
    units = ['m/s', 's', 'm', 'N', 'Nm']
    render_vars = list(filter( lambda x: hasattr(nc.variables[x], 'units'), nc.variables.keys() ))
    render_vars = list(filter( lambda x: nc.variables[x].units in units, render_vars ))

    scene_objs = [ str(var.int_label) for var in ed if bpy.data.objects[var.blender_object].select ]
    render_vars = list(filter( lambda x: active_object_rel('elem' in x, \
                   any(i in scene_objs for i in x.split('.'))), render_vars))
    return [(var, var, "") for var in render_vars]
# -----------------------------------------------------------
# end of get_render_vars() function

def get_display_group(self, context):
    mbs = context.scene.mbdyn

    dg = mbs.display_vars_group

    return [(group_name, group_name, "") for group_name in dg.keys()]

def netcdf_helper(nc, scene, key):
    mbs = scene.mbdyn
    freq = mbs.load_frequency
    tdx = scene.frame_current * freq
    frac = np.ceil(tdx) - tdx

    first = nc.variables[key][int(tdx)]
    second = nc.variables[key][int(np.ceil(tdx))]
    answer = first * frac + second * (1-frac)

    return answer

def parse_render_string(var, components):
    if hasattr(var, '__iter__'):
        return ', '.join(['{:.2f}'.format(item) if components[idx] else ' ' for idx, item in enumerate(var)])

    else:
        return '{:.2f}'.format(var)

def comp_repr(components, value, context):
    mbs = context.scene.mbdyn
    ncfile = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.nc')
    nc = Dataset(ncfile, "r", format="NETCDF3")
    var = nc.variables[value]
    dim = len(var.shape)

    comps = ''

    if dim == 2:
        n,m = var.shape
        comps = [str(mdx + 1) for mdx in range(m) if components[mdx] is True]
        comps = ','.join(comps)

    elif dim == 3:
        n,m,k = var.shape
        if mbs.plot_var[-1] == 'R':
            dims_names = ["(1,1)", "(1,2)", "(1,3)", "(2,2)", "(2,3)", "(3,3)"]

        else:
            dims_names = ["(1,1)", "(1,2)", "(1,3)",\
                          "(2,1)", "(2,2)", "(2,3)",\
                          "(3,1)", "(3,2)", "(3,3)"]

        comps = [ dims_names[mdx] for mdx in range(len(dims_names)) if components[mdx] is True]

    else:
        pass

    comps = '[' + comps+']' if comps else comps

    return comps

def set_motion_paths_netcdf(context):

    scene = context.scene
    mbs = scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems
    wm = context.window_manager

    ncfile = os.path.join(os.path.dirname(mbs.file_path), \
            mbs.file_basename + '.nc')
    nc = Dataset(ncfile, "r", format="NETCDF3")
    nctime = nc.variables["time"]

    mbs.time_step = nctime[1]

    freq = mbs.load_frequency
    # scene.frame_end = len(nctime)/freq - 1

    scene.frame_start = int(mbs.start_time/(mbs.time_step * mbs.load_frequency))
    scene.frame_end = int(mbs.end_time/(mbs.time_step * mbs.load_frequency)) + 1

    anim_nodes = list()
    for node in nd:
        if node.blender_object != 'none':
            anim_nodes.append(node.name)

    scene.frame_current = scene.frame_start

    loop_start = int(scene.frame_start * mbs.load_frequency)
    loop_end = int(scene.frame_end * mbs.load_frequency)

    if mbs.simtime:
        mbs.simtime.clear()

    for ii in np.arange(0, loop_start, mbs.load_frequency):
        mbs.simtime.add()

    for ii in np.arange(loop_start, loop_end, mbs.load_frequency):
        st = mbs.simtime.add()
        st.time = mbs.time_step * ii

    # set objects location and rotation
    wm.progress_begin(1, len(anim_nodes))

    kk = 0
    for ndx in anim_nodes:

        if str(nd[ndx].int_label) in mbs.disabled_output.split(' '):
            continue

        obj = bpy.data.objects[nd[ndx].blender_object]
        obj.select = True
        node_var = 'node.struct.' + str(nd[ndx].int_label) + '.'
        if obj.mbdyn.parametrization[0:5] == 'EULER':
            for frame in range(scene.frame_start, scene.frame_end):
                scene.frame_current = frame

                answer = netcdf_helper(nc, scene, node_var + 'X')
                obj.location = Vector((answer))
                obj.keyframe_insert(data_path = "location")

                answer = math.radians(1.0)*netcdf_helper(nc, scene, node_var + 'E')
                obj.rotation_euler = \
                        Euler( Vector((answer)),
                                axes[obj.mbdyn.parametrization[7]] +\
                                axes[obj.mbdyn.parametrization[6]] +\
                                axes[obj.mbdyn.parametrization[5]] )
                obj.keyframe_insert(data_path = "rotation_euler")
        elif obj.mbdyn.parametrization == 'PHI':
            for frame in range(scene.frame_start, scene.frame_end):
                scene.frame_current = frame

                answer = netcdf_helper(nc, scene, node_var + 'X')
                obj.location = Vector((answer))
                obj.keyframe_insert(data_path = "location")

                answer = netcdf_helper(nc, scene, node_var + 'Phi')
                rotvec = Vector((answer))
                rotvec_norm = rotvec.normalized()
                obj.rotation_axis_angle = Vector (( rotvec.magnitude, \
                        rotvec_norm[0], rotvec_norm[1], rotvec_norm[2] ))
                obj.keyframe_insert(data_path = "rotation_axis_angle")
        elif obj.mbdyn.parametrization == 'MATRIX':
            for frame in range(scene.frame_start, scene.frame_end):
                scene.frame_current = frame

                answer = netcdf_helper(nc, scene, node_var + 'X')
                obj.location = Vector((answer))
                obj.keyframe_insert(data_path = "location")

                answer = netcdf_helper(nc, scene, node_var + 'R')
                R = Matrix((answer))
                obj.rotation_quaternion = R.to_quaternion()
                obj.keyframe_insert(data_path = "rotation_quaternion")
        else:
            # Should not be reached
            print("Blendyn::set_motion_paths_netcdf() Error: unrecognised rotation parametrization")
            return {'CANCELLED'}
        obj.select = False
        kk = kk + 1
        wm.progress_update(kk)
    wm.progress_end()

    return {'FINISHED'}

# -----------------------------------------------------------
# end of set_motion_paths_netcdf() function
class BlenderHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        editor = bpy.data.texts[os.path.basename(logFile)]
        editor.write(log_entry + '\n')

def log_messages(mbs, baseLogger, saved_blend):
        try:
	        blendFile = os.path.basename(bpy.data.filepath) if bpy.data.is_saved \
	                    else 'untitled.blend'
	        blendFile = os.path.splitext(blendFile)[0]
	
	        formatter = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
	        datefmt = '%m/%d/%Y %I:%M:%S %p'
	        global logFile
	        logFile = ('{0}_{1}.bylog').format(mbs.file_path + blendFile, mbs.file_basename)
	
	        fh = logging.FileHandler(logFile)
	        fh.setFormatter(logging.Formatter(formatter, datefmt))
	
	        custom = BlenderHandler()
	        custom.setFormatter(logging.Formatter(formatter, datefmt))
	
	        baseLogger.addHandler(fh)
	        baseLogger.addHandler(custom)
	
	        if not saved_blend:
	            bpy.data.texts.new(os.path.basename(logFile))
        except PermissionError as ex:
            print("Blendyn::BlenderHandler::log_messages(): " +\
                    "caught PermissionError exception {0}".format(ex))

def delete_log():
    mbs = bpy.context.scene.mbdyn

    if not(bpy.data.is_saved) or mbs.del_log:
        try:
            os.remove(logFile)
            print("Blendyn::delete_log(): removed file" + logFile)
        except NameError as ex:
            print("Blendyn::delete_log(): NameError:" + str(e))
            pass

def logging_shutdown():
    print("Blendyn::logging_shutdown(): shutting down logs.")
    logging.shutdown()

atexit.register(delete_log)
atexit.register(logging_shutdown)
