# --------------------------------------------------------------------------
# Blendyn -- file aerolib.py
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
from bpy.props import *

from .utilslib import *

import pdb

## Parses aerodynamic body element entry in .log file
def parse_aero0(rw, ed):
    ret_val = True
    
    try: 
        el = ed['aero0_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_aero0()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_aero0()", el)

        el.nodes[0].int_label = int(rw[2])
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[6]), float(rw[7]), float(rw[8]) ))
        el.offsets[2].value = Vector(( float(rw[9]), float(rw[10]), float(rw[11]) ))
        el.offsets[3].value = Vector(( float(rw[12]), float(rw[13]), float(rw[14]) ))
        # FIXME: this is here to enhance backwards compatibility
        # Should disappear in future versions
        el.mbclass = 'elem.aero'

        el.is_imported = True

        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.aero'
        el.type = 'aero0'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_aero0()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_aero0()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[6]), float(rw[7]), float(rw[8]) ))
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[9]), float(rw[10]), float(rw[11]) ))
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[12]), float(rw[13]), float(rw[14]) ))

        el.import_function = "blendyn.import_aerodynamic_body"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_aero0(rw, ed) function

## Parses two-node aerodynamic beam element entry in .log file
def parse_aero2(rw, ed):
    ret_val = True
    try: 
        el = ed['aero2_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_aero2()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_aero2()", el)

        el.nodes[0].int_label = int(rw[2])
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[6]), float(rw[7]), float(rw[8]) ))
        el.nodes[1].int_label = int(rw[9])
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))
        
        # FIXME: this is here to enhance backwards compatibility
        # Should disappear in future versions
        el.mbclass = 'elem.aero'

        el.is_imported = True

        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.aero'
        el.type = 'aero2'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_aero0()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_aero0()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[6]), float(rw[7]), float(rw[8]) ))

        el.nodes.add()
        el.nodes[1].int_label = int(rw[9])

        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))

        el.import_function = "blendyn.import_aerodynamic_beam2"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_aero2(rw, ed) function

## Parses three-node aerodynamic beam element entry in .log file
def parse_aero3(rw, ed):
    ret_val = True
    # Debug message
    try: 
        el = ed['aero3_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_aero2()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_aero2()", el)

        el.nodes[0].int_label = int(rw[2])
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[6]), float(rw[7]), float(rw[8]) ))
        el.nodes[1].int_label = int(rw[9])
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))
        el.nodes[2].int_label = int(rw[16])
        el.offsets[4].value = Vector(( float(rw[17]), float(rw[18]), float(rw[19]) ))
        el.offsets[5].value = Vector(( float(rw[20]), float(rw[21]), float(rw[22]) ))
        
        # FIXME: this is here to enhance backwards compatibility
        # Should disappear in future versions
        el.mbclass = 'elem.aero'

        el.is_imported = True

        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.aero'
        el.type = 'aero3'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_aero0()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_aero0()", el)
       
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[6]), float(rw[7]), float(rw[8]) ))

        el.nodes.add()
        el.nodes[1].int_label = int(rw[9])

        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[10]), float(rw[11]), float(rw[12]) ))
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[13]), float(rw[14]), float(rw[15]) ))

        el.nodes.add()
        el.nodes[2].int_label = int(rw[16])

        el.offsets.add()
        el.offsets[4].value = Vector(( float(rw[17]), float(rw[18]), float(rw[19]) ))
        el.offsets.add()
        el.offsets[5].value = Vector(( float(rw[20]), float(rw[21]), float(rw[22]) ))

        el.import_function = "blendyn.import_aerodynamic_beam3"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_aero3(rw, ed) function

