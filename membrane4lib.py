# --------------------------------------------------------------------------
# Blendyn -- file membrane4lib.py
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

import bpy, bmesh

import logging

from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

## Parses Revolute Hinge joint entry in the .log file
def parse_membrane4(rw, ed):
    ret_val = True
    # Debug message
    print("parse_membrane4(): Parsing membrane4" + rw[1])
    try:
        el = ed['membrane4_' + str(rw[1])]
        print("parse_membrane4(): found existing entry in elements dictionary for element "\
                + rw[1] + ". Updating it")
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[3])
        el.nodes[2].int_label = int(rw[4])
        el.nodes[3].int_label = int(rw[5])
        el.is_imported = True
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
            el.is_imported = True
    except KeyError:
        print("parse_membrane4(): didn't find entry in elements dictionary. Creating one.")
        
        el = ed.add()
        el.type = 'membrane4'
        el.int_label = int(rw[1])
        
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        
        el.nodes.add()
        el.nodes[1].int_label = int(rw[3])
        
        el.nodes.add()
        el.nodes[2].int_label = int(rw[4])
        
        el.nodes.add()
        el.nodes[3].int_label = int(rw[5])
        
        el.import_function = "add.mbdyn_elem_membrane4"
        el.info_draw = "membrane4_info_draw"
        el.name = el.type + '_' + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass

    return ret_val
# -----------------------------------------------------------
# end of parse_membrane4(rw, ed) function 

# Creates the object representing a membrane4 element
def spawn_membrane4_element(elem, context):
    """ Draws a membrane4 element as a plane mesh with the vertices
        connected to the objects representing the nodes """

    nd = context.scene.mbdyn.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
 
    # try to find Blender objects associated with the nodes that 
    # the element connects
    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
        n1OBJ = bpy.data.objects[n1]
    except KeyError:
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
        n2OBJ = bpy.data.objects[n2]
    except KeyError:
        return {'NODE2_NOTFOUND'}
    try:
        n3 = nd['node_' + str(elem.nodes[2].int_label)].blender_object
        n3OBJ = bpy.data.objects[n3]
    except KeyError:
        return {'NODE3_NOTFOUND'}
    
    try:
        n4 = nd['node_' + str(elem.nodes[3].int_label)].blender_object
        n4OBJ = bpy.data.objects[n4]
    except KeyError:
        return {'NODE4_NOTFOUND'}
    
    avg_location = .25*(n1OBJ.location + n2OBJ.location + n3OBJ.location + n4OBJ.location)

    # create the mesh plane
    bpy.ops.mesh.primitive_plane_add(location = avg_location)
    membraneOBJ = bpy.context.scene.objects.active
    membraneOBJ.name = elem.name
    membraneOBJ.mbdyn.type = 'elem.membrane4'
    membraneOBJ.mbdyn.dkey = elem.name
    membraneOBJ.mbdyn.int_label = elem.int_label
    mesh = membraneOBJ.data

    # move vertices to nodes locations
    mesh.vertices[0].co = membraneOBJ.matrix_world.inverted()*n1OBJ.location
    mesh.vertices[1].co = membraneOBJ.matrix_world.inverted()*n2OBJ.location
    mesh.vertices[3].co = membraneOBJ.matrix_world.inverted()*n3OBJ.location
    mesh.vertices[2].co = membraneOBJ.matrix_world.inverted()*n4OBJ.location

    # create hooks
    bpy.ops.object.select_all()
    membraneOBJ.select = True
    bpy.context.scene.objects.active = membraneOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)

    # vertex 1 hook
    mesh = bmesh.from_edit_mesh(membraneOBJ.data)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    mesh.verts.ensure_lookup_table()
    mesh.verts[0].select = True
    mesh.select_flush(True)
    n1OBJ.select = True
    bpy.ops.object.hook_add_selob()
    n1OBJ.select = False

    # vertex 2 hook
    mesh = bmesh.from_edit_mesh(membraneOBJ.data)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    mesh.verts.ensure_lookup_table()
    mesh.verts[1].select = True
    mesh.select_flush(True)
    n2OBJ.select = True
    bpy.ops.object.hook_add_selob()
    n2OBJ.select = False

    # vertex 3 hook
    mesh = bmesh.from_edit_mesh(membraneOBJ.data)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    mesh.verts.ensure_lookup_table()
    mesh.verts[2].select = True
    mesh.select_flush(True)
    n4OBJ.select = True
    bpy.ops.object.hook_add_selob()
    n4OBJ.select = False

    # vertex 4 hook
    mesh = bmesh.from_edit_mesh(membraneOBJ.data)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    mesh.verts.ensure_lookup_table()
    mesh.verts[3].select = True
    mesh.select_flush(True)
    n3OBJ.select = True
    bpy.ops.object.hook_add_selob()
    n3OBJ.select = False

    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')


    # create group for element
    membraneOBJ.select = True
    n1OBJ.select = True
    n2OBJ.select = True
    n3OBJ.select = True
    n4OBJ.select = True
    bpy.ops.group.create(name = membraneOBJ.name)

    elem.blender_object = membraneOBJ.name
    return {'FINISHED'}

# function that displays membrane4 info in panel -- [ optional ]
def membrane4_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)
    
    try: 
        for ndx in range(4):
            node = nd['node_' + str(elem.nodes[ndx].int_label)]
            # Display node info
            col.prop(node, "int_label", text = "Node " + str(ndx + 1) + " ID ")
            col.prop(node, "string_label", text = "Node " + str(ndx + 1) + " label ")
            col.prop(node, "blender_object", text = "Node " + str(ndx + 1) + " Object: ")
            col.enabled = False
            return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}
# -----------------------------------------------------------
# end of membrane4_info_draw(elem, layout) function

class Scene_OT_MBDyn_Import_membrane4_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_membrane4"
    bl_label = "MBDyn membrane4 element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        try:
            elem = ed['membrane4_' + str(self.int_label)]
            retval = spawn_membrane4_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                message = "Element is already imported. Remove the Blender " +\
                            "object before re-importing"
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                message = "Could not find a Blender object associated to Node " \
                        + str(elem.nodes[0].int_label)
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                message = "Could not find a Blender object associated to Node " \
                        + str(elem.nodes[1].int_label)
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'NODE3_NOTFOUND'}:
                message = "Could not find a Blender object associated to Node " \
                        + str(elem.nodes[2].int_label)
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'NODE4_NOTFOUND'}:
                message = "Could not find a Blender object associated to Node " \
                        + str(elem.nodes[3].int_label)
                self.report({'ERROR'}, message)
                logging.error(message)
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            message = "Element membrane4_" + str(elem.int_label) + "not found"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
