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
from socket import socket, AF_INET, AF_UNIX, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from struct import pack, unpack
from threading import Thread
from collections import OrderedDict
from time import sleep
from os import path, remove

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

def connect_stream_socket(stream_obj, context):
    mbs = context.scene.mbdyn

    if stream_obj.type == 'UNIX':
        sock = socket(AF_UNIX, SOCK_STREAM)

        if path.isabs(stream_obj.path):
            sock.connect(stream_obj.path)
        else:
            sock_path = path.join(mbs.file_path, stream_obj.path)
            sock.connect(path.abspath(sock_path))

        return sock

    else:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((stream_obj.host, stream_obj.port))

        return sock

def remove_unix_stream(stream_obj):
    mbs = bpy.context.scene.mbdyn

    sock_path = path.join(mbs.file_path, stream_obj.path)
    remove(path.abspath(sock_path))

class StreamSender:
    def __init__(self, stream_obj, context):
        self.stream_obj = stream_obj
        self.socket = connect_stream_socket(stream_obj, context)
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

        if self.stream_obj.type == 'UNIX':
            remove_unix_stream(self.stream_obj)

        del self.socket

class StreamReceiver(Thread):
    def __init__(self, stream_obj, context, initial_data=None):
        Thread.__init__(self)
        self.stream_obj = stream_obj
        self.daemon = True
        motion_content = sum(stream_obj.motion_content)
        num_nodes = len(stream_obj.nodes.split(' '))
        self.recv_size = num_nodes * motion_content
        self.fmt = 'd' * self.recv_size
        self.recv_size *= 8
        if initial_data == None:
            initial_data = [0]*len(self.fmt)
        self.packed_data = pack(self.fmt, *initial_data)
        self.receiving = True
        self.socket = connect_stream_socket(stream_obj, context)
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

        if self.stream_obj.type == 'UNIX':
            remove_unix_stream(self.stream_obj)

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
