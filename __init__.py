# --------------------------------------------------------------------------
# MBDynImporter
# Copyright (C) 2015 Andrea Zanoni -- andrea.zanoni@polimi.it
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
bl_info = {
    "name": "MBDyn Motion Paths Importer",
    "author": "Andrea Zanoni - <andrea.zanoni@polimi.it>",
    "version": (1, 3),
    "blender": (2, 6, 0),
    "location": "View3D -> Animation -> MBDyn Motion Path",
    "description": "Imports simulation results of MBDyn (Open Source MultiBody Dynamic solver) output. See www.mbdyn.org for more details.",
    "warning": "Beta stage",
    "wiki_url": "",
    "bugtracker": "https://github.com/zanoni-mbdyn/mbdyn-blender/issues",
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
