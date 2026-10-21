# --------------------------------------------------------------------------
# Blendyn -- file fieldlib.py
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

# Visualization of the fields of flexible elements (displacement relative
# to a floating reference node, internal forces and strains).
#
# The flexible elements are drawn by the meshes of the flexible components
# (flexlib.py), which color them by calling update_fields() whenever they
# are moved. The data of the selected quantity is read from the NetCDF
# output once, for all the time steps, and kept in memory. The field
# settings are separate for each family of elements (beams, shell4,
# membrane4), so that components of different families can be colored at
# the same time.

import os
import math
import logging
import functools

import bpy
from bpy.props import *
from bpy.app.handlers import persistent

import numpy as np

from .utilslib import get_nc_dataset, frame_steps

try:
    import gpu
    import blf
    from gpu_extras.batch import batch_for_shader
    HAVE_GPU = True
except ImportError:
    HAVE_GPU = False

VALUE_ATTR = 'blendyn_field'
COLOR_ATTR = 'blendyn_field_color'

# Element families: Blendyn element types, NetCDF variable prefix
# and collection of the element objects
FAMILIES = {
    'SHELL4': {'label': 'Shells', 'types': ('shell4',), 'prefix': 'elem.shell4.', 'collection': 'plates'},
    'MEMBRANE4': {'label': 'Membranes', 'types': ('membrane4',), 'prefix': 'elem.membrane4.', 'collection': 'plates'},
    'BEAM': {'label': 'Beams', 'types': ('beam3', 'beam2'), 'prefix': 'elem.beam.', 'collection': 'beams'},
}

# Quantities: variable suffix and components (label, flat indices of the
# components of the variable; more than one index means their norm)
_SHELL_COMPS = lambda q: [(q + ij, (k,)) for k, ij in enumerate(('11', '12', '13', '21', '22', '23'))]
QUANTITIES = {
    'SHELL4': [
        ('n', 'Forces n', 'Internal forces per unit length', _SHELL_COMPS('n')),
        ('m', 'Moments m', 'Internal moments per unit length', _SHELL_COMPS('m')),
        ('eps', 'Strains eps', 'Linear strains', _SHELL_COMPS('eps')),
        ('k', 'Curvatures k', 'Angular strains', _SHELL_COMPS('k')),
    ],
    'MEMBRANE4': [
        ('n', 'Forces n', 'Internal forces per unit length',
            [('n11', (0,)), ('n22', (1,)), ('n12', (2,))]),
        ('eps', 'Strains E', 'Green-Lagrange strains',
            [('E11', (0,)), ('E22', (1,)), ('2 E12', (2,))]),
    ],
    'BEAM': [
        ('F', 'Forces F', 'Internal forces in the section frame',
            [('F1 (axial)', (0,)), ('F2', (1,)), ('F3', (2,)), ('|F|', (0, 1, 2))]),
        ('M', 'Moments M', 'Internal moments in the section frame',
            [('M1 (torsion)', (0,)), ('M2', (1,)), ('M3', (2,)), ('|M|', (0, 1, 2))]),
        ('nu', 'Strains nu', 'Linear strains in the section frame',
            [('nu1', (0,)), ('nu2', (1,)), ('nu3', (2,)), ('|nu|', (0, 1, 2))]),
        ('k', 'Curvatures k', 'Angular strains in the section frame',
            [('k1', (0,)), ('k2', (1,)), ('k3', (2,)), ('|k|', (0, 1, 2))]),
    ],
}
DISPLACEMENT = ('DISP', 'Displacement', 'Displacement relative to the reference node',
        [('u1', (0,)), ('u2', (1,)), ('u3', (2,)), ('|u|', (0, 1, 2))])

# Gauss points of shell4 and membrane4 and corners of the face,
# in natural coordinates scaled so that the Gauss points are at +/-1
# (MBDyn: xi_i in shelleasans.cc, node shape functions in shell.hc)
_IP_XI = np.array(((-1., -1.), (1., -1.), (1., 1.), (-1., 1.)))
_NODE_XI = np.array(((1., 1.), (-1., 1.), (-1., -1.), (1., -1.)))
# corner value = sum of IP values times these weights, either taking
# the IP closest to the corner, or extrapolating the bilinear
# interpolation of the IP values
_IP_NEAREST = np.array([[float(np.all(ip == nd)) for ip in _IP_XI] for nd in _NODE_XI])
_IP_EXTRAP = np.array([[(1. + ip[0]*nd[0]*math.sqrt(3.))*(1. + ip[1]*nd[1]*math.sqrt(3.))/4.
                        for ip in _IP_XI] for nd in _NODE_XI])

# beam evaluation points in the natural coordinate (MBDyn: shapefnc.cc)
_BEAM3_XI_EP = 1./math.sqrt(3.)

axes = {'1': 'X', '2': 'Y', '3': 'Z'}

# Colormaps, as sRGB stops
COLORMAPS = {
    'VIRIDIS': ((0.267, 0.005, 0.329), (0.283, 0.141, 0.458), (0.254, 0.265, 0.530),
                (0.207, 0.372, 0.553), (0.164, 0.471, 0.558), (0.128, 0.567, 0.551),
                (0.135, 0.659, 0.518), (0.267, 0.749, 0.441), (0.478, 0.821, 0.318),
                (0.741, 0.873, 0.150), (0.993, 0.906, 0.144)),
    'COOLWARM': ((0.230, 0.299, 0.754), (0.552, 0.690, 0.996), (0.866, 0.866, 0.866),
                (0.956, 0.604, 0.486), (0.706, 0.016, 0.150)),
    'JET': ((0.0, 0.0, 0.5), (0.0, 0.0, 1.0), (0.0, 0.5, 1.0), (0.0, 1.0, 1.0),
                (0.5, 1.0, 0.5), (1.0, 1.0, 0.0), (1.0, 0.5, 0.0), (1.0, 0.0, 0.0),
                (0.5, 0.0, 0.0)),
}


