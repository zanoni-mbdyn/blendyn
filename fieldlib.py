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
# Each family of flexible elements (shell4, membrane4, beams) is drawn by
# a single "field mesh", whose vertices are moved and colored by a frame
# change handler. The data of the selected quantity is read from the
# NetCDF output once, for all the time steps, and kept in memory.

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

FIELDS_COLLECTION = 'fields'
FIELD_MATERIAL = 'Blendyn Field'
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
# Field mesh construction

def _field_objects():
    return [obj for obj in bpy.data.objects if 'blendyn_field_family' in obj]


def _field_object(family):
    for obj in _field_objects():
        if obj['blendyn_field_family'] == family:
            return obj
    return None


def available_families(mbs):
    types = {elem.type for elem in mbs.elems}
    return [fam for fam, desc in FAMILIES.items() if types.intersection(desc['types'])]


def _family_elems(mbs, family):
    return [elem for elem in mbs.elems if elem.type in FAMILIES[family]['types']]


def _get_fields_collection(context):
    try:
        col = bpy.data.collections[FIELDS_COLLECTION]
    except KeyError:
        col = bpy.data.collections.new(FIELDS_COLLECTION)
    if col.name not in context.scene.collection.children:
        context.scene.collection.children.link(col)
    return col


def get_field_material():
    try:
        return bpy.data.materials[FIELD_MATERIAL]
    except KeyError:
        pass
    mat = bpy.data.materials.new(FIELD_MATERIAL)
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


def set_material_colormap(mat, name):
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


def set_material_range(mat, vmin, vmax):
    maprange = mat.node_tree.nodes['Range']
    if maprange.inputs['From Min'].default_value != vmin:
        maprange.inputs['From Min'].default_value = vmin
    if maprange.inputs['From Max'].default_value != vmax:
        maprange.inputs['From Max'].default_value = vmax


def _new_field_object(context, family, verts, faces):
    name = 'field.' + family.lower()
    old = bpy.data.objects.get(name)
    if old is not None:
        mesh = old.data
        bpy.data.objects.remove(old)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    _get_fields_collection(context).objects.link(obj)
    mesh.materials.append(get_field_material())
    obj['blendyn_field_family'] = family
    return obj


def build_plate_field(context, family):
    """ Mesh with one vertex per node and one quad per element """
    mbs = context.scene.mbdyn
    elems = _family_elems(mbs, family)
    node_idx = {}
    faces = []
    for elem in elems:
        face = []
        for k in range(4):
            label = elem.nodes[k].int_label
            face.append(node_idx.setdefault(label, len(node_idx)))
        faces.append(face)
    labels = list(node_idx.keys())
    verts = []
    for label in labels:
        try:
            verts.append(tuple(mbs.nodes['node_' + str(label)].initial_pos))
        except KeyError:
            verts.append((0., 0., 0.))
    obj = _new_field_object(context, family, verts, faces)
    obj['blendyn_nodes'] = labels
    obj['blendyn_elems'] = [elem.int_label for elem in elems]
    mesh = obj.data
    attr = mesh.attributes.new('blendyn_node', 'INT', 'POINT')
    attr.data.foreach_set('value', labels)
    attr = mesh.attributes.new('blendyn_elem', 'INT', 'FACE')
    attr.data.foreach_set('value', obj['blendyn_elems'])
    return obj


def _beam_groups(mbs, obj):
    """ beam3 and beam2 elements of the beam field mesh, in mesh order """
    ed = mbs.elems
    groups = []
    for etype, nn in (('beam3', 3), ('beam2', 2)):
        labels = list(obj.get('blendyn_' + etype, []))
        if labels:
            groups.append((etype, nn, [ed[etype + '_' + str(label)] for label in labels]))
    return groups


def _beam_shape(nn, xi):
    """ Shape functions and derivatives of the beam nodes at xi """
    xi = np.asarray(xi, dtype=float)
    if nn == 3:
        N = np.stack((xi*(xi - 1.)/2., 1. - xi**2, xi*(xi + 1.)/2.), axis=-1)
        dN = np.stack((xi - .5, -2.*xi, xi + .5), axis=-1)
    else:
        N = np.stack(((1. - xi)/2., (1. + xi)/2.), axis=-1)
        dN = np.stack((-.5*np.ones_like(xi), .5*np.ones_like(xi)), axis=-1)
    return N, dN


