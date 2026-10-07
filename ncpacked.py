# --------------------------------------------------------------------------
# Blendyn -- file ncpacked.py
# Copyright (C) 2015 -- 2026 Andrea Zanoni -- andrea.zanoni@polimi.it
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

# Compatibility layer for MBDyn "packed" NetCDF output
# (output results: netcdf, nc4, packed).
#
# In packed mode MBDyn does not create the time-dependent variables
# (e.g. node.struct.<label>.X). All their scalar components are stored
# as columns of the single variable packed.data(time, packed_signal),
# and each column is named after the original variable and component
# index in packed.signal_name (e.g. 'node.struct.10000.X[0]').
# Time-independent variables (label lists, eigenanalysis results, ...)
# keep the classic layout.
#
# PackedNcDataset wraps such a file and exposes the time-dependent
# variables again as virtual variables with the classic shape, so that
# the rest of Blendyn can access them as nc.variables[name][...].

import re
import numpy as np

from netCDF4 import chartostring

# maximum size of packed.data that is loaded in memory when a variable
# is read over (most of) the time axis: the packed data is chunked by
# blocks of time steps over all the signals, so reading a single
# variable over all time steps from the file means reading it all
_PACKED_MEMORY_LIMIT = 512*1024*1024

_signal_re = re.compile(r'^(.*)\[(\d+)\]$')


def is_packed(ds):
    """ True if the NetCDF dataset contains MBDyn packed output """
    return 'packed.data' in ds.variables and 'packed.signal_name' in ds.variables


def _strings(ncvar):
    return [str(s).strip() for s in chartostring(ncvar[:], encoding='utf-8')]


class PackedNcVariable:
    """ Virtual time-dependent variable, mapped to a contiguous block
        of columns of packed.data """

    def __init__(self, owner, name, c0, width, units, description):
        self._owner = owner
        self._c0 = c0
        self._width = width
        self.name = name
        if width == 1:
            self._comp_shape = ()
            self.dimensions = ('time',)
        elif width == 3:
            self._comp_shape = (3,)
            self.dimensions = ('time', 'Vec3')
        elif width == 9:
            # Mat3x3: stored in the same order as in the classic
            # (time, Vec3, Vec3) variable
            self._comp_shape = (3, 3)
            self.dimensions = ('time', 'Vec3', 'Vec3')
        else:
            self._comp_shape = (width,)
            self.dimensions = ('time', 'packed_dim_' + str(width))
        self.dtype = np.dtype('float64')
        self._attrs = {}
        if units:
            self.units = units
            self._attrs['units'] = units
        if description:
            self.description = description
            self._attrs['description'] = description

    @property
    def shape(self):
        return (self._owner.num_times(),) + self._comp_shape

    @property
    def ndim(self):
        return 1 + len(self._comp_shape)

    @property
    def size(self):
        return int(np.prod(self.shape))

    def __len__(self):
        return self._owner.num_times()

    def ncattrs(self):
        return list(self._attrs.keys())

    def getncattr(self, attr):
        return self._attrs[attr]

    def __array__(self, dtype=None, copy=None):
        return np.asarray(self[:], dtype=dtype)

    def __repr__(self):
        return "<packed MBDyn NetCDF variable {}, shape {}>".format(self.name, self.shape)

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        if any(k is Ellipsis for k in key):
            # rare: read everything and let numpy deal with the key
            data = self._owner.read(slice(None), self._c0, self._width)
            res = data.reshape((-1,) + self._comp_shape)[key]
        else:
            tkey = key[0]
            ckey = key[1:]
            if isinstance(tkey, (float, np.floating)):
                tkey = int(tkey)
            data = self._owner.read(tkey, self._c0, self._width)
            if isinstance(tkey, (int, np.integer)):
                res = data.reshape(self._comp_shape)[ckey]
            else:
                res = data.reshape((-1,) + self._comp_shape)[(slice(None),) + ckey]
        if isinstance(res, np.ndarray) and res.ndim == 0:
            return res[()]
        return res


