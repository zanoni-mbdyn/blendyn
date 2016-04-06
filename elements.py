# --------------------------------------------------------------------------
# MBDynImporter -- file element.py
# Copyright (C) 2015 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of MBDynImporter, add-on script for Blender.
#
#    MBDynImporter is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MBDynImporter  is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with MBDynImporter.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

# TODO: check for unnecessary stuff
import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import BoolProperty, IntProperty, IntVectorProperty, FloatVectorProperty
from bpy.props import StringProperty, BoolVectorProperty, PointerProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper

import ntpath, os, csv, math
from collections import namedtuple

from .elementlib import *

class MBDynElemOffset(bpy.types.PropertyGroup):
    value = FloatVectorProperty(
        name = "Offset value",
	description = "The offset vector, with respect to the node",
        size = 3,
        precision = 6
	)
bpy.utils.register_class(MBDynElemOffset)
# -----------------------------------------------------------
# end of MBDynElemOffset class 

class MBDynElemRotOffset(bpy.types.PropertyGroup):
    value = FloatVectorProperty(
        name = "Offset value",
        description = "The rotational offset quaternion, with respect to the node",
        size = 4,
        precision = 6
        )
bpy.utils.register_class(MBDynElemRotOffset)
# -----------------------------------------------------------
# end of MBDynElemRotOffset class 

class MBDynElemNodesColl(bpy.types.PropertyGroup):
    int_label = IntProperty(
        name = "MBDyn node ID",
        description = "",
        )
bpy.utils.register_class(MBDynElemNodesColl)
# -----------------------------------------------------------
# end of MBDynElemNodesColl class 

class MBDynElemsDictionary(bpy.types.PropertyGroup):
    type = StringProperty(
        name = "Type of MBDyn element",
        description = ""
        )

    int_label = IntProperty(
        name = "Integer label of element",
        description = ""
        )

    string_label = StringProperty(
        name = "String label of element",
        description = ""
        )

    nodes = CollectionProperty(
        type = MBDynElemNodesColl,
        name = "Connected nodes",
        description = "MBDyn nodes that the element connects"
        )

    offsets = CollectionProperty(
        type = MBDynElemOffset,
        name = "Offsets of attach points",
        description = "Collector of offsets of element attaching points"
        )

    rotoffsets = CollectionProperty(
        type = MBDynElemRotOffset,
        name = "Rotational offsets of attach R.Fs. of joint",
        description = "Collector of rotational offsets of element attach R.Fs."
        )

    import_function = StringProperty(
        name = "Import operator",
        description = "Id name of the class defining the import operator for the element"
        )

    draw_function = StringProperty(
        name = "Draw function",
        description = "Id of the function that is called when the element configuration is updated",
        )

    update_info_operator = StringProperty(
        name = "Update operator",
        description = "Id name of the operator that updates the element info using \
            the current position of the blender objects representing it",
        default = 'none'
        )

    write_operator = StringProperty(
        name = "Input write operator",
        description = "Id name of the operator that writes the element input contribute",
        default = 'none'
        )

    info_draw = StringProperty(
        name = "Element Info Function",
        description = "Name of the function used to display element data in the View3D panel",
        default = "elem_info_draw"
        )

    blender_object = StringProperty(
        name = "Blender Object",
        description = "Name of the Blender Object associated with this element"
        )

    is_imported = BoolProperty(
        name = "Is imported flag",
        description = "Flag set to true at the end of the import process"
        )
bpy.utils.register_class(MBDynElemsDictionary)
# -----------------------------------------------------------
# end of MBDynElemsDictionary class 

