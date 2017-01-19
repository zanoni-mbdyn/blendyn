# --------------------------------------------------------------------------
# Blendyn -- file forcelib.py
# Copyright (C) 2015 -- 2017 Andrea Zanoni -- andrea.zanoni@polimi.it
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
from bpy.types import Operator, Panel
from bpy.props import *

import pdb

try: 
    from netCDF4 import Dataset
except ImportError:
    pass

## Parses structural absolute force entry in the .log file 
#  (see section E.2.22 of input manual for details)
def parse_structural_absolute_force(rw, ed): 
    ret_val = True
    # Debug message
    print("parse_structural_absolute_force(): Parsing structural absolute force" + rw[3])
    try:
        el = ed['structural_absolute_force_' + str(rw[3])]
        
        print("parse_structural_absolute_force(): found existing entry in \
                elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[4])
        
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))
         
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        pass
        print("parse_structural_absolute_force(): didn't found en entry in \
                elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'structural_absolute_force'
        el.int_label = int(rw[3])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[4])
 
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))

        el.import_function = "add.mbdyn_elem_structural_absolute_force"
        el.update = "update_structural_force"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_structural_absolute_force(rw, ed) function

## Parses structural follower force entry in the .log file 
#  (see section E.2.22 of input manual for details)
def parse_structural_follower_force(rw, ed): 
    ret_val = True
    # Debug message
    print("parse_structural_follower_force(): Parsing structural follower force" + rw[3])
    try:
        el = ed['structural_follower_force_' + str(rw[3])]
        
        print("parse_structural_follower_force(): found existing entry in \
                elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[4])
        
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))
         
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        pass
        print("parse_structural_follower_force(): didn't found en entry in \
                elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'structural_follower_force'
        el.int_label = int(rw[3])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[4])
 
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))

        el.import_function = "add.mbdyn_elem_structural_follower_force"
        el.update = "update_structural_force"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_structural_follower_force(rw, ed) function

## Parses structural absolute couple entry in the .log file 
#  (see section E.2.22 of input manual for details)
def parse_structural_absolute_couple(rw, ed): 
    ret_val = True
    # Debug message
    print("parse_structural_absolute_couple(): Parsing structural absolute force" + rw[3])
    try:
        el = ed['structural_absolute_couple_' + str(rw[3])]
        
        print("parse_structural_absolute_couple(): found existing entry in \
                elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[4])
        
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))
         
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        pass
        print("parse_structural_absolute_couple(): didn't found en entry in \
                elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'structural_absolute_couple'
        el.int_label = int(rw[3])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[4])
 
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))

        el.import_function = "add.mbdyn_elem_structural_absolute_couple"
        el.update = "update_structural_couple"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_structural_absolute_couple(rw, ed) function

## Parses structural follower couple entry in the .log file 
#  (see section E.2.22 of input manual for details)
def parse_structural_follower_couple(rw, ed): 
    ret_val = True
    # Debug message
    print("parse_structural_follower_couple(): Parsing structural follower force" + rw[3])
    try:
        el = ed['structural_follower_couple_' + str(rw[3])]
        
        print("parse_structural_follower_couple(): found existing entry in \
                elements dictionary. Updating it.")
        
        el.nodes[0].int_label = int(rw[4])
        
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))
         
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
        el.is_imported = True
        pass
    except KeyError:
        pass
        print("parse_structural_follower_couple(): didn't found en entry in \
                elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'structural_follower_couple'
        el.int_label = int(rw[3])

        el.nodes.add()
        el.nodes[0].int_label = int(rw[4])
 
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[5]), float(rw[6]), float(rw[7]) ))

        el.import_function = "add.mbdyn_elem_structural_follower_couple"
        el.update = "update_structural_couple"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
    return ret_val
# -----------------------------------------------------------
# end of parse_structural_follower_couple(rw, ed) function

