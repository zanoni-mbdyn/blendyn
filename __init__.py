# --------------------------------------------------------------------------
# Blendyn - file __init__.py
# Copyright (C) 2015 -- 2017 Andrea Zanoni -- andrea.zanoni@polimi.it
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
bl_info = {
    "name": "Blendyn -- MBDyn physics, Blender graphics",
    "author": "Andrea Zanoni - <andrea.zanoni@polimi.it>",
    "version": (1, 0, 0),
    "blender": (2, 6, 0),
    "location": "View3D -> MBDyn",
    "description": "Imports simulation results of MBDyn (Open Source MultiBody
    Dynamic solver -- https://www.mbdyn.org/).",
    "wiki_url": "https://github.com/zanoni-mbdyn/blendyn/wiki",
    "bugtracker": "https://github.com/zanoni-mbdyn/blendyn/issues",
    "category": "Animation"}

if "bpy" in locals():
    import imp
    if "base" in locals():
        imp.reload(base)
else:
    import bpy
    from . import base


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
