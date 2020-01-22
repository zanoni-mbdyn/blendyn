# --------------------------------------------------------------------------
# Blendyn -- file clamipjlib.py
# Copyright (C) 2015 -- 2019 Andrea Zanoni -- andrea.zanoni@polimi.it
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

## Parses clamp joint entry in the .log file (see section E.2.8 of input manual for details)
def parse_clamp(rw, ed):
    ret_val = True
    try:
        el = ed['clamp_' + str(rw[1])]
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_clamp()", el)
        eldbmsg({'FOUND_DICT'}, "BLENDYN::parse_clamp()", el) 
        
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
        el.type = 'clamp'
        el.int_label = int(rw[1])
        
        eldbmsg({'PARSE_ELEM'}, "BLENDYN::parse_clamp()", el)
        eldbmsg({'NOTFOUND_DICT'}, "BLENDYN::parse_clamp()", el)  

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

        el.import_function = "blendyn.import_clamp"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_clamp(rw, ed) function

## Spawns a Blender object representing a clamp joint
def spawn_clamp_element(elem, context):
    """ Draws a clamp joint element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        return {'NODE1_NOTFOUND'}

    # node object
    n1OBJ = bpy.data.objects[n1]

    try:

        set_active_collection('joints')
        elcol = bpy.data.collections.new(name = elem.name)
        bpy.data.collections['joints'].children.link(elcol)
        set_active_collection(elcol.name)

        # load the wireframe joint object from the library
        bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'library', 'joints.blend', 'Object'), filename = 'clamp')
        # the append operator leaves just the imported object selected
        clampjOBJ = bpy.context.selected_objects[0]
        clampjOBJ.name = elem.name

        # automatic scaling
        s = n1OBJ.scale.magnitude*(1./sqrt(3.))
        clampjOBJ.scale = Vector(( s, s, s ))

        # joint offsets with respect to nodes
        f1 = elem.offsets[0].value
        q1 = elem.rotoffsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = Vector(( f1[0], f1[1], f1[2] ))
    
        # place the joint object in the position defined relative to node 1
        clampjOBJ.location = p1
        clampjOBJ.rotation_mode = 'QUATERNION'
        clampjOBJ.rotation_quaternion = Quaternion(( q1[0], q1[1], q1[2], q1[3] ))

        # set parenting of wireframe obj
        parenting(clampjOBJ, n1OBJ)

        clampjOBJ.mbdyn.dkey = elem.name
        clampjOBJ.mbdyn.type = 'element'
        elem.blender_object = clampjOBJ.name
        
        # link objects to element collection
        elcol.objects.link(n1OBJ)
        set_active_collection('Master Collection')

        return {'FINISHED'}
    except FileNotFoundError:
        return {'LIBRARY_ERROR'}
    except KeyError:
        return {'COLLECTION_ERROR'}
# -----------------------------------------------------------
# end of spawn_clamp_elem(elem, layout) function

# Imports a Clamp Joint in the scene
class BLENDYN_OT_import_clamp(bpy.types.Operator):
    """ Imports a clamp joint element into the Blender scene """
    bl_idname = "blendyn.import_clamp"
    bl_label = "Imports a clamp joint element"
    int_label: bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = context.scene.mbdyn.elems
        nd = context.scene.mbdyn.nodes

        try:
            elem = ed['clamp_' + str(self.int_label)]
            retval = spawn_clamp_element(elem, context)
            if retval == {'OBJECT_EXISTS'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'NODE1_NOTFOUND'}:
                eldbmsg(retval, type(self).__name__ + '::execute()', elem)
                return {'CANCELLED'}
            elif retval == {'LIBRARY_ERROR'}:
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
# end of BLENDYN_OT_import_clamp class
