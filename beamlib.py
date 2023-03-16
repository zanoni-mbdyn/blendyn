# --------------------------------------------------------------------------
# Blendyn -- file beamlib.py
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
import numpy as np

from mathutils import *
from math import *

from bpy.app.handlers import persistent
from .utilslib import *

import logging

# helper function to parse beam2
def parse_beam2(rw, ed):
    ret_val = True
    try:
        el = ed['beam2_' + rw[1]]

        eldbmsg({'PARSE_ELEM'}, 'BLENDYN::parse_beam2()', el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_beam2()", el)

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.beam'

        el.is_imported = True

        pass

    except KeyError:

        el = ed.add()
        el.mbclass = 'elem.beam'
        el.type = 'beam2'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beam2()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_beam2()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        el.import_function = "blendyn.import_beam2"
        el.info_draw = "beam2_info_draw"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_beam2(rw, ed) function

def parse_beam3(rw, ed):

    ret_val = True
    try:
        el = ed['beam3_' + rw[1]]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beam3()", el)
        eldbmsg({'FOUND_IN_DICT'}, "BLENDYN::parse_beam3()", el)

        el.is_imported = False

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])
        el.nodes[2].int_label = int(rw[10])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets[1].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))

        # FIXME: this is here to enhance backwards compatibility.
        # Should disappear in future versions
        el.mbclass = 'elem.beam'

        el.is_imported = True

        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.beam'
        el.type = 'beam3'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_beam3()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_beam3()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        
        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))

        el.nodes.add()
        el.nodes[2].int_label = int(rw[10])

        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))

        el.import_function = "blendyn.import_beam3"
        el.info_draw = "beam3_info_draw"
        el.update = "update_beam3"
        el.name = el.type + "_" + str(el.int_label)

        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# -----------------------------------------------------------
# end of parse_beam3(rw, ed) function

# function that displays beam2 info in panel -- [ optional ]
def beam2_info_draw(elem, layout):
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
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of beam2_info_draw(elem, layout) function

# function that displays beam3 info in panel -- [ optional ]
def beam3_info_draw(elem, layout):
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
        layout.separator()

        node = nd['node_' + str(elem.nodes[2].int_label)]
        # Display node 3 info
        col.prop(node, "int_label", text = "Node 3 ID ")
        col.prop(node, "string_label", text = "Node 3 label ")
        col.prop(node, "blender_object", text = "Node 3 Object: ")
        col.enabled = False

        # Display offset of node 3 info
        row = layout.row()
        row.label(text = "offset 3 w.r.t. Node " + node.string_label + " R.F.")
        col = layout.column(align = True)
        col.prop(elem.offsets[2], "value", text = "", slider = False)
        layout.separator()

        return {'FINISHED'}
    except KeyError:
        return {'NODE_NOTFOUND'}

# -----------------------------------------------------------
# end of beam3_info_draw(elem, layout) function