# Creates the object representing an aerodynamic body element
def spawn_aero0_element(elem, context):
    """ Draws an aerodynamic body element as a rectangular mesh object
        whose vertices are rigidly connected to the parent node object"""

    nd = context.scene.mbdyn.nodes
 
    # try to find Blender objects associated with the node that 
    # the element belongs to
    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}

    n1OBJ = bpy.data.objects[n1]
    R1 = n1OBJ.rotation_quaternion.to_matrix()

    # name of the plane object
    planeobj_id = elem.type + "_" + str(elem.int_label)

    # check if the object is already present. If it is, remove it
    if planeobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[planeobj_id])

    try:
        set_active_collection('aerodynamic')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['aerodynamic'].children.link(elcol)
        set_active_collection(elcol.name)
    except KeyError:
        return {'COLLECTION_ERROR'}

    # create a mesh plane
    bpy.ops.mesh.primitive_plane_add(location = (0.0, 0.0, 0.0))
    aero0OBJ = bpy.context.view_layer.objects.active
    aero0OBJ.name = elem.name
    aero0OBJ.mbdyn.type = 'element'
    aero0OBJ.mbdyn.dkey = elem.name
    mesh = aero0OBJ.data

    # move vertices
    mesh.vertices[0].co = n1OBJ.location + R1@Vector(( elem.offsets[0].value ))
    mesh.vertices[1].co = n1OBJ.location + R1@Vector(( elem.offsets[1].value ))
    mesh.vertices[2].co = n1OBJ.location + R1@Vector(( elem.offsets[2].value ))
    mesh.vertices[3].co = n1OBJ.location + R1@Vector(( elem.offsets[3].value ))
  
    aero0OBJ.rotation_mode = n1OBJ.rotation_mode
    aero0OBJ.lock_scale[0] = True
    aero0OBJ.lock_scale[1] = True
    aero0OBJ.lock_scale[2] = True
    
    # set parenting for plane obj
    parenting(aero0OBJ, n1OBJ)

    aero0OBJ.mbdyn.dkey = elem.name
    aero0OBJ.mbdyn.type = 'element'
    elem.blender_object = aero0OBJ.name
    
    # set collections
    elcol.objects.link(n1OBJ)
    set_active_collection('Master Collection')

    return{'FINISHED'}
# -----------------------------------------------------------
# end of spawn_aero0_element() function

def hook_vertices(bm, vidx, obj):
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bm.verts.ensure_lookup_table()
    for ii in vidx:
        bm.verts[ii].select = True
    bm.select_flush(True)
    obj.select_set(state = True)
    bpy.ops.object.hook_add_selob()
    obj.select_set(state = False)
# -----------------------------------------------------------
# end of hook_vertices() function

# Creates the object representing an aerodynamic body element
def spawn_aero2_element(elem, context):
    """ Draws an aerodynamic body element as a rectangular mesh object
        whose vertices are rigidly connected to the parent nodes objects """

    nd = context.scene.mbdyn.nodes
 
    # try to find Blender objects associated with the nodes that 
    # the element belongs to
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

    # name of the plane object
    planeobj_id = elem.type + "_" + str(elem.int_label)

    # check if the object is already present. If it is, remove it
    if planeobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[planeobj_id])

    try:
        set_active_collection('aerodynamic')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['aerodynamic'].children.link(elcol)
        set_active_collection(elcol.name)
    except KeyError:
        return {'COLLECTION_ERROR'}
    
    # create a mesh plane
    bpy.ops.mesh.primitive_plane_add(location = (0.0, 0.0, 0.0))
    aero2OBJ = bpy.context.view_layer.objects.active
    aero2OBJ.name = elem.name
    aero2OBJ.mbdyn.type = 'element'
    aero2OBJ.mbdyn.dkey = elem.name
    mesh = aero2OBJ.data

    # move vertices
    mesh.vertices[0].co = n1OBJ.matrix_world@Vector(( elem.offsets[0].value ))
    mesh.vertices[1].co = n1OBJ.matrix_world@Vector(( elem.offsets[1].value ))
    mesh.vertices[2].co = n2OBJ.matrix_world@Vector(( elem.offsets[2].value ))
    mesh.vertices[3].co = n2OBJ.matrix_world@Vector(( elem.offsets[3].value ))

    bpy.ops.object.select_all(action = 'DESELECT')
    aero2OBJ.select_set(state = True)
    bpy.context.view_layer.objects.active = aero2OBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)

    # add hooks
    hook_vertices(bmesh.from_edit_mesh(mesh), {0, 1}, n1OBJ)
    hook_vertices(bmesh.from_edit_mesh(mesh), {2, 3}, n2OBJ)

    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')

    aero2OBJ.rotation_mode = n1OBJ.rotation_mode
    aero2OBJ.lock_scale[0] = True
    aero2OBJ.lock_scale[1] = True
    aero2OBJ.lock_scale[2] = True

    aero2OBJ.mbdyn.dkey = elem.name
    aero2OBJ.mbdyn.type = 'element'
    elem.blender_object = aero2OBJ.name

    # set collections
    elcol.objects.link(n1OBJ)
    elcol.objects.link(n2OBJ)
    set_active_collection('Master Collection')

    return{'FINISHED'}
# -----------------------------------------------------------
# end of spawn_aero2_element() function

