# --------------------------------------------------------------------------
# Blendyn -- file revjlib.py
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

from mathutils import *
from math import *

from .utilslib import *

# helper function to parse revolute hinge joints
def parse_revolute_hinge(rw, ed):
    ret_val = True
    try:
        el = ed['revolute_hinge_' + str(rw[1])]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_revolute_hinge()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_revolute_hinge()", el)

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        # FIXME: this is here to enhance backwards compatibility.
        # should disappear in future versions
        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'revolute_hinge'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_revolute_hinge()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_revolute_hinge()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[15])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        el.rotoffsets.add()
        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        el.import_function = "blendyn.import_revolute_hinge"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# --------------------------------------------------------------------------
# end of parse_revolue_hinge(rw, ed) function

# helper function to parse revolute pin joints
def parse_revolute_pin(rw, ed):
    ret_val = True
    try:
        el = ed['revolute_pin_' + str(rw[1])]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_revolute_pin()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_revolute_pin()", el)

        el.nodes[0].int_label = int(rw[2])
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        # FIXME: this is here to enhance backwards compatibility.
        # should disappear in future versions
        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'revolute_pin'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_revolute_pin()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_revolute_pin()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.import_function = "blendyn.import_revolute_pin"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# --------------------------------------------------------------------------
# end of parse_revolute_pin(rw, ed) function

# helper function to parse revolute rot joints
def parse_revolute_rot(rw, ed):
    ret_val = True
    try:
        el = ed['revolute_rot_' + str(rw[1])]

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_revolute_rot()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_revolute_rot()", el)

        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[15])

        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        # FIXME: this is here to enhance backwards compatibility.
        # should disappear in future versions
        el.mbclass = 'elem.joint'

        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'revolute_rot'
        el.int_label = int(rw[1])

        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_revolute_rot()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_revolute_rot()", el)

        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.nodes.add()
        el.nodes[1].int_label = int(rw[15])

        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))

        el.rotoffsets.add()
        R1 = Matrix().to_3x3()
        parse_rotmat(rw, 6, R1)
        el.rotoffsets[0].value = R1.to_quaternion();

        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[16]), float(rw[17]), float(rw[18]) ))

        el.rotoffsets.add()
        R2 = Matrix().to_3x3()
        parse_rotmat(rw, 19, R2)
        el.rotoffsets[1].value = R2.to_quaternion();

        el.import_function = "blendyn.import_revolute_rotation"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass
    return ret_val
# --------------------------------------------------------------------------
# end of parse_revolue_rot(rw, ed) function

# Creates the object representing a revolute hinge joint element
def spawn_revolute_hinge_element(elem, context):
    """ Draws a revolute hinge joint element, loading a wireframe
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

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe revolute joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'revolute hinge')
        # the append operator leaves just the imported object selected
        revjOBJ = bpy.context.selected_objects[0]
        revjOBJ.name = elem.name

        # automatic scaling
        s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + \
        n2OBJ.scale.magnitude)
        revjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = Vector(( elem.offsets[0].value[0:] ))
        f2 = Vector(( elem.offsets[1].value[0:] ))
        q1 = Quaternion(( elem.rotoffsets[0].value[0:] ))
        q2 = Quaternion(( elem.rotoffsets[1].value[0:] ))

        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        R2 = n2OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1@f1
        p2 = n2OBJ.location + R2@f2

        # place the joint object in the position defined relative to node 1
        revjOBJ.location = p1
        revjOBJ.rotation_mode = 'QUATERNION'
        revjOBJ.rotation_quaternion = q1@n1OBJ.rotation_quaternion 

        # create an object representing the second RF used by the joint
        # for model debugging
        bpy.ops.object.empty_add(type = 'ARROWS', location = p2)
        RF2 = bpy.context.selected_objects[0]
        RF2.rotation_mode = 'QUATERNION'
        RF2.rotation_quaternion = q2@n2OBJ.rotation_quaternion 
        RF2.scale = .33*revjOBJ.scale
        RF2.name = revjOBJ.name + '_RF2'
        parenting(RF2, revjOBJ)
        RF2.hide_set(state = True)

        # set parenting of wireframe obj
        parenting(revjOBJ, n1OBJ)

        revjOBJ.mbdyn.dkey = elem.name
        revjOBJ.mbdyn.type = 'element'
        elem.blender_object = revjOBJ.name

        # link objects to element collection
        elcol.objects.link(n1OBJ)
        elcol.objects.link(n2OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_revolute_hinge_element(elem, context) function

# Imports a Revolute Hinge Joint in the scene
class BLENDYN_OT_import_revolute_hinge(bpy.types.Operator):
    """ Imports a revolute hinge joint element into the Blender scene """
    bl_idname = "blendyn.import_revolute_hinge"
    bl_label = "MBDyn revolute hinge joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['revolute_hinge_' + str(self.int_label)]
            retval = spawn_revolute_hinge_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
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
# end of BLENDYN_OT_import_revolute_hinge class

# Creates the object representing a revolute joint element
def spawn_revolute_pin_element(elem, context):
    """ Draws a revolute pin joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}

    # nodes' objects
    n1OBJ = bpy.data.objects[n1]

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe revolute joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'revolute pin')

        # the append operator leaves just the imported object selected
        revjOBJ = bpy.context.selected_objects[0]
        revjOBJ.name = elem.name

        # automatic scaling
        s = n1OBJ.scale.magnitude*(1./sqrt(3.))
        revjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = Vector(( elem.offsets[0].value[0:] ))
        q1 = Quaternion(( elem.rotoffsets[0].value[0:] ))

        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1@f1

        # the position defined relative to node 1
        revjOBJ.location = p1
        revjOBJ.rotation_mode = 'QUATERNION'
        revjOBJ.rotation_quaternion = q1@n1OBJ.rotation_quaternion 

        # set parenting of wireframe obj
        parenting(revjOBJ, n1OBJ)

        revjOBJ.mbdyn.dkey = elem.name
        revjOBJ.mbdyn.dkey = 'element'
        elem.blender_object = revjOBJ.name

        # link objects to element collection
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_revolute_pin_element(elem, context) function

