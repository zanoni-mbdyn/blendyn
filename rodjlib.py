# --------------------------------------------------------------------------
# MBDynImporter -- file rodlib.py
# Copyright (C) 2016 Andrea Zanoni -- andrea.zanoni@polimi.it
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

import bpy
from mathutils import *
from math import *
from bpy.types import Operator, Panel
from bpy.props import *

# helper function to parse rod joints
def parse_rodj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_rodj(): Parsing rod " + rw[1])

    try:
        el = ed['rod_' + str(rw[1])]
        print("parse_rodj(): found existing entry in elements dictionary for element "\
                + rw[1] + ". Updating it.")
        el.nodes[0].int_label = int(rw[2])
        el.nodes[1].int_label = int(rw[6])
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.is_imported = True
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
    except KeyError:
        print("parse_rodj(): didn't find entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'rodj'
        el.int_label = int(rw[1])
        el.nodes.add()
        el.nodes[0].int_label = int(rw[2])
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
        el.nodes.add()
        el.nodes[1].int_label = int(rw[6])
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.import_function = "add.mbdyn_elem_rod"
        el.update_info_operator = "update.rod"
        el.write_operator = "write.rod"
        el.name = el.type + "_" + str(el.int_label)
        el.is_imported = True
        ret_val = False
        pass 

    return ret_val
# -------------------------------------------------------------------------------
# end of parse_rodj(rw, ed) function

# helper function to parse rod bezier joint
def parse_rodbezj(rw, ed):
    ret_val = True
    # Debug message
    print("parse_rodbezj(): Parsing rod bezier " + rw[2])
    try:
        el = ed['rod_bezier_' + rw[2]]
        print("parse_rodbezj(): found existing entry in elements dictionary.\
                Updating it.")
        el.nodes[0].int_label = int(rw[3])
        el.nodes[1].int_label = int(rw[10])
        el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
        el.offsets[3].value = Vector(( float(rw[14]), float(rw[15]), float(rw[16]) ))
        if el.name in bpy.data.objects.keys():
            el.blender_object = el.name
            el.is_imported = True
    except KeyError:
        print("parse_rodbezj(): didn't find entry in elements dictionary. Creating one.")
        el = ed.add()
        el.type = 'rod bezier'
        el.int_label = int(rw[2])
        el.nodes.add()
        el.nodes[0].int_label = int(rw[3])
        el.offsets.add()
        el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
        el.offsets.add()
        el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        el.nodes.add()
        el.nodes[1].int_label = int(rw[10])
        el.offsets.add()
        el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
        el.offsets.add()
        el.offsets[3].value = Vector(( float(rw[14]), float(rw[15]), float(rw[16]) ))
        el.import_function = "add.mbdyn_elem_rodbez"
        el.info_draw = "rodbez_info_draw"
        el.update_info_operator = "update.rodbez"
        el.write_operator = "write.rodbez"
        el.name = "rod_bezier_" + str(el.int_label)
        ret_val = False
        pass
    return ret_val
# -------------------------------------------------------------------------------
# end of parse_rodbezj(rw, ed) function

# Function that displays Rod Element info in panel
def rod_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:

            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display offset of node 1 info
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)

            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            row = layout.row()
            col = layout.column(align = True)
            col.prop(node, "int_label", text = "Node 2 ID ")
            col.prop(node, "string_label", text = "Node 2 label ")
            col.prop(node, "blender_object", text = "Node 2 Object: ")
            col.enabled = False

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[2], "value", text = "", slider = False)

            layout.separator()
# -----------------------------------------------------------
# end of rod_info_draw() function

# Function that displays Bezier Rod Element info in panel
def rodbez_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn.nodes
    row = layout.row()
    col = layout.column(align=True)
    
    # curve data for blender object representing the element
    cvdata = bpy.data.curves[elem.blender_object + "_cvdata"].splines[0]

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:
 
            # Display node 1 info
            col.prop(node, "int_label", text = "Node 1 ID ")
            col.prop(node, "string_label", text = "Node 1 label ")
            col.prop(node, "blender_object", text = "Node 1 Object: ")
            col.enabled = False

            # Display first offset of node 1 info
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "", slider = False)

            # Display second offset of node 1 info
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[1], "value", text = "", slider = False)
            # col.enabled = False
            
            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            row = layout.row()
            col = layout.column(align = True)
            col.prop(node, "int_label", text = "Node 2 ID ")
            col.prop(node, "string_label", text = "Node 2 label ")
            col.prop(node, "blender_object", text = "Node 2 Object: ")
            col.enabled = False

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 1 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[2], "value", text = "", slider = False)

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 2 in Node " + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[3], "value", text = "", slider = False)

            layout.separator()
# -----------------------------------------------------------
# end of rodbez_info_draw() function