## Updates info for Rod element
class RodUpdate(Operator):
    bl_idname = "update.rodbez"
    bl_label = "MBDyn Rod Bezier info updater"
    elem_key = bpy.props.StringProperty()
    
    def execute(self, context):
        elem = bpy.context.scene.mbdyn_settings.elems_dictionary[self.elem_key]
        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
        cvdata = bpy.data.curves[elem.blender_object + "_cvdata"].splines[0]
        for node in nd:
            if node.int_label == elem.nodes[0].int_label:
                
                # Node 1 offset
                fA = cvdata.points[0].co
                RN1 = bpy.data.objects[node.blender_object].matrix_world.to_3x3().normalized()
                xN1 = bpy.data.objects[node.blender_object].location
                elem.offsets[0]['value'] = RN1.transposed()*(fA - xN1)

            elif node.int_label == elem.nodes[1].int_label:
                
                # Node 2 offset
                fN = cvdata.points[1].co
                RN2 = bpy.data.objects[node.blender_object].matrix_world.to_3x3().normalized()
                xN2 = bpy.data.objects[node.blender_object].location
                elem.offsets[1]['value'] = RN2.transposed()*(fB - xN2)

        return {'FINISHED'} 
bpy.utils.register_class(RodUpdate)
# -----------------------------------------------------------
# end of RodUpdate class

## Updates info for Bezier Rod element
class RodBezUpdate(Operator):
    bl_idname = "update.rodbez"
    bl_label = "MBDyn Rod Bezier info updater"
    elem_key = bpy.props.StringProperty()

    def execute(self, context):
        elem = bpy.context.scene.mbdyn_settings.elems_dictionary[self.elem_key]
        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
        cvdata = bpy.data.curves[elem.blender_object + "_cvdata"].splines[0]
        for node in nd:
            if node.int_label == elem.nodes[0].int_label:
    
                # node 1 offset 1
                fOG = cvdata.bezier_points[0].co
                RN1 = bpy.data.objects[node.blender_object].matrix_world.to_3x3().normalized()
                xN1 = bpy.data.objects[node.blender_object].location
                elem.offsets[0]['value'] = RN1.transposed()*(fOG - xN1)
    
                # node 1 offset 2
                fAG = cvdata.bezier_points[0].handle_right
                elem.offsets[1]['value'] = RN1.transposed()*(fAG - xN1) 
        
            elif node.int_label == elem.nodes[1].int_label:
    
                # node 2 offset 1
                fBG = cvdata.bezier_points[1].handle_left
                RN2 = bpy.data.objects[node.blender_object].matrix_world.to_3x3().normalized()
                xN2 = bpy.data.objects[node.blender_object].location
                elem.offsets[2]['value'] = RN2.transposed()*(fBG - xN2)
    
                # offset 2
                fIG = cvdata.bezier_points[1].co
                elem.offsets[3]['value'] = RN2.transposed()*(fIG - xN2)

        return {'FINISHED'}
bpy.utils.register_class(RodBezUpdate)
# -----------------------------------------------------------
# end of RodBezUpdate class

## Writes the input for Rod Element in the text panel
class RodWrite(Operator):
    bl_idname = "write.rodbez"
    bl_label = "MBDyn Rod Bezier input writer"
    elem_key = bpy.props.StringProperty()

    def execute(self, context):
        elem = bpy.context.scene.mbdyn_settings.elems_dictionary[self.elem_key]
        fA = elem.offsets[0].value
        fB = elem.offsets[1].value

        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
        n1 = nd['node_' + str(elem.nodes[0].int_label)]
        n2 = nd['node_' + str(elem.nodes[1].int_label)]
        
        node_1_label = "Node_" + str(elem.nodes[0].int_label)
        if n1.string_label != node_1_label:
            node_1_label = n1.string_label
        else:
            node_1_label = str(n1.int_label)
        
        node_2_label = "Node_" + str(elem.nodes[1].int_label)
        if n2.string_label != node_2_label:
            node_2_label = n2.string_label
        else:
            node_2_label = str(n2.int_label)

        # create new text object
        rbtext = bpy.data.texts.new(self.elem_key)

        # write rod input
        rbtext.write("joint: " + self.elem_key + ",\n")
        rbtext.write("\trod,\n")
        rbtext.write("\t" + node_1_label + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_1_label + ",\n")
        rbtext.write("\t\t\t" + str(fA[0]) + "*msfx" + ",\n")
        rbtext.write("\t\t\t" + str(fA[1]) + "*msfy" + ",\n")
        rbtext.write("\t\t\t" + str(fA[2]) + "*msfz" + ",\n")
        rbtext.write("\t" + node_2_label + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_2_label + ",\n")
        rbtext.write("\t\t\t" + str(fB[0]) + "*msfx" + ",\n")
        rbtext.write("\t\t\t" + str(fB[1]) + "*msfy" + ",\n")
        rbtext.write("\t\t\t" + str(fB[2]) + "*msfz" + ",\n")
        rbtext.write("\tfrom nodes;")

        self.report({'INFO'}, "Input file contribute for element written. See " +\
                        rbtext.name + " in text editor")
        return {'FINISHED'}