# Creates the object representing a beam2 element
def spawn_beam2_element(elem, context):
    """ Draws a two node beam element as a line connecting two points
        belonging to two objects """

    nd = context.scene.mbdyn.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    # try to find Blender objects associated with the nodes that
    # the element connects
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

    # names for curve and object
    beamobj_id = 'beam2_' + str(elem.int_label)
    beamcv_id = beamobj_id + '_cvdata'

    try:
        # put it all in the 'beams' collection
        set_active_collection('beams')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['beams'].children.link(elcol)
        set_active_collection(elcol.name)
    except KeyError:
        return {'COLLECTION_ERROR'}

    # check if the object is already present. If it is, remove it.
    if beamobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[beamobj_id])

    # check if the curve is already present. If it is, remove it.
    if beamcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[beamcv_id])

    # create a new curve
    cvdata = bpy.data.curves.new(beamcv_id, type = 'CURVE')
    cvdata.dimensions = '3D'
    polydata = cvdata.splines.new('POLY')
    polydata.points.add(1)

    # get offsets in local frame
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # assign coordinates of curve knots in global frame
    R1 = n1OBJ.rotation_quaternion.to_matrix()
    R2 = n2OBJ.rotation_quaternion.to_matrix()
    p1 = n1OBJ.location + R1@Vector(( f1[0], f1[1], f1[2] ))
    p2 = n2OBJ.location + R2@Vector(( f2[0], f2[1], f2[2] ))

    polydata.points[0].co = p1.to_4d()
    polydata.points[1].co = p2.to_4d()

    # create the object
    beamOBJ = bpy.data.objects.new(beamobj_id, cvdata)
    beamOBJ.mbdyn.type = 'element'
    beamOBJ.mbdyn.dkey = elem.name
    elcol.objects.link(beamOBJ)
    elem.blender_object = beamOBJ.name

    beamOBJ.lock_scale[0] = True
    beamOBJ.lock_scale[1] = True
    beamOBJ.lock_scale[2] = True

    beamOBJ.select_set(state = True)

    # Hook control points and add internal RFs objects
    objs = [n1OBJ, n2OBJ]
    names = ['P1', 'P2']
    RFpos = [p1, p2]
    M = Matrix()
    for i, (p, obj, name) in enumerate(zip(beamOBJ.data.splines[0].points, objs, names)):
        hook = beamOBJ.modifiers.new(name, type = 'HOOK')
        hook.object = obj
        hook.vertex_indices_set([i])
        hook.matrix_inverse = M.Translation(-obj.location)
        nobj = bpy.data.objects.new(beamOBJ.name + 'RF' + str(i + 1), None)
        nobj.empty_display_type = 'ARROWS'
        nobj.location = RFpos[i].to_3d()
        dim = obj.dimensions.magnitude/sqrt(3) if obj.data else obj.empty_display_size
        nobj.empty_display_size = .33*dim
        parenting(nobj, obj)
        elcol.objects.link(nobj)
        nobj.hide_set(state = True)

    # link objects to the element collection
    elcol.objects.link(n1OBJ)
    elcol.objects.link(n2OBJ)
    set_active_collection('Master Collection')

    elem.is_imported = True
    return {'FINISHED'}

# -----------------------------------------------------------
# end of spawn_beam2_element(elem, context) function

