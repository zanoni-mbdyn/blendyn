bl_info = {
    "name": "MBDyn Motion Paths",
    "author": "Andrea Zanoni - <a.zanoni.mbdyn@gmail.com>",
    "version": (0, 5),
    "blender": (2, 65, 0),
    "location": "Properties -> Object -> MBDyn Motion Path",
    "description": "Loads motion file from MBDyn (OpenSource MultiBody Dynamic solver) output. See www.mbdyn.org for more details.",
    "warning": "Alpha stage",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"}
    
import bpy
from bpy.types import Operator, Panel
from bpy.props import BoolProperty, IntProperty, IntVectorProperty, FloatVectorProperty
from bpy.props import StringProperty, BoolVectorProperty, PointerProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Euler

import ntpath, os, csv
import pdb	# <-- Python Debugger

# Nodes Dictionary: contains integer/string labels associations
class MBDynNodesDictionary(bpy.types.PropertyGroup):
    int_label = IntProperty(
            name = "node int label",
            description = "",
            )
    string_label = StringProperty(
            name = "node string label",
            description = ""
            )
    blender_id = StringProperty(
            name = "blender object label",
            description = "",
            default = "none"
            )
            
class MBDynElemOffset(bpy.types.PropertyGroup):
    value = FloatVectorProperty(
        name = "Offset value",
	description = "The offset vector, with respect to the node",
        size = 3
	)

bpy.utils.register_class(MBDynElemOffset)

class MBDynElemProps(bpy.types.PropertyGroup):
    type = StringProperty(
    	name = "MBDyn element type",
	description = "Type of MBDyn element attached to the parent node"
	)
    int_label = IntProperty(
    	name = "MBDyn element integer label",
	description = "Integer label of MBDyn element attached to the parent node"
	)
    offsets = CollectionProperty(
        type = MBDynElemOffset,
	name = "MBDyn element offsets",
        description = "Collector of offsets of element attaching points"
	)

bpy.utils.register_class(MBDynElemProps)

class MBDynElemNodesColl(bpy.types.PropertyGroup):
    int_label = IntProperty(
        name = "MBDyn node ID",
        description = "",
        )

bpy.utils.register_class(MBDynElemNodesColl)

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
    import_function = StringProperty(
        name = "Import operator",
        description = "Id name of the class defining the import operator for the element"
        )
    is_imported = BoolProperty(
        name = "Import flag",
        description = "Flag that is true if the element has been imported in the scene"
        )

bpy.utils.register_class(MBDynNodesDictionary)
bpy.utils.register_class(MBDynElemsDictionary)

# Helper function to strip filename of path
def path_leaf(path):
    head, tail = ntpath.split(path)
    tail1 = (tail or ntpath.basename(head))
    return path.replace(tail1, ''), os.path.splitext(tail1)[0]

## Set scene properties

class MBDynSettingsScene(bpy.types.PropertyGroup):
    # Boolean: is the .mov file loaded properly?
    is_loaded = BoolProperty(
            name = "MBDyn files loaded",
            description = "True if MBDyn files are loaded correctly"
            )
    # MBDyn's imported files path
    file_path = StringProperty(
            name = "MBDyn file path",
            description = "Path of MBDyn's imported files",
            default = '',
            )
    # Base name of MBDyn's imported files
    file_basename = StringProperty(
            name = "MBDyn base file name",
            description = "Base file name of MBDyn's imported files",
            default = "not yet loaded"
            )
    # Number of rows (output time steps * number of nodes) in MBDyn's .mov file
    num_rows = IntProperty(
            name = "MBDyn .mov file number of rows",
            description = "Total number of rows in MBDyn .mov file, corresponding (total time steps * number of nodes)"
            )
    # Load frequency: if different than 1, the .mov file is read every N time steps
    load_frequency = IntProperty(
            name = "frequency",
            description = "If this value is X, different than 1, then the MBDyn output is loaded every X time steps",
            min = 1,
            default = 1
            )
    # Nodes dictionary -- holds the association between MBDyn nodes and blender objects
    nodes_dictionary = CollectionProperty(
            name = "MBDyn nodes collection",
	    type = MBDynNodesDictionary
            )
    # Elements dictionary -- holds the collection of the elements defined in the .log file
    elems_dictionary = CollectionProperty(
            name = "MBDyn elements collection",
            type = MBDynElemsDictionary
            )
    # MBDyn's node count
    num_nodes = IntProperty(
            name = "MBDyn nodes number",
            description = "MBDyn node count"
            )
    # MBDyn's time steps count
    num_timesteps = IntProperty(
            name = "MBDyn time steps",
            description = "MBDyn time steps count"
            )
    # Boolean flag that indicates if the .mov file is loaded correctly and the nodes dictionary is ready,
    # used to indicate that all is ready for the object's to be animated        
    is_ready = BoolProperty(
            name = "ready to animate",
            description = "True if .mov file and nodes dictionary loaded correctly",
            )

def update_parametrization(context):
    # utility renaming
    mbs = context.scene.mbdyn_settings
    obj = context.object
    file_dir = mbs.file_path
    file_basename = mbs.file_basename
    
    # .log file must share the same basename as the .mov file
    log_file = file_dir + file_basename + '.log'
    
    # Try to find node's rotation parametrization in .log file. If not present, assume Euler123
    # Debug message
    print("Reading .log file:", log_file)
    try:
        with open(log_file) as log:
            reader = csv.reader(log, delimiter=' ', skipinitialspace=True)
            for line in log:
                line = next(reader)
                if line[0] == 'structural' and int(line[2]) == obj.mbdyn_settings.int_label:
                    obj.mbdyn_settings.parametrization = line[6]
    except IOError:
        print("Can't find .log file ", log_file)
        pass
    except StopIteration:
        print("End of .log file")
        pass
    return
    
def update_label(self, context):
    # Function to assign MBDyn node to Blender Object
    
    # utility renaming
    obj = context.object
    nd = context.scene.mbdyn_settings.nodes_dictionary
    
    # Debug Messages
    print("MBDynPanel::update_label(): updating MBDyn node associated to object " + obj.name)
    print("MBDynPanel::update_label(): selected MBDyn node = ", str(obj.mbdyn_settings.int_label))
    
    # Search for int label and assign corresponding string label, if found.
    # If not, signal it by assign the "not found" label
    node_string_label = "not_found"
    obj.mbdyn_settings.is_assigned = False
    for item in nd:
        if item.int_label == obj.mbdyn_settings.int_label:
            node_string_label = item.string_label
            item.blender_id = obj.name
            obj.mbdyn_settings.is_assigned = True
    
    obj.mbdyn_settings.string_label = node_string_label
    if obj.mbdyn_settings.is_assigned:
        update_parametrization(context)
    return

class MBDynSettingsObject(bpy.types.PropertyGroup): 
    # Boolean: has the current object being assigned an MBDyn's node?
    is_assigned = BoolProperty(
            name = "MBdyn node ok",
            description = "True if the object has been assigned an MBDyn node",
            )
    # Integer representing MBDyn's node label assigned to the object
    int_label = IntProperty(
            name = "MBDyn node",
            description = "Integer label of MBDyn's node assigned to the object",
            update = update_label
            )
    # String representing MBDyn's node string label assigned to the object. 
    # Non-null only if a .lab file with correct syntax is found
    string_label = StringProperty(
            name = "MBDyn's node or joint string label",
            description = "String label of MBDyn's node assigned to the object (if present)",
            default = "not assigned"
            )
    # Rotation parametrization of node
    parametrization = StringProperty(
            name = "Rotation parametrization",
            description = "Rotation parametrization of node.",
            default = "euler123"
            )
    # Connected elements
    elements = CollectionProperty(
    	    type = MBDynElemProps,
	    description = "Properties of connected elements (if any)"
	    )

bpy.utils.register_class(MBDynSettingsScene)
bpy.utils.register_class(MBDynSettingsObject)

bpy.types.Scene.mbdyn_settings = PointerProperty(type=MBDynSettingsScene)
bpy.types.Object.mbdyn_settings = PointerProperty(type=MBDynSettingsObject)

# Simple function to count number of rows in file
def file_len(filepath):
    with open(filepath) as f:
        for kk, ll in enumerate(f):
            pass
    return kk + 1

def reset_nodes_dict():
    bpy.context.scene.mbdyn_settings.nodes_dictionary.clear()
    return

# Function that populates the nodes dictionary
def create_nodes_dict(file_dir, file_basename):
    
    # reset nodes dictionary first
    reset_nodes_dict()
    
    # .lab file must share the same basename as the .mov file -- TODO: allow for different filenames?
    mov_file = file_dir + file_basename + '.mov'
    lab_file = file_dir + file_basename + '.lab'
    
    # Utility rename
    context = bpy.context
    
    # Initial loop to find MBDyn's nodes - default labels
    # Debug message
    print("Reading node list from file: ", mov_file) 
    
    with open(mov_file) as mf:
        # open the reader, skipping initial whitespaces
        reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
        
        # get first node label
        rw = next(reader)
        first_node = int(rw[0])
        ndi = context.scene.mbdyn_settings.nodes_dictionary.add()
        ndi.int_label = first_node
        ndi.string_label = 'Node_1'
        
        # get the remaining ones
        done = False
        kk = 1
        while not done:
            rw = next(reader)
            curr_node = int(rw[0])
            if first_node != curr_node:
                kk = kk + 1
                ndi = context.scene.mbdyn_settings.nodes_dictionary.add()
                ndi.int_label = curr_node
                ndi.string_label = 'Node_' + str(kk)
            else:
                done = True
       
        context.scene.mbdyn_settings.num_nodes = kk;
               
    # Try to find string labels in .lab file
    # Debug message -- gets printed on console (TODO: feedback the user)
    print("Reading node labels from file: ", lab_file)
    set_strings = ["set: const integer Node_", "set: integer Node_", "set: const integer node_", "set: integer node_"]
    try: 
        with open(lab_file) as lf:
            for line in lf:
                for set_string in set_strings:
                    if set_string in line:
                        line_str = line.rstrip()
                        eq_idx = line_str.find('=') + 1
                        node_label_int = int(line_str[eq_idx:-1].strip())
                        node_label_str = line_str[len(set_string):(eq_idx - 1)].strip()
                        for item in context.scene.mbdyn_settings.nodes_dictionary:
                            if node_label_int == item.int_label:
                                item.string_label = node_label_str
    except IOError:
	# TODO: warn the user through the Blender interface that the file is not found
        print("Can't find labels file {}, using default node labeling...".format(lab_file)) 
        pass
                    
    context.scene.mbdyn_settings.is_ready = True
    
    # Debug message
    print("Nodes dictionary:")
    for item in context.scene.mbdyn_settings.nodes_dictionary:
        print(item.int_label, '\t{}'.format(item.string_label))

# Function that parses the single row of the .log file and stores
# the element definition in elems_dictionary
def parse_joint(context, jnt_type, rw):
    objects = context.scene.objects
    ed = context.scene.mbdyn_settings.elems_dictionary

    # helper function to parse rod joints
    def parse_rodj():
        # Debug message
        print("parse_rodj(): Parsing rod " + rw[1])
        el = None
        for elem in ed:
            if elem.int_label == int(rw[1]) and elem.type == 'rod':
                # Debug message
                print("parse_rodj(): found existing entry in elements dictionary. Updating it.")
                el = elem
                el.nodes[0].int_label = int(rw[2])
                el.nodes[1].int_label = int(rw[6])
                el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
                el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
        if el == None:
            print("parse_rodj(): didn't find entry in elements dictionary. Creating one.")
            el = ed.add()
            el.type = 'rod'
            el.int_label = int(rw[1])
            el.nodes.add()
            el.nodes[0].int_label = int(rw[2])
            el.offsets.add()
            el.offsets[0].value = Vector(( float(rw[3]), float(rw[4]), float(rw[5]) ))
            el.nodes.add()
            el.nodes[1].int_label = int(rw[6])
            el.offsets.add()
            el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
            el.import_function = "imp_mbdyn_elem.rod"
            
    # helper function to parse rod bezier joint
    def parse_rodbezj():
        el = None
        for elem in ed:
            if elem.int_label == int(rw[2]) and elem.type == 'rod bezier':
                el = elem
                el.nodes[0].int_label = int(rw[3])
                el.nodes[1].int_label = int(rw[10])
                el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
                el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
                el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
                el.offsets[3].value = Vector(( float(rw[14]), float(rw[15]), float(rw[16]) ))
        if el == None:
            el = ed.add()
            el.type = 'rod'
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
            el.import_function = "imp_mbdyn_elem.rodbez"
            
    joint_types  = {    'rod' : parse_rodj,
                        'rod bezier' : parse_rodbezj}
 
    try:
        joint_types[jnt_type]()
    except KeyError:
        print("Element type " + jnt_type + " not implemented yet. Skipping")
        pass
# end of parse_joint() function ----

# Function that parses the .log file and calls parse_joints() to add elements
# to the elements dictionary
# TODO: support more joint types
def parse_log_file(context):

    # utility rename
    context = bpy.context
    mbs = context.scene.mbdyn_settings
    log_file = mbs.file_path + mbs.file_basename + '.log'

    # Debug message to console
    print("parse_log_file(): Reading elements from file: " + log_file)
    try:
        with open(log_file) as lf:
            # open the reader, skipping initial whitespaces
            reader = csv.reader(lf, delimiter=' ', skipinitialspace=True)
        
            for rw in lf:
                # get the next row
                rw = next(reader)
            
                jnt_type = rw[0]
                ii = 0
            
                while (rw[ii][-1] != ':') and (ii < min(3, (len(rw) - 1))):
                    ii = ii + 1
                    jnt_type = jnt_type + " " + rw[ii]
            
                if ii == len(rw):
                    print("parse_log_file(): row does not contain an element definition. Skipping...")
                else:
                    print("parse_log_file(): Found " + jnt_type + " element.")
                    parse_joint(context, jnt_type[:-1], rw)
    except IOError:
        # TODO: Warn the user!
        print("Could not locate the file " + log_file + ".")
        pass
    except StopIteration:
        print("Reached the end of .log file")
        pass
    return {'FINISHED'}
 
# Function to set global .mov file data
def read_mbdyn_data(context, filepath):
    
    # Debug console output
    print("Reading from file", filepath)
    
    # Row count
    fl = file_len(filepath)
    
    # Debug message
    print("File {} has {} rows".format(filepath, str(fl)))   
    
    # Setting of global (scene) properties
    context.scene.mbdyn_settings.is_active = True
    file_dir, file_basename = path_leaf(filepath)
    
    # Populates the nodes dictionary
    create_nodes_dict(file_dir, file_basename)    
    
    context.scene.mbdyn_settings.file_basename = file_basename
    context.scene.mbdyn_settings.file_path = file_dir
    context.scene.mbdyn_settings.num_rows = fl
    context.scene.mbdyn_settings.num_timesteps = fl/context.scene.mbdyn_settings.num_nodes
    
    
    return {'FINISHED'}
        
class MBDynImportMotionPath(Operator, ImportHelper):
    """ Helper class to set MBDyn's files path in Toolbar Panel """
    
    bl_idname = "import.import_path_from_mbdyn"
    bl_label = "MBDyn Motion Path Importer"
    
    filename_ext = ".mov"
    
    filter_glob = StringProperty(
            default = "*.mov",
            options = {'HIDDEN'},
            )
        
    def execute(self, context):
        return read_mbdyn_data(context, self.filepath)
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return{'RUNNING_MODAL'}

def set_obj_locrot(obj, rw):
    
    # Position
    obj.location[0] = float(rw[1])
    obj.location[1] = float(rw[2])
    obj.location[2] = float(rw[3])
    
    # Orientation
    parametrization = obj.mbdyn_settings.parametrization
    # Debug message
    print('Updating rotation of object', obj.name)
    
    if parametrization == 'euler123':
        obj.rotation_euler = Euler((float(rw[4]), float(rw[5]), float(rw[6])), 'XYZ')
    elif parametrization == 'matrix':
        ## WARNING: not implemented yet
        pass
    elif parametrization == 'phi':
        rotvec = Vector((float(rw[4]), float(rw[5]), float(rw[6])))
        rotvec_norm = rotvec.normalized()
        print(str(rotvec.magnitude), str(rotvec_norm[0]), str(rotvec_norm[1]), str(rotvec_norm[2]))
        obj.rotation_axis_angle = Vector((rotvec.magnitude, rotvec_norm[0], rotvec_norm[1], rotvec_norm[2]))
        pass
    else:
        print("Error: not recognised rotation parametrization")
    
    bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot')
    
    return

# Function that parses the .mov file and sets the motion paths
def set_motion_paths(context):
    # Debug message
    print("Setting Motion Paths...")
    
    # utility renaming
    scene = context.scene
    mbs = scene.mbdyn_settings
    
    # .mov filename
    mov_file = mbs.file_path + mbs.file_basename + '.mov'
    
    # Debug message
    print("Reading from file:", mov_file)
   
    # total number of frames to be animated
    num_frames = int(mbs.num_rows/mbs.num_nodes)
    scene.frame_end = int(num_frames/mbs.load_frequency)

    # list of animatable Blender object types
    anim_types = ['MESH', 'ARMATURE', 'EMPTY']    

    # main loop
    if  mbs.is_ready:
        with open(mov_file) as mf:
            
            # open the reader, skipping initial whitespaces
            reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
            
            # main for loop, from start frame to last 
            for frame in range(scene.frame_end):
                scene.frame_current = (frame + 1)
                for node in range(mbs.num_nodes):
                    rw = next(reader)
                    # cycle animatable objects and set their location and rotation parameters
                    for obj in bpy.data.objects:
                        if (obj.type in anim_types) and obj.mbdyn_settings.is_assigned and int(rw[0]) == obj.mbdyn_settings.int_label:
                            # make sure that the object is selected
                            obj.select = True
                            # set object location and orientation and insert keyframe
                            set_obj_locrot(obj, rw)
                        else:
                            pass
                if mbs.load_frequency > 1:
                    for ii in range(1, (mbs.load_frequency - 1)*mbs.num_nodes):
                        rw = next(reader)
                
    else:
        # TODO - Print message in notification bar
        print("Error: .mov file not loaded")
    
    return {'FINISHED'}

class MBDynSetMotionPaths(Operator):
    """ Sets the motion path for all the objects that have an assigned MBDyn's node """
    bl_idname = "animate.set_mbdyn_motion_path"
    bl_label = "MBDyn Motion Path setter"
    
    def execute(self, context):
        return set_motion_paths(context)
    
    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynSetMotionPaths)

