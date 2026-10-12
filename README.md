# Blendyn

Welcome to the **Blendyn** GitHub repository!

![Blendyn Logo](https://github.com/zanoni-mbdyn/blendyn/wiki/images/blendyn_logo_subtitle_big.png)

**Blendyn** is a [Blender](http://www.blender.org/) add-on, written in
Python, that allows to import the output of the
[free](http://www.gnu.org/philosophy/free-sw.html) multibody solver
[MBDyn](https://www.mbdyn.org/), developed at the [Aerospace Science and
Technology Department](https://www.aero.polimi.it/) of [Politecnico di Milano
University](http://www.polimi.it/). [MBDyn](https://www.mbdyn.org/) does not
come with a built-in graphical pre- or post-processor, as it is able to process
text-only input files and generates either text or binary (in
[NetCDF](http://www.unidata.ucar.edu/software/netcdf/) format) output. The
purpose of the **Blendyn** add-on is to exploit the numerous features of
the 3D graphics software [Blender](http://www.blender.org/) to post-process
[MBDyn](https://www.mbdyn.org/) output data. The add-on is, therefore, strictly
a post-processor, but the goal is to make it as useful as possible also during
the model definition phase.

Please refer to the [wiki pages](https://github.com/zanoni-mbdyn/blendyn/wiki) 
for the complete documentation.

## Model editor (experimental)

**Blendyn** can also build MBDyn models, as node trees: a block for every
node, element, drive caller, constitutive law, card and problem setting that
MBDyn's Python preprocessor (MBDynLib) knows, with typed sockets for the
references between them (structural nodes, reference frames, drives, ...).
It writes the MBDyn input through MBDynLib and runs it like **Run simulation**,
and the diagrams are the JSON files of MBDyn's Python model builder, so a
model drawn in its Qt editor opens here and the other way round.

1. Point **Edit → Preferences → Add-ons → Blendyn → MBDyn source checkout**
   at an MBDyn source tree (or set `MBDYN_SRC`); the editor uses its
   `contrib/PythonModelBuilder` and `contrib/PythonPreprocessor`. MBDynLib
   checks argument types when `pydantic` is installed.
2. In a Node Editor, choose the **MBDyn Model** tree type; the **MBDyn**
   sidebar tab creates a model or opens a diagram.
3. Add blocks with **Add → MBDyn** or **Add block…** (search), connect their
   sockets, and edit the active block in the sidebar. Values accept numbers or
   expressions over the **Parameters**; the script button of a field takes a
   raw MBDynLib value. A link between incompatible sockets is shown in red and
   ignored. Optional reference-frame sockets are hidden: **Ctrl H** shows them.
4. **Validate** writes the input to a text and marks the blocks in error;
   **Export** writes it to the **MBDyn input** file; **Run** also starts MBDyn.

Components (grouped sub-diagrams) of the Qt editor are expanded when a diagram
is opened. The tests are `prepro/test`: `test_fields.py` runs with plain Python
(`MBDYN_SRC=... python3 -m unittest discover -s prepro/test`), and
`blender_model_editor.py` in headless Blender (see its docstring).

## **Update: January, 2020**
The Blender **2.8x** version of **Blendyn** is now considered the **baseline** code for 
development, while the 2.7x version has been moved to the `blender27` branch and will **not** 
be updated, apart from occasional bugfixes, from now on. Therefore, the `master` branch now 
points to the Blender 2.8x version, be careful when updating!

## **Update: August, 2019**
The porting of **Blendyn** to the new Blender 2.80 API has been completed and is now available
in the `blender28` branch. If you are an interested user, please try it out! 
You can find the main **Blendyn** menu in the Sidbar Panel, accesses by pressing the `N` key.
Please report any bugs in the [Issues](https://github.com/zanoni-mbdyn/blendyn/issues) section.

*Please note that the documentation is currently lagging a little bit behind the latest code,
especially in the* `blender28` *branch. Basically, you might find some small differences in 
the addon UI with respect to what is described in the Wiki. The hope is that those differences
are small enough that they are not show-stoppers! The docs will be updated as soon as possible*
