# --------------------------------------------------------------------------
# Blendyn -- file stresslib.py
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


import bpy
import os
import math
from mathutils import *
import logging
try:
    from netCDF4 import Dataset
    import numpy as np
    import colorsys
except ModuleNotFoundError as ierr:
    print("BLENDYN::stresslib.py: could not import dependencies. Visualization of internal stresses and strains " \
          + "will be disabled. The reported error was:")
    print("{0}".format(ierr))

def ColorRamp_Position(head_pos, eval_pos, tail_pos):
    size = math.sqrt((head_pos[0]-tail_pos[0])**2+(head_pos[1]-tail_pos[1])**2+(head_pos[2]-tail_pos[2])**2)
    distance = math.sqrt((head_pos[0]-eval_pos[0])**2+(head_pos[1]-eval_pos[1])**2+(head_pos[2]-eval_pos[2])**2)
    return distance/size
#-------------------------------------------------------------------
# End of ColorRamp_Position function


def ColorRamp_Color(context, color_value):
    mbs = context.scene.mbdyn
    min = mbs.color_min_boundary
    max = mbs.color_max_boundary
    value_ratio = (color_value-min)/(max-min)
    if value_ratio > 1:
        h = 1
    elif value_ratio < 0:
        h = 2/3
    else:
        h = value_ratio*1/3 + 2/3
    return (h, 1, 1, 1)
#-------------------------------------------------------------------
# End of ColorRamp_Color function



def Beam_Position(curr_pos, size):
    """Calculate changing of beam position in space"""
    curr_pos = np.array(curr_pos)
    size = np.array(size)
    return curr_pos/size
#-------------------------------------------------------------------
# End of Beam_Position function