## Creates the object representing a beam3 element
def spawn_beam3_element(elem, context):
    """ Draws a beam3 element as a nurbs order 3 curve connecting three
        points belonging to three objects (and their associated MBDyn nodes """

    nd = context.scene.mbdyn.nodes
    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return{'OBJECT_EXISTS'}

    # try to find Blender objects associated with the nodes that
    # the element connects

    # we store in elem.rotoffsets the initial ortientation of the nodes,
    # to then set the tilt of the bevel section relative to it
    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
        elem.rotoffsets.add()
        elem.rotoffsets[0].value = bpy.data.objects[n1].matrix_world.to_quaternion()
    except KeyError:
        return {'NODE1_NOTFOUND'}

    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
        elem.rotoffsets.add()
        elem.rotoffsets[1].value = bpy.data.objects[n2].matrix_world.to_quaternion()
    except KeyError:
        return {'NODE2_NOTFOUND'}

    try:
        n3 = nd['node_' + str(elem.nodes[2].int_label)].blender_object
        elem.rotoffsets.add()
        elem.rotoffsets[2].value = bpy.data.objects[n3].matrix_world.to_quaternion()
    except KeyError:
        return {'NODE3_NOTFOUND'}

    # Create the NURBS order 3 curve
    beamobj_id = 'beam3_' + str(elem.int_label)
    beamcv_id = beamobj_id + '_cvdata'

    try:
        # put it all in the 'beams' collection
        set_active_collection('beams')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['beams'].children.link(elcol)
        set_active_collection(elcol.name)
    except KeyError:
        return {'COLLECTION_ERROR'}

    # Check if the object is already present. If it is, remove it.
    if beamobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[beamobj_id])

    # check if the curve is already present. If it is, remove it.
    if beamcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[beamcv_id])

    cvdata = bpy.data.curves.new(beamcv_id, type = 'CURVE')
    cvdata.dimensions = '3D'
    polydata = cvdata.splines.new('NURBS')
    polydata.points.add(3)
    polydata.order_u = 3
    polydata.use_endpoint_u = True

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    f3 = elem.offsets[2].value

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]
    n3OBJ = bpy.data.objects[n3]

    # refline points in global frame
    P1 = n1OBJ.matrix_world@Vector(( f1[0], f1[1], f1[2], 1.0 ))
    P2 = n2OBJ.matrix_world@Vector(( f2[0], f2[1], f2[2], 1.0 ))
    P3 = n3OBJ.matrix_world@Vector(( f3[0], f3[1], f3[2], 1.0 ))

    # define the two intermediate control points # FIXME: find a more efficient way!!
    t1 = -3*P1 + 4*P2 - P3
    t1.normalize()

    t2 = -P1 + P3
    t2.normalize()

    T = np.zeros((3,2))
    T[:,0] = t1.to_3d()
    T[:,1] = -t2.to_3d()

    d = np.linalg.pinv(T).dot(np.array((P2 - P1).to_3d()))

    M1 = Vector(( P2 - Vector((max(d)*t2)) ))
    M2 = Vector(( P2 + Vector((max(d)*t2)) ))

    polydata.points[0].co = P1
    polydata.points[1].co = M1
    polydata.points[2].co = M2
    polydata.points[3].co = P3
    
    # create the object
    beamOBJ = bpy.data.objects.new(beamobj_id, cvdata)
    beamOBJ.mbdyn.type = 'element'
    beamOBJ.mbdyn.dkey = elem.name
    ude = bpy.context.scene.mbdyn.elems_to_update.add()
    ude.dkey = elem.name
    ude.name = elem.name

    elcol.objects.link(beamOBJ)
    elem.blender_object = beamOBJ.name

    beamOBJ.lock_scale[0] = True
    beamOBJ.lock_scale[1] = True
    beamOBJ.lock_scale[2] = True

    beamOBJ.select_set(state = True)

    
    # add objects representing the position of the points on the beam axis, w.r.t. nodes
    nOBJs = [n1OBJ, n2OBJ, n3OBJ]
    RFpos = [P1, P2, P3]
    for i in range(3):
        obj = bpy.data.objects.new(beamOBJ.name + '_RF' + str(i + 1), None)
        obj.location = RFpos[i].to_3d()
        obj.empty_display_type = 'ARROWS'
        dim = nOBJs[i].dimensions.magnitude/sqrt(3) if nOBJs[i].data else nOBJs[i].empty_display_size
        obj.empty_display_size = .33*dim
        parenting(obj, nOBJs[i])
        elcol.objects.link(obj)
        obj.hide_set(state = True)

    # Hook control points
    obj2 = bpy.data.objects.new(beamOBJ.name + '_M1', None)
    obj2.location = M1[0:3]
    obj2.empty_display_type = 'PLAIN_AXES'
    dim = n2OBJ.dimensions.magnitude/sqrt(3) if n2OBJ.data else n2OBJ.empty_display_size
    obj2.empty_display_size = dim

    obj3 = bpy.data.objects.new(beamOBJ.name + '_M2', None)
    obj3.location = M2[0:3]
    obj3.empty_display_type = 'PLAIN_AXES'
    obj3.empty_display_size = dim

    objs = [n1OBJ, obj2, obj3, n3OBJ]
    names = ['P1', 'M1', 'M2', 'P3']
    M = Matrix()
    for i, (p, obj, name) in enumerate(zip(beamOBJ.data.splines[0].points, objs, names)):
        hook = beamOBJ.modifiers.new(name, type = 'HOOK')
        hook.object = obj
        hook.vertex_indices_set([i])
        hook.matrix_inverse = M.Translation(-obj.location)

    elem.is_imported = True

    # bpy.ops.object.select_all(action = 'DESELECT')

    # put them all in the element collection and hide the internal references
    elcol.objects.link(n1OBJ)
    elcol.objects.link(n2OBJ)
    elcol.objects.link(n3OBJ)
    elcol.objects.link(obj2)
    elcol.objects.link(obj3)
    obj2.hide_set(state = True)
    obj3.hide_set(state = True)
    set_active_collection('Master Collection')
    return {'FINISHED'}
# -----------------------------------------------------------
# end of spawn_beam3_element(elem, context) function

