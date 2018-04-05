# --------------------------------------------------------------------------
# Blendyn -- file rfmlib.py
# Copyright (C) 2015 -- 2018 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of Blendyn, add-on script for Blender.
#    https://github.com/zanoni-mbdyn/blendyn/
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

import bpy

import logging

from mathutils import *
from math import *

def parse_reference_frame(rw, rd):
    ret_val = True

    # Debug message
    print("Blendyn::parse_reference_frame(): Parsing Reference Frame " + rw[0])

    try:
        ref = rd['ref_' + str(rw[0]).strip()]
        print("Blendyn::parse_reference_frame(): found existing entry in references dictionary." \
                + " Updating it.")

        if ref.name in bpy.data.objects.keys():
            ref.blender_object = ref.name
    except KeyError:
        print("Blendyn::parse_reference_frame(): didn't found an entry in elements dictionary." \
                + " Creating one.")
        
        ref = rd.add()
        ref.int_label = int(rw[0].strip())
        ref.name = 'ref_' + str(rw[0]).strip()
        ret_val = False
        pass

    ref.pos = Vector(( float(rw[1]), float(rw[2]), float(rw[3]) ))

    phi = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
    ref.rot = Quaternion(phi.normalized(), phi.magnitude)

    ref.vel = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
    ref.angvel = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
    ref.is_imported = True
# -----------------------------------------------------------
# end of parse_reference_frame(rw, rd) function

def spawn_reference_frame(ref, context):
    """ Spawns an Empty Axes object to represent an MBDyn reference """
    mbs = context.scene.mbdyn

    if any(obj == ref.blender_object for obj in bpy.data.objects.keys()):
        print("Blendyn::spawn_reference_frame(): Reference already imported. \
            Remove the Blender object or rename it \
            before re-importing the element.")
        return {'OBJECT_EXISTS'}

    bpy.ops.object.empty_add(type = 'ARROWS', location = ref.pos)
    obj = context.scene.objects.active
    obj.mbdyn.type = 'reference'
    obj.mbdyn.int_label = ref.int_label
    obj.mbdyn.string_label = ref.string_label
    obj.mbdyn.parametrization = 'PHI'
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = ref.rot

    if obj.mbdyn.string_label != "none":
        obj.name = ref.string_label

    else:
        obj.name = ref.name
   
    obj.mbdyn.dkey = ref.name
    ref.blender_object = obj.name
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_reference_frame(ref, context) function

# Imports a Reference Frame in the scene
class Scene_OT_MBDyn_Import_Reference(bpy.types.Operator):
    bl_idname = "add.mbdyn_reference"
    bl_label = "MBDyn reference importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        rd = context.scene.mbdyn.references

        try:
            ref = rd['ref_' + str(self.int_label)]
            retval = spawn_reference_frame(ref, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "Found the Object " + ref.blender_object + \
                    " remove or rename it to re-import the element!"
                self.report({'WARNING'}, message)
                logging.warning(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Reference ref_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Reference class

def reference_info_draw(ref, layout):

    row = layout.row()
    col = layout.column(align = True)

    col.prop(ref, "pos")
    col.prop(ref, "rot")
    col.prop(ref, "vel")
    col.prop(ref, "angvel")

    pass