bpy.utils.register_class(RodWrite)
# -----------------------------------------------------------
# end of RodWrite class
         
## Writes the input for Bezier Rod Element in text panel
class RodBezWrite(Operator):
    bl_idname = "write.rodbez"
    bl_label = "MBDyn Rod Bezier input writer"
    elem_key = bpy.props.StringProperty()

    def execute(self, context):
        elem = bpy.context.scene.mbdyn_settings.elems_dictionary[self.elem_key]
        fO = elem.offsets[0].value
        fA = elem.offsets[1].value
        fB = elem.offsets[2].value
        fI = elem.offsets[3].value

        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
        n1 = nd['node_' + str(elem.nodes[0].int_label)]
        n2 = nd['node_' + str(elem.nodes[1].int_label)]
        
        node_1_label = "Node_" + str(elem.nodes[0].int_label)
        if n1.string_label != node_1_label:
            node_1_label = n1.string_label
        else:
            node_1_label = str(n1.int_label)
        
        node_2_label = "Node_" + str(elem.nodes[1].int_label)
        if n2.string_label != node_2_label:
            node_2_label = n2.string_label
        else:
            node_2_label = str(n2.int_label)

        # create new text object
        rbtext = bpy.data.texts.new(self.elem_key)
    
        # write rod bezier input
        rbtext.write("joint: " + self.elem_key + ",\n")
        rbtext.write("\trod bezier,\n")
        rbtext.write("\t" + node_1_label + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_1_label + ",\n")
        rbtext.write("\t\t\t" + str(fO[0]) + "*msfx" + ",\n")
        rbtext.write("\t\t\t" + str(fO[1]) + "*msfy" + ",\n")
        rbtext.write("\t\t\t" + str(fO[2]) + "*msfz" + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_1_label + ",\n")
        rbtext.write("\t\t\t" + str(fA[0]) + "*msfx" + ",\n")
        rbtext.write("\t\t\t" + str(fA[1]) + "*msfy" + ",\n")
        rbtext.write("\t\t\t" + str(fA[2]) + "*msfz" + ",\n")
        rbtext.write("\t" + node_2_label + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_2_label + ",\n")
        rbtext.write("\t\t\t" + str(fB[0]) + "*msfx" + ",\n")
        rbtext.write("\t\t\t" + str(fB[1]) + "*msfy" + ",\n")
        rbtext.write("\t\t\t" + str(fB[2]) + "*msfz" + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_2_label + ",\n")
        rbtext.write("\t\t\t" + str(fI[0]) + "*msfx" + ",\n")
        rbtext.write("\t\t\t" + str(fI[1]) + "*msfy" + ",\n")
        rbtext.write("\t\t\t" + str(fI[2]) + "*msfz" + ",\n")
        rbtext.write("\tfrom nodes;")

        self.report({'INFO'}, "Input file contribute for element written. See " +\
                        rbtext.name + " in text editor")
        return {'FINISHED'}
bpy.utils.register_class(RodBezWrite)
# -----------------------------------------------------------
# end of RodBezWrite class

