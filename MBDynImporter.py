bl_info = {
    "name": "MBDyn Motion Paths Importer",
    "author": "Andrea Zanoni - <andrea.zanoni@polimi.it>",
    "version": (1, 1),
    "blender": (2, 65, 0),
    "location": "View3D -> Animation -> MBDyn Motion Path",
    "description": "Imports simulation results of MBDyn (OpenSource MultiBody Dynamic solver) output. See www.mbdyn.org for more details.",
    "warning": "Beta stage",
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
from collections import namedtuple
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
    blender_object = StringProperty(
            name = "blender object label",
            description = "",
            default = "none"
            )
            
class MBDynElemOffset(bpy.types.PropertyGroup):
    value = FloatVectorProperty(
        name = "Offset value",
	description = "The offset vector, with respect to the node",
        size = 3,
        precision = 6
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
    update_operator = StringProperty(
        name = "Update operator",
        description = "Id name of the operator that updates the element info using the current position of the blender objects representing it",
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
    
    # Try to find node's rotation parametrization in .log file.
    # Debug message
    print("Reading .log file:", log_file)

    axes = {'1': 'X', '2': 'Y', '3': 'Z'}
    ret_val = ''
    try:
        with open(log_file) as log:
            reader = csv.reader(log, delimiter=' ', skipinitialspace=True)
            for line in log:
                line = next(reader)
                if line[0] == 'structural' and int(line[2]) == obj.mbdyn_settings.int_label:
                    obj.mbdyn_settings.parametrization = line[6]
                    if line[6] == 'phi':
                        obj.rotation_mode = 'AXIS_ANGLE'
                    elif line[6][0:5] == 'euler':
                        obj.rotation_mode = axes[line[6][5]] + axes[line[6][6]] + axes[line[6][7]] 
                    else:
                        print("update_parametrization(): rotation parametrization not supported (yet...)!")
                        ret_val = 'ROT_NOT_SUPPORTED'

    except IOError:
        print("Can't find .log file ", log_file)
        ret_val = 'LOG_NOT_FOUND'
        pass
    except StopIteration:
        print("End of .log file")
        ret_val = 'FINISHED'
        pass

    return ret_val
    


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
            item.blender_object = obj.name
            obj.mbdyn_settings.is_assigned = True
    
    obj.mbdyn_settings.string_label = node_string_label
    if obj.mbdyn_settings.is_assigned:
        ret_val = update_parametrization(context)

    if ret_val == 'ROT_NOT_SUPPORTED':
        self.report({'ERROR'}, "Rotation parametrization not supported, node " \
            + obj.mbdyn_settings.string_label)
    elif ret_val == 'LOG_NOT_FOUND':
        self.report({'ERROR'}, "MBDyn .log file not found")
    
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
    # NOTE: .lab file must share the same basename as the .mov file 
    mov_file = file_dir + file_basename + '.mov'
    lab_file = file_dir + file_basename + '.lab'
    
    # Utility rename
    context = bpy.context
    
    # Named tuple list to temporarily hold the nodes structure
    # found in the .mov file
    Node = namedtuple('Node', ['int_label', 'string_label', 'found'])
    nodes = []

    # Initial loop to find MBDyn's nodes - default labels
    # Debug message
    print("Reading node list from file: ", mov_file) 
    
    with open(mov_file) as mf:
        # open the reader, skipping initial whitespaces
        reader = csv.reader(mf, delimiter=' ', skipinitialspace=True)
        
        # get first node label
        rw = next(reader)
        first_node = int(rw[0])
        
        nodes.append(Node(first_node, 'Node_' + str(first_node), False))
        
        # get the remaining ones
        done = False
        while not done:
            rw = next(reader)
            curr_node = int(rw[0])
            if first_node != curr_node:
                nodes.append(Node(curr_node, 'Node_' + str(curr_node), False))
            else:
                done = True

    # if nodes_dictionary is not empty, check for consistency
    nodes_dict = context.scene.mbdyn_settings.nodes_dictionary
    nn = len(nodes_dict)
    if nn:  
        # Debug message
        print("create_nodes_dict(): dictionary already exists in scene.")
        print("create_nodes_dict(): Checking .mov file consistency.")
        if nn == len(nodes):
            for ii in range(len(nodes)):
                for item in nodes_dict:
                    if item.int_label == nodes[ii].int_label:
                        nodes[ii] = nodes[ii]._replace(found=True)
            if all(node.found == True for node in nodes):
                # OK - Model node list has not changed (hopefully)
                # TODO: Inform the user
                print("create_nodes_dict(): .mov file seems consistent with scene dictionary.")
            else:
                print("create_nodes_dict(): ERROR - .mov file is not consistent with scene dictionary")
                return 'MODEL_HAS_CHANGED'
    else:
        for node in nodes:
            ndi = nodes_dict.add()
            ndi.int_label = node.int_label
            ndi.name = "node_" + str(int_label)
            ndi.string_label = node.string_label 

    # Try to find string labels in .lab file
    print("create_nodes_dict(): Reading node labels from file: ", lab_file)
    set_strings = ["set: const integer Node_", \
                   "set: integer Node_", \
                   "set: const integer node_", \
                   "set: integer node_"]
    labels = 'FILE'
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
                                if item.string_label != node_label_str:
                                    print("create_nodes_dictionary(): WARNING "\
                                        "- String label of node " + str(item.int_label) + \
                                        " changed from '" + item.string_label + "' to " +\
                                        node_label_str)
                                    labels = 'FILE_UPDATED'
                                item.string_label = node_label_str
    except IOError:
        print("create_nodes_dict(): Can't find labels file {}, \
                using default node labeling...".format(lab_file))
        labels = 'DEFAULT'
        pass
                    
    context.scene.mbdyn_settings.is_ready = True
    
    # Debug message
    print("Nodes dictionary:")
    for item in context.scene.mbdyn_settings.nodes_dictionary:
        print(item.int_label, '\t{}'.format(item.string_label))

    return labels


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
            el.name = el.type + "_" + str(el.int_label)
            
    # helper function to parse rod bezier joint
    def parse_rodbezj():
        # Debug message
        print("parse_rodbezj(): Parsing rod bezier " + rw[1])
        el = None
        for elem in ed:
            if elem.int_label == int(rw[2]) and elem.type == 'rod bezier':
                # Debug message
                print("parse_rodbezj(): found existing entry in elements dictionary.\
                    Updating it.")
                el = elem
                el.nodes[0].int_label = int(rw[3])
                el.nodes[1].int_label = int(rw[10])
                el.offsets[0].value = Vector(( float(rw[4]), float(rw[5]), float(rw[6]) ))
                el.offsets[1].value = Vector(( float(rw[7]), float(rw[8]), float(rw[9]) ))
                el.offsets[2].value = Vector(( float(rw[11]), float(rw[12]), float(rw[13]) ))
                el.offsets[3].value = Vector(( float(rw[14]), float(rw[15]), float(rw[16]) ))
        if el == None:
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
            el.import_function = "imp_mbdyn_elem.rodbez"
            el.info_draw = "rodbez_info_draw"
            el.update_operator = "update.rodbez"
            el.name = el.type + "_" + str(el.int_label)

    joint_types  = {    "rod" : parse_rodj,
                        "rod bezier" : parse_rodbezj}
 
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

    # clear elements dictionary first
    mbs.elems_dictionary.clear()

    # Debug message to console
    print("parse_log_file(): Trying to read elements from file: " + log_file)
    ret_val = { 'FINISHED' }
    try:
        with open(log_file) as lf:
            # open the reader, skipping initial whitespaces
            reader = csv.reader(lf, delimiter=' ', skipinitialspace=True)
        
            jnt_type = ""
            while jnt_type[:-1] != "Symbol table":
                # get the next row
                rw = next(reader)
            
                jnt_type = rw[0]
                ii = 0
            
                while (rw[ii][-1] != ':') and (ii < min(3, (len(rw) - 1))):
                    ii = ii + 1
                    jnt_type = jnt_type + " " + rw[ii]
            
                if ii == min(3, (len(rw) - 1)):
                    print("parse_log_file(): row does not contain an element definition. Skipping...")
                else:
                    print("parse_log_file(): Found " + jnt_type[:-1] + " element.")
                    parse_joint(context, jnt_type[:-1], rw)
    except IOError:
        print("Could not locate the file " + log_file + ".")
        ret_val = {'CANCELLED'}
        pass
    except StopIteration:
        print("Reached the end of .log file")
        ret_val = {'FINISHED'}
        pass
        
    
    return ret_val


# Function to set global .mov file data
def read_mbdyn_data(context, filepath):
    
    # Debug console output
    print("Reading from file", filepath)
    
    # Row count
    fl = file_len(filepath)
    
    # Debug message
    print("File {} has {} rows".format(filepath, str(fl)))   
    
    # Setting of global (scene) properties
    file_dir, file_basename = path_leaf(filepath)
    
    # Populates the nodes dictionary
    retval = create_nodes_dict(file_dir, file_basename)
    
    mbs = context.scene.mbdyn_settings

    mbs.file_basename = file_basename
    mbs.file_path = file_dir
    mbs.num_rows = fl
    mbs.num_nodes = len(mbs.nodes_dictionary)
    mbs.num_timesteps = fl/mbs.num_nodes
 
    return retval
        
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
        retval = read_mbdyn_data(context, self.filepath)
        if retval == 'MODEL_HAS_CHANGED':
            self.report({'ERROR'}, "MBDyn .mov file is not consistent with scene settings!")
            return {'CANCELLED'}
        if retval == 'DEFAULT':
            self.report({'WARNING'}, "MBDyn .lab file not found: using default labels")
        elif retval == 'FILE':
            self.report({'INFO'}, "MBDyn node labels read from .lab file")
        elif retval == 'FILE_UPDATED':
            self.report({'WARNING'}, ".lab file contains different labeling with respect to scene data")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return{'RUNNING_MODAL'}

def set_obj_locrot(obj, rw):
   
    axes = {'1': 'X', '2': 'Y', '3': 'Z'}

    # Position
    obj.location[0] = float(rw[1])
    obj.location[1] = float(rw[2])
    obj.location[2] = float(rw[3])
    
    # Orientation
    parametrization = obj.mbdyn_settings.parametrization
    # Debug message
    print('Updating rotation of object', obj.name)
    
    if parametrization[0:5] == 'euler':
        euler_seq = axes[parametrization[5]] + axes[parametrization[6]] + axes[parametrization[7]]
        obj.rotation_euler = Euler((float(rw[4]), float(rw[5]), float(rw[6])), euler_seq)
    elif parametrization == 'phi':
        rotvec = Vector((float(rw[4]), float(rw[5]), float(rw[6])))
        rotvec_norm = rotvec.normalized()
        print(str(rotvec.magnitude), str(rotvec_norm[0]), str(rotvec_norm[1]), str(rotvec_norm[2]))
        obj.rotation_axis_angle = Vector((rotvec.magnitude, rotvec_norm[0], rotvec_norm[1], rotvec_norm[2]))
        pass
    else:
        print("Error: rotation parametrization not supported (yet...)")
    
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
        return{'CANCELLED'}
    
    return {'FINISHED'}

class MBDynClearData(Operator):
    """ Clears MBDyn elements and nodes dictionaries, essentially 'cleaning' the scene """
    bl_idname = "mbdyn.cleardata"
    bl_label = "Clear MBDyn Data"

    def execute(self, context):
        context.scene.mbdyn_settings.nodes_dictionary.clear()
        context.scene.mbdyn_settings.elems_dictionary.clear()
        self.report({'INFO'}, "Scene MBDyn data cleared.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynClearData)

class MBDynSetMotionPaths(Operator):
    """ Sets the motion path for all the objects that have an assigned MBDyn's node """
    bl_idname = "animate.set_mbdyn_motion_path"
    bl_label = "MBDyn Motion Path setter"
    
    def execute(self, context):
        ret_val = set_motion_paths(context)
        if ret_val == 'CANCELLED':
            self.report({'WARNING'}, "MBDyn. mov file not loaded")
        return ret_val

    
    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynSetMotionPaths)

class MBDynReadLog(Operator):
    """ Imports MBDyn elements by parsing the .log file """
    bl_idname = "animate.read_mbdyn_log_file"
    bl_label = "MBDyn .log file parsing"

    def execute(self, context):
        ret_val = parse_log_file(context)
        if ret_val == { 'CANCELLED' }:
            self.report({'ERROR'}, "MBDyn .log file not found")
        return  ret_val 

    def invoke(self, context, event):
        return self.execute(context)

bpy.utils.register_class(MBDynReadLog)

def elem_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
    col = layout.column(align=True)
    kk = 0
    for elnode in elem.nodes:
        kk = kk + 1
        for node in nd:
             if node.int_label == elnode.int_label:
                col.prop(node, "int_label", \
                    text = "Node " + str(kk) + " ID: ")
                col.prop(node, "string_label", \
                    text = "Node " + str(kk) + " label: ")
                col.prop(node, "blender_object", \
                    text = "Node " + str(kk) + " Object: ")
                col.enabled = False
    
    kk = 0
    for off in elem.offsets:
        kk = kk + 1
        row = layout.row()
        row.label(text = "offset " + str(kk))
        col = layout.column(align = True)
        col.prop(off, "value", text = "")
        col.enabled = False

# -----------------------------------------------------------
# end of elem_info_draw(elem, layout) function

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
                RN1 = bpy.data.objects[node.blender_object].matrix_world.to_3x3()
                fN1 = bpy.data.objects[node.blender_object].location
                elem.offsets[0]['value'] = RN1.transposed()*(fN1 - fOG)
    
                # node 1 offset 2
                fAG = cvdata.bezier_points[0].handle_right
                elem.offsets[1]['value'] = RN1.transposed()*(fN1 - fAG) 
        
            elif node.int_label == elem.nodes[1].int_label:
    
                # node 2 offset 1
                fBG = cvdata.bezier_points[1].handle_left
                RN2 = bpy.data.objects[node.blender_object].matrix_world.to_3x3()
                fN2 = bpy.data.objects[node.blender_object].location
                elem.offsets[2]['value'] = RN2.transposed()*(fN2 - fBG)
    
                # offset 2
                fIG = cvdata.bezier_points[1].co
                elem.offsets[3]['value'] = RN2.transposed()*(fN2 - fIG)
        return{'FINISHED'}
# -----------------------------------------------------------
# end of RodBezUpdate class

bpy.utils.register_class(RodBezUpdate)

def rodbez_info_draw(elem, layout):
    nd = bpy.context.scene.mbdyn_settings.nodes_dictionary
    row = layout.row()
    col = layout.column(align=True)
    
    # curve data for blender object representing the element
    cvdata = bpy.data.curves[elem.blender_object + "_cvdata"].splines[0]

    for node in nd:
        if node.int_label == elem.nodes[0].int_label:
 
            # Display node 1 info
            col.prop(node, "int_label", \
                    text = "Node 1 ID ")
            col.prop(node, "string_label", \
                    text = "Node 1 label ")
            col.prop(node, "blender_object", \
                    text = "Node 1 Object: ")
            col.enabled = False

            # Display first offset of node 1 info
            row = layout.row()
            row.label(text = "offset 1 in Node " \
                    + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[0], "value", text = "")
            col.enabled = False

            # Display second offset of node 1 info
            row = layout.row()
            row.label(text = "offset 2 in Node " \
                    + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[1], "value", text = "")
            col.enabled = False
            
            layout.separator()

        elif node.int_label == elem.nodes[1].int_label:
            
            # Display node 2 info
            row = layout.row()
            col = layout.column(align = True)
            col.prop(node, "int_label", \
                    text = "Node 2 ID ")
            col.prop(node, "string_label", \
                    text = "Node 2 label ")
            col.prop(node, "blender_object", \
                    text = "Node 2 Object: ")
            col.enabled = False

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 1 in Node " \
                    + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[2], "value", text = "")
            col.enabled = False

            # Display first offset of node 2 info
            row = layout.row()
            row.label(text = "offset 2 in Node " \
                    + node.string_label + " R.F.")
            col = layout.column(align = True)
            col.prop(elem.offsets[3], "value", text = "")
            col.enabled = False

            layout.separator()
# -----------------------------------------------------------
# end of rodbez_info_draw(elem, layout) function


class MBDynImportPanel(Panel):
    """ Imports results of MBDyn simulation - Toolbar Panel """
    bl_idname = "VIEW3D_TL_MBDyn_ImportPath" 
    bl_label = "MBDyn Motion Paths"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'Animation'
    
    def draw(self, context):
        
        # utility renaming        
        layout = self.layout
        obj = context.object
        sce = context.scene
        nd = sce.mbdyn_settings.nodes_dictionary
        ed = sce.mbdyn_settings.elems_dictionary

        # MBDyn file import
        row = layout.row()
        row.label(text="Import motion path from MBDyn")
        col = layout.column(align = True)
        col.operator(MBDynImportMotionPath.bl_idname, text="Select .mov file")
        col.prop(sce.mbdyn_settings, "load_frequency")

        # Clear MBDyn data for scene
        row = layout.row()
        row.label(text="Clear MBDyn data for scene")
        col = layout.column(align = True)
        col.operator(MBDynClearData.bl_idname, text = "CLEAR MBDYN DATA")

        

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
        try:
            row.label(text="Active object is: " + obj.name)

            if any(item.blender_object == obj.name for item in nd):

                # Display MBDyn node info
                row = layout.row()
                row.label(text = "MBDyn's node label:")
        
                # Select MBDyn node
                col = layout.column(align=True)
                col.prop(obj.mbdyn_settings, "string_label", text="")
                col.prop(obj.mbdyn_settings, "int_label")
                col.prop(obj.mbdyn_settings, "parametrization", text="")

            else:
                for elem in ed:
                    if elem.blender_object == obj.name:
                        # Display MBDyn elements info
                        row = layout.row()
                        row.label(text = "MBDyn's element info:")
                        eval(elem.info_draw + "(elem, layout)")
                        if elem.update_operator != 'none' and elem.is_imported == True:
                            row = layout.row()
                            row.operator(elem.update_operator, \
                                    text="UPDATE").elem_key = elem.name
        except AttributeError:
            row.label(text="No active objects")
            pass

        # Load elements
        col = layout.column(align=True)
        col.label(text = "Load elements from .log file")
        col.operator(MBDynReadLog.bl_idname, text = "LOAD ELEMENTS")

        # Insert keyframes for animation
        col = layout.column(align=True)
        col.label(text = "Start animating")
        col.operator(MBDynSetMotionPaths.bl_idname, text = "ANIMATE")
# -----------------------------------------------------------
# end of MBDynImportPanel class


class MBDynImportElement(bpy.types.Panel):
    bl_idname = "OBJECT_PT_MBdyn_elements"
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

        for elem in ed:
            row = layout.row()
            row.label(str(elem.int_label))
            row.label(elem.type)
            if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
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
                if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
                    #TODO: ask for user acceptance and replace it or upload it
                    print("Element is already imported. Remove it manually before updating it.")
                    return{'CANCELLED'}
                else:
                    n1 = "none"
                    n2 = "none"
                    
                    # try to find Blender objects associated with the nodes that the element connects
                    for node in nd:
                        if elem.nodes[0].int_label == node.int_label:
                            n1 = node.blender_object
                        elif elem.nodes[1].int_label == node.int_label:
                            n2 = node.blender_object
                    if n1 == "none":
                        print("MBDynImportElemRod(): Could not find a Blender object associated to Node " \
                            + str(elem.nodes[0].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object associated to Node " + \
                            str(elem.nodes[0].int_label) + " not found")
                        return {'CANCELLED'}
                    elif n2 == "none":
                        print("MBDynImportElemRod(): Could not find a Blender object associated to Node " \
                            + str(elem.nodes[1].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object associated to Node " + \
                            str(elem.nodes[1].int_label) + " not found")
                        return {'CANCELLED'}

                    # creation of line representing the rod
                    rodcv_id = "rod_" + str(elem.int_label) + "_cvdata"
                    # check if curve is already present.
                    # If it is, remove it. FIXME: this may be dangerous!
                    if rodcv_id in bpy.data.curves.keys():
                        bpy.data.curves.remove(bpy.data.curves[rodcv_id])
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
                if any(obj == elem.blender_object for obj in context.scene.objects.keys()):
                    #TODO: ask for user acceptance and replace it or upload it
                    print("Element is already imported. Remove it manually before updating it.")
                    return{'CANCELLED'}
                else:
                    elem.is_imported = False
                    n1 = "none"
                    n2 = "none"
                    
                    # try to find Blender objects associated with the nodes that the element connects
                    for node in nd:
                        if elem.nodes[0].int_label == node.int_label:
                            n1 = node.blender_object
                        elif elem.nodes[1].int_label == node.int_label:
                            n2 = node.blender_object
                    if n1 == "none":
                        print("MBDynImportElemRodBez(): Could not find a Blender object associated to Node " + \
                            str(elem.nodes[0].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object associated to Node " + \
                            str(elem.nodes[0].int_label) + " not found")
                        return{'CANCELLED'}
                    elif n2 == "none":
                        print("MBDynImportElemRodBez(): Could not find a Blender object associated to Node " + \
                            str(elem.nodes[1].int_label))
                        self.report({'ERROR'}, "Could not import element: Blender object associated to Node " + \
                            str(elem.nodes[1].int_label) + " not found")
                        return{'CANCELLED'}

                    # creation of line representing the rod
                    rodcv_id = "rod_bezier_" + str(elem.int_label) + "_cvdata"
                    # check if curve is already present. If it is, remove it. FIXME: may be dangerous
                    if rodcv_id in bpy.data.curves.keys():
                        bpy.data.curves.remove(bpy.data.curves[rodcv_id])
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
            if nd_entry.blender_object == obj.name:
                row.label(nd_entry.blender_object, icon = "OBJECT_DATA")
            else:
                row.label(nd_entry.blender_object)
            row.operator("sel.mbdynnode", text="SELECT").int_label = nd_entry.int_label
        
class MBDynOBJNodeSelectButton(bpy.types.Operator):
    bl_idname = "sel.mbdynnode"
    bl_label = "MBDyn Node Sel Button"
    int_label = bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'

    def execute(self, context):
        axes = {'1': 'X', '2': 'Y', '3': 'Z'}
        context.object.mbdyn_settings.int_label = self.int_label
        ret_val = ''
        for item in context.scene.mbdyn_settings.nodes_dictionary:
            if self.int_label == item.int_label:
                item.blender_object = context.object.name
                ret_val = update_parametrization(context)
            if ret_val == 'ROT_NOT_SUPPORTED':
                self.report({'ERROR'}, "Rotation parametrization not supported, node " \
                            + obj.mbdyn_settings.string_label)
            elif ret_val == 'LOG_NOT_FOUND':
                self.report({'ERROR'}, "MBDyn .log file not found")
            else:
                # DEBUG message to console
                print("Object " + context.object.name + \
                      " MBDyn node association updated to node " + \
                str(context.object.mbdyn_settings.int_label))
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
    bpy.utils.unregister_class(MBDynClearData)  
    bpy.utils.unregister_class(RodBezUpdate)
    bpy.utils.unregister_class(MBDynImportPanel)
    bpy.utils.unregister_class(MBDynImportMotionPath)
    bpy.utils.unregister_class(MBDynOBJNodeSelect)
    bpy.utils.unregister_class(MBDynOBJNodeSelectButton)
    bpy.utils.unregister_class(MBDynImportElement)
    bpy.utils.unregister_class(MBDynImportElemRod)
    bpy.utils.unregister_class(MBDynImportElemRodBez)
        
if __name__ == "__main__":
    register()