def build_beam_field(context, rings, sides):
    """ Tube mesh with rings x sides vertices per beam """
    mbs = context.scene.mbdyn
    elems = _family_elems(mbs, 'BEAM')
    beam3 = [elem for elem in elems if elem.type == 'beam3']
    beam2 = [elem for elem in elems if elem.type == 'beam2']
    nbeams = len(beam3) + len(beam2)
    nv = rings*sides
    # vertices placed on the chord, so that the mesh is not degenerate
    # before the first update
    verts = []
    xis = np.linspace(-1., 1., rings)
    for elem in beam3 + beam2:
        try:
            p0 = np.array(mbs.nodes['node_' + str(elem.nodes[0].int_label)].initial_pos)
            p1 = np.array(mbs.nodes['node_' + str(elem.nodes[len(elem.nodes) - 1].int_label)].initial_pos)
        except KeyError:
            p0, p1 = np.zeros(3), np.zeros(3)
        for xi in xis:
            p = p0 + (xi + 1.)/2.*(p1 - p0)
            verts.extend([tuple(p)]*sides)
    s = np.arange(rings - 1)[:, None]
    m = np.arange(sides)[None, :]
    quads = np.stack((s*sides + m, s*sides + (m + 1) % sides,
                      (s + 1)*sides + (m + 1) % sides, (s + 1)*sides + m), axis=-1).reshape((-1, 4))
    faces = (np.arange(nbeams)[:, None, None]*nv + quads[None]).reshape((-1, 4)).tolist()
    obj = _new_field_object(context, 'BEAM', verts, faces)
    obj['blendyn_beam3'] = [elem.int_label for elem in beam3]
    obj['blendyn_beam2'] = [elem.int_label for elem in beam2]
    obj['blendyn_rings'] = rings
    obj['blendyn_sides'] = sides
    mesh = obj.data
    labels = np.repeat([elem.int_label for elem in beam3 + beam2], nv)
    attr = mesh.attributes.new('blendyn_elem', 'INT', 'POINT')
    attr.data.foreach_set('value', labels.tolist())
    attr = mesh.attributes.new('blendyn_xi', 'FLOAT', 'POINT')
    attr.data.foreach_set('value', np.tile(np.repeat(xis, sides), nbeams).tolist())
    return obj

# -----------------------------------------------------------
# Field data: everything that is needed to update the mesh at any time,
# for the selected quantity. Values are already reduced to the mesh
# domain (corners or vertices) for all the time steps.

_field_cache = {}
# quantities in the output of each family
_available_cache = {}


def invalidate_cache():
    _field_cache.clear()
    _available_cache.clear()


def _settings_key(mbs, obj):
    fs = mbs.field
    return (nc_file_path(mbs), obj.name, obj.data.name, len(obj.data.vertices),
            fs.quantity, fs.component, fs.ref_node, fs.sampling)


def _quantity(family, quantity):
    if quantity == 'DISP':
        return DISPLACEMENT
    for q in QUANTITIES[family]:
        if q[0] == quantity:
            return q
    raise KeyError(quantity)


def _ref_node(mbs):
    try:
        return mbs.nodes[mbs.field.ref_node] if mbs.field.ref_node else None
    except KeyError:
        return None


def _units(nc, name):
    try:
        return nc.variables[name].getncattr('units')
    except (KeyError, AttributeError):
        return ''