## Updates info for Rod element
class RodUpdate(Operator):
    bl_idname = "update.rod"
    bl_label = "MBDyn Rod info updater"
    elem_key = bpy.props.StringProperty()
    
    def execute(self, context):
        elem = bpy.context.scene.mbdyn.elems[self.elem_key]
        nd = bpy.context.scene.mbdyn.nodes
        cvdata = bpy.data.curves[elem.blender_object + "_cvdata"].splines[0]
        for node in nd:
            if node.int_label == elem.nodes[0].int_label:
                
                # Node 1 offset
                f1 = cvdata.points[0].co.to_3d()
                RN1 = bpy.data.objects[node.blender_object].matrix_world.to_3x3().normalized()
                xN1 = bpy.data.objects[node.blender_object].location
                elem.offsets[0]['value'] = RN1.transposed()*(f1 - xN1)

            elif node.int_label == elem.nodes[1].int_label:
                
                # Node 2 offset
                f2 = cvdata.points[1].co.to_3d()
                RN2 = bpy.data.objects[node.blender_object].matrix_world.to_3x3().normalized()
                xN2 = bpy.data.objects[node.blender_object].location
                elem.offsets[1]['value'] = RN2.transposed()*(f2 - xN2)

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
        elem = bpy.context.scene.mbdyn.elems[self.elem_key]
        nd = bpy.context.scene.mbdyn.nodes
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

## Imports a Rob element in the scene as a line joining two nodes
class MBDynImportElemRod(bpy.types.Operator):
    bl_idname = "add.mbdyn_elem_rod"
    bl_label = "MBDyn rod element importer"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.aligment = 'LEFT'

    def execute(self, context):
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        try: 
            elem = ed['rod_' + str(self.int_label)]
            retval = spawn_rodj_element(elem, context)
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
            elif retval == 'NODE2_NOTFOUND':
                self.report({'ERROR'}, "Could not import element: Blender object \
                        associated to Node " + str(elem.nodes[1].int_label) + " not found")
                return {'CANCELLED'}
            else:
                return retval

        except KeyError:
            self.report({'ERROR'}, "Element rod_" + str(elem.int_label) + "not found.")
            return {'CANCELLED'}
            
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
        ed = bpy.context.scene.mbdyn.elems
        nd = bpy.context.scene.mbdyn.nodes
        try:
            elem = ed['rodbez_' + str(self.int_label)]
            retval = spawn_rodbezj_element(elem)
            if retval == 'OBJECT_EXISTS':
                self.report({'WARNING'}, "Found the Object " + elem.blender_object + \
                " remove or rename it to re-import the element!")
                print("Element is already imported. Remove it or rename it \
                    before re-importing the element.")
                return {'CANCELLED'}
            elif retval == 'NODE1_NOTFOUND':
                self.report({'ERROR'}, "Could not import element: Blender object \
                associated to Node " + str(elem.nodes[0].int_label) + " not found")
                return {'CANCELLED'}
            elif retval == 'NODE2_NOTFOUND':
                self.report({'ERROR'}, "Could not import element: Blender object \
                associated to Node " + str(elem.nodes[1].int_label) + " not found")
                return {'CANCELLED'}
            else:
                return retval
        except KeyError:
            self.report({'ERROR'}, "Element rod_" + str(self.int_label) + " not found.")

            return {'CANCELLED'}
bpy.utils.register_class(MBDynImportElemRodBez)
# -----------------------------------------------------------
# end of MBDynImportElemRodBez class


## Writes the input for Rod Element in the text panel
class RodWrite(Operator):
    bl_idname = "write.rod"
    bl_label = "MBDyn Rod input writer"
    elem_key = bpy.props.StringProperty()

    def execute(self, context):
        elem = bpy.context.scene.mbdyn.elems[self.elem_key]
        f1 = elem.offsets[0].value
        f2 = elem.offsets[1].value

        nd = bpy.context.scene.mbdyn.nodes
        n1 = nd['node_' + str(elem.nodes[0].int_label)]
        n2 = nd['node_' + str(elem.nodes[1].int_label)]
        
        if n1.string_label != 'none':
            node_1_label = n1.string_label
        else:
            node_1_label = str(n1.int_label)
        
        if n2.string_label != 'none':
            node_2_label = n2.string_label
        else:
            node_2_label = str(n2.int_label)

        if elem.string_label != 'none':
            joint_label = elem.string_label
        else:
            joint_label = str(elem.int_label)

        # create new text object
        rbtext = bpy.data.texts.new(self.elem_key)

        # write rod input
        rbtext.write("joint: " + joint_label + ",\n")
        rbtext.write("\trod,\n")
        rbtext.write("\t" + node_1_label + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_1_label + ",\n")
        rbtext.write("\t\t\t" + str(f1[0]) + ",\n")
        rbtext.write("\t\t\t" + str(f1[1]) + ",\n")
        rbtext.write("\t\t\t" + str(f1[2]) + ",\n")
        rbtext.write("\t" + node_2_label + ",\n")
        rbtext.write("\t\tposition, reference, node, " + node_2_label + ",\n")
        rbtext.write("\t\t\t" + str(f2[0]) + ",\n")
        rbtext.write("\t\t\t" + str(f2[1]) + ",\n")
        rbtext.write("\t\t\t" + str(f2[2]) + ",\n")
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
        elem = bpy.context.scene.mbdyn.elems[self.elem_key]
        fO = elem.offsets[0].value
        fA = elem.offsets[1].value
        fB = elem.offsets[2].value
        fI = elem.offsets[3].value

        nd = bpy.context.scene.mbdyn.nodes
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

