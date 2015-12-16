# Change Log
All notable changes to this project will be documented in this file
NOTE: this changelog has been added upon the release of version 1.3
	of the addon. Previous changes are untracked.

## [1.3.0] - 2015-12-10

### Added
- Automatic import for all MBDyn nodes at once;
- selection of labels file with basename different from the results'
  file basename;
- visualization of MBDyn nodes list in the Scene Properties panel;
- basic documentation in README (to be extended greatly).

### Changed
- Basic MBDyn model structure import has been rewritten and it is 
  now based entirely on the .log file of the simulation output, thus
  easing the visualization of models that fail during the assembly 
  phase;
- element list in the Scene Properties panel is now shown as a UI 
  List, with the same layout of the nodes list;
- the nodes list in the Object Properties panel now shows an "ADD"
  button to import for nodes that are not yet imported in the scene;
- the element import has been structured in the code: the addition
  of an element support to the addon can now be done in an organized
  way;

### Fixed
- Bug in setting the correct rotation parametrization for nodes;
- Various error and warning messages appearance

## [1.3.1] - 2015-xx

### Added
- Selection of Blender object to be used for automatic import of nodes

### Changed

### Fixed
- Bug in the import of orientation when matrix output is selected for
  nodes;
- Bug in re-parsing the log file after a model update;
- Bug in the loading of an empty .mov file;