## Helps import a Deformable Displacement Joint in the scene
class MBDynImportElemDefDisp(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_defdisp"
    bl_label = "MBDyn rod element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn_settings.elems_dictionary
        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary

        for elem in ed:
            if elem.int_label == self.int_label:
                if any(obj == elem.blender_object \
                        for obj in context.scene.objects.keys()):
                    self.report({'WARNING'}, "Found the Object " + \
                            elem.blender_object + \
                            " remove or rename it to re-import the element!")
                    print("Element is already imported. Remove the Blender object or rename it \
                            before re-importing the element.")
                    return{'CANCELLED'}
            else:
                n1 = "none"
                n2 = "none"

                # try to find the Blender objects associated with the nodes that
                # the element connects
                for node in nd:
                    if elem.nodes[0].int_label == node.int_label:
                        n1 = node.blender_object
                    elif elem.nodes[1].int_label == node.int_label:
                        n2 = node.blender_object
                if n1 == "none":
                    print("MBDynImportElemDefDisp(): Could not find a Blender object associated to Node " + str(elem.nodes[0].int_label) + " not found")
                    self.report({'ERROR'}, "Could not import element: Blender object associated to Node " + str(elem.nodes[0].int_label) + " not found")
                    return {'CANCELLED'}
                elif n2 == "none":
                    print("MBDynImportElemDefDisp(): Could not find a Blender object associated to Node " + str(elem.nodes[1].int_label) + " not found")
                    self.report({'ERROR'}, "Could not import element: Blender object associated to Node " + str(elem.nodes[1].int_label) + " not found")
                    return {'CANCELLED'}

                # create the Blender objects representing the element
                # TODO
                self.report({'WARNING'}, "Not implemented yet sorry!")
                return {'CANCELLED'}
bpy.utils.register_class(MBDynImportElemDefDisp)
# -----------------------------------------------------------
# end of MBDynImportElemDefDisp class

## Helps import a Rob element in the scene
class MBDynImportElemRod(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_rod"
    bl_label = "MBDyn rod element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn_settings.elems_dictionary
        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
        for elem in ed:
            if elem.int_label == self.int_label:
                if any(obj == elem.blender_object \
                        for obj in context.scene.objects.keys()):
                    self.report({'WARNING'}, "Found the Object " + \
                            elem.blender_object + \
                    " remove or rename it to re-import the element!")
                    print("Element is already imported. \
                            Remove the Blender object or rename it \
                            before re-importing the element.")
                    return{'CANCELLED'}
                else:
                    n1 = "none"
                    n2 = "none"
                    
                    # try to find Blender objects associated with the nodes that 
                    # the element connects
                    for node in nd:
                        if elem.nodes[0].int_label == node.int_label:
                            n1 = node.blender_object
                        elif elem.nodes[1].int_label == node.int_label:
                            n2 = node.blender_object
                    if n1 == "none":
                        print("MBDynImportElemRod(): Could not find a Blender \
                                object associated to Node " + \
                                str(elem.nodes[0].int_label))
                        self.report({'ERROR'}, \
                                "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[0].int_label) \
                        + " not found")
                        return {'CANCELLED'}
                    elif n2 == "none":
                        print("MBDynImportElemRod(): Could not find a Blender object \
                        associated to Node " + str(elem.nodes[1].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[1].int_label) + " not found")
                        return {'CANCELLED'}

                    # creation of line representing the rod
                    rodobj_id = "rod_" + str(elem.int_label)
                    rodcv_id = rodobj_id + "_cvdata"
                    
                    # check if the object is already present
                    # If it is, remove it. FIXME: this may be dangerous!
                    if rodobj_id in bpy.data.objects.keys():
                        bpy.data.objects.remove(bpy.data.objects[rodobj_id])
                    
                    # check if the curve is already present
                    # If it is, remove it. FIXME: this may be dangerous!
                    if rodcv_id in bpy.data.curves.keys():
                        bpy.data.curves.remove(bpy.data.curves[rodcv_id])

                    # create a new curve and its object
                    cvdata = bpy.data.curves.new(rodcv_id, type = 'CURVE')
                    cvdata.dimensions = '3D'
                    polydata = cvdata.splines.new('POLY')
                    polydata.points.add(1)

                    # get offsets
                    f1 = elem.offsets[0].value
                    f2 = elem.offsets[1].value

                    # assign coordinates of knots in global frame
                    polydata.points[0].co = \
                    bpy.data.objects[n1].matrix_world*Vector(( f1[0], f1[1], f1[2], 1.0 ))
                    polydata.points[1].co = \
                    bpy.data.objects[n2].matrix_world*Vector(( f2[0], f2[1], f2[2], 1.0 ))
                    
                    rodOBJ = bpy.data.objects.new("rod_" + str(elem.int_label), cvdata)
                    bpy.context.scene.objects.link(rodOBJ)
                    elem.blender_object = rodOBJ.name
                    elem.name = rodOBJ.name
                    rodOBJ.select = True
                    
                    ## hooking of the line ends to the Blender objects
                    
                    # deselect all objects (guaranteed by previous the selection of rodOBJ)
                    bpy.ops.object.select_all()
                    
                    # select rod, set it to active and enter edit mode
                    rodOBJ.select = True
                    bpy.context.scene.objects.active = rodOBJ
                    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)

                    # select first end of curve and parent object for node 1, 
                    # then set the hook and deselect object of node 1
                    bpy.data.curves[rodcv_id].splines[0].points[0].select = True
                    bpy.data.objects[n1].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.objects[n1].select = False
                    bpy.data.curves[rodcv_id].splines[0].points[0].select = False

                    # select second end of curve and parent object for node 2, 
                    # then set the hook.
                    bpy.data.curves[rodcv_id].splines[0].points[1].select = True
                    bpy.data.objects[n2].select = True
                    bpy.ops.object.hook_add_selob()

                    # exit edit mode and deselect all
                    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
                    bpy.ops.object.select_all()

                    elem.is_imported = True
                    return{'FINISHED'}

        # Debug message
        print("MBDynInsertElementButton: Importing element " + str(self.int_label) + " to scene.")
        return {'FINISHED'}
bpy.utils.register_class(MBDynImportElemRod)
# -----------------------------------------------------------
# end of MBDynImportElemRod class

## Helps import a Rob Bezier element in the scene
class MBDynImportElemRodBez(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_rodbez"
    bl_label = "MBDyn rod element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn_settings.elems_dictionary
        nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
        for elem in ed:
            if elem.int_label == self.int_label:
                if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
                    self.report({'WARNING'}, "Found the Object " + elem.blender_object + \
                    " remove or rename it to re-import the element!")
                    print("Element is already imported. Remove it or rename it \
                        before re-importing the element.")
                    return{'CANCELLED'}
                else:
                    elem.is_imported = False
                    n1 = "none"
                    n2 = "none"
                    
                    # try to find Blender objects associated with the nodes that 
                    # the element connects
                    for node in nd:
                        if elem.nodes[0].int_label == node.int_label:
                            n1 = node.blender_object
                        elif elem.nodes[1].int_label == node.int_label:
                            n2 = node.blender_object
                    if n1 == "none":
                        print("MBDynImportElemRodBez(): Could not find a Blender object \
                        associated to Node " + str(elem.nodes[0].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[0].int_label) + " not found")
                        return{'CANCELLED'}
                    elif n2 == "none":
                        print("MBDynImportElemRodBez(): Could not find a Blender object \
                        associated to Node " + str(elem.nodes[1].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[1].int_label) + " not found")
                        return{'CANCELLED'}

                    # creation of line representing the rod
                    rodobj_id = "rod_bezier_" + str(elem.int_label)
                    rodcv_id =  rodobj_id + "_cvdata"
                    
                    # check if the object is already present
                    # If it is, remove it. FIXME: this may be dangerous!
                    if rodobj_id in bpy.data.objects.keys():
                        bpy.data.objects.remove(bpy.data.objects[rodobj_id])
                    
                    # check if curve is already present
                    # If it is, remove it. FIXME: this may be dangerous!
                    if rodcv_id in bpy.data.curves.keys():
                        bpy.data.curves.remove(bpy.data.curves[rodcv_id])
                    
                    # create a new curve and its object
                    cvdata = bpy.data.curves.new(rodcv_id, type = 'CURVE')
                    cvdata.dimensions = '3D'
                    polydata = cvdata.splines.new('BEZIER')
                    polydata.bezier_points.add(1)
                    
                    # Get offsets
                    fO = elem.offsets[0].value
                    fA = elem.offsets[1].value
                    fB = elem.offsets[2].value
                    fI = elem.offsets[3].value
                    
                    # Rotate and translate offsets
                    fOG = bpy.data.objects[n1].matrix_world*Vector(( fO[0], fO[1], fO[2], 1.0 ))
                    fAG = bpy.data.objects[n1].matrix_world*Vector(( fA[0], fA[1], fA[2], 1.0 ))
                    fBG = bpy.data.objects[n2].matrix_world*Vector(( fB[0], fB[1], fB[2], 1.0 ))
                    fIG = bpy.data.objects[n2].matrix_world*Vector(( fI[0], fI[1], fI[2], 1.0 ))

                    # node 1
                    polydata.bezier_points[0].co = Vector(( fOG[0], fOG[1], fOG[2] ))
                    polydata.bezier_points[0].handle_left_type = 'FREE'
                    polydata.bezier_points[0].handle_left = polydata.bezier_points[0].co
                    polydata.bezier_points[0].handle_right_type = 'FREE'
                    polydata.bezier_points[0].handle_right = Vector(( fAG[0], fAG[1], fAG[2] ))
                    
                    # node 2
                    polydata.bezier_points[1].co = Vector(( fIG[0], fIG[1], fIG[2] ))
                    polydata.bezier_points[1].handle_left_type = 'FREE'
                    polydata.bezier_points[1].handle_left = Vector(( fBG[0], fBG[1], fBG[2] ))
                    polydata.bezier_points[1].handle_right_type = 'FREE'
                    polydata.bezier_points[1].handle_right = polydata.bezier_points[1].co

                    rodOBJ = bpy.data.objects.new("rod_bezier_" + str(elem.int_label), cvdata)
                    bpy.context.scene.objects.link(rodOBJ)
                    elem.blender_object = rodOBJ.name
                    elem.name = rodOBJ.name
                    rodOBJ.select = True

                    ## hooking of the line ends to the Blender objects
                    
                    # deselect all objects (guaranteed by previous the selection of rodOBJ)
                    bpy.ops.object.select_all()
                    
                    # select rod, set it to active and enter edit mode
                    rodOBJ.select = True
                    bpy.context.scene.objects.active = rodOBJ

                    # select first control point and its handles and object 1,
                    # then set the hook and deselect object of node 1
                    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
                    
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_control_point = True
                    bpy.data.objects[n1].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_control_point = False
                    bpy.data.objects[n1].select = False

                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_left_handle = True
                    bpy.data.objects[n1].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_left_handle = False
                    bpy.data.objects[n1].select = False 
                    
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_right_handle = True
                    bpy.data.objects[n1].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_right_handle = False
                    bpy.data.objects[n1].select = False

                    # exit edit mode and deselect all
                    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
                    bpy.ops.object.select_all()

                    # select first control point and its handles and object 2,
                    # then set the hook and deselect object of node 2
                    
                    rodOBJ.select = True
                    bpy.context.scene.objects.active = rodOBJ
                    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
                    
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_control_point = True
                    bpy.data.objects[n2].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_control_point = False
                    bpy.data.objects[n2].select = False

                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_left_handle = True
                    bpy.data.objects[n2].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_left_handle = False
                    bpy.data.objects[n2].select = False 
                    
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_right_handle = True
                    bpy.data.objects[n2].select = True
                    bpy.ops.object.hook_add_selob()
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_right_handle = False
                    bpy.data.objects[n2].select = False

                    # exit edit mode and deselect all
                    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
                    bpy.ops.object.select_all()

                    elem.is_imported = True
                    return{'FINISHED'}
bpy.utils.register_class(MBDynImportElemRodBez)
# -----------------------------------------------------------
# end of MBDynImportElemRodBez class