def beam2_import_stress(context, elem):
    mbs = context.scene.mbdyn

    # Set up bevel
    elem_cv = bpy.data.curves[elem.blender_object + '_cvdata']
    elem_cv.bevel_depth = 0.07
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    elemOBJ = bpy.data.objects[elem.blender_object]

    # Take the elem material
    elem_mat = bpy.data.materials.new(name=elem.name + '_mat')
    elemOBJ.data.materials.append(elem_mat)

    # Create new shader nodes
    elem_mat.use_nodes = True
    nodes = elem_mat.node_tree.nodes
    RGB = nodes.new(type = 'ShaderNodeRGB')

    # Create new shader links
    links = elem_mat.node_tree.links
    links.new(RGB.outputs[0], nodes['Principled BSDF'].inputs[0])

    # Set up color value
    ncfile = os.path.join(os.path.dirname(mbs.file_path), mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    if mbs.internal_visualize == 'Internal Force':
        variable_name = 'elem.beam.' + str(elem.int_label) + '.F'
    else:
        variable_name = 'elem.beam.' + str(elem.int_label) + '.M'

    ## Clarify the direction of internal force/moment
    if mbs.internal_visualize_dimension == "X":
        value = nc.variables[variable_name][0][0]
    elif mbs.internal_visualize_dimension == "Y":
        value = nc.variables[variable_name][0][1]
    else:
        value = nc.variables[variable_name][0][2]

    hsv = ColorRamp_Color(context, value)
    rgb = colorsys.hsv_to_rgb(hsv[0], 1 ,1)
    rgba = (rgb[0],rgb[1], rgb[2], 1)
    RGB.outputs[0].default_value = rgba
    return {'FINISHED'}
#-------------------------------------------------------------------
# End of beam2_import_stress function


def beam3_import_stress(context, elem):
    mbs = context.scene.mbdyn
    nd = mbs.nodes
    ed = mbs.elems

    # find nodes' Blender objects
    try:
        n1 = bpy.data.objects[elem.blender_object + '_RF1']
        n2 = bpy.data.objects[elem.blender_object + '_RF2']
        n3 = bpy.data.objects[elem.blender_object + '_RF3']
    except KeyError:
        return {'OBJECTS_NOTFOUND'}

    Head_pos = n1.location
    Middle_pos = n2.location
    Tail_pos = n3.location


    # Set up bevel
    elem_cv = bpy.data.curves[elem.blender_object+'_cvdata']
    elem_cv.bevel_depth = 0.07
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    elemOBJ = bpy.data.objects[elem.blender_object]

    # Take the elem material
    elem_mat = bpy.data.materials.new(name = elem.name+'_mat')
    elemOBJ.data.materials.append(elem_mat)

    # Create new shader nodes
    elem_mat.use_nodes = True
    nodes = elem_mat.node_tree.nodes
    TexCoord = nodes.new(type = 'ShaderNodeTexCoord')
    Mapping = nodes.new(type = 'ShaderNodeMapping')
    SepXYZ = nodes.new(type = 'ShaderNodeSeparateXYZ')
    ColorRamp = nodes.new(type = 'ShaderNodeValToRGB')


    # Create new shader links
    links = elem_mat.node_tree.links
    links.new(TexCoord.outputs[3], Mapping.inputs[0])
    links.new(Mapping.outputs[0], SepXYZ.inputs[0])
    links.new(SepXYZ.outputs[0], ColorRamp.inputs[0])
    links.new(ColorRamp.outputs[0], nodes['Principled BSDF'].inputs[0])

    # Set up variables value for each shader nodes
    # Select object to be origin of texture
    TexCoord.object = n2

    # Value for the first Vector Math
    Mapping.inputs[1].default_value = (0.5+elem.offsets[1].value[0], elem.offsets[1].value[1], elem.offsets[1].value[2])
    Mapping.inputs[3].default_value = (1/math.sqrt((Tail_pos[0]-Head_pos[0])**2+(Tail_pos[1]-Head_pos[1])**2+(Tail_pos[2]-Head_pos[2])**2), 1, 1)

    # Value position for three ColorRamp nodes
    ColorRamp.color_ramp.elements[0].position = 0.25
    ColorRamp.color_ramp.elements[1].position = 0.75

    # Color for three ColorRamp nodes
    ncfile = os.path.join(os.path.dirname(mbs.file_path), mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    if mbs.internal_visualize == 'Internal Force':
        variable_name_1 = 'elem.beam.'+str(elem.int_label)+'.F_I'
        variable_name_2 = 'elem.beam.'+str(elem.int_label)+'.F_II'
    else:
        variable_name_1 = 'elem.beam.' + str(elem.int_label) + '.M_I'
        variable_name_2 = 'elem.beam.' + str(elem.int_label) + '.M_II'

    ## Need to clarify the direction of internal force/moment
    if mbs.internal_visualize_dimension == "X":
        value1 = nc.variables[variable_name_1][0][0]
        value2 = nc.variables[variable_name_2][0][0]
    elif mbs.internal_visualize_dimension == "Y":
        value1 = nc.variables[variable_name_1][0][1]
        value2 = nc.variables[variable_name_2][0][1]
    else:
        value1 = nc.variables[variable_name_1][0][2]
        value2 = nc.variables[variable_name_2][0][2]

    ColorRamp.color_ramp.color_mode = 'RGB'

    hsv1 = ColorRamp_Color(context, value1)
    rgb1 = colorsys.hsv_to_rgb(hsv1[0], 1, 1)
    rgba1 = (rgb1[0], rgb1[1], rgb1[2], 1)

    hsv2 = ColorRamp_Color(context, value2)
    rgb2 = colorsys.hsv_to_rgb(hsv2[0], 1, 1)
    rgba2 = (rgb2[0], rgb2[1], rgb2[2], 1)


    ColorRamp.color_ramp.elements[0].color = rgba1
    ColorRamp.color_ramp.elements[1].color = rgba2
    return {'FINISHED'}
#-------------------------------------------------------------------
# End of beam3_import_stress function



def shell4_import_stress(context, elem):
    mbs = context.scene.mbdyn
    ed = mbs.elems
    nd = mbs.nodes
    ecol = bpy.data.collections[elem.name]
    elemOBJ = bpy.data.objects[elem.blender_object]
    try:
        n1 = bpy.data.objects[nd['node_' + str(elem.nodes[0].int_label)].blender_object]
        n2 = bpy.data.objects[nd['node_' + str(elem.nodes[1].int_label)].blender_object]
        n3 = bpy.data.objects[nd['node_' + str(elem.nodes[2].int_label)].blender_object]
        n4 = bpy.data.objects[nd['node_' + str(elem.nodes[3].int_label)].blender_object]
    except KeyError:
        return {'OBJECTS_NOTFOUND'}
    # Create the central node
    ctr_node = bpy.data.objects.new(elem.name + '_ctr', None)
    ctr_node.empty_display_type = "PLAIN_AXES"

    # Assign location and euler angle
    ctr_node.location = 0.25*(n1.location + n2.location + n3.location + n4.location)
    euler1 = 0.25 * (n1.rotation_euler[0] + n2.rotation_euler[0] + n3.rotation_euler[0] + n4.rotation_euler[0])
    euler2 = 0.25 * (n1.rotation_euler[1] + n2.rotation_euler[1] + n3.rotation_euler[1] + n4.rotation_euler[1])
    euler3 = 0.25 * (n1.rotation_euler[2] + n2.rotation_euler[2] + n3.rotation_euler[2] + n4.rotation_euler[2])
    ctr_node.rotation_euler = (euler1, euler2, euler3)
    ctr_node.hide_set(state = True)

    # Link the object into element collection
    ecol.objects.link(ctr_node)

    # Create shading material
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()

    # Take the elem material
    elem_mat = bpy.data.materials.new(name=elem.name + '_mat')
    elemOBJ.data.materials.append(elem_mat)

    # Create new shader nodes
    elem_mat.use_nodes = True
    nodes = elem_mat.node_tree.nodes
    TexCoord = nodes.new(type='ShaderNodeTexCoord')
    Mapping = nodes.new(type='ShaderNodeMapping')
    SepXYZ = nodes.new(type='ShaderNodeSeparateXYZ')
    ColorRamp1 = nodes.new(type='ShaderNodeValToRGB')
    ColorRamp2 = nodes.new(type='ShaderNodeValToRGB')
    MixRGB = nodes.new(type='ShaderNodeMixRGB')

    # Create new shader links
    links = elem_mat.node_tree.links
    links.new(TexCoord.outputs[3], Mapping.inputs[0])
    links.new(Mapping.outputs[0], SepXYZ.inputs[0])
    links.new(SepXYZ.outputs[0], ColorRamp1.inputs[0])
    links.new(SepXYZ.outputs[1], ColorRamp2.inputs[0])
    links.new(ColorRamp1.outputs[0], MixRGB.inputs[1])
    links.new(ColorRamp2.outputs[0], MixRGB.inputs[2])
    links.new(MixRGB.outputs[0], nodes['Principled BSDF'].inputs[0])

    # Extract data from netCDF file
    # Should be modified if there is change in future variables name
    ncfile = os.path.join(mbs.file_path, mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    try:
        if mbs.internal_visualize == 'Internal Force':
            var_name_1 = 'elem.shell4.'+str(elem.int_label)+'.F_I'
            var_name_2 = 'elem.shell4.'+str(elem.int_label)+'.F_II'
            var_name_3 = 'elem.shell4.'+str(elem.int_label)+'.F_III'
            var_name_4 = 'elem.shell4.'+str(elem.int_label)+'.F_VI'
        else:
            var_name_1 = 'elem.shell4.' + str(elem.int_label) + '.M_I'
            var_name_2 = 'elem.shell4.' + str(elem.int_label) + '.M_II'
            var_name_3 = 'elem.shell4.' + str(elem.int_label) + '.M_III'
            var_name_4 = 'elem.shell4.' + str(elem.int_label) + '.M_VI'

        if mbs.internal_visualize_dimension == "X":
            dim = 0
        elif mbs.internal_visualize_dimension == "Y":
            dim = 1
        else:
            dim = 2

        value1 = nc.variables[var_name_1][0][dim]
        value2 = nc.variables[var_name_2][0][dim]
        value3 = nc.variables[var_name_3][0][dim]
        value4 = nc.variables[var_name_4][0][dim]

        # Set up variables for shader nodes
        TexCoord.object = ctr_node
        Mapping.inputs[1] = (0.5, 0.5, 0)

        ColorRamp1.color_ramp.color_mode = 'RGB'
        ColorRamp2.color_ramp.color_mode = 'RGB'

        hsv1 = ColorRamp_Color(context, value1)
        rgb1 = colorsys.hsv_to_rgb(hsv1[0], 1, 1)
        rgba1 = (rgb1[0], rgb1[1], rgb1[2], 1)

        hsv2 = ColorRamp_Color(context, value2)
        rgb2 = colorsys.hsv_to_rgb(hsv2[0], 1, 1)
        rgba2 = (rgb2[0], rgb2[1], rgb2[2], 1)

        hsv3 = ColorRamp_Color(context, value3)
        rgb3 = colorsys.hsv_to_rgb(hsv3[0], 1, 1)
        rgba3 = (rgb3[0], rgb3[1], rgb3[2], 1)

        hsv4 = ColorRamp_Color(context, value4)
        rgb4 = colorsys.hsv_to_rgb(hsv4[0], 1, 1)
        rgba4 = (rgb4[0], rgb4[1], rgb4[2], 1)

        ColorRamp1.color_ramp.elements[0].color = rgba1
        ColorRamp1.color_ramp.elements[1].color = rgba3
        ColorRamp2.color_ramp.elements[0].color = rgba2
        ColorRamp2.color_ramp.elements[1].color = rgba4
    except KeyError:
        pass
    return {'FINISHED'}
#-------------------------------------------------------------------
# End of shell4_import_stress function



def membrane4_import_stress(context, elem):
    mbs = context.scene.mbdyn
    ed = mbs.elems
    nd = mbs.nodes
    ecol = bpy.data.collections[elem.name]
    elemOBJ = bpy.data.objects[elem.blender_object]
    try:
        n1 = bpy.data.objects[nd['node_' + str(elem.nodes[0].int_label)].blender_object]
        n2 = bpy.data.objects[nd['node_' + str(elem.nodes[1].int_label)].blender_object]
        n3 = bpy.data.objects[nd['node_' + str(elem.nodes[2].int_label)].blender_object]
        n4 = bpy.data.objects[nd['node_' + str(elem.nodes[3].int_label)].blender_object]
    except KeyError:
        return {'OBJECTS_NOTFOUND'}

    # Create the central node
    ctr_node = bpy.data.objects.new(elem.name + '_ctr', None)
    ctr_node.empty_display_type = "PLAIN_AXES"

    # Assign location and euler angle
    ctr_node.location = 0.25 * (n1.location + n2.location + n3.location + n4.location)
    euler1 = 0.25 * (n1.rotation_euler[0] + n2.rotation_euler[0] + n3.rotation_euler[0] + n4.rotation_euler[0])
    euler2 = 0.25 * (n1.rotation_euler[1] + n2.rotation_euler[1] + n3.rotation_euler[1] + n4.rotation_euler[1])
    euler3 = 0.25 * (n1.rotation_euler[2] + n2.rotation_euler[2] + n3.rotation_euler[2] + n4.rotation_euler[2])
    ctr_node.rotation_euler = (euler1, euler2, euler3)
    ctr_node.hide_set(state=True)

    # Link the object into element collection
    ecol.objects.link(ctr_node)

    # Create shading material
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()

    # Take the elem material
    elem_mat = bpy.data.materials.new(name=elem.name + '_mat')
    elemOBJ.data.materials.append(elem_mat)

    # Create new shader nodes
    elem_mat.use_nodes = True
    nodes = elem_mat.node_tree.nodes
    TexCoord = nodes.new(type='ShaderNodeTexCoord')
    Mapping = nodes.new(type='ShaderNodeMapping')
    SepXYZ = nodes.new(type='ShaderNodeSeparateXYZ')
    ColorRamp1 = nodes.new(type='ShaderNodeValToRGB')
    ColorRamp2 = nodes.new(type='ShaderNodeValToRGB')
    MixRGB = nodes.new(type='ShaderNodeMixRGB')

    # Create new shader links
    links = elem_mat.node_tree.links
    links.new(TexCoord.outputs[3], Mapping.inputs[0])
    links.new(Mapping.outputs[0], SepXYZ.inputs[0])
    links.new(SepXYZ.outputs[0], ColorRamp1.inputs[0])
    links.new(SepXYZ.outputs[1], ColorRamp2.inputs[0])
    links.new(ColorRamp1.outputs[0], MixRGB.inputs[1])
    links.new(ColorRamp2.outputs[0], MixRGB.inputs[2])
    links.new(MixRGB.outputs[0], nodes['Principled BSDF'].inputs[0])

    # Extract data from netCDF file
    # Should be modified if there is change in future variables name
    ncfile = os.path.join(mbs.file_path, mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    try:
        if mbs.internal_visualize == 'Internal Force':
            var_name_1 = 'elem.membrane4.' + str(elem.int_label) + '.F_I'
            var_name_2 = 'elem.membrane4.' + str(elem.int_label) + '.F_II'
            var_name_3 = 'elem.membrane4.' + str(elem.int_label) + '.F_III'
            var_name_4 = 'elem.membrane4.' + str(elem.int_label) + '.F_VI'
        else:
            var_name_1 = 'elem.membrane4.' + str(elem.int_label) + '.M_I'
            var_name_2 = 'elem.membrane4.' + str(elem.int_label) + '.M_II'
            var_name_3 = 'elem.membrane4.' + str(elem.int_label) + '.M_III'
            var_name_4 = 'elem.membrane4.' + str(elem.int_label) + '.M_VI'

        if mbs.internal_visualize_dimension == "X":
            dim = 0
        elif mbs.internal_visualize_dimension == "Y":
            dim = 1
        else:
            dim = 2

        value1 = nc.variables[var_name_1][0][dim]
        value2 = nc.variables[var_name_2][0][dim]
        value3 = nc.variables[var_name_3][0][dim]
        value4 = nc.variables[var_name_4][0][dim]

        # Set up variables for shader nodes
        TexCoord.object = ctr_node
        Mapping.inputs[1] = (0.5, 0.5, 0)

        ColorRamp1.color_ramp.color_mode = 'RGB'
        ColorRamp2.color_ramp.color_mode = 'RGB'

        hsv1 = ColorRamp_Color(context, value1)
        rgb1 = colorsys.hsv_to_rgb(hsv1[0], 1, 1)
        rgba1 = (rgb1[0], rgb1[1], rgb1[2], 1)

        hsv2 = ColorRamp_Color(context, value2)
        rgb2 = colorsys.hsv_to_rgb(hsv2[0], 1, 1)
        rgba2 = (rgb2[0], rgb2[1], rgb2[2], 1)

        hsv3 = ColorRamp_Color(context, value3)
        rgb3 = colorsys.hsv_to_rgb(hsv3[0], 1, 1)
        rgba3 = (rgb3[0], rgb3[1], rgb3[2], 1)

        hsv4 = ColorRamp_Color(context, value4)
        rgb4 = colorsys.hsv_to_rgb(hsv4[0], 1, 1)
        rgba4 = (rgb4[0], rgb4[1], rgb4[2], 1)

        ColorRamp1.color_ramp.elements[0].color = rgba1
        ColorRamp1.color_ramp.elements[1].color = rgba3
        ColorRamp2.color_ramp.elements[0].color = rgba2
        ColorRamp2.color_ramp.elements[1].color = rgba4
    except KeyError:
        pass
    return {'FINISHED'}
#-------------------------------------------------------------------
# End of membrane4_import_stress function


def setup_import_stress(context):
    mbs = context.scene.mbdyn
    elems = mbs.elems
    nd = mbs.nodes
    DEFORMABLE_ELEMENTS = {'beam3', 'beam2', 'shell4', 'membrane4'}
    stress_elems = [elem for elem in elems \
            if (elem.type in DEFORMABLE_ELEMENTS) and (elem.blender_object != 'none')]
    for elem in stress_elems:
        if elem.type == 'beam3':
            if beam3_import_stress(context, elem) == {'OBJECTS NOTFOUND'}:
                message = "Can't find the node object for "+ elem.name
                logging.error(message)
        elif elem.type == 'beam2':
            if beam2_import_stress(context, elem) == {'OBJECTS NOTFOUND'}:
                message = "Can't find the node object for " + elem.name
                logging.error(message)
        ## Fixme: Waiting for future update in MBDyn output data for internal force and internal moment of shell4 and membrane4 elements.
        """
        elif elem.type == 'shell4':
            if shell4_import_stress(context, elem) == {'OBJECTS NOTFOUND'}:
                message = "Can't find the node object for " + elem.name
                logging.error(message)
        elif elem.type == 'membrane4':
            if membrane4_import_stress(context, elem) == {'OBJECTS NOTFOUND'}:
                message = "Can't find the node object for " + elem.name
                logging.error(message)
        """
    return {'FINISHED'}
#-------------------------------------------------------------------
# end of setup_import_stress function



class BLENDYN_OT_import_stress(bpy.types.Operator):
    """ Import current stress into the scene"""
    bl_idname = "blendyn.import_stress"
    bl_label = "Stress import"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ret_val = ''
        if mbs.sim_stress:
            ret_val = setup_import_stress(context)
        return {'FINISHED'}
    def invoke(self, context, event):
        return self.execute(context)

#------------------------------------------------------------------
# end of BLENDYN_OT_import_stress class

def beam3_update_stress(context, elem):
    """Recalculate variables in each shader nodes for beam3 elements"""
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    # update the scene information
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    # find nodes' Blender objects
    try:
        n1 = bpy.data.objects[elem.blender_object + '_RF1']
        n2 = bpy.data.objects[elem.blender_object + '_RF2']
        n3 = bpy.data.objects[elem.blender_object + '_RF3']
    except KeyError:
        return {'OBJECTS_NOTFOUND'}


    Head_pos   = n1.location
    Middle_pos = n2.location
    Tail_pos   = n3.location


    # Take the elem material
    elem_mat = bpy.data.materials[elem.name + '_mat']
    nodes = elem_mat.node_tree.nodes

    ColorRamp = nodes['ColorRamp']
    Mapping = nodes['Mapping']

    # Value for the first Vector Math
    Mapping.inputs[3].default_value = (1 / math.sqrt((Tail_pos[0] - Head_pos[0]) ** 2 + (Tail_pos[1] - Head_pos[1]) ** 2 + (Tail_pos[2] - Head_pos[2]) ** 2), 1, 1)
    Mapping.inputs[3].keyframe_insert(data_path = "default_value")

    # Color for three ColorRamp nodes
    ncfile = os.path.join(os.path.dirname(mbs.file_path), mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    if mbs.internal_visualize == 'Internal Force':
        variable_name_1 = 'elem.beam.' + str(elem.int_label) + '.F_I'
        variable_name_2 = 'elem.beam.' + str(elem.int_label) + '.F_II'
    else:
        variable_name_1 = 'elem.beam.' + str(elem.int_label) + '.M_I'
        variable_name_2 = 'elem.beam.' + str(elem.int_label) + '.M_II'

    ## Need to clarify the direction of internal force/moment
    tdx = context.scene.frame_current * mbs.load_frequency

    if int(tdx) == tdx:
        if mbs.internal_visualize_dimension == "X":
            value1 = nc.variables[variable_name_1][int(tdx)][0]
            value2 = nc.variables[variable_name_2][int(tdx)][0]
        elif mbs.internal_visualize_dimension == "Y":
            value1 = nc.variables[variable_name_1][int(tdx)][1]
            value2 = nc.variables[variable_name_2][int(tdx)][1]
        else:
            value1 = nc.variables[variable_name_1][int(tdx)][2]
            value2 = nc.variables[variable_name_2][int(tdx)][2]
    else:
        frac = np.ceil(tdx) - tdx
        if mbs.internal_visualize_dimension == "X":
            value1 = nc.variables[variable_name_1][int(tdx)][0] * frac + nc.variables[variable_name_1][int(tdx)+1][0] * (1-frac)
            value2 = nc.variables[variable_name_2][int(tdx)][0] * frac + nc.variables[variable_name_2][int(tdx)+1][0] * (1-frac)
        elif mbs.internal_visualize_dimension == "Y":
            value1 = nc.variables[variable_name_1][int(tdx)][1] * frac + nc.variables[variable_name_1][int(tdx) + 1][1] * (1 - frac)
            value2 = nc.variables[variable_name_2][int(tdx)][1] * frac + nc.variables[variable_name_2][int(tdx) + 1][1] * (1 - frac)
        else:
            value1 = nc.variables[variable_name_1][int(tdx)][2] * frac + nc.variables[variable_name_1][int(tdx) + 1][2] * (1 - frac)
            value2 = nc.variables[variable_name_2][int(tdx)][2] * frac + nc.variables[variable_name_2][int(tdx) + 1][2] * (1 - frac)

    hsv1 = ColorRamp_Color(context, value1)
    rgb1 = colorsys.hsv_to_rgb(hsv1[0], 1, 1)
    rgba1 = (rgb1[0], rgb1[1], rgb1[2], 1)

    hsv2 = ColorRamp_Color(context, value2)
    rgb2 = colorsys.hsv_to_rgb(hsv2[0], 1, 1)
    rgba2 = (rgb2[0], rgb2[1], rgb2[2], 1)

    ColorRamp.color_ramp.elements[0].color = rgba1
    ColorRamp.color_ramp.elements[1].color = rgba2
    ColorRamp.color_ramp.elements[0].keyframe_insert(data_path="color")
    ColorRamp.color_ramp.elements[1].keyframe_insert(data_path="color")
    return {'FINISHED'}
#-------------------------------------------------------------------
# End of beam3_update_stress function

def beam2_update_stress(context, elem):
    """Recalculate the color for beam2 element"""
    mbs = context.scene.mbdyn
    elem_mat = bpy.data.materials[elem.blender_object+'_mat']

    nodes = elem_mat.node_tree.nodes
    RGB = nodes['RGB']

    # update the scene information
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()

    # Set up color value
    try:
        ncfile = os.path.join(os.path.dirname(mbs.file_path), mbs.file_basename + '.nc')
    except IOError:
        return {'FILE NOT FOUND'}

    nc = Dataset(ncfile, 'r')
    if mbs.internal_visualize == 'Internal Force':
        variable_name = 'elem.beam.' + str(elem.int_label) + '.F'
    else:
        variable_name = 'elem.beam.' + str(elem.int_label) + '.M'

    ## Need to clarify the direction of internal force/moment
    tdx = context.scene.frame_current * mbs.load_frequency
    if int(tdx) == tdx:
        if mbs.internal_visualize_dimension == "X":
            value = nc.variables[variable_name][int(tdx)][0]
        elif mbs.internal_visualize_dimension == "Y":
            value = nc.variables[variable_name][int(tdx)][1]
        else:
            value = nc.variables[variable_name][int(tdx)][2]
    else:
        frac = np.ceil(tdx) - tdx
        if mbs.internal_visualize_dimension == "X":
            value = nc.variables[variable_name][int(tdx)][0]*frac + nc.variables[variable_name][int(tdx)+1][0]*(1-frac)
        elif mbs.internal_visualize_dimension == "Y":
            value = nc.variables[variable_name][int(tdx)][1]*frac + nc.variables[variable_name][int(tdx)+1][1]*(1-frac)
        else:
            value = nc.variables[variable_name][int(tdx)][2]*frac + nc.variables[variable_name][int(tdx)+1][2]*(1-frac)
    hsv = ColorRamp_Color(context, value)
    rgb = colorsys.hsv_to_rgb(hsv[0], 1, 1)
    rgba = (rgb[0], rgb[1], rgb[2], 1)
    RGB.outputs[0].default_value = rgba
    RGB.outputs[0].keyframe_insert(data_path = "default_value")
    return {'FINISHED'}
#------------------------------------------------------------------
# end of beam2_update_stress function


def shell4_update_stress(context, elem):
    """Recalculate position for central node and color for elements in ColorRamp nodes"""
    mbs = context.scene.mbdyn
    ed = mbs.elems
    nd = mbs.nodes
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ecol = bpy.data.collections[elem.name]
    elemOBJ = bpy.data.objects[elem.blender_object]

    n1 = bpy.data.objects[nd['node_' + str(elem.nodes[0].int_label)].blender_object]
    n2 = bpy.data.objects[nd['node_' + str(elem.nodes[1].int_label)].blender_object]
    n3 = bpy.data.objects[nd['node_' + str(elem.nodes[2].int_label)].blender_object]
    n4 = bpy.data.objects[nd['node_' + str(elem.nodes[3].int_label)].blender_object]

    ctr_node = bpy.data.objects[elem.name + '_ctr']

    # Recompute location and euler angle
    ctr_node.location = 0.25 * (n1.location + n2.location + n3.location + n4.location)
    euler1 = 0.25 * (n1.rotation_euler[0] + n2.rotation_euler[0] + n3.rotation_euler[0] + n4.rotation_euler[0])
    euler2 = 0.25 * (n1.rotation_euler[1] + n2.rotation_euler[1] + n3.rotation_euler[1] + n4.rotation_euler[1])
    euler3 = 0.25 * (n1.rotation_euler[2] + n2.rotation_euler[2] + n3.rotation_euler[2] + n4.rotation_euler[2])
    ctr_node.rotation_euler = (euler1, euler2, euler3)

    elem_mat = bpy.data.materials[elem.name + '_mat']

    nodes = elem_mat.node_tree.nodes
    ColorRamp1 = nodes['ColorRamp']
    ColorRamp2 = nodes['ColorRamp.001']

    # Extract data from netCDF file
    # Should be modified if there is change in future variables name
    ncfile = os.path.join(mbs.file_path, mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    ## Fixme: change the below variables name according to future netCDF internal variable's name
    try:
        if mbs.internal_visualize == 'Internal Force':
            var_name_1 = 'elem.shell4.' + str(elem.int_label) + '.F_I'
            var_name_2 = 'elem.shell4.' + str(elem.int_label) + '.F_II'
            var_name_3 = 'elem.shell4.' + str(elem.int_label) + '.F_III'
            var_name_4 = 'elem.shell4.' + str(elem.int_label) + '.F_VI'
        else:
            var_name_1 = 'elem.shell4.' + str(elem.int_label) + '.M_I'
            var_name_2 = 'elem.shell4.' + str(elem.int_label) + '.M_II'
            var_name_3 = 'elem.shell4.' + str(elem.int_label) + '.M_III'
            var_name_4 = 'elem.shell4.' + str(elem.int_label) + '.M_VI'

        if mbs.internal_visualize_dimension == "X":
            dim = 0
        elif mbs.internal_visualize_dimension == "Y":
            dim = 1
        else:
            dim = 2

        tdx = context.scene.frame_current * mbs.load_frequency

        if int(tdx) == tdx:
            value1 = nc.variables[var_name_1][int(tdx)][dim]
            value2 = nc.variables[var_name_2][int(tdx)][dim]
            value3 = nc.variables[var_name_2][int(tdx)][dim]
            value4 = nc.variables[var_name_2][int(tdx)][dim]
        else:
            frac = np.ceil(tdx) - tdx
            value1 = nc.variables[var_name_1][int(tdx)][0] * frac + \
                     nc.variables[var_name_1][int(tdx) + 1][0] * (1 - frac)
            value2 = nc.variables[var_name_2][int(tdx)][0] * frac + \
                     nc.variables[var_name_2][int(tdx) + 1][0] * (1 - frac)
            value3 = nc.variables[var_name_2][int(tdx)][0] * frac + \
                     nc.variables[var_name_2][int(tdx) + 1][0] * (1 - frac)
            value4 = nc.variables[var_name_2][int(tdx)][0] * frac + \
                     nc.variables[var_name_2][int(tdx) + 1][0] * (1 - frac)

        hsv1 = ColorRamp_Color(context, value1)
        rgb1 = colorsys.hsv_to_rgb(hsv1[0], 1, 1)
        rgba1 = (rgb1[0], rgb1[1], rgb1[2], 1)

        hsv2 = ColorRamp_Color(context, value2)
        rgb2 = colorsys.hsv_to_rgb(hsv2[0], 1, 1)
        rgba2 = (rgb2[0], rgb2[1], rgb2[2], 1)

        hsv3 = ColorRamp_Color(context, value3)
        rgb3 = colorsys.hsv_to_rgb(hsv3[0], 1, 1)
        rgba3 = (rgb3[0], rgb3[1], rgb3[2], 1)

        hsv4 = ColorRamp_Color(context, value4)
        rgb4 = colorsys.hsv_to_rgb(hsv4[0], 1, 1)
        rgba4 = (rgb4[0], rgb4[1], rgb4[2], 1)

        ColorRamp1.color_ramp.elements[0].color = rgba1
        ColorRamp1.color_ramp.elements[1].color = rgba3
        ColorRamp2.color_ramp.elements[0].color = rgba2
        ColorRamp2.color_ramp.elements[1].color = rgba4
    except KeyError:
        pass
    return {'FINISHED'}
#------------------------------------------------------------------
# end of shell4_update_stress function


def membrane4_update_stress(context, elem):
    """Recalculate position for central node and color for elements in ColorRamp nodes"""
    mbs = context.scene.mbdyn
    ed = mbs.elems
    nd = mbs.nodes
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ecol = bpy.data.collections[elem.name]
    elemOBJ = bpy.data.objects[elem.blender_object]

    n1 = bpy.data.objects[nd['node_' + str(elem.nodes[0].int_label)].blender_object]
    n2 = bpy.data.objects[nd['node_' + str(elem.nodes[1].int_label)].blender_object]
    n3 = bpy.data.objects[nd['node_' + str(elem.nodes[2].int_label)].blender_object]
    n4 = bpy.data.objects[nd['node_' + str(elem.nodes[3].int_label)].blender_object]

    ctr_node = bpy.data.objects[elem.name + '_ctr']

    # Recompute location and euler angle
    ctr_node.location = 0.25 * (n1.location + n2.location + n3.location + n4.location)
    euler1 = 0.25 * (n1.rotation_euler[0] + n2.rotation_euler[0] + n3.rotation_euler[0] + n4.rotation_euler[0])
    euler2 = 0.25 * (n1.rotation_euler[1] + n2.rotation_euler[1] + n3.rotation_euler[1] + n4.rotation_euler[1])
    euler3 = 0.25 * (n1.rotation_euler[2] + n2.rotation_euler[2] + n3.rotation_euler[2] + n4.rotation_euler[2])
    ctr_node.rotation_euler = (euler1, euler2, euler3)

    elem_mat = bpy.data.materials[elem.name + '_mat']

    nodes = elem_mat.node_tree.nodes
    ColorRamp1 = nodes['ColorRamp']
    ColorRamp2 = nodes['ColorRamp.001']

    # Extract data from netCDF file
    # Should be modified if there is change in future variables name
    ncfile = os.path.join(mbs.file_path, mbs.file_basename + '.nc')
    nc = Dataset(ncfile, 'r')
    ## Fixme: change the below variables name according to future netCDF internal variable's name
    try:
        if mbs.internal_visualize == 'Internal Force':
            var_name_1 = 'elem.membrane4.' + str(elem.int_label) + '.F_I'
            var_name_2 = 'elem.membrane4.' + str(elem.int_label) + '.F_II'
            var_name_3 = 'elem.membrane4.' + str(elem.int_label) + '.F_III'
            var_name_4 = 'elem.membrane4.' + str(elem.int_label) + '.F_VI'
        else:
            var_name_1 = 'elem.membrane4.' + str(elem.int_label) + '.M_I'
            var_name_2 = 'elem.membrane4.' + str(elem.int_label) + '.M_II'
            var_name_3 = 'elem.membrane4.' + str(elem.int_label) + '.M_III'
            var_name_4 = 'elem.membrane4.' + str(elem.int_label) + '.M_VI'

        if mbs.internal_visualize_dimension == "X":
            dim = 0
        elif mbs.internal_visualize_dimension == "Y":
            dim = 1
        else:
            dim = 2

        tdx = context.scene.frame_current * mbs.load_frequency

        if int(tdx) == tdx:
            value1 = nc.variables[var_name_1][int(tdx)][dim]
            value2 = nc.variables[var_name_2][int(tdx)][dim]
            value3 = nc.variables[var_name_2][int(tdx)][dim]
            value4 = nc.variables[var_name_2][int(tdx)][dim]
        else:
            frac = np.ceil(tdx) - tdx
            value1 = nc.variables[var_name_1][int(tdx)][0] * frac + \
                     nc.variables[var_name_1][int(tdx) + 1][0] * (1 - frac)
            value2 = nc.variables[var_name_2][int(tdx)][0] * frac + \
                     nc.variables[var_name_2][int(tdx) + 1][0] * (1 - frac)
            value3 = nc.variables[var_name_2][int(tdx)][0] * frac + \
                     nc.variables[var_name_2][int(tdx) + 1][0] * (1 - frac)
            value4 = nc.variables[var_name_2][int(tdx)][0] * frac + \
                     nc.variables[var_name_2][int(tdx) + 1][0] * (1 - frac)

        hsv1 = ColorRamp_Color(context, value1)
        rgb1 = colorsys.hsv_to_rgb(hsv1[0], 1, 1)
        rgba1 = (rgb1[0], rgb1[1], rgb1[2], 1)

        hsv2 = ColorRamp_Color(context, value2)
        rgb2 = colorsys.hsv_to_rgb(hsv2[0], 1, 1)
        rgba2 = (rgb2[0], rgb2[1], rgb2[2], 1)

        hsv3 = ColorRamp_Color(context, value3)
        rgb3 = colorsys.hsv_to_rgb(hsv3[0], 1, 1)
        rgba3 = (rgb3[0], rgb3[1], rgb3[2], 1)

        hsv4 = ColorRamp_Color(context, value4)
        rgb4 = colorsys.hsv_to_rgb(hsv4[0], 1, 1)
        rgba4 = (rgb4[0], rgb4[1], rgb4[2], 1)

        ColorRamp1.color_ramp.elements[0].color = rgba1
        ColorRamp1.color_ramp.elements[1].color = rgba3
        ColorRamp2.color_ramp.elements[0].color = rgba2
        ColorRamp2.color_ramp.elements[1].color = rgba4
    except KeyError:
        pass
    return {'FINISHED'}
#------------------------------------------------------------------
# end of membrane4_update_stress function


def update_stress(context):
    mbs = context.scene.mbdyn
    elems = mbs.elems
    DEFORMABLE_ELEMENTS = {'beam3', 'beam2', 'shell4', 'membrane4'}
    stress_elems = [elem for elem in elems \
                    if (elem.type in DEFORMABLE_ELEMENTS) and (elem.blender_object != 'none')]
    for elem in stress_elems:
        if elem.type == 'beam3':
            beam3_update_stress(context, elem)
        elif elem.type == 'beam2':
            beam2_update_stress(context, elem)
        ## Fixme: Waiting for future update in internal force and internal moment output of shell4 and membrane4 elements
        """
        elif elem.type == 'shell4':
            shell4_update_stress(context, elem)
        elif elem.type == 'membrane4':
            membrane4_update_stress(context, elem)
        """
    return {'FINISHED'}
#------------------------------------------------------------------
# end of update_stress function


class BLENDYN_OT_color_boundary_autosetup(bpy.types.Operator):
    """ Reading information inside netCDF file and setup the maximum and minimum boundary for
     internal force and internal moment visualization"""

    bl_idname = "blendyn.color_boundary_autosetup"
    bl_label = "Automatically setup color boundary base on netCDF data information"

    def execute(self, context):
        mbs = context.scene.mbdyn
        ncfile = os.path.join(mbs.file_path, mbs.file_basename+".nc")
        nc = Dataset(ncfile, 'r')
        min = mbs.color_min_boundary
        max = mbs.color_max_boundary

        if mbs.internal_visualize_dimension == 'X':
            dim = 0
        elif mbs.internal_visualize_dimension == 'Y':
            dim = 1
        else:
            dim = 2

        variable_names = []

        # Get the variable names
        for variable_name in nc.variables.keys():
            split = variable_name.split(".")
            if split[-1][0] == "F" and mbs.internal_visualize == "Internal Force":
                variable_names.append(variable_name)
            elif split[-1][0] == "M" and mbs.internal_visualize != "Internal Force":
                variable_names.append(variable_name)

        for variable_name in variable_names:
            for i in range(len(nc.variables[variable_name])):
                val = nc.variables[variable_name][i][dim]
                if val > max:
                    max = val
                elif val < min:
                    min = val

        mbs.color_max_boundary = max
        mbs.color_min_boundary = min
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
#-----------------------------------------------------------------------------
# end of BLENDYN_OT_color_boundary_autosetup class
