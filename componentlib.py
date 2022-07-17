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

DEFORMABLE_ELEMENTS = {'beam3', 'beam2', 'shell4', 'membrane4', 'modal'}

import pdb

def update_cd_index(self, context):
    mbs = context.scene.mbdyn
    comps = mbs.components

    if len(comps):
        if (mbs.cd_index != len(comps) - 1) and mbs.adding_component:
            mbs.cd_index = len(comps) - 1
        elif mbs.cd_index >= len(comps):
            mbs.cd_index = len(comps) - 1
# -----------------------------------------------------------
# end of update_cd_index() function


def get_comp_mesh_objects(self, context):
    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems
    comps = mbs.components

    mesh_objs = [obj for obj in bpy.data.objects \
            if (obj.type == 'MESH') and (obj.mbdyn.dkey not in nd.keys()) and (obj.mbdyn.dkey not in ed.keys())]
    mo = [(mesh_obj.name, mesh_obj.name, "") for mesh_obj in mesh_objs]
    # allow to not set any object, and just create the armature
    mo.append(('', '', ''))        
    return mo 
# -----------------------------------------------------------
# end of get_comp_mesh_objects() function


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
        elements definitions, and (optionally) assigning it to the 
        selected mesh object """

    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    # helper functions: add bones to armature of component for each
    # type of elements

    def add_comp_armature_bones_plate(armOBJ, armature, component, celem):
        # shell and membrane elements

        elem = ed[celem.elem]
        elcol = bpy.data.collections[elem.name]
        node_objs = []

        # find element nodes' objects
        for obj in elcol.objects:
            try:
                node_objs.append(nd[obj.mbdyn.dkey])
            except KeyError:
                pass

        N1 = elcol.objects[node_objs[0].blender_object]
        N2 = elcol.objects[node_objs[1].blender_object]
        N3 = elcol.objects[node_objs[2].blender_object]
        N4 = elcol.objects[node_objs[3].blender_object]

        pN1 = N1.matrix_world.to_translation()
        pN2 = N2.matrix_world.to_translation()
        pN3 = N3.matrix_world.to_translation()
        pN4 = N4.matrix_world.to_translation()

        t1 = (pN2 - pN1)
        L1 = t1.length
        t2 = (pN3 - pN2)
        L2 = t2.length
        t3 = (pN4 - pN3)
        L3 = t3.length
        t4 = (pN1 - pN4)
        L4 = t4.length

        if L1 == 0 or L2 == 0 or L3 == 0 or L4 == 0:
            return {'ZERO VOLUME BONE'}

        t1.normalize()
        t2.normalize()
        t3.normalize()
        t4.normalize()

        # enter edit mode and add bones
        bpy.context.view_layer.objects.active = armOBJ
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        edit_bones = armature.edit_bones 

        # node 1 -- aligned with (pN2 - pN1)
        bN1_21 = edit_bones.new(elem.name + '_' + N1.name + '_21')
        bN1_21.head = pN1
        bN1_21.tail = pN1 + 0.001*t1*L1
        bN1_21.use_deform = False
        # node 2 -- aligned with (pN2 - pN1)
        bN2_21 = edit_bones.new(elem.name + '_' + N2.name + '_21')
        bN2_21.head = pN2 - 0.001*t1*L1
        bN2_21.tail = pN2
        bN2_21.use_deform = False
        # node 2 -- aligned with (pN3 - pN2)
        bN2_32 = edit_bones.new(elem.name + '_' + N2.name + '_32')
        bN2_32.head = pN2
        bN2_32.tail = pN2 + 0.001*t2*L2
        bN2_32.use_deform = False
        # node 3 -- aligned with (pN3 - pN2)
        bN3_32 = edit_bones.new(elem.name + '_' + N3.name + '_32')
        bN3_32.head = pN3 - 0.001*t2*L2
        bN3_32.tail = pN3
        bN3_32.use_deform = False
        # node 3 -- aligned with (pN4 - pN3)
        bN3_43 = edit_bones.new(elem.name + '_' + N3.name + '_43')
        bN3_43.head = pN3
        bN3_43.tail = pN3 + 0.001*t3*L3
        bN3_43.use_deform = False
        # node 4 -- aligned with (pN4 - pN3)
        bN4_43 = edit_bones.new(elem.name + '_' + N4.name + '_43')
        bN4_43.head = pN4 - 0.001*t3*L3
        bN4_43.tail = pN4
        bN4_43.use_deform = False
        # node 4 -- aligned with (pN1 - pN4)
        bN4_14 = edit_bones.new(elem.name + '_' + N4.name + '_14')
        bN4_14.head = pN4
        bN4_14.tail = pN4 + 0.001*t4*L4
        bN4_14.use_deform = False
        # node 1 -- aligned with (pN1 - pN4)
        bN1_14 = edit_bones.new(elem.name + '_' + N1.name + '_14')
        bN1_14.head = pN1 - 0.001*t4*L4
        bN1_14.tail = pN1
        bN1_14.use_deform = False

        # volume 1 (node 1 -- node 2)
        bV1 = edit_bones.new(elem.name + '_V1')
        bV1.head = bN1_21.tail
        bV1.tail = bN2_21.head
        bV1.bbone_segments = celem.arm_ns
        # volume 2 (node 2 -- node 3)
        bV2 = edit_bones.new(elem.name + '_V2')
        bV2.head = bN2_32.tail
        bV2.tail = bN3_32.head
        bV2.bbone_segments = celem.arm_ns
        # volume 3 (node 3 -- node 4)
        bV3 = edit_bones.new(elem.name + '_V3')
        bV3.head = bN3_43.tail
        bV3.tail = bN4_43.head
        bV3.bbone_segments = celem.arm_ns
        # volume 4 (node 4 -- node 1)
        bV4 = edit_bones.new(elem.name + '_V4')
        bV4.head = bN4_14.head
        bV4.tail = bN1_14.tail
        bV4.bbone_segments = celem.arm_ns

        # parenting
        bV1.parent = bN1_21
        bV2.parent = bN2_32
        bV3.parent = bN3_43
        bV4.parent = bN4_14

        # show as Bendy Bone
        armOBJ.data.display_type = 'BBONE'

        # constraints
        bpy.ops.object.mode_set(mode = 'POSE', toggle = False)

        # volume 1
        V1 = armOBJ.pose.bones[elem.name + '_V1']
        stV1N2 = V1.constraints.new(type = 'STRETCH_TO')
        stV1N2.target = armOBJ
        stV1N2.subtarget = elem.name + '_' + N2.name + '_21'
        V1 = armOBJ.data.bones[elem.name + '_V1']
        V1.bbone_handle_type_start = 'TANGENT'
        V1.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + N1.name + '_21']
        V1.bbone_handle_type_end = 'TANGENT'
        V1.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + N2.name + '_21']
        # volume 2
        V2 = armOBJ.pose.bones[elem.name + '_V2']
        stV2N3 = V2.constraints.new(type = 'STRETCH_TO')
        stV2N3.target = armOBJ
        stV2N3.subtarget = elem.name + '_' + N3.name + '_32'
        V2 = armOBJ.data.bones[elem.name + '_V2']
        V2.bbone_handle_type_start = 'TANGENT'
        V2.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + N2.name + '_32']
        V2.bbone_handle_type_end = 'TANGENT'
        V2.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + N3.name + '_32']
        # volume 3
        V3 = armOBJ.pose.bones[elem.name + '_V3']
        stV3N4 = V3.constraints.new(type = 'STRETCH_TO')
        stV3N4.target = armOBJ
        stV3N4.subtarget = elem.name + '_' + N4.name + '_43'
        V4 = armOBJ.data.bones[elem.name + '_V4']
        V4.bbone_handle_type_start = 'TANGENT'
        V4.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + N3.name + '_43']
        V4.bbone_handle_type_end = 'TANGENT'
        V4.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + N4.name + '_43']
        # volume 4
        V4 = armOBJ.pose.bones[elem.name + '_V4']
        stV4N1 = V4.constraints.new(type = 'STRETCH_TO')
        stV4N1.target = armOBJ
        stV4N1.subtarget = elem.name + '_' + N1.name + '_14'
        V4 = armOBJ.data.bones[elem.name + '_V4']
        V4.bbone_handle_type_start = 'TANGENT'
        V4.bbone_custom_handle_start = armOBJ.data.bones[elem.name + '_' + N4.name + '_14']
        V4.bbone_handle_type_end = 'TANGENT'
        V4.bbone_custom_handle_end = armOBJ.data.bones[elem.name + '_' + N1.name + '_14']
        
        # node 1 -- aligned with (pN2 - pN1)
        pbN1_21 = armOBJ.pose.bones[elem.name + '_' + N1.name + '_21']
        clN1_21 = pbN1_21.constraints.new(type = 'COPY_LOCATION')
        clN1_21.target = N1
        crN1_21 = pbN1_21.constraints.new(type = 'CHILD_OF')
        crN1_21.use_location_x = False
        crN1_21.use_location_y = False
        crN1_21.use_location_z = False
        crN1_21.use_scale_x = False
        crN1_21.use_scale_y = False
        crN1_21.use_scale_z = False
        crN1_21.target = N1
        crN1_21.inverse_matrix = N1.matrix_world.inverted()
        
        # node 1 -- aligned with (pN1 - pN4)
        pbN1_14 = armOBJ.pose.bones[elem.name + '_' + N1.name + '_14']
        clN1_14 = pbN1_14.constraints.new(type = 'COPY_LOCATION')
        clN1_14.target = N1
        crN1_14 = pbN1_14.constraints.new(type = 'CHILD_OF')
        crN1_14.use_location_x = False
        crN1_14.use_location_y = False
        crN1_14.use_location_z = False
        crN1_14.use_scale_x = False
        crN1_14.use_scale_y = False
        crN1_14.use_scale_z = False
        crN1_14.target = N1
        crN1_14.inverse_matrix = N1.matrix_world.inverted()
        
        # node 2 -- aligned with (pN2 - pN1)
        pbN2_21 = armOBJ.pose.bones[elem.name + '_' + N2.name + '_21']
        clN2_21 = pbN2_21.constraints.new(type = 'COPY_LOCATION')
        clN2_21.target = N2
        crN2_21 = pbN2_21.constraints.new(type = 'CHILD_OF')
        crN2_21.use_location_x = False
        crN2_21.use_location_y = False
        crN2_21.use_location_z = False
        crN2_21.use_scale_x = False
        crN2_21.use_scale_y = False
        crN2_21.use_scale_z = False
        crN2_21.target = N2
        crN2_21.inverse_matrix = N2.matrix_world.inverted()
        
        # node 2 -- aligned with (pN3 - pN2)
        pbN2_32 = armOBJ.pose.bones[elem.name + '_' + N2.name + '_32']
        clN2_32 = pbN2_32.constraints.new(type = 'COPY_LOCATION')
        clN2_32.target = N2
        crN2_32 = pbN2_32.constraints.new(type = 'CHILD_OF')
        crN2_32.use_location_x = False
        crN2_32.use_location_y = False
        crN2_32.use_location_z = False
        crN2_32.use_scale_x = False
        crN2_32.use_scale_y = False
        crN2_32.use_scale_z = False
        crN2_32.target = N2
        crN2_32.inverse_matrix = N2.matrix_world.inverted() 

        # node 3 -- aligned with (pN3 - pN2)
        pbN3_32 = armOBJ.pose.bones[elem.name + '_' + N3.name + '_32']
        clN3_32 = pbN3_32.constraints.new(type = 'COPY_LOCATION')
        clN3_32.target = N3
        crN3_32 = pbN3_32.constraints.new(type = 'CHILD_OF')
        crN3_32.use_location_x = False
        crN3_32.use_location_y = False
        crN3_32.use_location_z = False
        crN3_32.use_scale_x = False
        crN3_32.use_scale_y = False
        crN3_32.use_scale_z = False
        crN3_32.target = N3
        crN3_32.inverse_matrix = N3.matrix_world.inverted()
        
        # node 3 -- aligned with (pN4 - pN3)
        pbN3_43 = armOBJ.pose.bones[elem.name + '_' + N3.name + '_43']
        clN3_43 = pbN3_43.constraints.new(type = 'COPY_LOCATION')
        clN3_43.target = N3
        crN3_43 = pbN3_43.constraints.new(type = 'CHILD_OF')
        crN3_43.use_location_x = False
        crN3_43.use_location_y = False
        crN3_43.use_location_z = False
        crN3_43.use_scale_x = False
        crN3_43.use_scale_y = False
        crN3_43.use_scale_z = False
        crN3_43.target = N3
        crN3_43.inverse_matrix = N3.matrix_world.inverted()

        # node 4 -- aligned with (pN4 - pN3)
        pbN4_43 = armOBJ.pose.bones[elem.name + '_' + N4.name + '_43']
        clN4_43 = pbN4_43.constraints.new(type = 'COPY_LOCATION')
        clN4_43.target = N4
        crN4_43 = pbN4_43.constraints.new(type = 'CHILD_OF')
        crN4_43.use_location_x = False
        crN4_43.use_location_y = False
        crN4_43.use_location_z = False
        crN4_43.use_scale_x = False
        crN4_43.use_scale_y = False
        crN4_43.use_scale_z = False
        crN4_43.target = N4
        crN4_43.inverse_matrix = N4.matrix_world.inverted() 
        
        # node 4 -- aligned with (pN1 - pN4)
        pbN4_14 = armOBJ.pose.bones[elem.name + '_' + N4.name + '_14']
        clN4_14 = pbN4_14.constraints.new(type = 'COPY_LOCATION')
        clN4_14.target = N4
        crN4_14 = pbN4_14.constraints.new(type = 'CHILD_OF')
        crN4_14.use_location_x = False
        crN4_14.use_location_y = False
        crN4_14.use_location_z = False
        crN4_14.use_scale_x = False
        crN4_14.use_scale_y = False
        crN4_14.use_scale_z = False
        crN4_14.target = N4
        crN4_14.inverse_matrix = N4.matrix_world.inverted()

        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
        # -------------------------------------------------------
        # end of add_comp_armature_bones_plate() helper function

    def add_comp_armature_bones_beam3(armOBJ, armature, component, celem):
        elem = ed[celem.elem]
        elcol = bpy.data.collections[elem.name]
        node_objs = []

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

        if L1 == 0  or L2 == 0:
            return {'ZERO VOLUME BONE'}

        # enter edit mode and add bones
        bpy.context.view_layer.objects.active = armOBJ
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        edit_bones = armature.edit_bones 

        # node 1
        bN1 = edit_bones.new(RF1.name)
        bN1.head = pRF1
        bN1.tail = pRF1 + 0.001*t1*L1
        bN1.use_deform = False
        # node 2
        bN2 = edit_bones.new(RF2.name)
        bN2.head = pRF2 - 0.001*L1*t2
        bN2.tail = pRF2 + 0.001*L2*t2
        bN2.use_deform = False
        # node 3
        bN3 = edit_bones.new(RF3.name)
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

        # show as Bendy Bone
        armOBJ.data.display_type = 'BBONE'

        # constraints
        bpy.ops.object.mode_set(mode = 'POSE', toggle = False)

        # volume 1
        V1 = armOBJ.pose.bones[elem.name + '_V1']
        stV1N2 = V1.constraints.new(type = 'STRETCH_TO')
        stV1N2.target = armOBJ
        stV1N2.subtarget = RF2.name
        V1 = armOBJ.data.bones[elem.name + '_V1']
        V1.bbone_handle_type_start = 'TANGENT'
        V1.bbone_custom_handle_start = armOBJ.data.bones[RF1.name]
        V1.bbone_handle_type_end = 'TANGENT'
        V1.bbone_custom_handle_end = armOBJ.data.bones[RF2.name]
        # volume 2
        V2 = armOBJ.pose.bones[elem.name + '_V2']
        stV2N3 = V2.constraints.new(type = 'STRETCH_TO')
        stV2N3.target = armOBJ
        stV2N3.subtarget = RF3.name
        V2 = armOBJ.data.bones[elem.name + '_V2']
        V2.bbone_handle_type_start = 'TANGENT'
        V2.bbone_custom_handle_start = armOBJ.data.bones[RF2.name]
        V2.bbone_handle_type_end = 'TANGENT'
        V2.bbone_custom_handle_end = armOBJ.data.bones[RF3.name]
        # node 1
        N1 = armOBJ.pose.bones[RF1.name]
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
        N2 = armOBJ.pose.bones[RF2.name]
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
        N3 = armOBJ.pose.bones[RF3.name]
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
        
        RF1 = elcol.objects[elem.name + '_RF1'] 
        RF2 = elcol.objects[elem.name + '_RF2']
        pRF1 = RF1.matrix_world.to_translation()
        pRF2 = RF2.matrix_world.to_translation()


        # unit vector pointing along beam axis from RF1
        t1 = -pRF1 + pRF2
        t1.normalize()

        # beam length
        L = (pRF2 - pRF1).length

        if L == 0:
            return {'ZERO VOLUME BONE'}

        # enter edit mode and add bones

        bpy.context.view_layer.objects.active = armOBJ
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        edit_bones = armature.edit_bones

        # node 1
        bN1 = edit_bones.new(RF1.name)
        bN1.head = pRF1 
        bN1.tail = pRF1 + 0.001*t1*L
        bN1.use_deform = False
        # node 2
        bN2 = edit_bones.new(RF2.name)
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
        stV1N2.subtarget = RF2.name
        V1 = armOBJ.data.bones[elem.name + '_V1']
        V1.bbone_handle_type_start = 'TANGENT'
        V1.bbone_custom_handle_start = armOBJ.data.bones[RF1.name]
        V1.bbone_handle_type_end = 'TANGENT'
        V1.bbone_custom_handle_end = armOBJ.data.bones[RF2.name]
        # node 1
        N1 = armOBJ.pose.bones[RF1.name]
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
        N2 = armOBJ.pose.bones[RF2.name]
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

    def add_comp_armature_bones_modal(armOBJ, armature, component, celem):
        elem = ed[celem.elem]
        elcol = bpy.data.collections[elem.name]


        for connect in elem.fem_connects:
            node_objs = []
            N1 = elcol.objects[nd["node_" + str(connect.node_1_int_label)].blender_object]
            N2 = elcol.objects[nd["node_" + str(connect.node_2_int_label)].blender_object]
            lN1 = N1.location
            lN2 = N2.location
            pN1 = Vector((lN1[0], lN1[1], lN1[2]))
            pN2 = Vector((lN2[0], lN2[1], lN2[2]))
            if pN1 == pN2:
                return {'ZERO VOLUME BONE'}

            # unit vector pointing along connect axis from N1
            t1 = -pN1 + pN2
            t1.normalize()

            # connect length
            L = (pN2 - pN1).length

            # enter edit mode and add bones
            bpy.context.view_layer.objects.active = armOBJ
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            edit_bones = armature.edit_bones

            # node 1
            bN1 = edit_bones.new(connect.name +'_'+ N1.name)
            bN1.head = pN1
            bN1.tail = pN1 + 0.001 * t1 * L
            bN1.use_deform = False
            # node 2
            bN2 = edit_bones.new(connect.name +'_'+ N2.name)
            bN2.head = pN2 - 0.001 * t1 * L
            bN2.tail = pN2
            bN2.use_deform = False
            # volume 1 (node 1 -- node 2)
            bV1 = edit_bones.new(connect.name + '_V1')
            bV1.head = bN1.tail
            bV1.tail = bN2.head
            bV1.bbone_segments = celem.arm_ns
            # parenting
            bV1.parent = bN1
            armOBJ.data.display_type = 'BBONE'

            # contraints
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            # volume 1
            V1 = armOBJ.pose.bones[connect.name + '_V1']
            stV1N2 = V1.constraints.new(type='STRETCH_TO')
            stV1N2.target = N2
            #stV1N2.subtarget = N2.name
            V1 = armOBJ.data.bones[connect.name + '_V1']
            V1.bbone_handle_type_start = 'TANGENT'
            V1.bbone_custom_handle_start = armOBJ.data.bones[connect.name +'_'+N1.name]
            V1.bbone_handle_type_end = 'TANGENT'
            V1.bbone_custom_handle_end = armOBJ.data.bones[connect.name +'_'+N2.name]
            # node 1
            pbN1 = armOBJ.pose.bones[connect.name +'_'+ N1.name]
            clpbN1 = pbN1.constraints.new(type='COPY_LOCATION')
            clpbN1.target = N1
            crpbN1 = pbN1.constraints.new(type='CHILD_OF')
            crpbN1.use_location_x = False
            crpbN1.use_location_y = False
            crpbN1.use_location_z = False
            crpbN1.use_scale_x = False
            crpbN1.use_scale_y = False
            crpbN1.use_scale_z = False
            crpbN1.target = N1
            crpbN1.inverse_matrix = N1.matrix_world.inverted()
            # node 2
            pbN2 = armOBJ.pose.bones[connect.name +'_'+ N2.name]
            clpbN2 = pbN2.constraints.new(type='COPY_LOCATION')
            clpbN2.target = N2
            crpbN2 = pbN2.constraints.new(type='CHILD_OF')
            crpbN2.use_location_x = False
            crpbN2.use_location_y = False
            crpbN2.use_location_z = False
            crpbN2.use_scale_x = False
            crpbN2.use_scale_y = False
            crpbN2.use_scale_z = False
            crpbN2.target = N2
            crpbN2.inverse_matrix = N2.matrix_world.inverted()

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # -------------------------------------------------------
        # end of add_comp_armature_bones_modal() helper function

    # add the armature object
    armature = bpy.data.armatures.new(component.name)
    armOBJ = bpy.data.objects.new(component.name, armature)
    try:
        mccol = bpy.data.collections['mbdyn.components']
        mccol.objects.link(armOBJ)
    except KeyError:
        mccol = bpy.data.collections.new(name = 'mbdyn.components')
        bpy.context.scene.collection.children.link(mccol)
        mccol.objects.link(armOBJ)
    set_active_collection('mbdyn.components')
    bpy.context.view_layer.objects.active = armOBJ

    # add bones
    for celem in component.elements:
        elem = ed[celem.elem]
        if elem.type == 'beam3':
            add_comp_armature_bones_beam3(armOBJ, armature, component, celem)
        elif elem.type == 'beam2':
            add_comp_armature_bones_beam2(armOBJ, armature, component, celem)
        elif elem.type in {'shell4', 'membrane4'}:
            add_comp_armature_bones_plate(armOBJ, armature, component, celem)
        elif elem.type in {'modal'}:
            add_comp_armature_bones_modal(armOBJ, armature, component, celem)
        else:
            return {'ELEM_TYPE_UNSUPPORTED'}

    # remove component elements from the update list
    celems = component.elements.keys()
    etu = mbs.elems_to_update
    if component.remove_from_etu:
        for ude in etu:
            if ude.dkey in celems:
                etu.remove(etu.find(ude.name))

    # if a mesh object is selected for the component, 
    # parent the object deformation to armature
    # FIXME: is there a way to do this without bpy.ops?
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    bpy.ops.object.select_all(action = 'DESELECT')
    component.armature = armature

    retval = {'FINISHED'}

    if component.object:
        ## Set parent
        compOBJ = bpy.data.objects[component.object]
        if compOBJ.name not in mccol.objects.keys():
            mccol.objects.link(compOBJ)
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


