# Blendyn

Welcome to the **Blendyn** GitHub repository!

![Blendyn Logo](https://github.com/zanoni-mbdyn/blendyn/wiki/images/blendyn_logo_subtitle_big.png)

**Blendyn** is a [Blender](http://www.blender.org/) add-on, written in
Python, that allows to import the output of the
[free](http://www.gnu.org/philosophy/free-sw.html) multibody solver
[MBDyn](https://www.mbdyn.org /), developed at the [Aerospace Science and
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



## **Update: August, 2019**
The porting of **Blendyn** to the new Blender 2.80 API has been completed and is now available
in the `blender28` branch. If you are an interested user, please try it out! 
You can find the main **Blendyn** menu in the Sidbar Panel, accesses by pressing the `N` key.
Please report any bugs in the [Issues](https://github.com/zanoni-mbdyn/blendyn/issues) section.

*Please note that the documentation is currently lagging a little bit behind the latest code,
especially in the* `blender28` *branch. Basically, you might find some small differences in 
the addon UI with respect to what is described in the Wiki. The hope is that those differences
are small enough that they are not show-stoppers! The docs will be updated as soon as possible*
