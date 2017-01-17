# --------------------------------------------------------------------------
# Blendyn -- file elements.py
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
import bpy, bmesh
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

class MBDynElemToBeUpdated(bpy.types.PropertyGroup):
    dkey = StringProperty(
            name = "Key of element to be updated",
            description = "",
            )
bpy.utils.register_class(MBDynElemToBeUpdated)
# -----------------------------------------------------------
# end of MBDynToBeUpdated class 

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

# Override delete operator to remove element from elements dictionary
# when the related object is deleted



class Scene_OT_MBDyn_Import_Elements_as_Mesh(bpy.types.Operator):
    """ Imports all the elements selected (by type and label range) into a single
        mesh Blender Object. Currently useful only for shell4 elements. """
    bl_idname =  "add.mbdyn_elem_as_mesh"
    bl_label = "Import MBDyn elements as single mesh"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ed = mbs.elems
        nd = mbs.nodes

        verts = list()
        faces = list()
        nodes = list()
        elems = list()

        for elem in ed:
            if (elem.type == mbs.elem_type_import) \
                    and (elem.int_label >= mbs.min_elem_import) \
                    and (elem.int_label <= mbs.max_elem_import):
                elems.append(elem.name)
                n1 = 'node_' + str(elem.nodes[0].int_label)
                n2 = 'node_' + str(elem.nodes[1].int_label)
                n3 = 'node_' + str(elem.nodes[2].int_label)
                n4 = 'node_' + str(elem.nodes[3].int_label)
                nodes.extend((n1, n2, n3, n4))

        node_set = set(nodes)
        for node in node_set:
                try:
                    verts.append(bpy.data.objects[nd[node].blender_object].location)
                except KeyError:
                    self.report({'ERROR'}, "Could not find Blender Objects for " + \
                            elem.name + " import")
        
        node_to_vert = dict(zip((node_set), range(len(verts))))

        for ekey in elems:
            elem = ed[ekey]
            faces.append(\
                    (node_to_vert['node_' + str(elem.nodes[0].int_label)],\
                    node_to_vert['node_' + str(elem.nodes[1].int_label)],\
                    node_to_vert['node_' + str(elem.nodes[2].int_label)],\
                    node_to_vert['node_' + str(elem.nodes[3].int_label)]),\
                    )
        
        if len(verts) and len(faces):
            objname = mbs.elem_type_import + '_' + \
                    str(mbs.min_elem_import) + '_' + \
                    str(mbs.max_elem_import)
           
            mesh = bpy.data.meshes.new(objname + '_mesh')
            mesh.from_pydata(verts, [], faces)
            mesh.update()

            obj = bpy.data.objects.new(objname, mesh)
            context.scene.objects.link(obj)
            obj.select = True
            context.scene.objects.active = obj
            
            for node in node_set:
                vg = obj.vertex_groups.new('v-' + str(node_to_vert[node]))
                vg.add([node_to_vert[node]], 1.0, 'ADD')
                hook_mod = obj.modifiers.new('Hook' + vg.name, 'HOOK')
                hook_mod.object = bpy.data.objects[nd[node].blender_object]
                hook_mod.vertex_group = vg.name
                hook_mod.show_in_editmode = True

            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No mesh data was created")
            return {'CANCELLED'}