def update_beam3(elem, insert_keyframe = False):
    """ Updates the configuration of a 3-node beam by re-computing
        the positions of the two intermediate control points """

    cvdata = bpy.data.objects[elem.blender_object].data
    nd = bpy.context.scene.mbdyn.nodes

    # find nodes' Blender objects
    try:
        cp2 = bpy.data.objects[elem.blender_object + '_M1']
        cp3 = bpy.data.objects[elem.blender_object + '_M2']
        n1 = bpy.data.objects[nd['node_' + str(elem.nodes[0].int_label)].blender_object]
        n2 = bpy.data.objects[nd['node_' + str(elem.nodes[1].int_label)].blender_object]
        n3 = bpy.data.objects[nd['node_' + str(elem.nodes[2].int_label)].blender_object]
    except KeyError:
        return {'OBJECTS_NOTFOUND'}

    # offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value
    f3 = elem.offsets[2].value

    # points on beam
    P1 = n1.matrix_world@Vector(( f1[0], f1[1], f1[2], 1.0 ))
    P2 = n2.matrix_world@Vector(( f2[0], f2[1], f2[2], 1.0 ))
    P3 = n3.matrix_world@Vector(( f3[0], f3[1], f3[2], 1.0 ))

    # redefine the two intermediate control points
    t1 = (-3*P1 + 4*P2 - P3)
    t1.normalize()

    t2 = -P1 + P3
    t2.normalize()

    T = np.zeros((3,2))
    T[:,0] = t1.to_3d()
    T[:,1] = -t2.to_3d()

    d = np.linalg.pinv(T).dot(np.array((P2 - P1).to_3d()))

    cp2.location = Vector(( P2 - Vector((max(d)*t2)) )).to_3d()
    cp3.location = Vector(( P2 + Vector((max(d)*t2)) )).to_3d()

    if insert_keyframe:
        try:
            cp2.select_set(state = True)
            cp2.keyframe_insert(data_path = "location")

            cp3.select_set(state = True)
            cp3.keyframe_insert(data_path = "location")

        except RuntimeError as err:
            if 'context is incorrect' in str(err):
                pass
            else:
                message = str(err)
                self.report({'WARNING'}, message)
                logging.warning(message)
        except TypeError:
            pass

    return {'FINISHED'}
# -----------------------------------------------------------
# end of update_beam3() function


## Imports a Beam 2 element in the scene as a line joining two nodes
class BLENDYN_OT_import_beam2(bpy.types.Operator):
    """ Imports a beam2 element into the Blender scene """
    bl_idname = "blendyn.import_beam2"
    bl_label = "Imports a beam2 element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        try:
            elem = ed['beam2_' + str(self.int_label)]
            retval = spawn_beam2_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                logging.error(message)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'FINISHED'}:
                eldbmsg({'IMPORT_SUCCESS'}, type(self).__name__ + '::execute()', elem)
            else:
                return retval

        except KeyError:
            eldbmsg({'DICT_ERROR'}, type(self).__name__ + '::execute()', elem)
            return {'CANCELLED'}

        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_import_beam2 class

## Imports a Beam 3 element in the scene as a line joining two nodes
class BLENDYN_OT_import_beam3(bpy.types.Operator):
    bl_idname = "blendyn.import_beam3"
    bl_label = "Imports a beam3 element"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        try:
            elem = ed['beam3_' + str(self.int_label)]
            retval = spawn_beam3_element(elem, context)
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
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
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
# end of BLENDYN_OT_import_beam3 class

class BLENDYN_OT_update_beam3(bpy.types.Operator):
    """ Calls the update_beam3() function to update the current configuration
        of the curve representing the beam3 element """
    bl_idname = "blendyn.update_beam3"
    bl_label = "Updates beam3 curve configuration"

    def execute(self, context):
        ed = context.scene.mbdyn.elems
        ret_val = update_beam3(ed[context.object.name])
        if ret_val == {'OBJECTS_NOTFOUND'}:
            message = type(self).__name__ + "::execute(): " \
                    + "Unable to find Blender objects to update"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
        else:
            return ret_val
        pass
