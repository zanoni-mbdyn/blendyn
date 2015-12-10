# mbdyn-blender
Animation Addon that imports the output of free multibody analysis code MBDyn:
see http://www.mbdyn.org/ for more details

# INSTALLATION
Download the complete repository with the "Download .zip" option and install in
Blender from File->User Preferences->Addons->Install from file..." A very simple
example can be found in the test/ directory

# BASIC USAGE
Once installed, the addon provides for additional panels in the Toolbar (in the
Animation tab) and Properties panels (in the Scene and Object tab)  of Blender.

Assuming that an [MBDyn](http://www.mbdyn.org/) simulation has been performed
and that the output files have basename `test`, so that the standard output
would consist in the `test.mov`, `test.log`, `test.jnt` and `test.out` files,
the general procedure to import and visualize the model are described in the
following sections.

## Step 1: Select the simulation .mov file
From the left toolbar panel, located in the Animation tab of the 3D view area of
Blender, click on the "Select .mov file" and locate the .mov file of the
simulation output. Please note that the `.mov` file *does not* necessarily contain
a valid simulation output: the initial structure of the model is loaded from the
`.log` file, which is always written, even in the case the initial assembly phase
of the simulation fails. The `.mov` file selection essentially serves to identify
the path and the basename of the [MBDyn](http://www.mbdyn.org/) output files.
![mbdyn-blender panel in Animation sidebar](doc/tools_animation_panel.png
"Addon panel in Animation sidebar")
If the `.mov` file is located properly, some general info about its structure is
displayed after the "Loaded .mov file" label in the panel. Please notice that
until the `.log` file is loaded, the number of nodes and number of time steps in
the info panel will remain null.

## Step 2: Load the .log file
Once the basename and the path of the simulation output files has been set by
the selection of the `.mov` file, the `.log` file can be loaded by pressing the
"Load .log file" button in the panel. An message should appear in the Blender
toolbar at the top, informing the user that all the
[MBDyn](http://www.mbdyn.org/) entities have been imported correctly. The number
of nodes and number of time steps is now displayed in the panel above the "Load
.log file" button.

## Step 3 [optional]: Load a labels file
The addon will, by default, assign a standard labeling to the imported
[MBDyn](http://www.mbdyn.org/) entities, based on the integer labels found in
the `.log` file. If a different labeling is desired, a labels file can be
loaded. The labels file should contain [MBDyn](http://www.mbdyn.org/) `set`
statements in the following (alternative) forms:
	set: integer node_ground = 1;
	set: integer Node_ground = 1;
	set: integer NODE_ground = 1;
	set: const integer node_ground = 1;
	set: const integer Node_ground = 1;
	set: const integer NODE_ground = 1;
In this case, the object associated to node 1 will be called node_ground,
(or Node_ground or NODE_ground) when it is added to the Blender scene.
In the same way, the labeling can be assigned to joints and beams. For example
	set: integer joint_revolute = 1;
	set: const integer BEAM_cantilever = 5;
	set: integer JOINT_cardano = 1700;
	set: integer Beam_Link = 435;
all generate valid labels. Please notice, though, that at the current state the
addon recognises only `rod` elements. The addition of support for other elements
is the first development priority as of now.
## Step 4: Add [MBDyn](http://www.mbdyn.org/) nodes automatically or assign them to existing Blender objects
Once the `.log` file has been loaded, the addon populates two lists of
[MBDyn](http://www.mbdyn.org/) objects in the Properties toolbar of Blender,
under the Scene tab.
![mbdyn-blender panel in the Properties->Scene
sidebar](doc/properties_scene_panel.png "Addon panel in Properties->Scene
sidebar)

The first list is made of the [MBDyn](http://www.mbdyn.org/) nodes found in the
`.log` file of model. Selecting a node in the list will update the info shown at
the bottom of the list: the string label of the node is not "none" only if a
valid labels file has been selected and the label corresponding to the node has
been found. The button "Add all nodes to scene" triggers the spawning of an
'Empty' Blender object of type 'axes' for every node found in the list, in the
initial position and having the initial orientation of the node itself as found
in the `.log` file.

The second list contains the elements found in the `.log` file and recognised by
the addon. Please notice that *this is the most experimental part of the addon*,
and that *the majority of the elements are not supported as of now*. Only `rod`
joints are supported fully. The "Add element to the scene" button will spawn an
object (a straight line) representing the `rod` element. It will do nothing for
the other types of elements, right now. 

If a Blender object is selected, another panel is drawn in the
Properties->Object sidebar. The Panel allows the user to directly assign an
[MBDyn](http://www.mbdyn.org/) node to the currently selected Blender object by
pressing on the "ASSIGN" button, or to import it separately using the "ADD"
button. In the first case, the node will be associated with the Blender object,
using the Blender local Axes of the object as the reference frame: basically,
the node position and orientation will be assigned to the position and
orientation of the Blender Axes for that object. The user should put care into
moving the axes in the correct position with respect to the mesh to reproduce
the correct visualization. 

![mbdyn-blender panel in the Properties->Object
sidebar](doc/properties_object_panel.png "Addon panel in Properties->Object
sidebar)

## Step 5: Animate the Blender scene
Once all the nodes and the elements of interest are loaded in the Blender scene,
pressing the "Animate scene" button in the Animation toolbar (left panel)
will trigger the addition of keyframes and the update of the position and
orientation of each Blender object that is associated with an
[MBDyn](http://www.mbdyn.org/) node or
element, according to the simulation outputs contained in the loaded `.mov`
file. As an option, the user can select to animate the scene only once every *n*
timesteps, where *n* is an integer set with the "frequency" slider found after
the button.