class MBDynReadLog(Operator):
    """ Imports MBDyn elements by parsing the .log file """
    bl_idname = "animate.read_mbdyn_log_file"
    bl_label = "MBDyn .log file parsing"

    def execute(self, context):
        return parse_log_file(context)

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynReadLog)

class MBDynImportPanel(Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    
    bl_label = "MBDyn Motion Path"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    
    def draw(self, context):
        
        # utility renaming        
        layout = self.layout
        obj = context.object
        sce = context.scene

        # MBDyn file import
        row = layout.row()
        row.label(text="Import motion path from MBDyn")
        col = layout.column(align=True)
        col.operator(MBDynImportMotionPath.bl_idname, text="Select .mov file")
        col.prop(sce.mbdyn_settings, "load_frequency")
        
        # Display MBDyn file basename and info
        row = layout.row()
        row.label(text="MBDyn files basename:")
        col = layout.column(align=True)
        col.prop(sce.mbdyn_settings, "file_basename", text="")
        col.prop(sce.mbdyn_settings, "num_nodes", text="# of nodes")
        col.prop(sce.mbdyn_settings, "num_rows", text="# of rows")
        col.prop(sce.mbdyn_settings, "num_timesteps", text="# of time steps")
        col.enabled = False
        
        # Display the active object 
        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        
        row = layout.row()
        row.label(text="MBDyn's node label:")
        
        col = layout.column(align=True)
        col.prop(obj.mbdyn_settings, "string_label", text="")
        col.prop(obj.mbdyn_settings, "int_label")
        col.prop(obj.mbdyn_settings, "parametrization", text="")

        # Insert elements -- EXPERIMENTAL
        col = layout.column(align=True)
        col.label(text = "Load elements from .log file")
        col.operator(MBDynReadLog.bl_idname, text = "LOAD ELEMENTS")

        # Insert keyframes for animation
        col = layout.column(align=True)
        col.label(text = "Start animating")
        col.operator(MBDynSetMotionPaths.bl_idname, text = "ANIMATE")


class MBDynImportElement(bpy.types.Panel):
    bl_label = "MBdyn elements"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene
        mbs = scene.mbdyn_settings

        layout = self.layout
        layout.alignment = 'LEFT'

        ed = mbs.elems_dictionary
        row = layout.row()

        # TODO: add element label
        row.label("Element #")
        row.label("Element type")
        row.label("")

        # FIXME: rod bezier not recognised properly
        for elem in ed:
            row = layout.row()
            row.label(str(elem.int_label))
            row.label(elem.type)
            if elem.is_imported:
                row.operator(elem.import_function, text = "RE-IMPORT").int_label = elem.int_label
            else:
                row.operator(elem.import_function, text = "IMPORT").int_label = elem.int_label

class MBDynImportElemRod(bpy.types.Operator):
    bl_idname = "imp_mbdyn_elem.rod"
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
                if elem.is_imported:
                    # TODO: ask for user acceptance and replace
                    print("Element is already imported. Remove it manually before updating it.")
                    return{'CANCELLED'}
                else:
                    n1 = "none"
                    n2 = "none"
                    
                    # try to find Blender objects associated with the nodes that the element connects
                    for node in nd:
                        if elem.nodes[0].int_label == node.int_label:
                            n1 = node.blender_id
                        elif elem.nodes[1].int_label == node.int_label:
                            n2 = node.blender_id
                    if n1 == "none":
                        # TODO: warn the user through the Blender interface
                        print("MBDynImportElemRod(): Could not find a Blender object associated to Node " + str(elem.int_label))
                        return{'CANCELLED'}
                    elif n2 == "none":
                        print("MBDynImportElemRod(): Could not find a Blender object associated to Node " + str(elem.int_label))
                        return{'CANCELLED'}

                    # creation of line representing the rod
                    rodcv_id = "rod_" + str(elem.int_label) + "_cvdata"
                    # check if curve is already present. If it is, remove it. FIXME: may be dangerous
                    if rodcv_id in bpy.data.curves.keys():
                        bpy.data.curves.remove(rodcv_id)
                    cvdata = bpy.data.curves.new(rodcv_id, type = 'CURVE')
                    cvdata.dimensions = '3D'
                    polydata = cvdata.splines.new('POLY')
                    polydata.points.add(1)
                    f1 = elem.offsets[0].value
                    f2 = elem.offsets[1].value
                    polydata.points[0].co = bpy.data.objects[n1].matrix_world*Vector(( f1[0], f1[1], f1[2], 1.0 ))
                    polydata.points[1].co = bpy.data.objects[n2].matrix_world*Vector(( f2[0], f2[1], f2[2], 1.0 ))
                    rodOBJ = bpy.data.objects.new("rod_" + str(elem.int_label), cvdata)
                    bpy.context.scene.objects.link(rodOBJ)
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

class MBDynImportElemRodBez(bpy.types.Operator):
    bl_idname = "imp_mbdyn_elem.rodbez"
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
                if elem.is_imported:
                    # TODO: ask for user acceptance and replace
                    print("Element is already imported. Remove it manually before updating it.")
                    return{'CANCELLED'}
                else:
                    n1 = "none"
                    n2 = "none"
                    
                    # try to find Blender objects associated with the nodes that the element connects
                    for node in nd:
                        if elem.nodes[0].int_label == node.int_label:
                            n1 = node.blender_id
                        elif elem.nodes[1].int_label == node.int_label:
                            n2 = node.blender_id
                    if n1 == "none":
                        # TODO: warn the user through the Blender interface
                        print("MBDynImportElemRod(): Could not find a Blender object associated to Node " + str(elem.int_label))
                        return{'CANCELLED'}
                    elif n2 == "none":
                        print("MBDynImportElemRod(): Could not find a Blender object associated to Node " + str(elem.int_label))
                        return{'CANCELLED'}

                    # creation of line representing the rod
                    rodcv_id = "rod_bezier_" + str(elem.int_label) + "_cvdata"
                    # check if curve is already present. If it is, remove it. FIXME: may be dangerous
                    if rodcv_id in bpy.data.curves.keys():
                        bpy.data.curves.remove(rodcv_id)
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
                    rodOBJ.select = True

                    ## hooking of the line ends to the Blender objects
                    
                    # deselect all objects (guaranteed by previous the selection of rodOBJ)
                    bpy.ops.object.select_all()
                    
                    # select rod, set it to active and enter edit mode
                    rodOBJ.select = True
                    bpy.context.scene.objects.active = rodOBJ
                    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)

                    # select first control point and its handles and object 1,
                    # then set the hook and deselect object of node 1
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_control_point = True
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_left_handle = True
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[0].select_right_handle = True
                    bpy.data.objects[n1].select = True
                    bpy.ops.object.hook_add_selob()
                    bpt.ops.object.select_all()

                    # select first control point and its handles and object 2,
                    # then set the hook and deselect object of node 2
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_control_point = True
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_left_handle = True
                    bpy.data.curves[rodcv_id].splines[0].bezier_points[1].select_right_handle = True
                    bpy.data.objects[n2].select = True
                    bpy.ops.object.hook_add_selob()
                    bpt.ops.object.select_all()

                    # exit edit mode and deselect all
                    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
                    bpy.ops.object.select_all()

                    elem.is_imported = True
                    return{'FINISHED'}