def _srgb_to_linear(c):
    c = np.asarray(c, dtype=float)
    return np.where(c <= 0.04045, c/12.92, ((c + 0.055)/1.055)**2.4)


def _linear_to_srgb(c):
    c = np.clip(np.asarray(c, dtype=float), 0., 1.)
    return np.where(c <= 0.0031308, 12.92*c, 1.055*c**(1./2.4) - 0.055)


def colormap_stops(name):
    """ Positions and scene-linear colors of the colormap stops """
    stops = _srgb_to_linear(COLORMAPS[name])
    return np.linspace(0., 1., len(stops)), stops


@functools.lru_cache(maxsize=None)
def colormap_lut(name, size=256):
    """ Scene-linear colors of the colormap, interpolated in linear
        space as in a ColorRamp node """
    pos, stops = colormap_stops(name)
    x = np.linspace(0., 1., size)
    return np.stack([np.interp(x, pos, stops[:, k]) for k in range(3)], axis=1)


def map_colors(values, vmin, vmax, lut):
    """ RGBA colors of the values """
    if vmax > vmin:
        t = (values - vmin)/(vmax - vmin)
    else:
        t = np.full_like(values, 0.5)
    t = np.nan_to_num(np.clip(t, 0., 1.), nan=0.)
    idx = np.rint(t*(len(lut) - 1)).astype(int)
    rgba = np.ones((values.size, 4), dtype=np.float32)
    rgba[:, :3] = lut[idx.ravel()]
    return rgba

# -----------------------------------------------------------
# Data access

def nc_file_path(mbs):
    return os.path.join(os.path.dirname(mbs.file_path), mbs.file_basename + '.nc')


def _file_stamp(ncfile):
    """ Identifies a version of the results file, so that the caches
        are rebuilt when MBDyn writes it again """
    try:
        st = os.stat(ncfile)
        return (ncfile, st.st_mtime_ns, st.st_size)
    except OSError:
        return (ncfile,)


def _num_steps(nc):
    return len(nc.variables['time'])


def read_components(nc, items):
    """ Values of the components (variable name, flat index) over all the
        time steps, as an array (time steps, len(items)). Components of
        variables missing in the file are NaN """
    nt = _num_steps(nc)
    res = np.full((nt, len(items)), np.nan, dtype=np.float32)
    present = [(k, name, idx) for k, (name, idx) in enumerate(items) if name in nc.variables]
    if not present:
        return res
    if hasattr(nc, 'read_columns'):
        # packed output: read all the columns at once
        cols = [nc.variables[name].column(idx) for _, name, idx in present]
        res[:, [k for k, _, _ in present]] = nc.read_columns(cols)
        return res
    by_name = {}
    for k, name, idx in present:
        by_name.setdefault(name, []).append((k, idx))
    for name, kidx in by_name.items():
        data = np.ma.filled(nc.variables[name][:], np.nan).reshape((nt, -1))
        res[:, [k for k, _ in kidx]] = data[:, [idx for _, idx in kidx]]
    return res


def _node_var(label, name):
    return 'node.struct.' + str(label) + '.' + name


def node_positions(nc, labels):
    """ Positions of the nodes, (time steps, nodes, 3) """
    items = [(_node_var(label, 'X'), k) for label in labels for k in range(3)]
    return read_components(nc, items).reshape((-1, len(labels), 3))


def _rotvec_to_matrix(phi):
    """ Rotation matrices of the rotation vectors phi (..., 3) """
    theta = np.linalg.norm(phi, axis=-1)[..., None, None]
    K = np.zeros(phi.shape[:-1] + (3, 3))
    K[..., 0, 1], K[..., 0, 2] = -phi[..., 2], phi[..., 1]
    K[..., 1, 0], K[..., 1, 2] = phi[..., 2], -phi[..., 0]
    K[..., 2, 0], K[..., 2, 1] = -phi[..., 1], phi[..., 0]
    with np.errstate(invalid='ignore', divide='ignore'):
        a = np.where(theta > 1e-12, np.sin(theta)/theta, 1.)
        b = np.where(theta > 1e-12, (1. - np.cos(theta))/theta**2, .5)
    return np.eye(3) + a*K + b*(K @ K)


def _axis_rotation(axis, angle):
    c, s = np.cos(angle), np.sin(angle)
    R = np.zeros(angle.shape + (3, 3))
    i = 'XYZ'.index(axis)
    j, k = (i + 1) % 3, (i + 2) % 3
    R[..., i, i] = 1.
    R[..., j, j], R[..., j, k] = c, -s
    R[..., k, j], R[..., k, k] = s, c
    return R


