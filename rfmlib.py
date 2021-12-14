# --------------------------------------------------------------------------
# Blendyn -- file rfmlib.py
# Copyright (C) 2015 -- 2021 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import bpy

import logging

from mathutils import *
from math import *

from .utilslib import *
from .nodelib import axes

def parse_reference_frame(rw, rd):
    ret_val = True

    # Debug message
    message = "BLENDYN::parse_reference_frame(): " \
            + "parsing reference frame " + rw[0]
    print(message)
    logging.info(message)

    try:
        ref = rd['ref_' + str(rw[0]).strip()]
        message = "BLENDYN::parse_reference_frame(): "\
                + "found entry in dictionary. Updating it."
        print(message)
        logging.info(message)

        if ref.name in bpy.data.objects.keys():
            ref.blender_object = ref.name
    except KeyError:
        ref = rd.add()
        ref.int_label = int(rw[0].strip())
        ref.name = 'ref_' + str(rw[0]).strip()
        ret_val = False
        message = "BLENDYN::parse_reference_frame(): "\
                + "did not find entry in dictionary. Creating it."
        print(message)
        logging.info(message)
        pass

    ref.pos = Vector(( float(rw[1]), float(rw[2]), float(rw[3]) ))
    idx = set_ref_rotation(ref, rw, bpy.context.scene.mbdyn.nodes[0].parametrization)

    ref.vel = Vector(( float(rw[idx + 1]), float(rw[idx + 2]), float(rw[idx + 3]) ))
    ref.angvel = Vector(( float(rw[idx + 4]), float(rw[idx + 5]), float(rw[idx + 6]) ))
    ref.is_imported = True
# -----------------------------------------------------------
# end of parse_reference_frame(rw, rd) function

def set_ref_rotation(ref, rw, par):
    idx = 3
    if (par == 'PHI'):
        phi = Vector(( float(rw[idx + 1]), float(rw[idx + 2]), float(rw[idx + 3]) ))
        idx += 3;
        ref.rot = Quaternion(phi.normalized(), phi.magnitude)
    elif (par[0:5] == 'EULER'):
        ref.rot = Euler(Vector((radians(float(rw[idx + int(par[5])])),\
                                radians(float(rw[idx + int(par[6])])),\
                                radians(float(rw[idx + int(par[7])])) )),\
                                axes[par[7]] + axes[par[6]] + axes[par[5]]\
                        ).to_quaternion()
        idx += 3
    elif (par == 'MATRIX'):
        ref.rot = Matrix((\
                    (( float(rw[idx + 1]), float(rw[idx + 2]), float(rw[idx + 3]) )),\
                    (( float(rw[idx + 4]), float(rw[idx + 5]), float(rw[idx + 6]) )),\
                    (( float(rw[idx + 7]), float(rw[idx + 8]), float(rw[idx + 9]) )),\
                 )).to_quaternion()
        idx += 9
    else:
        # Should not be reached
        message = "BLENDYN::set_ref_rotation(): "\
                + "unsupported rotation parametrization"
        print(message)
        logging.error(message)
    return idx
# -----------------------------------------------------------
# end of set_ref_rotation(ref, rw, par) function


def spawn_reference_frame(ref, context):
    """ Spawns an Empty Axes object to represent an MBDyn reference """
    mbs = context.scene.mbdyn

    if any(obj == ref.blender_object for obj in bpy.data.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        set_active_collection('mbdyn.references')
    except KeyError:
        return {'COLLECTION_ERROR'}

    bpy.ops.object.empty_add(type = 'ARROWS', location = ref.pos)
    obj = context.view_layer.objects.active
    obj.mbdyn.type = 'reference'
    obj.mbdyn.dkey = ref.name
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = ref.rot

    if ref.string_label != "none":
        obj.name = ref.string_label
    else:
        obj.name = ref.name

    ref.blender_object = obj.name

    set_active_collection('Master Collection')
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_reference_frame(ref, context) function

# Imports a Reference Frame in the scene
class BLENDYN_OT_import_reference(bpy.types.Operator):
    """ Imports a reference frame into the Blender scene
        as an Empty of type AXES"""
    bl_idname = "blendyn.import_reference"
    bl_label = "Imports a reference"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        rd = context.scene.mbdyn.references

        try:
            ref = rd['ref_' + str(self.int_label)]
            retval = spawn_reference_frame(ref, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "BLENDYN::parse_reference_frame(): "\
                + "object already exists. Remove it before re-importing."
                print(message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'FINISHED'}:
                message = "BLENDYN::parse_reference_frame(): "\
                + "Imported reference frame " + str(rfm.int_label)
                print(message)
                logging.info(message)
                return retval
            elif retval == {'COLLECTION_ERROR'}:
                message = "BLENDYN::parse_reference_frame(): "\
                + "references collection not found "
                print(message)
                logging.info(message)
                return {'CANCELLED'}
            else:
                # Should not be reached
                return retval
        except KeyError:
            message = "BLENDYN::parse_reference_frame(): "\
            + "Did not find a dictionary entry for reference frame "
            + str(rfm.int_label)
            print(message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_import_reference class

def reference_info_draw(ref, layout):

    row = layout.row()
    col = layout.column(align = True)

    col.prop(ref, "pos")
    col.prop(ref, "rot")
    col.prop(ref, "vel")
    col.prop(ref, "angvel")

    pass