class MBDynOBJNodeSelect(bpy.types.Panel):
    bl_label = "MBdyn nodes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        obj = context.object
        mbs = context.scene.mbdyn_settings
        
        layout = self.layout
        layout.alignment = 'LEFT'
        
        nd = mbs.nodes_dictionary
        row = layout.row()
        row.label("Node #")
        row.label("Node label")
        row.label("Blender Object")
        row.label("")
        for nd_entry in nd:
            row = layout.row()
            row.label(str(nd_entry.int_label))
            row.label(nd_entry.string_label)
            if nd_entry.blender_id == obj.name:
                row.label(nd_entry.blender_id, icon = "OBJECT_DATA")
            else:
                row.label(nd_entry.blender_id)
            row.operator("sel.mbdynnode", text="SELECT").int_label = nd_entry.int_label
        
class MBDynOBJNodeSelectButton(bpy.types.Operator):
    bl_idname = "sel.mbdynnode"
    bl_label = "MBDyn Node Sel Button"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        context.object.mbdyn_settings.int_label = self.int_label
        for item in context.scene.mbdyn_settings.nodes_dictionary:
            if self.int_label == item.int_label:
                item.blender_id = context.object.name
        # DEBUG message to console
        print("Object " + context.object.name + " MBDyn node association updated to node " + str(context.object.mbdyn_settings.int_label))
        return{'FINISHED'}

