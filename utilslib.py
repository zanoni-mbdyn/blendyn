# --------------------------------------------------------------------------
# MBDynImporter -- file utilslib.py
# Copyright (C) 2016 Andrea Zanoni -- andrea.zanoni@polimi.it
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

class Object_OT_MBDyn_load_section(bpy.types.Operator, ImportHelper):
    """ Loads NACA airfoil profile in Selig format """
    bl_idname = "load.mbdyn_naca_selig"
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
                    self.report({'INFO'}, "Couldn't find an empty layer. Using the active layer")
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
           self.report({'ERROR'}, {'Could not locate file'})
           return {'CANCELLED'}
        except StopIteration:
            self.report({'WARNING'}, {'Reached the end of file'})
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of fmin function Object_OT_MBDyn_load_section class


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

