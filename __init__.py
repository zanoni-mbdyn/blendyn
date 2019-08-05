# --------------------------------------------------------------------------
# Blendyn - file __init__.py
# Copyright (C) 2015 -- 2019 Andrea Zanoni -- andrea.zanoni@polimi.it
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
import inspect

bl_info = {
    "name": "Blendyn -- MBDyn physics, Blender graphics",
    "author": "Andrea Zanoni - <andrea.zanoni@polimi.it>",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D -> Properties -> Physics",
    "description": "Imports simulation results of MBDyn (Open Source MultiBody\
    Dynamics solver -- https://www.mbdyn.org/).",
    "wiki_url": "https://github.com/zanoni-mbdyn/blendyn/wiki",
    "bugtracker": "https://github.com/zanoni-mbdyn/blendyn/issues",
    "category": "Animation"}

if "bpy" in locals():
    import importlib
    if "blendyn" in locals():
        importlib.reload(base)
else:
    import bpy
    from . import blendyn

classes = inspect.getmembers(blendyn)

def register():
    for cls in classes
    bpy.utils.register_class(cls)

def unregister():
    for cls in classes
    bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
