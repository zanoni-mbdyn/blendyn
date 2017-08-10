# --------------------------------------------------------------------------
# Blendyn -- file driverlib.py
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

import bpy
# from mathutils import *
# from math import *
# from bpy.types import Operator, Panel
from bpy.props import *

# import logging

class MBDynFileDriversDictionary(bpy.types.PropertyGroup):

    int_label = IntProperty(
        name = "Integer label of driver",
        description = ""
        )

    type = StringProperty(
        name = "Type of MBDyn driver",
        description = ""
        )

    name = StringProperty(
        name = "Name of Stream File Driver",
        description =""
        )

    path = StringProperty(
        name = "Path of sock file if UNIX socket used",
        )

    host = StringProperty(
        name = "Hostname of driver",
        default = ""
        )

    port = IntProperty(
        name = "Port Address of driver",
        default = 9011
        )

    protocol = StringProperty(
        name = "Protocol used in stream driver",
        description = ""
        )

    create = BoolProperty(
        name = "Check if socket is created",
        default = True
        )

    signal = BoolProperty(
        name = "Signal of File Driver",
        )

    timeout = FloatProperty(
        name = "Timeout of socket",
        )

    columns_number = IntProperty(
        name = "Columns Number"
        )

    value = IntProperty(
        name = 'Value of Driver',
        default = 0
        )

bpy.utils.register_class(MBDynFileDriversDictionary)
# -----------------------------------------------------------
# end of MBDynFileDriversDictionary class 


def parse_filedriver(context, rw):
    mbs = context.scene.mbdyn
    drs = mbs.drivers

    def update_filedriver(driver, rw):
        # driver.host = rw[5]
        # Change this after Andrea's changes

        driver.type = rw[3]

        if driver.type == 'UNIX':
            driver.path = rw[5]
        else:
            driver.port = int(rw[5])

        driver.protocol = rw[6]
        driver.create = bool(rw[7])
        driver.timeout = float(rw[12])
        driver.columns_number = int(rw[13])

        try:
            driver.value = float(rw[14])
        except IndexError:
            pass

    try:
        driver = drs["{0}_{1}".format(rw[4], rw[1])]
        print("parse_filedriver(): found existing entry in drivers dictionary for driver " + rw[1]\
        + ". Updating it.")
        update_filedriver(driver, rw)
    except KeyError:
        print("parse_filedriver(): didn't find an existing entry in drivers dictionary for driver " + rw[2]\
                + ". Creating it.")
        driver = drs.add()
        driver.int_label = int(rw[1])
        driver.name = "{0}_{1}".format(rw[4], rw[1])
        update_filedriver(driver, rw)

