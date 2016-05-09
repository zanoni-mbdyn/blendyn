# --------------------------------------------------------------------------
# MBDynImporter -- file element.py
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
from bpy.types import Operator, Panel
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from bpy.app.handlers import persistent

from mathutils import *
from math import *


import ntpath, os, csv

from .elementlib import *

class MBDynElemOffset(bpy.types.PropertyGroup):
    value = FloatVectorProperty(
        name = "Offset value",
	description = "The offset vector, with respect to the node",
        size = 3,
        precision = 6
	)
bpy.utils.register_class(MBDynElemOffset)
# -----------------------------------------------------------
# end of MBDynElemOffset class 

class MBDynElemRotOffset(bpy.types.PropertyGroup):
    value = FloatVectorProperty(
        name = "Offset value",
        description = "The rotational offset quaternion, with respect to the node",
        size = 4,
        precision = 6
        )
bpy.utils.register_class(MBDynElemRotOffset)
# -----------------------------------------------------------
# end of MBDynElemRotOffset class 

class MBDynElemNodesColl(bpy.types.PropertyGroup):
    int_label = IntProperty(
        name = "MBDyn node ID",
        description = "",
        )
bpy.utils.register_class(MBDynElemNodesColl)
# -----------------------------------------------------------
# end of MBDynElemNodesColl class 

class MBDynElemsDictionary(bpy.types.PropertyGroup):
    type = StringProperty(
        name = "Type of MBDyn element",
        description = ""
        )

    int_label = IntProperty(
        name = "Integer label of element",
        description = ""
        )

    string_label = StringProperty(
        name = "String label of element",
        description = "",
        default = "none"
        )

    nodes = CollectionProperty(
        type = MBDynElemNodesColl,
        name = "Connected nodes",
        description = "MBDyn nodes that the element connects"
        )

    offsets = CollectionProperty(
        type = MBDynElemOffset,
        name = "Offsets of attach points",
        description = "Collector of offsets of element attaching points"
        )

    rotoffsets = CollectionProperty(
        type = MBDynElemRotOffset,
        name = "Rotational offsets of attach R.Fs. of joint",
        description = "Collector of rotational offsets of element attach R.Fs."
        )

    import_function = StringProperty(
        name = "Import operator",
        description = "Id name of the class defining the import operator for the element"
        )

    draw_function = StringProperty(
        name = "Draw function",
        description = "Id of the function that is called when the element configuration is updated",
        )

    update_info_operator = StringProperty(
        name = "Update operator",
        description = "Id name of the operator that updates the element info using \
            the current position of the blender objects representing it",
        default = 'none'
        )

    write_operator = StringProperty(
        name = "Input write operator",
        description = "Id name of the operator that writes the element input contribute",
        default = 'none'
        )

    info_draw = StringProperty(
        name = "Element Info Function",
        description = "Name of the function used to display element data in the View3D panel",
        default = "elem_info_draw"
        )

    blender_object = StringProperty(
        name = "Blender Object",
        description = "Name of the Blender Object associated with this element"
        )

    is_imported = BoolProperty(
        name = "Is imported flag",
        description = "Flag set to true at the end of the import process"
        )

    update = StringProperty(
        name = "Update function",
        description = "Function that updates the visualization of the element",
        default = 'none'
        )
bpy.utils.register_class(MBDynElemsDictionary)
# -----------------------------------------------------------
# end of MBDynElemsDictionary class 

# App handler to update the elems dictionary when an object is removed
@persistent
def update_ed(scene):
    ed = scene.mbdyn.elems
    for elem in ed:
        if not(elem.blender_object in bpy.data.objects.keys()):
            elem.blender_object = 'none'
            elem.is_imported = False

bpy.app.handlers.scene_update_post.append(update_ed)
