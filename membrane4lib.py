# --------------------------------------------------------------------------
# Blendyn -- file membrane4lib.py
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

from mathutils import *
from math import *

from .utilslib import *

def parse_membrane4(rw, ed):
    """ Parses a membrane4 element entry in the .log file """

    ret_val = True
    try:
        el = ed['membrane4_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_membrane4()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_membrane4()", el)  
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[3])
        el.nodes[2].int_label = int(rw[4])
        el.nodes[3].int_label = int(rw[5])
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.joint'
        
        el.is_imported = True
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
            el.is_imported = True
    except KeyError:
        
        el = ed.add()
        el.mbclass = 'elem.shell'
        el.type = 'membrane4'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_membrane4()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_membrane4()", el)   
        
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        
        el.nodes.add()
        el.nodes[1].int_label = int(rw[3])
        
        el.nodes.add()
        el.nodes[2].int_label = int(rw[4])
        
        el.nodes.add()
        el.nodes[3].int_label = int(rw[5])
        
        el.import_function = "blendyn.import_membrane4"
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

    try:
        # put it all in the 'plates' collection
        set_active_collection('plates')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['plates'].children.link(elcol)
        set_active_collection(elcol.name)
    except KeyError:
        return {'COLLECTION_ERROR'}

    # create the mesh plane
    bpy.ops.mesh.primitive_plane_add(location = avg_location)
    shellOBJ = bpy.context.view_layer.objects.active
    shellOBJ.name = elem.name
    shellOBJ.mbdyn.type = 'element'
    shellOBJ.mbdyn.dkey = elem.name
    mesh = shellOBJ.data

    # move vertices to nodes locations
    mesh.vertices[0].co = shellOBJ.matrix_world.inverted()@n1OBJ.location
    mesh.vertices[1].co = shellOBJ.matrix_world.inverted()@n2OBJ.location
    mesh.vertices[3].co = shellOBJ.matrix_world.inverted()@n3OBJ.location
    mesh.vertices[2].co = shellOBJ.matrix_world.inverted()@n4OBJ.location

    # create hooks 
    objs = [n1OBJ, n2OBJ, n4OBJ, n3OBJ]
    names = ['P1', 'P2', 'P4', 'P3']
    for i, (obj, name) in enumerate(zip(objs, names)):
        hook = shellOBJ.modifiers.new(name, type = 'HOOK')
        hook.object = obj
        hook.vertex_indices_set([i])
    
    # lock object's scale
    shellOBJ.lock_scale[0] = True
    shellOBJ.lock_scale[1] = True
    shellOBJ.lock_scale[2] = True

    # put them all in the element collection
    elcol.objects.link(n1OBJ)
    elcol.objects.link(n2OBJ)
    elcol.objects.link(n3OBJ)
    elcol.objects.link(n4OBJ)
    set_active_collection('Master Collection')

    elem.blender_object = shellOBJ.name
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

class BLENDYN_OT_import_membrane4(bpy.types.Operator):
    """ Imports a membrane4 element into the Blender scene """
    bl_idname = "blendyn.import_membrane4"
    bl_label = "Imports a membrane4 element"
    int_label: bpy.props.IntProperty()

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
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE3_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE4_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'FINISHED'}:
                eldbmsg({'IMPORT_SUCCESS'}, type(self).__name__ + '::execute()', elem)
                return retval 
            else:
                # Should not be reached
                return retval
        except KeyError:
            eldbmsg({'DICT_ERROR'}, type(self).__name__ + '::execute()', elem)
            return {'CANCELLED'}
# --------------------------------------------------------------
# end of BLENDYN_OT_import_membrane4 class
