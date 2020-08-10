# --------------------------------------------------------------------------
# Blendyn -- file dependencies.py
# Copyright (C) 2015 -- 2020 Andrea Zanoni -- andrea.zanoni@polimi.it
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

from collections import namedtuple

global deps

class Dependency:
    # Generic dependency.
    # :module: name of the module
    # :package: name of the python package (if None, package = module)
    # :name: name to be given to module during import (if None, name = module)
    # :installed: boolean flag indicating if the dependency is found in the system
    module = None
    package = None
    name = None
    is_installed = False

    def __init__(self, module, package, name):
        self.module = module
        self.package = package
        self.name = name

    def installed(self):
        # getter for is_installed Flag
        return self.is_installed

    def installed(self, flag):
        # setter for is_installed Flag
        self.is_installed = flag
        return


# NetCDF
netcdf_deps = (\
        Dependency("netCDF4", None, None),\
        )

# Plotting with Pygal/Cairosvg
plotting_pygal_deps = (\
        Dependency("pygal", None, None),\
        Dependency("cairosvg", None, None)\
        )

# Control of MBDyn simulation from Blender
psutil_deps = (\
        Dependency("psutil", None, None),\
        )

# Dictionary of dependencies
deps = {
    "NetCDF": netcdf_deps,
    "Plot-Pygal": plotting_pygal_deps,
    "Psutil": psutil_deps
    }
