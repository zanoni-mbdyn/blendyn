# --------------------------------------------------------------------------
# Blendyn -- file componentlib.py
# Copyright (C) 2020 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import os
import bpy

import logging
baseLogger = logging.getLogger()
baseLogger.setLevel(logging.DEBUG)

from mathutils import *
from math import *

from .utilslib import *

DEFORMABLE_ELEMENTS = {'beam3', 'beam3'}

def update_cd_index(self, context):
    mbs = context.scene.mbdyn
    comps = mbs.components

    if (mbs.cd_index != len(comps) - 1) and mbs.adding_component:
        mbs.cd_index = len(comps) - 1
    elif mbs.cd_index >= len(comps):
        mbs.cd_index = len(comps) - 1

def get_comp_mesh_objects(self, context):
    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems
    comps = mbs.components

    mesh_objs = [obj for obj in bpy.data.objects \
            if (obj.type == 'MESH') and (obj.mbdyn.dkey not in nd.keys()) and (obj.mbdyn.dkey not in ed.keys())]
    return [(mesh_obj.name, mesh_obj.name, "") for mesh_obj in mesh_objs]

def update_elem_str_idx(self, context):
    # Updates the order of the elements in component
    # FIXME: find a more efficient way!!
    comp = eval('context.scene.mbdyn.' + self.path_from_id().split('.')[1])
    if self.str_idx == len(comp.elements):
        self.str_idx = 0
    else:
        for elem in comp.elements:
            if elem != self and elem.str_idx == self.str_idx:
                elem.str_idx += 1
                break
# -----------------------------------------------------------
# end of update_elem_str_idx() function