def _plate_data(nc, mbs, obj, family):
    fs = mbs.field
    labels = list(obj['blendyn_nodes'])
    elems = list(obj['blendyn_elems'])
    mesh = obj.data
    corners = np.empty(len(mesh.loops), dtype=int)
    mesh.loops.foreach_get('vertex_index', corners)
    data = {'positions': node_positions(nc, labels)}
    qid, qlabel, qdesc, comps = _quantity(family, fs.quantity)
    comp_label, comp = comps[int(fs.component)] if fs.component.isdigit() else comps[0]
    if qid == 'DISP':
        u = displacements(nc, mbs, labels, _ref_node(mbs))
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
        weights = _IP_NEAREST if fs.sampling == 'IP' else _IP_EXTRAP
        corner = (ip @ weights.T).reshape((ip.shape[0], -1))
        if fs.sampling == 'NODAL_AVG':
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
    fs = mbs.field
    nd = mbs.nodes
    rings = obj['blendyn_rings']
    xis = np.linspace(-1., 1., rings)
    groups = _beam_groups(mbs, obj)
    qid, qlabel, qdesc, comps = _quantity('BEAM', fs.quantity)
    comp_label, comp = comps[int(fs.component)] if fs.component.isdigit() else comps[0]
    data = {'groups': [], 'domain': 'POINT', 'label': qlabel + ' ' + comp_label, 'units': ''}
    values = []
    ref_node = _ref_node(mbs)
    for etype, nn, elems in groups:
        node_labels = [[elem.nodes[k].int_label for k in range(nn)] for elem in elems]
        flat = [label for labels in node_labels for label in labels]
        position = {label: i for i, label in enumerate(dict.fromkeys(flat))}
        uniq = list(position.keys())
        uidx = np.array([position[label] for label in flat])
        X = node_positions(nc, uniq)
        R = node_rotations(nc, [nd['node_' + str(label)] for label in uniq])
        offsets = np.array([[tuple(elem.offsets[k].value) for k in range(nn)] for elem in elems])
        # points on the beam reference line, (time steps, beams, nodes, 3)
        Xb = X[:, uidx].reshape((-1, len(elems), nn, 3))
        Rb = R[:, uidx].reshape((-1, len(elems), nn, 3, 3))
        P = Xb + np.einsum('tbkij,bkj->tbki', Rb, offsets)
        # reference vectors of the section, normal to the initial chord
        # and carried along by the rotation of the nodes
        chord = P[0, :, -1] - P[0, :, 0]
        chord /= np.maximum(np.linalg.norm(chord, axis=-1, keepdims=True), 1e-12)
        e = np.eye(3)[np.argmin(np.abs(chord), axis=-1)]
        n0 = np.cross(chord, e)
        n0 /= np.maximum(np.linalg.norm(n0, axis=-1, keepdims=True), 1e-12)
        n0k = np.einsum('bkji,bj->bki', Rb[0], n0)
        W = np.einsum('tbkij,bkj->tbki', Rb, n0k)
        N, dN = _beam_shape(nn, xis)
        data['groups'].append({'P': P.astype(np.float32), 'W': W.astype(np.float32), 'N': N, 'dN': dN})

        # values at the rings, (time steps, beams, rings)
        if qid == 'DISP':
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
            if fs.sampling == 'IP':
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
    key = (ncfile, family)
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
    key = _settings_key(mbs, obj)
    cached = _field_cache.get(obj.name)
    if cached is not None and cached[0] == key:
        return cached[1]
    nc = get_nc_dataset(nc_file_path(mbs))
    family = obj['blendyn_field_family']
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
# Field mesh update

def _beam_positions(data, i0, i1, frac, radius, sides):
    theta = 2.*np.pi*np.arange(sides)/sides
    ct, st = np.cos(theta), np.sin(theta)
    res = []
    for g in data['groups']:
        P = g['P'][i0]*frac + g['P'][i1]*(1. - frac)
        W = g['W'][i0]*frac + g['W'][i1]*(1. - frac)
        p = np.einsum('rk,bki->bri', g['N'], P)
        t = np.einsum('rk,bki->bri', g['dN'], P)
        n = np.einsum('rk,bki->bri', g['N'], W)
        t /= np.maximum(np.linalg.norm(t, axis=-1, keepdims=True), 1e-12)
        n -= np.sum(n*t, axis=-1, keepdims=True)*t
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
        b = np.cross(t, n)
        v = p[:, :, None, :] + radius*(ct[None, None, :, None]*n[:, :, None, :] \
                + st[None, None, :, None]*b[:, :, None, :])
        res.append(v.reshape((-1, 3)))
    return np.concatenate(res) if res else np.zeros((0, 3))


def _set_attribute(mesh, name, atype, domain, prop, values):
    attr = mesh.attributes.get(name)
    if attr is not None and (attr.domain != domain or attr.data_type != atype):
        mesh.attributes.remove(attr)
        attr = None
    if attr is None:
        attr = mesh.attributes.new(name, atype, domain)
    attr.data.foreach_set(prop, values)
    return attr


def effective_range(mbs, data, values):
    fs = mbs.field
    if fs.range_mode == 'MANUAL':
        vmin, vmax = fs.vmin, fs.vmax
    elif fs.range_mode == 'PER_FRAME' and values.size and not np.all(np.isnan(values)):
        vmin, vmax = float(np.nanmin(values)), float(np.nanmax(values))
    else:
        vmin, vmax = data['vmin'], data['vmax']
    if fs.symmetric:
        m = max(abs(vmin), abs(vmax))
        vmin, vmax = -m, m
    return vmin, vmax