def _euler_to_matrix(angles, par):
    """ Rotation matrices from MBDyn Euler angles (degrees), as built
        for the node objects by set_motion_paths_netcdf() """
    a = np.radians(angles)
    values = {'X': a[..., int(par[5]) - 1], 'Y': a[..., int(par[6]) - 1], 'Z': a[..., int(par[7]) - 1]}
    order = axes[par[7]] + axes[par[6]] + axes[par[5]]
    # mathutils.Euler: the rotations are applied in the given order
    R = _axis_rotation(order[0], values[order[0]])
    for axis in order[1:]:
        R = _axis_rotation(axis, values[axis]) @ R
    return R


def node_rotations(nc, nodes):
    """ Orientation matrices of the nodes, (time steps, nodes, 3, 3).
        Nodes without orientation output get the identity """
    nt = _num_steps(nc)
    res = np.tile(np.eye(3), (nt, len(nodes), 1, 1))
    groups = {}
    for n, node in enumerate(nodes):
        par = node.parametrization
        if par == 'MATRIX':
            key, width = 'R', 9
        elif par == 'PHI':
            key, width = 'Phi', 3
        elif par[0:5] == 'EULER':
            key, width = 'E', 3
        else:
            continue
        if _node_var(node.int_label, key) not in nc.variables:
            continue
        groups.setdefault((par, key, width), []).append(n)
    for (par, key, width), idx in groups.items():
        items = [(_node_var(nodes[n].int_label, key), k) for n in idx for k in range(width)]
        data = read_components(nc, items).astype(float).reshape((nt, len(idx), width))
        if key == 'R':
            # as in the node objects: the matrix read from the file
            # is the transpose of the orientation matrix
            R = np.swapaxes(data.reshape((nt, len(idx), 3, 3)), -1, -2)
        elif key == 'Phi':
            R = _rotvec_to_matrix(data)
        else:
            R = _euler_to_matrix(data, par)
        res[:, idx] = R
    return res


def displacements(nc, mbs, labels, ref_node):
    """ Displacements of the nodes (time steps, nodes, 3) relative to
        the reference node, in its frame, from the first time step.
        Without reference node, the global displacements """
    X = node_positions(nc, labels).astype(float)
    if ref_node is None:
        return X - X[0]
    xr = node_positions(nc, [ref_node.int_label])[:, 0].astype(float)
    Rr = node_rotations(nc, [ref_node])[:, 0]
    local = np.einsum('tji,tnj->tni', Rr, X - xr[:, None, :])
    return local - local[0]


def _reduce_components(data, comps):
    """ data (..., ncomp): the component, or the norm of more components """
    if len(comps) == 1:
        return data[..., comps[0]]
    return np.linalg.norm(data[..., list(comps)], axis=-1)

# -----------------------------------------------------------
# Field meshes: the meshes of the confirmed flexible components
# (flexlib.py). Their custom properties tell what they draw:
#   'blendyn_field_family': 'BEAM', 'SHELL4' or 'MEMBRANE4';
#   plates: 'blendyn_nodes', the node labels, one per vertex, and
#           'blendyn_elems', the element labels, one per face;
#   beams: 'blendyn_beam3' and 'blendyn_beam2', the element labels in
#          mesh order (beam3 first), 'blendyn_rings' and 'blendyn_sides':
#          each beam has rings x sides vertices, ring after ring, with
#          the rings equally spaced in the natural coordinate.

FLEXIBLE_TYPES = {etype for desc in FAMILIES.values() for etype in desc['types']}

# property of BLENDYN_PG_field_settings holding the settings of each family
FAMILY_PROP = {'BEAM': 'beam', 'SHELL4': 'shell4', 'MEMBRANE4': 'membrane4'}
_PROP_FAMILY = {prop: family for family, prop in FAMILY_PROP.items()}

PLAIN_MATERIAL = 'Blendyn Component'


def family_settings(mbs, family):
    return getattr(mbs.field, FAMILY_PROP[family])


def field_objects(mbs, family=None):
    """ Meshes of the confirmed flexible components (of a family) """
    return [comp.object for comp in mbs.flex_components
            if comp.state == 'CONFIRMED' and comp.object is not None
            and (family is None or comp.family == family)]


def available_families(mbs):
    types = {elem.type for elem in mbs.elems}
    return [fam for fam, desc in FAMILIES.items() if types.intersection(desc['types'])]


def _family_elems(mbs, family):
    return [elem for elem in mbs.elems if elem.type in FAMILIES[family]['types']]


def field_material_name(family):
    return 'Blendyn Field ' + FAMILIES[family]['label']