def add_mesh_component(context, component):
    """ Finalized a component definition by creating the armature 
        controlling the component deformation, based on the component
        elements definitions, and assigning it to the selected mesh
        object """

    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    # helper functions: add bones to armature of component for each
    # type of elemens
    def add_comp_armature_bones_beam3(armOBJ, armature, component, celem):
        elem = ed[celem.elem]
        elcol = bpy.data.collections[elem.name]
        node_objs = []
        # find element nodes' objects
        for obj in elcol.objects:
            try:
                node_objs.append(nd[obj.mbdyn.dkey])
            except KeyError:
                pass
        for elnode in elem.nodes:
            for node in nd:
                if node.int_label == elnode.int_label:
                    node_objs.append(bpy.data.objects[node.blender_object])
                    break
        RF1 = elcol.objects[elem.name + '_RF1'] 
        RF2 = elcol.objects[elem.name + '_RF2']
        RF3 = elcol.objects[elem.name + '_RF3']
        pRF1 = RF1.matrix_world.to_translation()
        pRF2 = RF2.matrix_world.to_translation()
        pRF3 = RF3.matrix_world.to_translation()

        t1 = -3*pRF1 + 4*pRF2 - pRF3
        t1.normalize()
        t2 = -pRF1 + pRF3
        t2.normalize()
        t3 = 3*pRF3 - 4*pRF2 + pRF1
        t3.normalize()
      
        # approximate length (FIXME: use 'exact' length?)
        L1 = (pRF2 - pRF1).length
        L2 = (pRF3 - pRF2).length 

        # enter edit mode and add bones
        bpy.context.view_layer.objects.active = armOBJ
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        edit_bones = armature.edit_bones 

        # node 1
        bN1 = edit_bones.new(elem.name + '_' + node_objs[0].name)
        bN1.head = pRF1
        bN1.tail = pRF1 + 0.001*t1*L1
        bN1.use_deform = False
        # node 2
        bN2 = edit_bones.new(elem.name + '_' + node_objs[1].name)
        bN2.head = pRF2 - 0.001*L1*t2
        bN2.tail = pRF2 + 0.001*L2*t2
        bN2.use_deform = False
        # node 3
        bN3 = edit_bones.new(elem.name + '_' + node_objs[2].name)
        bN3.head = pRF3 - 0.001*L1*t3
        bN3.tail = pRF3
        bN3.use_deform = False
        # volume 1 (node 1 -- node 2)
        bV1 = edit_bones.new(elem.name + '_V1')
        bV1.head = bN1.tail
        bV1.tail = bN2.head
        bV1.bbone_segments = celem.arm_ns
        # volume 2 (node 2 -- node 3)
        bV2 = edit_bones.new(elem.name + '_V2')
        bV2.head = bN2.tail
        bV2.tail = bN3.head
        bV2.bbone_segments = celem.arm_ns
        # parenting
        bV1.parent = bN1
        bV2.parent = bN2
        armOBJ.data.display_type = 'BBONE'

        # contraints
        bpy.ops.object.mode_set(mode = 'POSE', toggle = False)

        # volume 1
        V1 = armOBJ.pose.bones[elem.name + '_V1']
        stV1N2 = V1.constraints.new(type = 'STRETCH_TO')
        stV1N2.target = armOBJ
        stV1N2.subtarget = elem.name + '_' + node_objs[1].name
        V1 = armOBJ.data.bones[elem.name + '_V1']
        V1.bbone_handle_type_start = 'TANGENT'
        V1.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + node_objs[0].name]
        V1.bbone_handle_type_end = 'TANGENT'
        V1.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + node_objs[1].name]
        # volume 2
        V2 = armOBJ.pose.bones[elem.name + '_V2']
        stV2N3 = V2.constraints.new(type = 'STRETCH_TO')
        stV2N3.target = armOBJ
        stV2N3.subtarget = elem.name + '_' + node_objs[2].name
        V2 = armOBJ.data.bones[elem.name + '_V2']
        V2.bbone_handle_type_start = 'TANGENT'
        V2.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + node_objs[1].name]
        V2.bbone_handle_type_end = 'TANGENT'
        V2.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + node_objs[2].name]
        # node 1
        N1 = armOBJ.pose.bones[elem.name + '_' + node_objs[0].name]
        clN1RF1 = N1.constraints.new(type = 'COPY_LOCATION')
        clN1RF1.target = RF1
        crN1RF1 = N1.constraints.new(type = 'CHILD_OF')
        crN1RF1.use_location_x = False
        crN1RF1.use_location_y = False
        crN1RF1.use_location_z = False
        crN1RF1.use_scale_x = False
        crN1RF1.use_scale_y = False
        crN1RF1.use_scale_z = False
        crN1RF1.target = RF1
        crN1RF1.inverse_matrix = RF1.matrix_world.inverted()
        # node 2
        N2 = armOBJ.pose.bones[elem.name + '_' + node_objs[1].name]
        clN2RF2 = N2.constraints.new(type = 'COPY_LOCATION')
        clN2RF2.target = RF2
        crN2RF2 = N2.constraints.new(type = 'CHILD_OF')
        crN2RF2.use_location_x = False
        crN2RF2.use_location_y = False
        crN2RF2.use_location_z = False
        crN2RF2.use_scale_x = False
        crN2RF2.use_scale_y = False
        crN2RF2.use_scale_z = False
        crN2RF2.target = RF2
        crN2RF2.inverse_matrix = RF2.matrix_world.inverted()
        # node 3
        N3 = armOBJ.pose.bones[elem.name + '_' + node_objs[2].name]
        clN3RF3 = N3.constraints.new(type = 'COPY_LOCATION')
        clN3RF3.target = RF3
        crN3RF3 = N3.constraints.new(type = 'CHILD_OF')
        crN3RF3.use_location_x = False
        crN3RF3.use_location_y = False
        crN3RF3.use_location_z = False
        crN3RF3.use_scale_x = False
        crN3RF3.use_scale_y = False
        crN3RF3.use_scale_z = False
        crN3RF3.target = RF3
        crN3RF3.inverse_matrix = RF3.matrix_world.inverted()

        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
        # -------------------------------------------------------
        # end of add_comp_armature_bones_beam3() helper function
    
    def add_comp_armature_bones_beam2(armOBJ, armature, component, celem):
        elem = ed[celem.elem]
        elcol = bpy.data.collections[elem.name]
        node_objs = []
        # find element nodes' objects
        for obj in elcol.objects:
            try:
                node_objs.append(nd[obj.mbdyn.dkey])
            except KeyError:
                pass
        for elnode in elem.nodes:
            for node in nd:
                if node.int_label == elnode.int_label:
                    node_objs.append(bpy.data.objects[node.blender_object])
                    break
        RF1 = elcol.objects[elem.name + '_RF1'] 
        RF2 = elcol.objects[elem.name + '_RF2']
        pRF1 = RF1.matrix_world.to_translation()
        pRF2 = RF2.matrix_world.to_translation()

        # unit vector pointing along beam axis from RF1
        t1 = -pRF1 + pRF2
        t1.normalize()

        # beam length
        L = (pRF2 - pRF1).length

        # enter edit mode and add bones
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        edit_bones = armature.edit_bones 

        # node 1
        bN1 = edit_bones.new(elem.name + '_' + node_objs[0].name)
        bN1.head = pRF1 
        bN1.tail = pRF1 + 0.001*t1*L
        bN1.use_deform = False
        # node 2
        bN2 = edit_bones.new(elem.name + '_' + node_objs[1].name)
        bN2.head = pRF2 - 0.001*t1*L
        bN2.tail = pRF2
        bN2.use_deform = False
        # volume 1 (node 1 -- node 2)
        bV1 = edit_bones.new(elem.name + '_V1')
        bV1.head = bN1.tail
        bV1.tail = bN2.head
        bV1.bbone_segments = celem.arm_ns
        # parenting
        bV1.parent = bN1
        armOBJ.data.display_type = 'BBONE'

        # contraints
        bpy.ops.object.mode_set(mode = 'POSE', toggle = False)

        # volume 1
        V1 = armOBJ.pose.bones[elem.name + '_V1']
        stV1N2 = V1.constraints.new(type = 'STRETCH_TO')
        stV1N2.target = armOBJ
        stV1N2.subtarget = elem.name + '_' + node_objs[1].name
        V1 = armOBJ.data.bones['_V1']
        V1.bbone_handle_type_start = 'TANGENT'
        V1.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + node_objs[0].name]
        V1.bbone_handle_type_end = 'TANGENT'
        V1.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + node_objs[1].name]
        # node 1
        N1 = armOBJ.pose.bones[node_objs[0].name]
        clN1RF1 = N1.constraints.new(type = 'COPY_LOCATION')
        clN1RF1.target = RF1
        crN1RF1 = N1.constraints.new(type = 'CHILD_OF')
        crN1RF1.use_location_x = False
        crN1RF1.use_location_y = False
        crN1RF1.use_location_z = False
        crN1RF1.use_scale_x = False
        crN1RF1.use_scale_y = False
        crN1RF1.use_scale_z = False
        crN1RF1.target = RF1
        crN1RF1.inverse_matrix = RF1.matrix_world.inverted()
        # node 2
        N2 = armOBJ.pose.bones[node_objs[1].name]
        clN2RF2 = N2.constraints.new(type = 'COPY_LOCATION')
        clN2RF2.target = RF2
        crN2RF2 = N2.constraints.new(type = 'CHILD_OF')
        crN2RF2.use_location_x = False
        crN2RF2.use_location_y = False
        crN2RF2.use_location_z = False
        crN2RF2.use_scale_x = False
        crN2RF2.use_scale_y = False
        crN2RF2.use_scale_z = False
        crN2RF2.target = RF2
        crN2RF2.inverse_matrix = RF2.matrix_world.inverted()

        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
        # -------------------------------------------------------
        # end of add_comp_armature_bones_beam2() helper function

    # add the armature object
    armature = bpy.data.armatures.new(component.name)
    armOBJ = bpy.data.objects.new(component.name, armature)
    try: 
        bpy.data.collections['mbdyn.components'].objects.link(armOBJ)
    except KeyError:
        mccol = bpy.data.collections.new(name = 'mbdyn.components')
        bpy.context.scene.collection.children.link(mccol)
        mccol.objects.link(armOBJ)
    set_active_collection('mbdyn.components')
    bpy.context.view_layer.objects.active = armOBJ

    # add bones
    reference = []      # reference object
    for celem in component.elements:
        elem = ed[celem.elem]
        if elem.type == 'beam3':
            if not reference:
                elcol = bpy.data.collections[elem.name]
                reference = elcol.objects[elem.name + '_RF1']
            add_comp_armature_bones_beam3(armOBJ, armature, component, celem)
        elif elem.type == 'beam2':
            if not reference:
                elcol = bpy.data.collections[elem.name]
                reference = elcol.objects[elem.name + '_RF1']
            add_comp_armature_bones_beam2(armOBJ, armature, component, celem)
        else: 
            return {'ELEM_TYPE_UNSUPPORTED'}

    # parent object deformation to armature
    # FIXME: is there a way to do this without bpy.ops?
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')

    compOBJ = bpy.data.objects[component.object]
    compOBJ.matrix_world = reference.matrix_world
    compOBJ.select_set(state = True)
    armOBJ.select_set(state = True)
    bpy.context.view_layer.objects.active = armOBJ
    retval = bpy.ops.object.parent_set(type = 'ARMATURE_AUTO')
    bpy.ops.object.select_all(action = 'DESELECT') 

    if retval == {'FINISHED'}:
        return retval
    elif retval == {'CANCELED'}:
        message = "Unable to parent component armature to mesh."
        return {'ARMATURE_PARENT_FAILED'}

# -----------------------------------------------------------
# end of add_mesh_component() function


