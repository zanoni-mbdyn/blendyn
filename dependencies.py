# --------------------------------------------------------------------------
# Blendyn -- file dependencies.py
# Copyright (C) 2015 -- 2021 Andrea Zanoni -- andrea.zanoni@polimi.it
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
    # :system_note: optional string warning about required system-level software
    #               beyond what pip can provide (e.g. shared libraries, browsers)
    # :installed: boolean flag indicating if the dependency is found in the system
    module = None
    package = None
    name = None
    system_note = None
    is_installed = False

    def __init__(self, module, package, name, system_note=None):
        self.module = module
        self.package = package
        self.name = name
        self.system_note = system_note

    def installed(self, flag = None):
        if not flag:
            # getter for is_installed Flag
            return self.is_installed
        else:
            # setter for is_installed Flag
            self.is_installed = flag
# -----------------------------------------------------------
# end of Dependency class 

# Numpy (FIXME: check if really needed)
numpy_deps = (\
        Dependency("numpy", None, None),\
        )

# NetCDF — bundled as a wheel in wheels/; no pip installation needed.
# The following is kept for reference and for the preferences panel display.
netcdf_deps = (\
        Dependency("netCDF4", None, None),\
        )

# Plotting with Pygal/Cairosvg
plotting_pygal_deps = (\
        Dependency("pygal", None, None),\
        Dependency("cairosvg", None, None,
                   system_note="cairosvg also needs the Cairo graphics library (libcairo). "
                               "Install it via your package manager before pip "
                               "(e.g. libcairo2-dev on Debian/Ubuntu, cairo on Arch Linux).")\
        )

# Control of MBDyn simulation from Blender
psutil_deps = (\
        Dependency("psutil", None, None),\
        )

# Plotting with Matplotlib
plotting_matplotlib_deps = (\
        Dependency("matplotlib", None, None),\
)

# Plotting with Bokeh and html2image
plotting_bokeh_deps = (
        Dependency("bokeh", None, None),
        Dependency("html2image", None, None,
                   system_note="html2image requires a Chromium-based browser installed "
                               "on your system (chromium, google-chrome, etc.).")
)

# Dictionary of pip-installable optional dependencies.
# Note: NetCDF4 is bundled as a wheel and is NOT listed here.
deps = {
    "Numpy": numpy_deps,
    "Plotting - Pygal": plotting_pygal_deps,
    "Plotting - Matplotlib": plotting_matplotlib_deps,
    "Plotting - Bokeh": plotting_bokeh_deps,
    "Running MBDyn from Blender UI -- WARNING: Needs Python headers! ---": psutil_deps
}