# state of the last update, for the legend
_legend = {}


def update_field_object(scene, obj):
    mbs = scene.mbdyn
    fs = mbs.field
    data = get_field_data(scene, obj)
    i0, i1, frac = frame_steps(scene.frame_current, mbs.load_frequency, data['num_steps'])
    mesh = obj.data
    if obj['blendyn_field_family'] == 'BEAM':
        pos = _beam_positions(data, i0, i1, frac, fs.beam_radius, obj['blendyn_sides'])
    else:
        P = data['positions']
        pos = P[i0]*frac + P[i1]*(1. - frac)
    if len(pos) == len(mesh.vertices):
        mesh.vertices.foreach_set('co', np.asarray(pos, dtype=np.float32).ravel())
    values = data['values'][i0]*frac + data['values'][i1]*(1. - frac)
    vmin, vmax = effective_range(mbs, data, values)
    _set_attribute(mesh, VALUE_ATTR, 'FLOAT', data['domain'], 'value',
            np.nan_to_num(values, nan=0.).astype(np.float32))
    colors = map_colors(values, vmin, vmax, colormap_lut(fs.colormap))
    col = _set_attribute(mesh, COLOR_ATTR, 'FLOAT_COLOR', data['domain'], 'color', colors.ravel())
    if mesh.color_attributes.active_color_name != COLOR_ATTR:
        mesh.color_attributes.active_color = col
    try:
        if mesh.color_attributes.render_color_index != mesh.color_attributes.active_color_index:
            mesh.color_attributes.render_color_index = mesh.color_attributes.active_color_index
    except AttributeError:
        pass
    mesh.update()
    set_material_range(get_field_material(), vmin, vmax)
    time = data['time'][i0]*frac + data['time'][i1]*(1. - frac)
    _legend.update({'label': data['label'], 'units': data['units'], 'vmin': vmin, 'vmax': vmax,
                    'colormap': fs.colormap, 'time': float(time)})


def update_fields(scene):
    """ Updates the field mesh of the active family, and hides the others """
    mbs = scene.mbdyn
    if not (mbs.field.enable and mbs.use_netcdf):
        return
    for obj in _field_objects():
        active = obj['blendyn_field_family'] == mbs.field.family
        if obj.hide_viewport == active:
            obj.hide_viewport = not active
            obj.hide_render = not active
        if not active:
            continue
        try:
            update_field_object(scene, obj)
        except (KeyError, IndexError, ValueError, OSError, RuntimeError) as err:
            message = "BLENDYN::update_fields(): could not update {}: {}".format(obj.name, err)
            print(message)
            logging.error(message)


@persistent
def update_fields_handler(scene, depsgraph=None):
    update_fields(scene)


@persistent
def clear_fields_cache(*args):
    invalidate_cache()
    _legend.clear()


def _remove_handler(handlers, name):
    for h in [h for h in handlers if getattr(h, '__name__', '') == name]:
        handlers.remove(h)


_remove_handler(bpy.app.handlers.frame_change_pre, update_fields_handler.__name__)
bpy.app.handlers.frame_change_pre.append(update_fields_handler)
_remove_handler(bpy.app.handlers.load_post, clear_fields_cache.__name__)
bpy.app.handlers.load_post.append(clear_fields_cache)

# -----------------------------------------------------------
# Settings

# references to the dynamic enum items must be kept alive
_enum_items = {}


def _family_items(self, context):
    mbs = context.scene.mbdyn
    items = [(fam, FAMILIES[fam]['label'], '', i)
             for i, fam in enumerate(FAMILIES) if fam in available_families(mbs)]
    if not items:
        items = [('NONE', 'None', 'No flexible elements', 0)]
    _enum_items['family'] = items
    return items


def _quantity_items(self, context):
    family = self.family if self.family in QUANTITIES else None
    items = [('DISP', DISPLACEMENT[1], DISPLACEMENT[2], 0)]
    if family is not None:
        available = available_quantities(context.scene.mbdyn, family)
        items += [(q[0], q[1], q[2], i + 1) for i, q in enumerate(QUANTITIES[family])
                  if q[0] in available]
    _enum_items['quantity'] = items
    return items