def get_field_material(family):
    """ Material coloring the meshes of a family by the field value
        (one per family, since the material holds the color range) """
    name = field_material_name(family)
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    attr = nodes.new('ShaderNodeAttribute')
    attr.name = 'Field'
    attr.attribute_type = 'GEOMETRY'
    attr.attribute_name = VALUE_ATTR
    attr.location = (-900, 300)
    maprange = nodes.new('ShaderNodeMapRange')
    maprange.name = 'Range'
    maprange.clamp = True
    maprange.location = (-650, 300)
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.name = 'Colormap'
    ramp.location = (-400, 300)
    links.new(attr.outputs['Fac'], maprange.inputs['Value'])
    links.new(maprange.outputs['Result'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def get_plain_material():
    """ Material of the meshes of flexible components without fields """
    mat = bpy.data.materials.get(PLAIN_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(PLAIN_MATERIAL)
        mat.diffuse_color = (0.6, 0.6, 0.6, 1.)
    return mat


def set_mesh_material(mesh, mat):
    if not mesh.materials:
        mesh.materials.append(mat)
    elif mesh.materials[0] != mat:
        mesh.materials[0] = mat


def set_material_colormap(mat, name):
    if mat.get('blendyn_colormap') == name:
        return
    ramp = mat.node_tree.nodes['Colormap'].color_ramp
    ramp.interpolation = 'LINEAR'
    pos, stops = colormap_stops(name)
    while len(ramp.elements) > 1:
        ramp.elements.remove(ramp.elements[-1])
    ramp.elements[0].position = 0.
    ramp.elements[0].color = tuple(stops[0]) + (1.,)
    for p, c in zip(pos[1:], stops[1:]):
        el = ramp.elements.new(float(p))
        el.color = tuple(c) + (1.,)
    mat['blendyn_colormap'] = name


def set_material_range(mat, vmin, vmax):
    maprange = mat.node_tree.nodes['Range']
    if maprange.inputs['From Min'].default_value != vmin:
        maprange.inputs['From Min'].default_value = vmin
    if maprange.inputs['From Max'].default_value != vmax:
        maprange.inputs['From Max'].default_value = vmax


def _beam_groups(mbs, obj):
    """ beam3 and beam2 elements of the beam field mesh, in mesh order """
    ed = mbs.elems
    groups = []
    for etype, nn in (('beam3', 3), ('beam2', 2)):
        labels = list(obj.get('blendyn_' + etype, []))
        if labels:
            groups.append((etype, nn, [ed[etype + '_' + str(label)] for label in labels]))
    return groups


def beam_shape(nn, xi):
    """ Shape functions and derivatives of the beam nodes at xi """
    xi = np.asarray(xi, dtype=float)
    if nn == 3:
        N = np.stack((xi*(xi - 1.)/2., 1. - xi**2, xi*(xi + 1.)/2.), axis=-1)
        dN = np.stack((xi - .5, -2.*xi, xi + .5), axis=-1)
    else:
        N = np.stack(((1. - xi)/2., (1. + xi)/2.), axis=-1)
        dN = np.stack((-.5*np.ones_like(xi), .5*np.ones_like(xi)), axis=-1)
    return N, dN

# -----------------------------------------------------------
# Field data: everything that is needed to color a mesh at any time,
# for the selected quantity. Values are already reduced to the mesh
# domain (corners or vertices) for all the time steps.

_field_cache = {}
# quantities in the output of each family
_available_cache = {}


def invalidate_cache():
    _field_cache.clear()
    _available_cache.clear()


def invalidate_object(name):
    """ To be called when the mesh of a component is built again """
    _field_cache.pop(name, None)


def _settings_key(mbs, obj, family):
    ff = family_settings(mbs, family)
    mesh = obj.data
    return (_file_stamp(nc_file_path(mbs)), mesh.name, len(mesh.vertices), len(mesh.loops),
            ff.quantity, ff.component, ff.ref_node, ff.sampling)


def _quantity(family, quantity):
    if quantity == 'DISP':
        return DISPLACEMENT
    for q in QUANTITIES[family]:
        if q[0] == quantity:
            return q
    raise KeyError(quantity)


def _ref_node(mbs, ff):
    try:
        return mbs.nodes[ff.ref_node] if ff.ref_node else None
    except KeyError:
        return None


def _units(nc, name):
    try:
        return nc.variables[name].getncattr('units')
    except (KeyError, AttributeError):
        return ''


def _plate_data(nc, mbs, obj, family):
    ff = family_settings(mbs, family)
    labels = list(obj['blendyn_nodes'])
    elems = list(obj['blendyn_elems'])
    mesh = obj.data
    corners = np.empty(len(mesh.loops), dtype=int)
    mesh.loops.foreach_get('vertex_index', corners)
    data = {}
    qid, qlabel, qdesc, comps = _quantity(family, ff.quantity)
    comp_label, comp = comps[int(ff.component)] if ff.component.isdigit() else comps[0]
    if qid == 'DISP':
        u = displacements(nc, mbs, labels, _ref_node(mbs, ff))
        data['values'] = _reduce_components(u, comp).astype(np.float32)
        data['domain'] = 'POINT'
        data['units'] = _units(nc, _node_var(labels[0], 'X')) if labels else ''
    else:
        prefix = FAMILIES[family]['prefix']
        ncomp = 6 if family == 'SHELL4' else 3
        names = [prefix + str(label) + '.' + qid for label in elems]
        items = [(name, ip*ncomp + c) for name in names for ip in range(4) for c in comp]
        ip = read_components(nc, items).reshape((-1, len(elems), 4, len(comp)))
        ip = _reduce_components(ip, tuple(range(len(comp))))
        weights = _IP_NEAREST if ff.sampling == 'IP' else _IP_EXTRAP
        corner = (ip @ weights.T).reshape((ip.shape[0], -1))
        if ff.sampling == 'NODAL_AVG':
            counts = np.bincount(corners, minlength=len(labels))
            values = np.zeros((corner.shape[0], len(labels)), dtype=np.float32)
            np.add.at(values, (slice(None), corners), corner)
            data['values'] = values/np.maximum(counts, 1)
            data['domain'] = 'POINT'
        else:
            data['values'] = corner.astype(np.float32)
            data['domain'] = 'CORNER'
        data['units'] = _units(nc, names[0]) if names else ''
    data['label'] = qlabel + ' ' + comp_label
    return data


def _beam_data(nc, mbs, obj):
    ff = family_settings(mbs, 'BEAM')
    rings = obj['blendyn_rings']
    xis = np.linspace(-1., 1., rings)
    groups = _beam_groups(mbs, obj)
    qid, qlabel, qdesc, comps = _quantity('BEAM', ff.quantity)
    comp_label, comp = comps[int(ff.component)] if ff.component.isdigit() else comps[0]
    data = {'domain': 'POINT', 'label': qlabel + ' ' + comp_label, 'units': ''}
    values = []
    ref_node = _ref_node(mbs, ff)
    for etype, nn, elems in groups:
        # values at the rings, (time steps, beams, rings)
        if qid == 'DISP':
            node_labels = [[elem.nodes[k].int_label for k in range(nn)] for elem in elems]
            flat = [label for labels in node_labels for label in labels]
            position = {label: i for i, label in enumerate(dict.fromkeys(flat))}
            uniq = list(position.keys())
            uidx = np.array([position[label] for label in flat])
            N, dN = beam_shape(nn, xis)
            u = displacements(nc, mbs, uniq, ref_node)[:, uidx].reshape((-1, len(elems), nn, 3))
            u = np.einsum('rk,tbkc->tbrc', N, u)
            values.append(_reduce_components(u, comp))
            data['units'] = _units(nc, _node_var(uniq[0], 'X'))
            continue
        prefix = FAMILIES['BEAM']['prefix']
        # components at the rings, (time steps, beams, rings, components),
        # interpolated before computing their norm
        if etype == 'beam3':
            names = [prefix + str(elem.int_label) + '.' + qid + sez for elem in elems for sez in ('_I', '_II')]
            ep = read_components(nc, [(name, c) for name in names for c in comp])
            ep = ep.reshape((-1, len(elems), 2, len(comp)))
            if ff.sampling == 'IP':
                ring = np.where(xis < 0., 0, 1)
                ep = ep[:, :, ring]
            else:
                vm = (ep[:, :, 0] + ep[:, :, 1])/2.
                dv = (ep[:, :, 1] - ep[:, :, 0])/(2.*_BEAM3_XI_EP)
                ep = vm[:, :, None] + dv[:, :, None]*xis[None, :, None]
        else:
            names = [prefix + str(elem.int_label) + '.' + qid for elem in elems]
            ep = read_components(nc, [(name, c) for name in names for c in comp])
            ep = np.repeat(ep.reshape((-1, len(elems), 1, len(comp))), rings, axis=2)
        values.append(_reduce_components(ep, tuple(range(len(comp)))))
        if names and not data['units']:
            data['units'] = _units(nc, names[0])
    sides = obj['blendyn_sides']
    values = np.concatenate([v.reshape((v.shape[0], -1)) for v in values], axis=1)
    data['values'] = np.repeat(values, sides, axis=1).astype(np.float32)
    return data


def available_quantities(mbs, family):
    """ Quantities of the family that are in the output, judging from
        the first element (the output of beam strains is optional) """
    ncfile = nc_file_path(mbs)
    key = (_file_stamp(ncfile), family)
    if key not in _available_cache:
        try:
            nc = get_nc_dataset(ncfile)
            elems = _family_elems(mbs, family)
            elem = next((e for e in elems if e.type == 'beam3'), elems[0])
            suffix = '_I' if elem.type == 'beam3' else ''
            name = FAMILIES[family]['prefix'] + str(elem.int_label) + '.'
            _available_cache[key] = {q[0] for q in QUANTITIES[family]
                                     if name + q[0] + suffix in nc.variables}
        except (IndexError, OSError, TypeError, AttributeError):
            return set()
    return _available_cache[key]


def get_field_data(scene, obj):
    mbs = scene.mbdyn
    family = obj['blendyn_field_family']
    key = _settings_key(mbs, obj, family)
    cached = _field_cache.get(obj.name)
    if cached is not None and cached[0] == key:
        return cached[1]
    nc = get_nc_dataset(nc_file_path(mbs))
    if family == 'BEAM':
        data = _beam_data(nc, mbs, obj)
    else:
        data = _plate_data(nc, mbs, obj, family)
    values = data['values']
    with np.errstate(invalid='ignore'):
        data['vmin'] = float(np.nanmin(values)) if values.size and not np.all(np.isnan(values)) else 0.
        data['vmax'] = float(np.nanmax(values)) if values.size and not np.all(np.isnan(values)) else 0.
    data['num_steps'] = values.shape[0]
    data['time'] = np.ma.filled(nc.variables['time'][:], np.nan).astype(float)
    _field_cache[obj.name] = (key, data)
    return data

# -----------------------------------------------------------
# Coloring of the meshes

def _set_attribute(mesh, name, atype, domain, prop, values):
    attr = mesh.attributes.get(name)
    if attr is not None and (attr.domain != domain or attr.data_type != atype):
        mesh.attributes.remove(attr)
        attr = None
    if attr is None:
        attr = mesh.attributes.new(name, atype, domain)
    attr.data.foreach_set(prop, values)
    return attr


def effective_range(ff, entries):
    """ Color range of a family: entries are (data, values at the frame)
        of all its meshes """
    if ff.range_mode == 'MANUAL':
        vmin, vmax = ff.vmin, ff.vmax
    else:
        if ff.range_mode == 'PER_FRAME':
            values = np.concatenate([np.ravel(values) for _, values in entries])
            ranges = [(float(np.nanmin(values)), float(np.nanmax(values)))] \
                    if values.size and not np.all(np.isnan(values)) else []
        else:
            ranges = [(data['vmin'], data['vmax']) for data, _ in entries]
        vmin = min((r[0] for r in ranges), default=0.)
        vmax = max((r[1] for r in ranges), default=0.)
    if ff.symmetric:
        m = max(abs(vmin), abs(vmax))
        vmin, vmax = -m, m
    return vmin, vmax


# state of the last update of each family, for the legends
_legend = {}


def fields_active(mbs):
    return mbs.field.enable and mbs.use_netcdf


def update_family_fields(scene, family, objs):
    """ Colors the meshes objs of a family by the selected quantity, at
        the current frame """
    mbs = scene.mbdyn
    ff = family_settings(mbs, family)
    entries = []
    for obj in objs:
        try:
            data = get_field_data(scene, obj)
        except (KeyError, IndexError, ValueError, OSError, RuntimeError) as err:
            message = "BLENDYN::update_family_fields(): could not color {}: {}".format(obj.name, err)
            print(message)
            logging.error(message)
            set_mesh_material(obj.data, get_plain_material())
            continue
        i0, i1, frac = frame_steps(scene.frame_current, mbs.load_frequency, data['num_steps'])
        values = data['values'][i0]*frac + data['values'][i1]*(1. - frac)
        if values.size != (len(obj.data.loops) if data['domain'] == 'CORNER' else len(obj.data.vertices)):
            # the mesh was changed after the data was cached
            invalidate_object(obj.name)
            continue
        time = data['time'][i0]*frac + data['time'][i1]*(1. - frac)
        entries.append((obj, data, values, time))
    if not entries:
        _legend.pop(family, None)
        return
    vmin, vmax = effective_range(ff, [(data, values) for _, data, values, _ in entries])
    mat = get_field_material(family)
    set_material_colormap(mat, ff.colormap)
    set_material_range(mat, vmin, vmax)
    lut = colormap_lut(ff.colormap)
    for obj, data, values, time in entries:
        mesh = obj.data
        _set_attribute(mesh, VALUE_ATTR, 'FLOAT', data['domain'], 'value',
                np.nan_to_num(values, nan=0.).astype(np.float32))
        colors = map_colors(values, vmin, vmax, lut)
        col = _set_attribute(mesh, COLOR_ATTR, 'FLOAT_COLOR', data['domain'], 'color', colors.ravel())
        if mesh.color_attributes.active_color_name != COLOR_ATTR:
            mesh.color_attributes.active_color = col
        try:
            if mesh.color_attributes.render_color_index != mesh.color_attributes.active_color_index:
                mesh.color_attributes.render_color_index = mesh.color_attributes.active_color_index
        except AttributeError:
            pass
        set_mesh_material(mesh, mat)
        mesh.update()
    data, time = entries[0][1], entries[0][3]
    _legend[family] = {'label': data['label'], 'units': data['units'], 'vmin': vmin, 'vmax': vmax,
                       'colormap': ff.colormap, 'time': float(time)}


def clear_family_fields(family, objs):
    """ Shows the meshes of a family without colors """
    for obj in objs:
        set_mesh_material(obj.data, get_plain_material())
    _legend.pop(family, None)


def update_fields(scene, families=None):
    """ Colors the meshes of the confirmed flexible components, of the
        given families only when families is not None (e.g. those whose
        nodes are animated: otherwise the colors would change on meshes
        that stand still) """
    mbs = scene.mbdyn
    for family in FAMILIES:
        objs = field_objects(mbs, family)
        if not objs:
            _legend.pop(family, None)
        elif fields_active(mbs) and (families is None or family in families):
            update_family_fields(scene, family, objs)
        else:
            clear_family_fields(family, objs)


# Called when the field settings change: set by flexlib.py to the update
# of the flexible components, which colors them as well
refresh_hook = None


def _refresh(self, context):
    if refresh_hook is not None:
        refresh_hook(context.scene)
    else:
        update_fields(context.scene)


@persistent
def clear_fields_cache(*args):
    invalidate_cache()
    _legend.clear()


def _remove_handler(handlers, name):
    for h in [h for h in handlers if getattr(h, '__name__', '') == name]:
        handlers.remove(h)


# the field meshes used to be updated on frame_change_pre, before the
# flexible components: remove the handler when reloading the add-on
_remove_handler(bpy.app.handlers.frame_change_pre, 'update_fields_handler')
_remove_handler(bpy.app.handlers.load_post, clear_fields_cache.__name__)
bpy.app.handlers.load_post.append(clear_fields_cache)

# -----------------------------------------------------------
# Settings

# references to the dynamic enum items must be kept alive
_enum_items = {}


def _pg_family(pg):
    """ Family of a BLENDYN_PG_field_family. pg.path_from_id() would
        search through all the scene data, which takes seconds with many
        nodes and elements """
    try:
        fs = pg.id_data.mbdyn.field
    except AttributeError:
        return None
    ptr = pg.as_pointer()
    for family, prop in FAMILY_PROP.items():
        if getattr(fs, prop).as_pointer() == ptr:
            return family
    return None


def _quantity_items(self, context):
    family = _pg_family(self)
    items = [('DISP', DISPLACEMENT[1], DISPLACEMENT[2], 0)]
    if family is not None:
        available = available_quantities(context.scene.mbdyn, family)
        items += [(q[0], q[1], q[2], i + 1) for i, q in enumerate(QUANTITIES[family])
                  if q[0] in available]
    _enum_items[(family, 'quantity')] = items
    return items


def _component_items(self, context):
    family = _pg_family(self)
    try:
        comps = _quantity(family, self.quantity)[3]
    except KeyError:
        comps = DISPLACEMENT[3]
    items = [(str(i), label, '', i) for i, (label, _) in enumerate(comps)]
    _enum_items[(family, 'component')] = items
    return items


def _update_quantity(self, context):
    # the values of the dynamic enums are stored as numbers, that may
    # not be valid any more: check them without reading the enums
    if self.get('component', 0) not in [it[3] for it in _component_items(self, context)]:
        self['component'] = 0
    _refresh(self, context)


class BLENDYN_PG_field_family(bpy.types.PropertyGroup):
    """ Field shown on the flexible components of a family """
    quantity: EnumProperty(
            items = _quantity_items,
            name = "Quantity",
            description = "Quantity shown",
            update = _update_quantity
    )
    component: EnumProperty(
            items = _component_items,
            name = "Component",
            description = "Component of the quantity shown",
            update = _refresh
    )
    ref_node: StringProperty(
            name = "Reference node",
            description = "Node whose frame is used for the displacements. "\
                    + "Without it, the displacements are in the global frame",
            default = "",
            update = _refresh
    )
    sampling: EnumProperty(
            items = [('IP', "Integration points", "Value of the closest integration point "\
                            + "(piecewise constant)", 0),
                     ('EXTRAPOLATED', "Extrapolated", "Values extrapolated from the integration "\
                             + "points to the element corners (beams: along the element)", 1),
                     ('NODAL_AVG', "Nodal average", "Extrapolated values averaged at the nodes "\
                             + "(shells and membranes only)", 2)],
            name = "Sampling",
            description = "How values at the integration points are shown on the mesh",
            default = 'EXTRAPOLATED',
            update = _refresh
    )
    range_mode: EnumProperty(
            items = [('GLOBAL', "Global", "Minimum and maximum over all time steps "\
                            + "and all the components of the family", 0),
                     ('PER_FRAME', "Per frame", "Minimum and maximum at the current frame", 1),
                     ('MANUAL', "Manual", "User-defined range", 2)],
            name = "Range",
            description = "Range of values mapped to the colormap",
            default = 'GLOBAL',
            update = _refresh
    )
    vmin: FloatProperty(
            name = "Min",
            description = "Value mapped to the first color",
            default = 0.,
            update = _refresh
    )
    vmax: FloatProperty(
            name = "Max",
            description = "Value mapped to the last color",
            default = 1.,
            update = _refresh
    )
    symmetric: BoolProperty(
            name = "Symmetric",
            description = "Make the range symmetric with respect to zero",
            default = False,
            update = _refresh
    )
    colormap: EnumProperty(
            items = [('VIRIDIS', "Viridis", "Perceptually uniform sequential colormap", 0),
                     ('COOLWARM', "Cool-warm", "Diverging colormap", 1),
                     ('JET', "Jet", "Rainbow colormap", 2)],
            name = "Colormap",
            default = 'VIRIDIS',
            update = _refresh
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_field_family class

bpy.utils.register_class(BLENDYN_PG_field_family)


class BLENDYN_PG_field_settings(bpy.types.PropertyGroup):
    enable: BoolProperty(
            name = "Show fields",
            description = "Color the flexible components by the selected fields",
            default = True,
            update = _refresh
    )
    show_legend: BoolProperty(
            name = "Legend",
            description = "Show the color legends in the 3D viewport",
            default = True,
            update = _refresh
    )
    edit_family: EnumProperty(
            items = [(fam, desc['label'], "Field shown on the " + desc['label'].lower(), i)
                     for i, (fam, desc) in enumerate(FAMILIES.items())],
            name = "Elements",
            description = "Family of flexible elements whose field settings are shown"
    )
    beam: PointerProperty(type = BLENDYN_PG_field_family)
    shell4: PointerProperty(type = BLENDYN_PG_field_family)
    membrane4: PointerProperty(type = BLENDYN_PG_field_family)
# -----------------------------------------------------------
# end of BLENDYN_PG_field_settings class

bpy.utils.register_class(BLENDYN_PG_field_settings)

# -----------------------------------------------------------
# Operators

class BLENDYN_OT_field_autorange(bpy.types.Operator):
    """ Sets the manual range to the minimum and maximum over all time
        steps and all the components of the family """
    bl_idname = "blendyn.field_autorange"
    bl_label = "Set range from data"

    def execute(self, context):
        mbs = context.scene.mbdyn
        family = mbs.field.edit_family
        objs = field_objects(mbs, family)
        if not objs:
            self.report({'ERROR'}, "No confirmed flexible components of this family")
            return {'CANCELLED'}
        data = [get_field_data(context.scene, obj) for obj in objs]
        ff = family_settings(mbs, family)
        ff.range_mode = 'MANUAL'
        ff.vmin = min(d['vmin'] for d in data)
        ff.vmax = max(d['vmax'] for d in data)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_field_autorange class


class BLENDYN_OT_field_solid_view(bpy.types.Operator):
    """ Shows the field colors in the Solid shading of the 3D viewports """
    bl_idname = "blendyn.field_solid_view"
    bl_label = "Show in Solid view"

    def execute(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                shading = area.spaces.active.shading
                shading.type = 'SOLID'
                shading.color_type = 'VERTEX'
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_field_solid_view class

# -----------------------------------------------------------
# Panel

class BLENDYN_PT_fields(bpy.types.Panel):
    """ Visualization of the fields of flexible elements - Toolbar Panel """
    bl_idname = "BLENDYN_PT_fields"
    bl_label = "Fields of flexible elements"
    bl_category = 'Blendyn'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return context.scene.mbdyn.use_netcdf

    def draw(self, context):
        layout = self.layout
        mbs = context.scene.mbdyn
        fs = mbs.field

        col = layout.column()
        col.prop(fs, "enable")
        col.prop(fs, "edit_family")
        family = fs.edit_family
        ff = family_settings(mbs, family)
        if not field_objects(mbs, family):
            box = col.box()
            box.label(text = "No confirmed components", icon = 'INFO')
            box.label(text = "of this family: see Flexible components")
            return

        col.prop(ff, "quantity")
        if not available_quantities(mbs, family):
            # e.g. results of an MBDyn version without NetCDF plate output
            box = col.box()
            box.label(text = "No internal forces or strains", icon = 'INFO')
            box.label(text = "in the results file: " + FAMILIES[family]['prefix']
                    + "<label>." + ", .".join(q[0] for q in QUANTITIES[family]))
        col.prop(ff, "component")
        if ff.quantity == 'DISP':
            col.prop_search(ff, "ref_node", mbs, "nodes")
        else:
            col.prop(ff, "sampling")

        col = layout.column()
        col.prop(ff, "colormap")
        col.prop(ff, "range_mode")
        if ff.range_mode == 'MANUAL':
            row = col.row(align = True)
            row.prop(ff, "vmin")
            row.prop(ff, "vmax")
        col.prop(ff, "symmetric")
        col.operator(BLENDYN_OT_field_autorange.bl_idname)

        col = layout.column()
        col.prop(fs, "show_legend")
        col.operator(BLENDYN_OT_field_solid_view.bl_idname)
# -----------------------------------------------------------
# end of BLENDYN_PT_fields class

# -----------------------------------------------------------
# Viewport legends, one for each family with colored components,
# side by side from the bottom-right corner

def _draw_legend():
    try:
        mbs = bpy.context.scene.mbdyn
        fs = mbs.field
        if not (fs.show_legend and fs.enable and _legend):
            return
        families = [f for f in FAMILIES if f in _legend and field_objects(mbs, f)]
        if not families:
            return
        region = bpy.context.region
        ui_scale = bpy.context.preferences.system.ui_scale
        # left of the sidebar when it overlaps the viewport
        right = region.width
        if bpy.context.preferences.system.use_region_overlap:
            for r in bpy.context.area.regions:
                if r.type == 'UI' and r.alignment == 'RIGHT' and r.width > 1:
                    right -= r.width
        w, h = 20*ui_scale, min(250*ui_scale, region.height*0.5)
        y0 = 40*ui_scale
        font = 0
        blf.size(font, 11*ui_scale)
        blf.color(font, 1., 1., 1., 1.)
        shader = gpu.shader.from_builtin('SMOOTH_COLOR')
        x_right = right - 10*ui_scale
        for k, family in enumerate(reversed(families)):
            leg = _legend[family]
            vmin, vmax = leg['vmin'], leg['vmax']
            ticks = ['{:.4g}'.format(vmin + (vmax - vmin)*i/4.) for i in range(5)]
            title = FAMILIES[family]['label'] + ': ' + leg['label'] \
                    + (' [' + leg['units'] + ']' if leg['units'] else '')
            tick_w = max(blf.dimensions(font, tick)[0] for tick in ticks)
            title_w = blf.dimensions(font, title)[0]
            block_w = max(w + 6*ui_scale + tick_w, title_w)
            x0 = x_right - block_w

            n = 32
            lut = _linear_to_srgb(colormap_lut(leg['colormap'], n))
            coords, colors, indices = [], [], []
            for i in range(n):
                y = y0 + h*i/(n - 1)
                coords += [(x0, y, 0.), (x0 + w, y, 0.)]
                colors += [tuple(lut[i]) + (1.,)]*2
                if i:
                    j = 2*i
                    indices += [(j - 2, j - 1, j + 1), (j - 2, j + 1, j)]
            batch = batch_for_shader(shader, 'TRIS', {"pos": coords, "color": colors}, indices = indices)
            gpu.state.blend_set('ALPHA')
            shader.bind()
            batch.draw(shader)
            gpu.state.blend_set('NONE')

            for i, tick in enumerate(ticks):
                blf.position(font, x0 + w + 6*ui_scale, y0 + h*i/4. - 4*ui_scale, 0)
                blf.draw(font, tick)
            blf.position(font, x0, y0 + h + 12*ui_scale, 0)
            blf.draw(font, title)
            if k == 0:
                blf.position(font, x0, y0 - 18*ui_scale, 0)
                blf.draw(font, 't = {:.4g}'.format(leg['time']))
            x_right = x0 - 30*ui_scale
    except (AttributeError, KeyError, ReferenceError):
        pass


_legend_handle = None


def register_legend():
    global _legend_handle
    if HAVE_GPU and _legend_handle is None and not bpy.app.background:
        _legend_handle = bpy.types.SpaceView3D.draw_handler_add(_draw_legend, (), 'WINDOW', 'POST_PIXEL')


def unregister_legend():
    global _legend_handle
    if _legend_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_legend_handle, 'WINDOW')
        _legend_handle = None