# Created the object representing a rod joint element
def spawn_rodj_element(elem, context):
    """ Draws a rod joint element as a line connecting two points 
        belonging to two objects """

    nd = context.scene.mbdyn.nodes

    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
        print("spawn_rodj_element(): Element is already imported. \
                Remove the Blender object or rename it \
                before re-importing the element.")
        return{'CANCELLED'}
 
    # try to find Blender objects associated with the nodes that 
    # the element connects

    try:
        n1 = nd['node_' + str(elem.nodes[0].int_label)].blender_object
    except KeyError:
        print("spawn_rodj_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[0].int_label))
        return {'NODE1_NOTFOUND'}
    
    try:
        n2 = nd['node_' + str(elem.nodes[1].int_label)].blender_object
    except KeyError:
        print("spawn_rodj_element(): Could not find a Blender \
                object associated to Node " + \
                str(elem.nodes[1].int_label))
        return {'NODE2_NOTFOUND'}


    # nodes' objects
    n1OBJ = bpy.data.objects[n1]
    n2OBJ = bpy.data.objects[n2]

    # creation of line representing the rod
    rodobj_id = 'rodj_' + str(elem.int_label)
    rodcv_id = rodobj_id + '_cvdata'
        
    # check if the object is already present. If it is, remove it.
    if rodobj_id in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[rodobj_id])
       
    # check if the curve is already present. If it is, remove it.
    if rodcv_id in bpy.data.curves.keys():
        bpy.data.curves.remove(bpy.data.curves[rodcv_id])

    # create a new curve
    cvdata = bpy.data.curves.new(rodcv_id, type = 'CURVE')
    cvdata.dimensions = '3D'
    polydata = cvdata.splines.new('POLY')
    polydata.points.add(1)

    # get offsets
    f1 = elem.offsets[0].value
    f2 = elem.offsets[1].value

    # assign coordinates of knots in global frame
    polydata.points[0].co = n1OBJ.matrix_world*Vector(( f1[0], f1[1], f1[2], 1.0 ))
    polydata.points[1].co = n2OBJ.matrix_world*Vector(( f2[0], f2[1], f2[2], 1.0 ))
        
    rodOBJ = bpy.data.objects.new(rodobj_id, cvdata)
    rodOBJ.mbdyn.type = 'elem.joint'
    rodOBJ.mbdyn.int_label= elem.int_label
    bpy.context.scene.objects.link(rodOBJ)
    elem.blender_object = rodOBJ.name
        
    ## hooking of the line ends to the Blender objects 
    
    # P1 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n1OBJ.select = True
    rodOBJ.select = True
    bpy.context.scene.objects.active = rodOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    rodOBJ.data.splines[0].points[0].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # P2 hook
    bpy.ops.object.select_all(action = 'DESELECT')
    n2OBJ.select = True
    rodOBJ.select = True
    bpy.context.scene.objects.active = rodOBJ
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    bpy.ops.curve.select_all(action = 'DESELECT')
    rodOBJ.data.splines[0].points[1].select = True
    bpy.ops.object.hook_add_selob(use_bone = False)
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    bpy.ops.object.select_all(action = 'DESELECT')

    # create group for element
    rodOBJ.select = True
    n1OBJ.select = True
    n2OBJ.select = True
    bpy.ops.group.create(name = rodOBJ.name)

    elem.is_imported = True
    return{'FINISHED'}
# -----------------------------------------------------------
# end of spawn_rodj_element(elem) function

def spawn_rodbezj_element(elem):
    if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
        return {'OBJECT_EXISTS'}
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
            return {'NODE1_NOTFOUND'}
        elif n2 == "none":
            print("MBDynImportElemRodBez(): Could not find a Blender object \
            associated to Node " + str(elem.nodes[1].int_label))
            return {'NODE2_NOTFOUND'}

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
        rodOBJ.mbdyn.type = 'elem.joint'
        rodOBJ.mbdyn.int_label = elem.int_label
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
        elem.is_imported = True
        return{'FINISHED'}
# -----------------------------------------------------------
# end of spawn_rodbezj_element(elem) function