def _component_items(self, context):
    try:
        comps = _quantity(self.family, self.quantity)[3]
    except KeyError:
        comps = DISPLACEMENT[3]
    items = [(str(i), label, '', i) for i, (label, _) in enumerate(comps)]
    _enum_items['component'] = items
    return items


def _refresh(self, context):
    update_fields(context.scene)


def _update_family(self, context):
    # the values of the dynamic enums are stored as numbers, that may
    # not be valid any more: check them without reading the enums
    if self.get('quantity', 0) not in [it[3] for it in _quantity_items(self, context)]:
        self['quantity'] = 0
    _update_quantity(self, context)


def _update_quantity(self, context):
    if self.get('component', 0) not in [it[3] for it in _component_items(self, context)]:
        self['component'] = 0
    update_fields(context.scene)


def _update_colormap(self, context):
    set_material_colormap(get_field_material(), self.colormap)
    update_fields(context.scene)


class BLENDYN_PG_field_settings(bpy.types.PropertyGroup):
    enable: BoolProperty(
            name = "Show fields",
            description = "Update the field meshes when the frame changes",
            default = True,
            update = _refresh
    )
    family: EnumProperty(
            items = _family_items,
            name = "Elements",
            description = "Flexible elements whose field is shown",
            update = _update_family
    )
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
            items = [('GLOBAL', "Global", "Minimum and maximum over all time steps", 0),
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
            update = _update_colormap
    )
    beam_radius: FloatProperty(
            name = "Beam radius",
            description = "Radius of the tubes drawing the beams",
            default = 0.05,
            min = 0.,
            update = _refresh
    )
    beam_rings: IntProperty(
            name = "Rings",
            description = "Sections of each beam tube (applied when the fields are built)",
            default = 8,
            min = 2
    )
    beam_sides: IntProperty(
            name = "Sides",
            description = "Sides of the beam tubes (applied when the fields are built)",
            default = 8,
            min = 3
    )
    show_legend: BoolProperty(
            name = "Legend",
            description = "Show the color legend in the 3D viewport",
            default = True,
            update = _refresh
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_field_settings class

bpy.utils.register_class(BLENDYN_PG_field_settings)

# -----------------------------------------------------------
# Operators

def _set_element_collections_hidden(families, hidden):
    for family in families:
        col = bpy.data.collections.get(FAMILIES[family]['collection'])
        if col is not None:
            col.hide_viewport = hidden
            col.hide_render = hidden


class BLENDYN_OT_field_build(bpy.types.Operator):
    """ Builds the meshes showing the fields of the flexible elements """
    bl_idname = "blendyn.field_build"
    bl_label = "Build field meshes"

    hide_elements: BoolProperty(
            name = "Hide elements",
            description = "Hide the objects of the elements shown by the field meshes",
            default = True
    )

    def execute(self, context):
        scene = context.scene
        mbs = scene.mbdyn
        if not mbs.use_netcdf:
            self.report({'ERROR'}, "Field visualization needs NetCDF output")
            return {'CANCELLED'}
        families = available_families(mbs)
        if not families:
            self.report({'WARNING'}, "No flexible elements found")
            return {'CANCELLED'}
        invalidate_cache()
        fs = mbs.field
        for family in families:
            if family == 'BEAM':
                build_beam_field(context, fs.beam_rings, fs.beam_sides)
            else:
                build_plate_field(context, family)
        set_material_colormap(get_field_material(), fs.colormap)
        if self.hide_elements:
            _set_element_collections_hidden(families, True)
        # writing mesh data from a frame change handler while rendering
        # is safe only with a locked interface
        scene.render.use_lock_interface = True
        # the stored family may not be among the available ones
        if fs.get('family', 0) not in [list(FAMILIES).index(f) for f in families]:
            fs.family = families[0]
        update_fields(scene)
        self.report({'INFO'}, "Built field meshes for: " \
                + ", ".join(FAMILIES[f]['label'] for f in families))
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_field_build class


class BLENDYN_OT_field_remove(bpy.types.Operator):
    """ Removes the field meshes """
    bl_idname = "blendyn.field_remove"
    bl_label = "Remove field meshes"

    def execute(self, context):
        families = set()
        for obj in _field_objects():
            families.add(obj['blendyn_field_family'])
            mesh = obj.data
            bpy.data.objects.remove(obj)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        col = bpy.data.collections.get(FIELDS_COLLECTION)
        if col is not None and not col.objects:
            bpy.data.collections.remove(col)
        _set_element_collections_hidden(families, False)
        invalidate_cache()
        _legend.clear()
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_field_remove class


class BLENDYN_OT_field_autorange(bpy.types.Operator):
    """ Sets the manual range to the minimum and maximum over all time steps """
    bl_idname = "blendyn.field_autorange"
    bl_label = "Set range from data"

    def execute(self, context):
        mbs = context.scene.mbdyn
        obj = _field_object(mbs.field.family)
        if obj is None:
            self.report({'ERROR'}, "Build the field meshes first")
            return {'CANCELLED'}
        data = get_field_data(context.scene, obj)
        fs = mbs.field
        fs.range_mode = 'MANUAL'
        fs.vmin = data['vmin']
        fs.vmax = data['vmax']
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

        col = layout.column(align = True)
        row = col.row(align = True)
        row.operator(BLENDYN_OT_field_build.bl_idname, text = "Build")
        row.operator(BLENDYN_OT_field_remove.bl_idname, text = "Remove")
        built = bool(_field_objects())
        if not built:
            return

        col = layout.column()
        col.prop(fs, "enable")
        col.prop(fs, "family")
        col.prop(fs, "quantity")
        col.prop(fs, "component")
        if fs.quantity == 'DISP':
            col.prop_search(fs, "ref_node", mbs, "nodes")
        else:
            col.prop(fs, "sampling")

        col = layout.column()
        col.prop(fs, "colormap")
        col.prop(fs, "range_mode")
        if fs.range_mode == 'MANUAL':
            row = col.row(align = True)
            row.prop(fs, "vmin")
            row.prop(fs, "vmax")
        col.prop(fs, "symmetric")
        col.operator(BLENDYN_OT_field_autorange.bl_idname)

        if fs.family == 'BEAM':
            col = layout.column(align = True)
            col.prop(fs, "beam_radius")
            row = col.row(align = True)
            row.prop(fs, "beam_rings")
            row.prop(fs, "beam_sides")

        col = layout.column()
        col.prop(fs, "show_legend")
        col.operator(BLENDYN_OT_field_solid_view.bl_idname)
# -----------------------------------------------------------
# end of BLENDYN_PT_fields class

# -----------------------------------------------------------
# Viewport legend

def _draw_legend():
    try:
        scene = bpy.context.scene
        mbs = scene.mbdyn
        fs = mbs.field
        if not (fs.show_legend and fs.enable and _legend) or _field_object(fs.family) is None:
            return
        region = bpy.context.region
        ui_scale = bpy.context.preferences.system.ui_scale
        w, h = 20*ui_scale, min(250*ui_scale, region.height*0.5)
        x0 = region.width - 120*ui_scale
        y0 = region.height - h - 60*ui_scale

        n = 32
        lut = _linear_to_srgb(colormap_lut(_legend['colormap'], n))
        coords, colors, indices = [], [], []
        for i in range(n):
            y = y0 + h*i/(n - 1)
            coords += [(x0, y, 0.), (x0 + w, y, 0.)]
            colors += [tuple(lut[i]) + (1.,)]*2
            if i:
                k = 2*i
                indices += [(k - 2, k - 1, k + 1), (k - 2, k + 1, k)]
        shader = gpu.shader.from_builtin('SMOOTH_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": coords, "color": colors}, indices = indices)
        gpu.state.blend_set('ALPHA')
        shader.bind()
        batch.draw(shader)
        gpu.state.blend_set('NONE')

        font = 0
        blf.size(font, 11*ui_scale)
        blf.color(font, 1., 1., 1., 1.)
        vmin, vmax = _legend['vmin'], _legend['vmax']
        for i in range(5):
            v = vmin + (vmax - vmin)*i/4.
            blf.position(font, x0 + w + 6*ui_scale, y0 + h*i/4. - 4*ui_scale, 0)
            blf.draw(font, '{:.4g}'.format(v))
        title = _legend['label'] + (' [' + _legend['units'] + ']' if _legend['units'] else '')
        tw, _ = blf.dimensions(font, title)
        blf.position(font, min(x0, region.width - tw - 10*ui_scale), y0 + h + 12*ui_scale, 0)
        blf.draw(font, title)
        blf.position(font, x0, y0 - 18*ui_scale, 0)
        blf.draw(font, 't = {:.4g}'.format(_legend['time']))
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
