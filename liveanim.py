# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

import bpy
from math import sqrt
import bmesh
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from struct import pack, unpack
from threading import Thread
from collections import OrderedDict
from time import sleep

class Tree(OrderedDict):
    def get_leaves(self):
        ret = list()
        for key, value in self.items():
            if isinstance(value, Tree):
                ret.extend(value.get_leaves())
            else:
                ret.append(key)
        return ret

FORMAT = "{:.6g}".format

def safe_name(name):
    return "_".join("_".join(name.split(".")).split())

def create_stream_socket(host_name, port_number):
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((host_name, port_number))
        sock.listen(5)
        sock.settimeout(60.)
        try:
            streaming_socket, address = sock.accept()
            return streaming_socket
        except OSError as err:
            print(err)

class StreamSender:
    def __init__(self, host_name=None, port_number=None):
        self.socket = create_stream_socket(host_name if host_name is not None else "127.0.0.1", port_number if port_number is not None else 9012)
    def send(self, floats):
        self.socket.send(pack('d'*len(floats), *floats))
    def close(self):
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as err:
            if err.errno != 107:
                print(err)
        self.socket.close()
        print('Socket Closed')
        del self.socket

class StreamReceiver(Thread):
    def __init__(self, fmt, initial_data=None, host_name=None, port_number=None):
        Thread.__init__(self)
        self.daemon = True
        self.fmt = fmt
        self.packed_data = pack(self.fmt, *initial_data)
        self.recv_size = len(self.packed_data)
        self.receiving = True
        self.socket = create_stream_socket(host_name if host_name is not None else "127.0.0.1", port_number if port_number is not None else 9011)
        print (self.socket)
    def run(self):
        try:
            while self.receiving:
                self.packed_data += self.socket.recv(self.recv_size)
                self.packed_data = self.packed_data[( (len(self.packed_data) // self.recv_size) - 1) * self.recv_size : ]
        except Exception as e:
            sleep(1)
            if self.receiving:
                raise Exception(e)
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as err:
            if err.errno != 107:
                print(err)
        self.socket.close()
        del self.socket
    def get_data(self):
        retData = unpack(self.fmt, self.packed_data[:self.recv_size])
        # self.packed_data = self.packed_data[self.recv_size:]

        return retData

    def close(self):
        self.receiving = False

def write_vector(f, v, prepend=True):
    f.write((", " if prepend else "") + ", ".join([FORMAT(round(x, 6) if round(x, 6) != -0. else 0) for x in v]))

def write_orientation(f, m, pad=""):
    f.write(",\n" + pad + "euler")
    write_vector(f, m.to_euler('ZYX'))
    #f.write(",\n" + pad +"matr,\n" + ",\n\t".join([pad + ", ".join(FORMAT(round(x, 6) if round(x, 6) != -0. else 0) for x in r) for r in m]))

def subsurf(obj):
    subsurf = [m for m in obj.modifiers if m.type == 'SUBSURF']
    subsurf = subsurf[0] if subsurf else obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 3