## Spawns a Blender object representing a structural absolute force element
def spawn_structural_force_element(elem, context):
    """ Draws a structural force element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_structural_force(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_structural_force_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    # node object
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe force object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'blendyn-master', 'library', 'forces.blend', \
            'Object'), filename = 'force')

    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        forceOBJ = bpy.context.selected_objects[0]
        forceOBJ.name = elem.name

        # offsets with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    
        # place the joint object in the position defined relative to node 1
        forceOBJ.location = p1
        forceOBJ.rotation_mode = 'QUATERNION'

        # set parenting of wireframe obj
        bpy.ops.object.select_all(action = 'DESELECT')
        forceOBJ.select = True
        n1OBJ.select = True
        bpy.context.scene.objects.active = n1OBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        elem.blender_object = forceOBJ.name
        forceOBJ.mbdyn.int_label = elem.int_label

        # Flag the object to be updated
        ude = bpy.context.scene.mbdyn.elems_to_update.add()
        ude.dkey = elem.name
        ude.name = elem.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
    pass
# -----------------------------------------------------------
# end of spawn_structural_force_element(elem, layout) function

## Spawns a Blender object representing a structural absolute couple element
def spawn_structural_couple_element(elem, context):
    """ Draws a structural couple element, loading a wireframe
        object from the addon library """
    mbs = context.scene.mbdyn
    nd = mbs.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_structural_couple_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return {'CANCELLED'}

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_structural_couple_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}

    # node object
    n1OBJ = bpy.data.objects[n1]

    # load the wireframe couple object from the library
    app_retval = bpy.ops.wm.append(directory = os.path.join(mbs.addon_path,\
            'blendyn-master', 'library', 'forces.blend', \
            'Object'), filename = 'couple')

    if app_retval == {'FINISHED'}:
        # the append operator leaves just the imported object selected
        coupleOBJ = bpy.context.selected_objects[0]
        coupleOBJ.name = elem.name

        # offsets with respect to nodes
        f1 = elem.offsets[0].value
    
        # project offsets in global frame
        R1 = n1OBJ.rotation_quaternion.to_matrix()
        p1 = n1OBJ.location + R1*Vector(( f1[0], f1[1], f1[2] ))
    
        # place the joint object in the position defined relative to node 1
        coupleOBJ.location = p1
        coupleOBJ.rotation_mode = 'QUATERNION'

        # set parenting of wireframe obj
        bpy.ops.object.select_all(action = 'DESELECT')
        coupleOBJ.select = True
        n1OBJ.select = True
        bpy.context.scene.objects.active = n1OBJ
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)

        elem.blender_object = coupleOBJ.name
        coupleOBJ.mbdyn.int_label = elem.int_label

        # Flag the object to be updated
        ude = bpy.context.scene.mbdyn.elems_to_update.add()
        ude.dkey = elem.name
        ude.name = elem.name

        return {'FINISHED'}
    else:
        return {'LIBRARY_ERROR'}
    pass
# -----------------------------------------------------------
# end of spawn_structural_couple_element(elem, layout) function

# Imports a Structural Absolute Force Element in the scene
class Scene_OT_MBDyn_Import_Structural_Absolute_Force_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_structural_absolute_force"
    bl_label = "MBDyn structural absolute force element importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['structural_absolute_force_' + str(self.int_label)]
            retval = spawn_structural_force_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element structural_absolute_force_"\
                    + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Structural_Absolute_Force_Element class

# Imports a Structural Follower Force Element in the scene
class Scene_OT_MBDyn_Import_Structural_Follower_Force_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_structural_follower_force"
    bl_label = "MBDyn structural follower force element importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['structural_follower_force_' + str(self.int_label)]
            retval = spawn_structural_force_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element structural_follower_force_"\
                    + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Structural_Follower_Force_Element class

# Imports a Structural Absolute Couple Element in the scene
class Scene_OT_MBDyn_Import_Structural_Absolute_Couple_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_structural_absolute_couple"
    bl_label = "MBDyn structural absolute couple element importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['structural_absolute_couple_' + str(self.int_label)]
            retval = spawn_structural_couple_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element structural_absolute_couple_"\
                    + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Structural_Absolute_Couple_Element class

# Imports a Structural Follower Couple Element in the scene
class Scene_OT_MBDyn_Import_Structural_Follower_Couple_Element(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_structural_follower_couple"
    bl_label = "MBDyn structural follower couple element importer"
    int_label = bpy.props.IntProperty()
    
    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes

        try:
            elem = ed['structural_follower_couple_' + str(self.int_label)]
            retval = spawn_structural_couple_element(elem, context)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + \
                    elem.blender_object + \
                    " remove or rename it to re-import the element!")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, \
                    "Could not import element: Blender object \
                    associated to Node " + str(elem.nodes[0].int_label) \
                    + " not found")
                return {'CANCELLED'}
            elif retval == 'LIBRARY_ERROR':
                self.report({'ERROR'}, "Could not import element: could not \
                        load library object")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element structural_follower_couple_"\
                    + str(elem.int_label) + "not found")
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of Scene_OT_MBDyn_Import_Structural_Follower_Couple_Element class

def update_structural_force(elem, insert_keyframe = False):
    """ Updates the configuration of a structural force
        by scaling and orienting the arrow in the correct way """

    scene = bpy.context.scene
    mbs = scene.mbdyn
    nd = mbs.nodes
    
    if mbs.use_netcdf:

        tdx = scene.frame_current * mbs.load_frequency
        ncfile = mbs.file_path + mbs.file_basename + '.nc'
        nc = Dataset(ncfile, "r", format="NETCDF3")

        node = nd['node_' + str(elem.nodes[0].int_label)]
        nodeOBJ = bpy.data.objects[node.blender_object]
        R0 = nodeOBJ.matrix_world.to_3x3().normalized()
        
        obj = bpy.data.objects[elem.blender_object]
        F = Vector(( nc.variables['elem.force.' + str(elem.int_label) + '.F'][tdx,:] ))
        Fl = R0.transposed()*F

        obj.rotation_quaternion = (-Fl).to_track_quat('-Z', 'Y')
        obj.scale = Vector(( 1, 1, Fl.magnitude ))*elem.scale_factor
    else:
        pass
# -----------------------------------------------------------
# end of update_structural_force() function

def update_structural_couple(elem, insert_keyframe = False):
    """ Updates the configuration of a structural couple
        by scaling and orienting the arrow in the correct way """

    scene = bpy.context.scene
    mbs = scene.mbdyn
    nd = mbs.nodes
    
    if mbs.use_netcdf:

        tdx = scene.frame_current * mbs.load_frequency
        ncfile = mbs.file_path + mbs.file_basename + '.nc'
        nc = Dataset(ncfile, "r", format="NETCDF3")

        node = nd['node_' + str(elem.nodes[0].int_label)]
        nodeOBJ = bpy.data.objects[node.blender_object]
        R0 = nodeOBJ.matrix_world.to_3x3().normalized()
        
        obj = bpy.data.objects[elem.blender_object]
        M = Vector(( nc.variables['elem.couple.' + str(elem.int_label) + '.M'][tdx,:] ))
        Ml = R0.transposed()*M

        obj.rotation_quaternion = (-Ml).to_track_quat('-Z', 'Y')
        obj.scale = Vector(( Ml.magnitude, Ml.magnitude, 1.0 ))*elem.scale_factor
    else:
        pass
    pass
# -----------------------------------------------------------
# end of update_structural_couple() function
