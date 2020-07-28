# --------------------------------------------------------------------------
# Blendyn -- file defdisplib.py
# Copyright (C) 2015 -- 2020 Andrea Zanoni -- andrea.zanoni@polimi.it
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

# helper function to parse deformable displacement joints
def parse_deformable_displacement(rw, ed):
    ret_val = True
    try:
        el = ed['deformable_displacement_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_deformable_displacement()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_deformable_displacement()", el) 
        
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
        # Should disappear in future versions
        el.mbclass = 'elem.joint'
        
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True 
    except KeyError:
        el = ed.add()
        el.mbclass = 'elem.joint'
        el.type = 'deformable_displacement'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_deformable_displacement()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_deformable_displacement()", el)  

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

        el.import_function = "blendyn.import_deformable_displacement"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_deformable_displacement(rw, ed) function

# Creates the object representing a deformable displacement joint element
def spawn_deformable_displacement_joint_element(elem, context):
    """ Draws a deformable displacement joint, loading a wireframe
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
        
        # load the wireframe total joint object from the library
        lib_path = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object')
        bpy.ops.wm.append(directory = lib_path, filename = 'deformable displacement')
        
        ddOBJ = bpy.context.selected_objects[0]
        ddOBJ.name = elem.name
        ddOBJ = bpy.data.objects[elem.name]

        RF1 = bpy.context.selected_objects[1]
        RF1.name = elem.name + '_RF1'
        RF1 = bpy.data.objects[elem.name + '_RF1']

        RF2 = bpy.context.selected_objects[2]
        RF2.name = elem.name + '_RF2'
        RF2 = bpy.data.objects[elem.name + '_RF2']

        # place the joint objects in the position defined relative to node 1
        ddOBJ.location = elem.offsets[0].value
        ddOBJ.rotation_mode = 'QUATERNION'
        ddOBJ.rotation_quaternion = Quaternion(elem.rotoffsets[0].value[0:])

        RF1.location = elem.offsets[0].value
        RF1.rotation_mode = 'QUATERNION'
        RF1.rotation_quaternion = Quaternion(elem.rotoffsets[0].value[0:])
        parenting(RF1, n1OBJ)
        RF1.hide_viewport = True

        RF2.location = elem.offsets[1].value
        RF2.rotation_mode = 'QUATERNION'
        RF2.rotation_quaternion = Quaternion(elem.rotoffsets[1].value[0:])
        parenting(RF2, n2OBJ)
        RF2.hide_viewport = True

        # automatic scaling
        s = (.5/sqrt(3.))*(n1OBJ.scale.magnitude + n2OBJ.scale.magnitude)
        ddOBJ.scale = Vector((s, s, s))
        # ddOBJ.data.transforms(ddOBJ.matrix_world)
        # ddOBJ.matrix_world = Matrix()

        # parenting of wireframe objects
        parenting(ddOBJ, n1OBJ)

        # set mbdyn props of object
        elem.blender_object = ddOBJ.name
        ddOBJ.mbdyn.dkey = elem.name
        ddOBJ.mbdyn.type = 'element'

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
# end of spawn_deformable_displacament_joint_element(elem, context) function

## Imports a Deformable Displacement Joint in the scene
class BLENDYN_OT_import_deformable_displacement(bpy.types.Operator):
    bl_idname = "blendyn.import_deformable_displacement"
    bl_label = "MBDyn deformable displacement joint element importer"
    int_label: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
    
        try:
            elem = ed['deformable_displacement_' + str(self.int_label)]
            retval =  spawn_deformable_displacement_joint_element(elem, context)
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
# end of BLENDYN_OT_import_deformable_displacement class