class PackedNcDataset:
    """ Proxy for a netCDF4.Dataset containing MBDyn packed output:
        attributes are delegated to the underlying dataset, while
        variables contains the classic time-independent variables
        and the virtual time-dependent ones """

    def __init__(self, ds):
        object.__setattr__(self, '_ds', ds)
        object.__setattr__(self, '_data', ds.variables['packed.data'])
        object.__setattr__(self, '_cache', None)
        # querying the size of the unlimited dimension of a NetCDF-4 file
        # is expensive, and the shape of every virtual variable needs it
        object.__setattr__(self, '_num_times', ds.variables['packed.data'].shape[0])

        names = _strings(ds.variables['packed.signal_name'])
        units = _strings(ds.variables['packed.signal_units']) \
                if 'packed.signal_units' in ds.variables else [''] * len(names)
        descs = _strings(ds.variables['packed.signal_description']) \
                if 'packed.signal_description' in ds.variables else [''] * len(names)

        variables = {name: var for name, var in ds.variables.items()
                     if not name.startswith('packed.')}

        # columns of the same variable are contiguous
        base, c0, width = None, 0, 0
        for col, signal in enumerate(names):
            match = _signal_re.match(signal)
            if match is None:
                bname, idx = signal, 0
            else:
                bname, idx = match.group(1), int(match.group(2))
            if bname == base and idx == width:
                width += 1
                continue
            if base is not None:
                variables[base] = PackedNcVariable(self, base, c0, width, units[c0], descs[c0])
            base, c0, width = bname, col, 1
        if base is not None:
            variables[base] = PackedNcVariable(self, base, c0, width, units[c0], descs[c0])

        object.__setattr__(self, 'variables', variables)

    def __getattr__(self, attr):
        return getattr(self._ds, attr)

    def __setattr__(self, attr, value):
        setattr(self._ds, attr, value)

    def __repr__(self):
        return "<packed MBDyn NetCDF dataset> " + repr(self._ds)

    def num_times(self):
        return self._num_times

    def _load_cache(self):
        if self._cache is None:
            data = self._data[:]
            object.__setattr__(self, '_cache', np.ma.filled(data, np.nan))
        return self._cache

    def read(self, tkey, c0, width):
        """ Read columns c0 to c0 + width of packed.data at
            time index (or indices) tkey """
        cols = slice(c0, c0 + width)
        nt = self.num_times()

        if isinstance(tkey, (int, np.integer)):
            tdx = int(tkey)
            if tdx < -nt or tdx >= nt:
                raise IndexError("index {} is out of bounds for time dimension of size {}".format(tdx, nt))
            tkey = tdx % nt
            if self._cache is not None:
                return self._cache[tkey, cols]
            return np.ma.filled(self._data[tkey, cols], np.nan)

        if isinstance(tkey, slice):
            nsel = len(range(*tkey.indices(nt)))
            if self._cache is None and nsel > 128 and \
                    self._data.size * self._data.dtype.itemsize <= _PACKED_MEMORY_LIMIT:
                self._load_cache()
            if self._cache is not None:
                return self._cache[tkey, cols]
            return np.ma.filled(self._data[tkey, cols], np.nan)

        # integer or boolean sequence: read the sorted unique rows,
        # then rearrange them as requested
        tkey = np.asarray(tkey)
        if tkey.dtype == bool:
            tkey = np.nonzero(tkey)[0]
        tkey = tkey.astype(int)
        if tkey.size and (tkey.min() < -nt or tkey.max() >= nt):
            raise IndexError("index out of bounds for time dimension of size {}".format(nt))
        tkey = tkey % nt if nt else tkey
        if self._cache is not None:
            return self._cache[tkey, cols]
        rows, inverse = np.unique(tkey, return_inverse=True)
        if rows.size == 0:
            return np.empty((0, width))
        data = np.ma.filled(self._data[rows, cols], np.nan)
        return data.reshape((rows.size, width))[inverse.reshape(-1)].reshape(tkey.shape + (width,))
