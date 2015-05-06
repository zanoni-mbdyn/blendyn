bl_info = {
    "name": "MBDyn Motion Paths",
    "author": "Andrea Zanoni - <a.zanoni.mbdyn@gmail.com>",
    "version": (0, 1),
    "blender": (2, 65, 0),
    "location": "Properties -> Object -> MBDyn Motion Path",
    "description": "Loads motion file from MBDyn (OpenSource MultiBody Dynamic solver) output. See www.mbdyn.org for more details.",
    "warning": "Alpha stage",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"}
    
import bpy
from bpy.types import Operator, Panel
from bpy.props import BoolProperty, IntProperty, IntVectorProperty
from bpy.props import StringProperty, BoolVectorProperty, PointerProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Euler

import ntpath, os, csv


# Nodes Dictionary: contains integer/string labels associations
class MBDynNodesDictionary(bpy.types.PropertyGroup):
    int_label = IntProperty(
            name = "node int label",
            description = "",
            )
    string_label = StringProperty(
            name = "node string label",
            description = "",
            )
            
bpy.utils.register_class(MBDynNodesDictionary)

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
    # Number of rows (output time steps) in MBDyn's .mov file
    num_rows = IntProperty(
            name = "MBDyn time instants",
            description = "Total number of rows in MBDyn .mov file, corresponding to total time steps"
            )
    # Load frequency: if different than 1, the .mov file is read every N time steps
    load_frequency = IntProperty(
            name = "frequency",
            description = "If this value is X, different than 1, then the MBDyn output is loaded every X time steps",
            min = 1,
            default = 1
            )
    # Nodes dictionary -- holds the association between int labels and string labels of MBDyn's nodes
    nodes_dictionary = CollectionProperty(
            type = MBDynNodesDictionary
            )
    # MBDyn's node count
    num_nodes = IntProperty(
            name = "MBDyn nodes",
            description = "MBDyn node count"
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
        print("Can't find .log file", log_file)
        pass
    return
    
def update_label(self, context):
    # Function to assign MBDyn's string label to Blender Object
    
    # utility renaming
    obj = context.object
    nd = context.scene.mbdyn_settings.nodes_dictionary
    
    # Debug Messages
    print("updating string label for object")
    print("object int label:", str(obj.mbdyn_settings.int_label))
    
    # Search for int label and assign corresponding string label, if found.
    # If not, signal it by assign the "not found" label
    node_string_label = "not_found"
    obj.mbdyn_settings.is_assigned = False
    for item in nd:
        if item.int_label == obj.mbdyn_settings.int_label:
            node_string_label = item.string_label
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
            name = "MBDyn's node label",
            description = "String label of MBDyn's node assigned to the object (if present)",
            default = "not assigned"
            )
    parametrization = StringProperty(
            name = "Rotation parametrization",
            description = "Rotation parametrization for node.",
            default = "euler123"
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
    print("Reading node list from file:", mov_file) 
    
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
    print("Reading node labels from file:", lab_file)
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
           
# Function to set global .mov file data
def read_mbdyn_data(context, filepath):
    
    # Debug console output
    print("Reading from file", filepath)
    
    # Row count
    fl = file_len(filepath)
    
    # Debug message
    print("File {} has {} rows".format(filepath, str(fl)))   
    
    # Setting of global (scene) properties
    context.scene.mbdyn_settings.num_rows = fl
    context.scene.mbdyn_settings.is_active = True
    file_dir, file_basename = path_leaf(filepath)
    context.scene.mbdyn_settings.file_basename = file_basename
    context.scene.mbdyn_settings.file_path = file_dir
    
    # Populates the nodes dictionary
    create_nodes_dict(file_dir, file_basename)    
    
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
                    # cycle MESH objects and set their location and rotation parameters
                    for obj in bpy.data.objects:
                        if (obj.type in anim_types) and obj.mbdyn_settings.is_assigned and int(rw[0]) == obj.mbdyn_settings.int_label:
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
        
        # Display MBDyn file basename
        row = layout.row()
        row.label(text="MBDyn files basename:")
        col = layout.column(align=True)
        col.prop(sce.mbdyn_settings, "file_basename", text="")
        col.prop(sce.mbdyn_settings, "num_nodes", text="# of nodes")
        col.prop(sce.mbdyn_settings, "num_rows", text="# of time steps")
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
        
        # Insert keyframes for animation
        col = layout.column(align=True)
        col.label(text="Start animating")
        col.operator(MBDynSetMotionPaths.bl_idname, text="START")
        
                
def register():
    bpy.utils.register_class(MBDynImportMotionPath)
    bpy.utils.register_class(MBDynImportPanel)
def unregister():
    bpy.utils.unregister_class(MBDynImportPanel)
    bpy.utils.unregister_class(MBDynImportMotionPath)
        
if __name__ == "__main__":
    register()