def register():
    bpy.utils.register_class(MBDynImportMotionPath)
    bpy.utils.register_class(MBDynImportPanel)
    bpy.utils.register_class(MBDynOBJNodeSelect)
    bpy.utils.register_class(MBDynOBJNodeSelectButton)
    bpy.utils.register_class(MBDynImportElement)
    bpy.utils.register_class(MBDynImportElemRod)
    bpy.utils.register_class(MBDynImportElemRodBez)

def unregister():
    bpy.utils.unregister_class(MBDynNodesDictionary)
    bpy.utils.unregister_class(MBDynElemsDictionary)
    bpy.utils.unregister_class(MBDynElemOffset)
    bpy.utils.unregister_class(MBDynElemProps)
    bpy.utils.unregister_class(MBDynElemNodesColl)
    bpy.utils.unregister_class(MBDynSettingsScene)
    bpy.utils.unregister_class(MBDynSettingsObject)
    bpy.utils.unregister_class(MBDynSetMotionPaths)
    bpy.utils.unregister_class(MBDynReadLog)
    bpy.utils.unregister_class(MBDynImportPanel)
    bpy.utils.unregister_class(MBDynImportMotionPath)
    bpy.utils.unregister_class(MBDynOBJNodeSelect)
    bpy.utils.unregister_class(MBDynOBJNodeSelectButton)
    bpy.utils.unregister_class(MBDynImportElement)
    bpy.utils.unregister_class(MBDynImportElemRod)
    bpy.utils.unregister_class(MBDynImportElemRodBez)
        
if __name__ == "__main__":
    register()