# Imports a Revolute Pin Joint in the scene
class BLENDYN_OT_import_revolute_pin(bpy.types.Operator):
    bl_idname = "blendyn.import_revolute_pin"
    bl_label = "MBDyn revolute pin joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['revolute_pin_' + str(self.int_label)]
            retval = spawn_revolute_pin_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsf(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
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
# end of BLENDYN_OT_import_revolute_pin class

# Creates the object representing a revolute rot joint element
def spawn_revolute_rot_element(elem, context):
    """ Draws a revolute rot joint element, loading a wireframe
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

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe revolute joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'revolute rotation')

        # the append operator leaves just the imported object selected
        revjOBJ = bpy.context.selected_objects[0]
        revjOBJ.name = elem.name

        # automatic scaling
        s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + \
        n2OBJ.scale.magnitude)
        revjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = Vector(( elem.offsets[0].value[0:] ))
        f2 = Vector(( elem.offsets[1].value[0:] ))
        q1 = Quaternion(( elem.rotoffsets[0].value[0:] ))
        q2 = Quaternion(( elem.rotoffsets[1].value[0:] ))

        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        R2 = n2OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1@f1
        p2 = n2OBJ.location + R2@f2

        # place the joint object in the position defined relative to node 1
        revjOBJ.location = p1
        revjOBJ.rotation_mode = 'QUATERNION'
        revjOBJ.rotation_quaternion = q1@n1OBJ.rotation_quaternion 

        # create an object representing the second RF used by the joint
        # for model debugging
        bpy.ops.object.empty_add(type = 'ARROWS', location = p2)
        RF2 = bpy.context.selected_objects[0]
        RF2.rotation_mode = 'QUATERNION'
        RF2.rotation_quaternion = q2@n2OBJ.rotation_quaternion 
        RF2.scale = .33*revjOBJ.scale
        RF2.name = revjOBJ.name + '_RF2'
        parenting(RF2, revjOBJ)
        RF2.hide_viewport = True

        # set parenting of wireframe obj
        parenting(revjOBJ, n1OBJ)

        elem.blender_object = revjOBJ.name

        # link objects to element collection
        elcol.objects.link(n1OBJ)
        elcol.objects.link(n2OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_revolute_rot_element(elem, context) function

# Imports a Revolute Rotation Joint in the scene
class BLENDYN_OT_import_revolute_rotation(bpy.types.Operator):
    bl_idname = "blendyn.import_revolute_rotation"
    bl_label = "MBDyn revolute joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['revolute_rot_' + str(self.int_label)]
            retval = spawn_revolute_rot_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE2_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'COLLECTION_ERROR'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
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
# end of BLENDYN_OT_import_revolute_rotation class