# Creates the object representing an aerodynamic body element
def spawn_aero3_element(elem, context):
    """ Draws an aerodynamic beam3 element as two-quads mesh object
        whose vertices are rigidly connected to the parent nodes objects """

    nd = context.scene.mbdyn.nodes
 
    # try to find Blender objects associated with the nodes that 
    # the element belongs to
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

    # name of the plane object
    planeobj_id = elem.type + "_" + str(elem.int_label)
    
    try:
        set_active_collection('aerodynamic')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['aerodynamic'].children.link(elcol)
        set_active_collection(elcol.name)
    except KeyError:
        return {'COLLECTION_ERROR'}

    # check if the object is already present. If it is, remove it
    if planeobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[planeobj_id])

    # create a mesh plane
    bpy.ops.mesh.primitive_plane_add(location = (0.0, 0.0, 0.0))
    aero3OBJ = bpy.context.view_layer.objects.active
    aero3OBJ.name = elem.name
    aero3OBJ.mbdyn.type = 'element'
    aero3OBJ.mbdyn.dkey = elem.name
    mesh = aero3OBJ.data

    bpy.ops.object.select_all(action = 'DESELECT')
    aero3OBJ.select_set(state = True)
    bpy.context.view_layer.objects.active = aero3OBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    
    bm = bmesh.from_edit_mesh(aero3OBJ.data)
    sel_edges = [edge for edge in bm.edges if edge.index in {1,3}]
    bmesh.ops.subdivide_edges(bm, edges=sel_edges, cuts = 1)
    bmesh.update_edit_mesh(aero3OBJ.data)

    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')

    # move vertices
    mesh.vertices[0].co = n1OBJ.matrix_world@Vector(( elem.offsets[0].value ))
    mesh.vertices[2].co = n1OBJ.matrix_world@Vector(( elem.offsets[1].value ))
    mesh.vertices[4].co = n2OBJ.matrix_world@Vector(( elem.offsets[2].value ))
    mesh.vertices[5].co = n2OBJ.matrix_world@Vector(( elem.offsets[3].value ))
    mesh.vertices[1].co = n3OBJ.matrix_world@Vector(( elem.offsets[4].value ))
    mesh.vertices[3].co = n3OBJ.matrix_world@Vector(( elem.offsets[5].value ))
 
    bpy.ops.object.select_all(action = 'DESELECT')
    aero3OBJ.select_set(state = True)
    bpy.context.view_layer.objects.active = aero3OBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)

    # add hooks
    hook_vertices(bmesh.from_edit_mesh(mesh), {0, 2}, n1OBJ)
    hook_vertices(bmesh.from_edit_mesh(mesh), {1, 3}, n3OBJ)
    hook_vertices(bmesh.from_edit_mesh(mesh), {4, 5}, n2OBJ)

    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')
    
    aero3OBJ.rotation_mode = n1OBJ.rotation_mode
    aero3OBJ.lock_scale[0] = True
    aero3OBJ.lock_scale[1] = True
    aero3OBJ.lock_scale[2] = True

    aero3OBJ.mbdyn.dkey = elem.name
    aero3OBJ.mbdyn.type = 'element'
    elem.blender_object = aero3OBJ.name

    # set collections
    elcol.objects.link(n1OBJ)
    elcol.objects.link(n2OBJ)
    elcol.objects.link(n3OBJ)
    set_active_collection('Master Collection')

    return{'FINISHED'}
# -----------------------------------------------------------
# end of spawn_aero3_element() function

class BLENDYN_OT_import_aerodynamic_body(bpy.types.Operator):
    """ Imports an Aerodynamic Body in the scene """
    bl_idname = "blendyn.import_aerodynamic_body"
    bl_label = "MBDyn aerodynamic body element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['aero0_' + str(self.int_label)]
            retval = spawn_aero0_element(elem, context)
            if retval == {'NODE1_NOTFOUND'}:
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
# -----------------------------------------------------------
# end of BLENDYN_OT_import_aerodynamic_body class

class BLENDYN_OT_import_aerodynamic_beam2(bpy.types.Operator):
    """ Imports an Aerodynamic Beam2 in the scene """
    bl_idname = "blendyn.import_aerodynamic_beam2"
    bl_label = "MBDyn two-node aerodynamic beam element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['aero2_' + str(self.int_label)]
            retval = spawn_aero2_element(elem, context)
            if retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
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
# -----------------------------------------------------------
# end of BLENDYN_OT_import_aerodynamic_beam2class

class BLENDYN_OT_import_aerodynamic_beam3(bpy.types.Operator):
    """ Imports an Aerodynamic Beam2 in the scene """
    bl_idname = "blendyn.import_aerodynamic_beam3"
    bl_label = "MBDyn three-node aerodynamic beam element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['aero3_' + str(self.int_label)]
            retval = spawn_aero3_element(elem, context)
            if retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE3_NOTFOUND'}:
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
# -----------------------------------------------------------
# end of BLENDYN_OT_import_aerodynamic_beam3 class
