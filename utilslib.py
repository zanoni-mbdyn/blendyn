# --------------------------------------------------------------------------
# Blendyn -- file utilslib.py
# Copyright (C) 2015 -- 2019 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import logging
baseLogger = logging.getLogger()
baseLogger.setLevel(logging.DEBUG)

from mathutils import *
from math import *
from bpy.types import Operator
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import csv

class BLENDYN_OT_load_section(bpy.types.Operator, ImportHelper):
    """ Loads profile to assign to curve bevel, in Selig format """
    bl_idname = "blendyn.load_section"
    bl_label = "Load NACA profile in Selig format"

    filter_glob = bpy.props.StringProperty(
        default = "*.*",
        options = {'HIDDEN'},
        )

    def execute(self, context):
        try:
            with open(self.filepath, 'r') as sf:     
                reader = csv.reader(sf, delimiter=' ', skipinitialspace=True)
                name = next(reader)
                cvdata = bpy.data.curves.new(' '.join(name), 'CURVE')
                cvdata.dimensions = '2D'

                # if the curve already exists, Blender changes the name of the newly created one
                name = cvdata.name
                poly = cvdata.splines.new('POLY')

                # first point
                row = next(reader)
                poly.points[0].co = Vector(( float(row[0]), float(row[1]), 0.0, 0.0 ))

                # other points
                for row in reader:
                    poly.points.add(1)
                    poly.points[-1].co = Vector(( float(row[0]), float(row[1]), 0.0, 0.0 ))

                obj = bpy.data.objects.new(name, cvdata)
                context.scene.objects.link(obj)
            
                kk = 0
                layer_objs = [ob for ob in bpy.context.scene.objects if ob.layers[kk]]
                try:
                    while len(layer_objs):
                        kk = kk + 1
                        layer_objs.clear()
                        layer_objs = [ob for ob in bpy.context.scene.objects if ob.layers[kk]]
                    obj.layers[kk] = True
                    for jj in range(len(obj.layers)):
                        if jj != kk:
                            obj.layers[jj] = False
                except IndexError:
                    message = "BLENDYN_OT_load_section::execute(): "\
                            + "Couldn't find an empty layer. Using the active layer"
                    self.report({'INFO'}, message)
                    baseLogger.info(message)
                    pass
                
                # context.curve.bevel_object = obj

                for item in bpy.context.scene.objects:
                    if ('beam3_' in item.name) and item.select:
                        try:
                            item.data.bevel_object = obj
                        except AttributeError:
                            pass

                return {'FINISHED'}
        except IOError:
            message = "BLENDYN_OT_load_section::execute(): "\
                    + "Could not locate the selected file"
            self.report({'ERROR'}, message)
            baseLogger.error(message)
            return {'CANCELLED'}
        except StopIteration:
            message = "BLENDYN_OT_load_section::execute(): "\
                    + "Unespected end of file"
            self.report({'WARNING'}, message)
            baseLogger.warning(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of fmin function BLENDYN_OT_load_section class


## Utility functions
def fmin(x):
    min = x[0]
    loc = 0
    for idx in range(1, len(x)):
        if x[idx] < min:
            min = x[idx]
            loc = idx
    return (min, loc)
# -----------------------------------------------------------
# end of fmin function

def fmax(x):
    max = x[0]
    loc = 0
    for idx in range(1, len(x)):
        if x[idx] > max:
            max = x[idx]
            loc = idx
    return (max, loc)
# -----------------------------------------------------------
# end of fmax function

def parse_rotmat(rw, idx, R): 
    R[0][0] = float(rw[idx])
    R[0][1] = float(rw[idx + 1])
    R[0][2] = float(rw[idx + 2])
    R[1][0] = float(rw[idx + 3])
    R[1][1] = float(rw[idx + 4])
    R[1][2] = float(rw[idx + 5])
    R[2][0] = float(rw[idx + 6])
    R[2][1] = float(rw[idx + 7])
    R[2][2] = float(rw[idx + 8])
    pass

def parenting(child, parent):
    bpy.context.scene.objects.active = child
    bpy.ops.object.constraint_add(type='CHILD_OF')
    child.constraints["Child Of"].target = parent

    child.constraints["Child Of"].use_scale_x = False
    child.constraints["Child Of"].use_scale_y = False
    child.constraints["Child Of"].use_scale_z = False

# -----------------------------------------------------------
# end of parenting function

def grouping(context, elem_obj, obj_list):
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')

    elem_obj.select = True

    for obj in obj_list:
        obj.select = True

    bpy.ops.group.create(name = elem_obj.name)

# -----------------------------------------------------------
# end of grouping function


def eldbmsg(msg, who, elem):
    # Prints various standard debug messages for element import.

    def parse(message):
       message = message + "Parsing " + elem.type \
               + " " + str(elem.int_label)
       baseLogger.info(message)
       return message

    def foundid(message):
        message = message + \
                + "found existing entry in elements dictionary for "\
                + elem.type + " " + str(elem.int_label) + ". Updating it."
        baseLogger.info(message)
        return message

    def notfoundid(message):
        message = message + \
                + "didn't find entry in elements dictionary for "\
                + elem.type + " " + str(elem.int_label) + ". Creating it."
        baseLogger.info(message)
        return message

    def objexists(message):
        message = message + \
                + "Element " + elem.type + " " + str(elem.int_label) \
                + " is already imported. Remove the Blender object "\
                + "or rename it before re-importing the element."
        baseLogger.error(message)
        return message

    def objsnotfound(message):
        message = message + \
                + "Could not find Blender objects"
        baseLogger.error(message)
        return message

    def n1notfound(message):
        message = message + \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[0].int_label)
        baseLogger.error(message)
        return message 

    def n2notfound(message):
        message = message + \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[1].int_label)
        baseLogger.error(message)
        return message 

    def n3notfound(message):
        message = message + \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[2].int_label)
        baseLogger.error(message)
        return message 

    def n4notfound(message):
        message = message + \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[3].int_label)
        baseLogger.error(message)
        return message 
    
    def libraryerror(message):
        message = message + \
                + "Could not import " \
                + elem.type + " " + str(elem.int_label) \
                + ": could not load library object"
        baseLogger.error(message)
        return message

    def dicterror(message):
        message = message + \
                + "Element " + elem.type + " " + str(elem.int_label) + " " \
                + "not found."
        baseLogger.error(message)
        return message

    def importsuccess(message):
        message = message + \
                + "Element " + elem.type + " " + str(elem.int_label) + " " \
                + "imported correcly."
        baseLogger.info(message)
        return message

    # map messages
    messages = {{'PARSE_ELEM'} : parse,
                {'FOUND_DICT'} : foundid,
                {'NOTFOUND_DICT'} : notfoundid,
                {'OBJECT_EXISTS'} : objexists,
                {'OBJECTS_NOTFOUND'} : objsnotfound,
                {'NODE1_NOTFOUND'} : n1notfound,
                {'NODE2_NOTFOUND'} : n2notfound,
                {'NODE3_NOTFOUND'} : n3notfound,
                {'NODE4_NOTFOUND'} : n4notfound,
                {'LIBRARY_ERROR'} : libraryerror,
                {'DICT_ERROR'} : dicterror,
                {'IMPORT_SUCCESS'} : importsuccess,
                {'WRITE_SUCCESS'} : writesuccess
    }

    message = who + ": "
    message = messages[msg](message)
    print(message)
