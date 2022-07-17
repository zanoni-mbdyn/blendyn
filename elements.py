# --------------------------------------------------------------------------
# Blendyn -- file elements.py
# Copyright (C) 2015 -- 2021 Andrea Zanoni -- andrea.zanoni@polimi.it
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
#    Blendyn is distributed in the hope that it will be useful,
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
from bpy.types import Operator, Panel
from bpy.props import *

import logging

from mathutils import *
from math import *


import ntpath, os, csv

from .elementlib import *




class BLENDYN_PG_elem_pos_offset(bpy.types.PropertyGroup):
    value: FloatVectorProperty(
        name = "Offset value",
	description = "The offset vector, with respect to the node",
        size = 3,
        precision = 6
	)
# -----------------------------------------------------------
# end of BLENDYN_PG_elem_pos_offset class
bpy.utils.register_class(BLENDYN_PG_elem_pos_offset)


class BLENDYN_PG_elem_rot_offset(bpy.types.PropertyGroup):
    value: FloatVectorProperty(
        name = "Offset value",
        description = "The rotational offset quaternion, with respect to the node",
        size = 4,
        precision = 6
        )
# -----------------------------------------------------------
# end of BLENDYN_PG_elem_rot_offset class
bpy.utils.register_class(BLENDYN_PG_elem_rot_offset)


class BLENDYN_PG_nodes_collection(bpy.types.PropertyGroup):
    int_label: IntProperty(
        name = "MBDyn node ID",
        description = "",
        )
# -----------------------------------------------------------
# end of BLENDYN_PG_nodes_collection class
bpy.utils.register_class(BLENDYN_PG_nodes_collection)


class BLENDYN_PG_fem_connection(bpy.types.PropertyGroup):
    name: StringProperty(
        name = "FEM connection name",
        description = " Name of FEM connection"
        )

    node_1_int_label: EnumProperty(
        items = get_fem_connect_node1,
        name = "Node 1 FEM connection",
        description = "Node 1 in FEM connection for Modal visualization using armature",
        )

    node_2_int_label: EnumProperty(
        items = get_fem_connect_node2,
        name = "Node 2 FEM connection",
        description = "Node 2 in FEM connection for Modal visualization using armature",
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_modal_fem_nodes class
bpy.utils.register_class(BLENDYN_PG_fem_connection)


class BLENDYN_PG_elem_to_be_updated(bpy.types.PropertyGroup):
    dkey: StringProperty(
            name = "Key of element to be updated",
            description = "",
            )
# -----------------------------------------------------------
# end of BLENDYN_PG_elem_to_be_updated class
bpy.utils.register_class(BLENDYN_PG_elem_to_be_updated)


class BLENDYN_PG_elems_dictionary(bpy.types.PropertyGroup):
    mbclass: StringProperty(
            name = "Class of MBDyn element",
            description  = ""
            )

    type: StringProperty(
            name = "Type of MBDyn element",
            description = ""
            )

    int_label: IntProperty(
            name = "Integer label of element",
            description = ""
            )

    string_label: StringProperty(
            name = "String label of element",
            description = "",
            default = "none"
            )

    nodes: CollectionProperty(
            type = BLENDYN_PG_nodes_collection,
            name = "Connected nodes",
            description = "MBDyn nodes that the element connects"
            )

    node_index: IntProperty(
            name = "Index of element node",
            description = "Index using for displaying element nodes in Component Panel",
            default = 0
            )

    fem_connects: CollectionProperty(
            type = BLENDYN_PG_fem_connection,
            name = "FEM collection",
            description = "FEM connection for modal visualisation"
            )

    connect_index: IntProperty(
            name = "Index of modal connection",
            description = "Index using for displaying modal fem connection in Component Panel",
            default = -1
            )

    selected_node: EnumProperty(
            items = get_nodes_for_modal,
            name = "Group of nodes would be selected to be modal fem node",
            description = "Group of nodes would be selected to be modal fem node",
            )

    magnitude: FloatProperty(
            name = "Magnitude of element",
            description = "Magnitude of element if present (e.g. force, couple...)",
            default = 0.
            )

    offsets: CollectionProperty(
            type = BLENDYN_PG_elem_pos_offset,
            name = "Offsets of attach points",
            description = "Collector of offsets of element attaching points"
            )

    rotoffsets: CollectionProperty(
            type = BLENDYN_PG_elem_rot_offset,
            name = "Rotational offsets of attach R.Fs. of joint",
            description = "Collector of rotational offsets of element attach R.Fs."
            )

    beam_number: IntProperty(
            name="Number beam3",
            description="Number of beam3 connected with beam slider"
            )

    import_function: StringProperty(
            name = "Import operator",
            description = "Id name of the class defining the import operator for the element"
            )

    draw_function: StringProperty(
            name = "Draw function",
            description = "Id of the function that is called when the element configuration is updated",
            )

    update_info_operator: StringProperty(
            name = "Update operator",
            description = "Id name of the operator that updates the element info using \
                    the current position of the blender objects representing it",
                    default = 'none'
                    )

    write_operator: StringProperty(
            name = "Input write operator",
            description = "Id name of the operator that writes the element input contribute",
            default = 'none'
            )

    info_draw: StringProperty(
            name = "Element Info Function",
            description = "Name of the function used to display element data in the View3D panel",
            default = "elem_info_draw"
            )

    blender_object: StringProperty(
            name = "Blender Object",
            description = "Name of the Blender Object associated with this element"
            )

    is_imported: BoolProperty(
            name = "Is imported flag",
            description = "Flag set to true at the end of the import process"
            )

    update: StringProperty(
            name = "Update function",
            description = "Function that updates the visualization of the element",
            default = 'none'
            )
# -----------------------------------------------------------
# end of BLENDYN_PG_elems_dictionary class
bpy.utils.register_class(BLENDYN_PG_elems_dictionary)


# Override delete operator to remove element from elements dictionary
# when the related object is deleted
class BLENDYN_OT_import_elements_as_mesh(bpy.types.Operator):
    """ Imports all the elements selected (by type and label range) into a single
        mesh Blender Object. Currently useful only for shell4 elements. """
    bl_label = "Import MBDyn elements as single mesh"
    bl_idname = "blendyn.import_elments_asmesh"

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
                    message = type(self).__name__ + "::execute(): "\
                              + "Could not find Blender Objects for " \
                              + elem.name + " import"
                    self.report({'ERROR'}, message)
                    logging.error(message)

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
            context.scene.collection.objects.link(obj)
            obj.select_set(state = True)
            context.view_layer.objects.active = obj

            for node in node_set:
                vg = obj.vertex_groups.new('v-' + str(node_to_vert[node]))
                vg.add([node_to_vert[node]], 1.0, 'ADD')
                hook_mod = obj.modifiers.new('Hook' + vg.name, 'HOOK')
                hook_mod.object = bpy.data.objects[nd[node].blender_object]
                hook_mod.vertex_group = vg.name
                hook_mod.show_in_editmode = True

            return {'FINISHED'}
        else:
            message = type(self).__name__ + "::execute(): "\
                      + "No mesh data was created"
            self.report({'WARNING'}, message)
            logging.warning(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_import_elements_as_mesh class
