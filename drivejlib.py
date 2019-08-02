# --------------------------------------------------------------------------
# Blendyn -- file drivejlib.py
# Copyright (C) 2015 -- 2019 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of Blendyn, add-on script for Blender.
#
#    Blendyn is free software: you can redrvdispribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Blendyn  is drvdispributed in the hope that it will be useful,
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

from mathutils import *
from math import *

from .utilslib import parse_rotmat

# helper function to parse drive_displacement joints
def parse_drive_displacement(rw, ed):
    ret_val = True
    try:
        el = ed['drive_displacement_' + str(rw[1])]
        
        eldbmsg('PARSE_ELEM', "BLENDYN::parse_drive_displacement()", el)
        eldbmsg('FOUND_DICT', "BLENDYN::parse_drive_displacement()", el)  
        
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])
        
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        
        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'drive_displacement'
        el.int_label = int(rw[1])
        
        eldbmsg('PARSE_ELEM', "BLENDYN::parse_drive_displacement()", el)
        eldbmsg('NOTFOUND_DICT', "BLENDYN::parse_drive_displacement()", el)   

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        el.import_function = "mbdyn.BLENDYN_OT_import_drive_displacement"
        el.info_draw = "drive_displacement_info_draw"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------- 
# end of parse_drive_displacement(rw, ed) function

# function that displays drive_displacement info in panel -- [ optional ]
def drive_displacement_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    try:
        node = nd['node_' + str(elem.nodes[0].int_label)]
        # Display node 1 info
        col.prop(node, "int_label", text = "Node 1 ID ")
        col.prop(node, "string_label", text = "Node 1 label ")
        col.prop(node, "blender_object", text = "Node 1 Object: ")
        col.enabled = False

        # Display offset of node 1 info
        row = layout.row()
        row.label(text = "offset 1 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[0], "value", text = "", slider = False)

        node = nd['node_' + str(elem.nodes[1].int_label)]

        # Display node 2 info
        col.prop(node, "int_label", text = "Node 2 ID ")
        col.prop(node, "string_label", text = "Node 2 label ")
        col.prop(node, "blender_object", text = "Node 2 Object: ")
        col.enabled = False

        # Display offset of node 2 info
        row = layout.row()
        row.label(text = "offset 2 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[1], "value", text = "", slider = False)
        col.enabled = False

        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of drive_displacement_info_draw(elem, layout) function

# Creates the object representing a drive_displacement joint element
def spawn_drive_displacement_element(elem, context):
    """ Draws a drive_displacement joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        return {'NODE2_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # creation of line representing the drvdisp
    drvdispobj_id = 'drvdisp_' + str(elem.int_label)
    drvdispcv_id = drvdispobj_id + '_cvdata'

    # check if the object is already present. If it is, remove it.
    if drvdispobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[drvdispobj_id])

    # check if the curve is already present. If it is, remove it.
    if drvdispcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[drvdispcv_id])

    # create a new curve
    cvdata = bpy.data.curves.new(drvdispcv_id, type = 'CURVE')
    cvdata.dimensions = '3D'
    polydata = cvdata.splines.new('POLY')
    polydata.points.add(1)

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # assign coordinates of knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    p2 = n2OBJ.location + R2*Vector(( f2[0], f2[1], f2[2] ))

    polydata.points[0].co = p1.to_4d()
    polydata.points[1].co = p2.to_4d()


    drvdispOBJ = bpy.data.objects.new(drvdispobj_id, cvdata)
    drvdispOBJ.mbdyn.type = 'element'
    drvdispOBJ.mbdyn.dkey = elem.name
    bpy.context.scene.objects.link(drvdispOBJ)
    elem.blender_object = drvdispOBJ.name

    # Finishing up
    cvdata.fill_mode = 'FULL'
    length = (n2OBJ.location - n1OBJ.location).length
    radius = 0.02 * length
    cvdata.bevel_depth = radius
    cvdata.bevel_resolution = 10

    bpy.ops.mesh.primitive_uv_sphere_add(size = radius * 2, location = p1)
    bpy.context.active_object.name = drvdispOBJ.name + '_child1'
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.data.objects[drvdispOBJ.name + '_child1'].select = True
    drvdispOBJ.select = True
    bpy.context.scene.objects.active = drvdispOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    bpy.ops.mesh.primitive_uv_sphere_add(size = radius * 2, location = p2)
    bpy.context.active_object.name = drvdispOBJ.name + '_child2'
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.data.objects[drvdispOBJ.name + '_child2'].select = True
    drvdispOBJ.select = True
    bpy.context.scene.objects.active = drvdispOBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    #hooking of the line ends to the Blender objects
    
    # P1 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n1OBJ.select = True
    drvdispOBJ.select = True
    bpy.context.scene.objects.active = drvdispOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    drvdispOBJ.data.splines[0].points[0].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # P2 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n2OBJ.select = True
    drvdispOBJ.select = True
    bpy.context.scene.objects.active = drvdispOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    drvdispOBJ.data.splines[0].points[1].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    bpy.ops.object.select_all(action = 'DESELECT')

    # P1 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n1OBJ.select = True
    bpy.data.objects[drvdispOBJ.name + '_child1'].select = True
    bpy.context.scene.objects.active = bpy.data.objects[drvdispOBJ.name + '_child1']
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # P2 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n2OBJ.select = True
    bpy.data.objects[drvdispOBJ.name + '_child2'].select = True
    bpy.context.scene.objects.active = bpy.data.objects[drvdispOBJ.name + '_child2']
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    drvdispOBJ.draw_type = 'WIRE'
    bpy.data.objects[drvdispOBJ.name + '_child1'].draw_type = 'WIRE'
    bpy.data.objects[drvdispOBJ.name + '_child2'].draw_type = 'WIRE'

    bpy.ops.object.select_all(action = 'DESELECT')
    n1OBJ.select = True
    drvdispOBJ.select = True
    bpy.context.scene.objects.active = n1OBJ
    bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

    elem.is_imported = True
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_drive_displacement_element(elem, context) function

# Imports a drive_displacement Joint in the scene
class BLENDYN_OT_import_drive_displacement(bpy.types.Operator):
    bl_idname = "mbdyn.BLENDYN_OT_import_drive_displacement"
    bl_label = "MBDyn drive_displacement joint element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['drive_displacement_' + str(self.int_label)]
            retval = spawn_drive_displacement_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == 'NODE2_NOTFOUND':
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval {'FINISHED'}:
                eldbmsg('IMPORT_SUCCESS', type(self).__name__ + '::execute()', elem)
                return retval
            else:
                return retval
        except KeyError:
            eldbmsg('DICT_ERROR', type(self).__name__ + '::execute()', elem)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_import_drive_displacement class.
