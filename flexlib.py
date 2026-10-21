# --------------------------------------------------------------------------
# Blendyn -- file flexlib.py
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

# Flexible components: groups of flexible elements of the same family
# (beams, shell4 or membrane4) drawn by a single mesh, e.g. the beams of a
# rotor blade.
#
# A component is defined by the user (or built by default, with the
# elements of a family that are not in other components), built in the
# reference configuration as a preview, and then confirmed: from then on,
# a frame change handler moves its mesh with the node objects, and colors
# it by the fields of fieldlib.py.
#
# Plates are drawn by a mesh with a vertex for each node and a face for
# each element. Beams are drawn by tubes with rings x sides vertices for
# each element. The section of the tube at a node is a closed curve given
# by the user (or interpolated along the span, or a circle), perpendicular
# to the reference line of the beam in the reference configuration; the
# sections then move with the interpolated rotation of the nodes, as the
# beam sections do in MBDyn.

import math
import heapq
import logging
from collections import deque

import bpy
import bmesh
from bpy.props import *
from bpy.app.handlers import persistent
from bpy_extras import anim_utils
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Quaternion, Euler, Vector

import numpy as np

from . import fieldlib
from .fieldlib import FAMILIES, FLEXIBLE_TYPES, beam_shape, _rotvec_to_matrix

SECTIONS_COLLECTION = 'sections'
OBJECT_PREFIX = 'flex.'

FAMILY_ITEMS = [(fam, desc['label'], desc['label'] + ' (' + ', '.join(desc['types']) + ' elements)', i)
                for i, (fam, desc) in enumerate(FAMILIES.items())]

# -----------------------------------------------------------
# Rotations

def _quat_to_matrix(q):
    """ Rotation matrices of the quaternions q (..., 4), as (w, x, y, z) """
    q = q/np.maximum(np.linalg.norm(q, axis=-1, keepdims=True), 1e-12)
    w, x, y, z = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    R = np.empty(q.shape[:-1] + (3, 3))
    R[..., 0, 0] = 1. - 2.*(y*y + z*z)
    R[..., 0, 1] = 2.*(x*y - w*z)
    R[..., 0, 2] = 2.*(x*z + w*y)
    R[..., 1, 0] = 2.*(x*y + w*z)
    R[..., 1, 1] = 1. - 2.*(x*x + z*z)
    R[..., 1, 2] = 2.*(y*z - w*x)
    R[..., 2, 0] = 2.*(x*z - w*y)
    R[..., 2, 1] = 2.*(y*z + w*x)
    R[..., 2, 2] = 1. - 2.*(x*x + y*y)
    return R


def _matrix_to_rotvec(R):
    """ Rotation vectors of the rotation matrices R (..., 3, 3), with
        angles in [0, pi] """
    c = np.clip((np.trace(R, axis1=-2, axis2=-1) - 1.)/2., -1., 1.)
    theta = np.arccos(c)
    # sin(theta) times the axis
    v = np.stack((R[..., 2, 1] - R[..., 1, 2], R[..., 0, 2] - R[..., 2, 0],
                  R[..., 1, 0] - R[..., 0, 1]), axis=-1)/2.
    s = np.sin(theta)
    with np.errstate(invalid='ignore', divide='ignore'):
        scale = np.where(s > 1e-6, theta/s, 1. + theta**2/6.)
    phi = v*scale[..., None]
    # close to pi the axis is taken from the symmetric part,
    # (R + R^T)/2 = cos(theta) I + (1 - cos(theta)) a a^T
    near = theta > math.pi - 1e-3
    if np.any(near):
        Rn, cn = R[near], c[near]
        B = ((Rn + np.swapaxes(Rn, -1, -2))/2. - cn[:, None, None]*np.eye(3))/(1. - cn)[:, None, None]
        diag = np.clip(np.diagonal(B, axis1=-2, axis2=-1), 0., None)
        i = np.argmax(diag, axis=-1)
        rows = np.arange(len(i))
        a = B[rows, i, :]/np.sqrt(np.maximum(diag[rows, i], 1e-12))[:, None]
        sign = np.where(np.sum(a*v[near], axis=-1) < 0., -1., 1.)
        phi[near] = a*(sign*theta[near])[:, None]
    return phi


def _transport(u, a, b):
    """ u rotated by the minimal rotation taking the unit vector a onto
        the unit vector b """
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if c < -1. + 1e-9:
        return u
    return u*c + np.cross(v, u) + v*np.dot(v, u)/(1. + c)

# -----------------------------------------------------------
# Nodes

def _reference_nodes(mbs, labels):
    """ Positions (N, 3) and orientations (N, 3, 3) of the nodes in the
        reference configuration (from the .log file) """
    x0 = np.zeros((len(labels), 3))
    q0 = np.tile((1., 0., 0., 0.), (len(labels), 1))
    for i, label in enumerate(labels):
        node = mbs.nodes.get('node_' + str(label))
        if node is not None:
            x0[i] = node.initial_pos
            q0[i] = node.initial_rot
    return x0, _quat_to_matrix(q0)


def _node_objects(mbs, labels):
    objs = []
    for label in labels:
        node = mbs.nodes.get('node_' + str(label))
        objs.append(bpy.data.objects.get(node.blender_object) if node is not None else None)
    return objs


def _channel(fcurves, path, n, current, frame):
    values = list(current)
    for i in range(n):
        fc = fcurves.find(path, index=i)
        if fc is not None:
            values[i] = fc.evaluate(frame)
    return values


def _animated_transform(obj, frame):
    """ Position and orientation of an object at the frame, from its
        animation: used for the objects that are not evaluated by the
        depsgraph, e.g. those disabled in the viewport """
    ad = obj.animation_data
    fcurves = None
    if ad is not None and ad.action is not None:
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        fcurves = cb.fcurves if cb is not None else None
    if fcurves is None:
        M = obj.matrix_world
        return M.to_translation(), M.to_3x3().normalized()
    loc = _channel(fcurves, 'location', 3, obj.location, frame)
    mode = obj.rotation_mode
    if mode == 'QUATERNION':
        R = Quaternion(_channel(fcurves, 'rotation_quaternion', 4, obj.rotation_quaternion, frame)).normalized().to_matrix()
    elif mode == 'AXIS_ANGLE':
        a = _channel(fcurves, 'rotation_axis_angle', 4, obj.rotation_axis_angle, frame)
        axis = Vector(a[1:])
        R = Matrix.Rotation(a[0], 3, axis.normalized()) if axis.length > 0. else Matrix.Identity(3)
    else:
        R = Euler(_channel(fcurves, 'rotation_euler', 3, obj.rotation_euler, frame), mode).to_matrix()
    return Vector(loc), R


def node_frames(objs, x0, R0, depsgraph, frame):
    """ Current positions (N, 3) and orientations (N, 3, 3) of the node
        objects; nodes without object keep the reference ones """
    X, R = x0.copy(), R0.copy()
    evaluated = [(k, obj.evaluated_get(depsgraph)) for k, obj in enumerate(objs) if obj is not None]
    good = [(k, ev) for k, ev in evaluated if ev.is_evaluated]
    if good:
        idx = [k for k, _ in good]
        M = np.array([ev.matrix_world for _, ev in good])
        X[idx] = M[:, :3, 3]
        A = M[:, :3, :3]
        # node objects may be scaled
        R[idx] = A/np.maximum(np.linalg.norm(A, axis=-2, keepdims=True), 1e-12)
    if len(good) < len(evaluated):
        done = {k for k, _ in good}
        for k, obj in enumerate(objs):
            if obj is not None and k not in done:
                loc, rot = _animated_transform(obj, frame)
                X[k] = loc
                R[k] = np.array(rot)
    return X, R


def nodes_animated(objs):
    return all(obj is None or (obj.animation_data is not None and obj.animation_data.action is not None)
               for obj in objs)

# -----------------------------------------------------------
# Components and their elements

def _owner_component(pg):
    """ Flexible component holding a section entry. pg.path_from_id()
        would search through all the scene data, which takes seconds with
        many nodes and elements """
    ptr = pg.as_pointer()
    for comp in pg.id_data.mbdyn.flex_components:
        if any(sec.as_pointer() == ptr for sec in comp.sections):
            return comp
    return None


def component_elems(mbs, comp):
    """ Elements of the component that exist and belong to its family """
    ed = mbs.elems
    types = FAMILIES[comp.family]['types']
    return [ed[ce.elem] for ce in comp.elements if ce.elem in ed and ed[ce.elem].type in types]


def component_of_object(mbs, obj):
    for comp in mbs.flex_components:
        if comp.object == obj:
            return comp
    return None


def default_component(mbs, family):
    for comp in mbs.flex_components:
        if comp.is_default and comp.family == family:
            return comp
    return None


def _user_assigned(mbs):
    return {ce.elem for comp in mbs.flex_components if not comp.is_default for ce in comp.elements}


def _set_elements(comp, keys):
    comp.elements.clear()
    for key in keys:
        ce = comp.elements.add()
        ce.elem = key
        ce.name = key
    comp.el_index = 0


def _unique_name(mbs, base):
    names = {comp.name for comp in mbs.flex_components}
    if base not in names:
        return base
    k = 1
    while base + '.' + str(k).zfill(3) in names:
        k += 1
    return base + '.' + str(k).zfill(3)


def new_component(mbs, family, name=None, is_default=False):
    comp = mbs.flex_components.add()
    comp.name = _unique_name(mbs, name or FAMILIES[family]['label'][:-1])
    comp.family = family
    comp.is_default = is_default
    mbs.fc_index = len(mbs.flex_components) - 1
    return comp


def _delete_object(comp):
    obj = comp.object
    if obj is not None:
        fieldlib.invalidate_object(obj.name)
        _runtime.pop(obj.name, None)
        mesh = obj.data
        bpy.data.objects.remove(obj)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    comp.object = None


def remove_component(context, idx):
    mbs = context.scene.mbdyn
    comp = mbs.flex_components[idx]
    family, is_default = comp.family, comp.is_default
    _delete_object(comp)
    mbs.flex_components.remove(idx)
    mbs.fc_index = min(mbs.fc_index, max(len(mbs.flex_components) - 1, 0))
    if not is_default:
        # its elements go back to the default component
        refresh_default(context, family)


def _show_fields_of(mbs, family):
    """ Shows the field settings of the family in the Fields panel, unless
        it already shows a family with confirmed components """
    if not fieldlib.field_objects(mbs, mbs.field.edit_family):
        mbs.field.edit_family = family


def refresh_default(context, family):
    """ Updates the default component of the family, holding the elements
        that are not in other components: built and confirmed """
    mbs = context.scene.mbdyn
    assigned = _user_assigned(mbs)
    keys = [elem.name for elem in mbs.elems
            if elem.type in FAMILIES[family]['types'] and elem.name not in assigned]
    comp = default_component(mbs, family)
    if not keys:
        if comp is not None:
            remove_component(context, list(mbs.flex_components).index(comp))
        return None
    active = mbs.fc_index
    if comp is None:
        comp = new_component(mbs, family, FAMILIES[family]['label'], is_default=True)
        mbs.fc_index = active if active < len(mbs.flex_components) - 1 else mbs.fc_index
    if [ce.elem for ce in comp.elements] != keys or comp.object is None:
        _set_elements(comp, keys)
        build_component(context, comp)
    comp.state = 'CONFIRMED'
    _show_fields_of(mbs, family)
    return comp


def assign_elements(context, comp, keys):
    """ Adds the elements to the component, removing them from the
        others; the components that change are built again """
    mbs = context.scene.mbdyn
    ed = mbs.elems
    types = FAMILIES[comp.family]['types']
    keys = [key for key in dict.fromkeys(keys) if key in ed and ed[key].type in types]
    present = {ce.elem for ce in comp.elements}
    new = [key for key in keys if key not in present]
    if not new:
        return 0
    newset = set(new)
    for other in mbs.flex_components:
        if other == comp or other.is_default:
            continue
        kept = [ce.elem for ce in other.elements if ce.elem not in newset]
        if len(kept) != len(other.elements):
            _set_elements(other, kept)
            if other.object is not None:
                build_component(context, other)
    for key in new:
        ce = comp.elements.add()
        ce.elem = key
        ce.name = key
    if comp.object is not None:
        build_component(context, comp)
    if not comp.is_default:
        refresh_default(context, comp.family)
    return len(new)


def selected_elem_keys(context):
    """ Keys of the elements drawn by the selected faces of the meshes of
        the flexible components, and their families """
    mbs = context.scene.mbdyn
    ed = mbs.elems
    if context.mode == 'EDIT_MESH':
        objs = list(context.objects_in_mode)
    else:
        objs = list(context.selected_objects)
    keys, families = [], set()
    for obj in objs:
        comp = component_of_object(mbs, obj) if obj.type == 'MESH' else None
        if comp is None:
            continue
        if obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            layer = bm.faces.layers.int.get('blendyn_elem')
            labels = [face[layer] for face in bm.faces if face.select] if layer is not None else []
        else:
            mesh = obj.data
            attr = mesh.attributes.get('blendyn_elem')
            if attr is None or attr.domain != 'FACE':
                continue
            sel = np.zeros(len(mesh.polygons), dtype=bool)
            mesh.polygons.foreach_get('select', sel)
            values = np.zeros(len(mesh.polygons), dtype=np.int32)
            attr.data.foreach_get('value', values)
            labels = values[sel].tolist()
        for label in dict.fromkeys(labels):
            for etype in FAMILIES[comp.family]['types']:
                key = etype + '_' + str(label)
                if key in ed:
                    keys.append(key)
                    families.add(comp.family)
                    break
    return keys, families

# -----------------------------------------------------------
# Sections

def _boundary_loop(co, edges, faces):
    """ Vertex indices of the outline through the first vertex: the
        edges not shared by two faces, walked from vertex 0 (or from the
        first end of an open outline) """
    count = {}
    for face in faces:
        n = len(face)
        for i in range(n):
            key = tuple(sorted((face[i], face[(i + 1) % n])))
            count[key] = count.get(key, 0) + 1
    adj = {}
    for a, b in edges:
        if count.get(tuple(sorted((a, b))), 0) < 2:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    if not adj:
        return []
    start = 0 if 0 in adj else min(adj)
    if len(adj[start]) != 2:
        # open outline: start from the end of its piece with the lowest index
        piece, todo = set(), [start]
        while todo:
            v = todo.pop()
            if v not in piece:
                piece.add(v)
                todo.extend(adj[v])
        ends = sorted(v for v in piece if len(adj[v]) == 1)
        if ends:
            start = ends[0]
    loop, prev, v = [start], None, start
    while True:
        nxt = [w for w in adj[v] if w != prev]
        if not nxt or nxt[0] == start:
            break
        prev, v = v, nxt[0]
        if v in loop:
            break
        loop.append(v)
    return loop


def resample_loop(pts, sides):
    """ sides points equally spaced along the closed polyline pts (n, 2),
        starting from its first point """
    closed = np.vstack((pts, pts[:1]))
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    cum = np.concatenate(([0.], np.cumsum(seg)))
    if cum[-1] <= 0.:
        raise ValueError("degenerate section")
    s = cum[-1]*np.arange(sides)/sides
    return np.stack((np.interp(s, cum, closed[:, 0]), np.interp(s, cum, closed[:, 1])), axis=1)


def circle_section(radius, sides):
    phi = 2.*np.pi*np.arange(sides)/sides
    return np.stack((radius*np.cos(phi), radius*np.sin(phi)), axis=1)


def section_from_object(obj, depsgraph, sides):
    """ Section drawn by a curve (or a mesh with edges only) in its local
        X-Y plane: the points, counterclockwise from the first one and
        resampled to sides points, scaled by the object scale, and the
        rotation of the object about its Z axis """
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    try:
        co = np.array([v.co[:2] for v in mesh.vertices]).reshape((-1, 2))
        edges = [tuple(e.vertices) for e in mesh.edges]
        faces = [tuple(p.vertices) for p in mesh.polygons]
    finally:
        ev.to_mesh_clear()
    loop = _boundary_loop(co, edges, faces)
    if len(loop) < 3:
        raise ValueError("the section " + obj.name + " has no closed outline")
    M = obj.matrix_basis
    scale = M.to_scale()
    pts = co[loop]*np.array((scale[0], scale[1]))
    # counterclockwise, keeping the first point
    area = np.sum(pts[:, 0]*np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1)*pts[:, 1])
    if area < 0.:
        pts = np.vstack((pts[:1], pts[:0:-1]))
    R = M.to_3x3().normalized()
    theta = math.atan2(R[1][0], R[0][0])
    return resample_loop(pts, sides), theta


def _sections_collection(context):
    col = bpy.data.collections.get(SECTIONS_COLLECTION)
    if col is None:
        col = bpy.data.collections.new(SECTIONS_COLLECTION)
        context.scene.collection.children.link(col)
    return col


def new_section_object(context, name, pts):
    """ Closed polyline curve in the X-Y plane, in the sections collection """
    cv = bpy.data.curves.new(name, 'CURVE')
    cv.dimensions = '2D'
    cv.fill_mode = 'NONE'
    spline = cv.splines.new('POLY')
    spline.points.add(len(pts) - 1)
    for p, xy in zip(spline.points, pts):
        p.co = (float(xy[0]), float(xy[1]), 0., 1.)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(cv.name, cv)
    _sections_collection(context).objects.link(obj)
    return obj

# -----------------------------------------------------------
# Geometry of the beams in the reference configuration

def _beam_layout(mbs, elems):
    """ Node labels, offsets and number of nodes of the beams """
    labels = [[elem.nodes[k].int_label for k in range(3 if elem.type == 'beam3' else 2)] for elem in elems]
    offsets = [np.array([tuple(elem.offsets[k].value) for k in range(len(lab))]) for elem, lab in zip(elems, labels)]
    return labels, offsets


def _traverse(ends, T0, R0, node_index):
    """ Direction of each beam along the component (+1 from its first to
        its last node), and the reference axis 2 of the sections at the
        rings: perpendicular to the tangent, carried along the beams by
        the minimal rotations between the tangents. Each connected part of
        the component starts from its end with the lowest node label (or
        from the first node of its first beam, for closed loops), where the
        axis 2 comes from the axis of the node most perpendicular to the
        tangent """
    E, rings = T0.shape[:2]
    adj = {}
    for e, (a, b) in enumerate(ends):
        adj.setdefault(a, []).append(e)
        adj.setdefault(b, []).append(e)
    sigma = np.ones(E)
    U = np.zeros((E, rings, 3))
    visited = [False]*E
    while not all(visited):
        free = [n for n, es in adj.items() if len(es) == 1 and not visited[es[0]]]
        if free:
            start = min(free)
            e0 = adj[start][0]
        else:
            e0 = visited.index(False)
            start = ends[e0][0]
        sgn = 1. if ends[e0][0] == start else -1.
        tau0 = sgn*T0[e0, 0 if sgn > 0 else -1]
        axes = R0[node_index[start]].T
        k = int(np.argmin(np.abs(axes @ tau0)))
        u = axes[k] - np.dot(axes[k], tau0)*tau0
        u /= np.linalg.norm(u)
        visited[e0] = True
        queue = deque([(e0, start, u, tau0)])
        while queue:
            e, entry, u, tau_prev = queue.popleft()
            sgn = 1. if ends[e][0] == entry else -1.
            sigma[e] = sgn
            for r in (range(rings) if sgn > 0 else range(rings - 1, -1, -1)):
                tau = sgn*T0[e, r]
                u = _transport(u, tau_prev, tau)
                u = u - np.dot(u, tau)*tau
                u /= max(np.linalg.norm(u), 1e-12)
                U[e, r] = u
                tau_prev = tau
            exit_node = ends[e][1] if sgn > 0 else ends[e][0]
            for e2 in adj[exit_node]:
                if not visited[e2]:
                    visited[e2] = True
                    queue.append((e2, exit_node, u.copy(), tau_prev.copy()))
    return sigma, U


def _station_graph(labels, lengths):
    """ Graph of the nodes along the beams: each beam joins its
        consecutive nodes, with the arc lengths between them """
    graph = {}
    for lab, lens in zip(labels, lengths):
        for a, b, d in zip(lab[:-1], lab[1:], lens):
            graph.setdefault(a, {})[b] = min(d, graph.get(a, {}).get(b, np.inf))
            graph.setdefault(b, {})[a] = min(d, graph.get(b, {}).get(a, np.inf))
    return graph


def _connected_parts(graph):
    parts, seen = [], set()
    for n in sorted(graph):
        if n in seen:
            continue
        part, todo = [], [n]
        seen.add(n)
        while todo:
            v = todo.pop()
            part.append(v)
            for w in graph[v]:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        parts.append(part)
    return parts


def _dijkstra(graph, source):
    dist = {source: 0.}
    heap = [(0., source)]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist.get(v, np.inf):
            continue
        for w, l in graph[v].items():
            if d + l < dist.get(w, np.inf):
                dist[w] = d + l
                heapq.heappush(heap, (d + l, w))
    return dist


def station_sections(graph, positions, assigned, default):
    """ Section (points, angle) at each node of the graph: the assigned
        ones, the others interpolated along the span. On a chain of beams,
        linearly in the arc length between the closest assigned nodes on
        each side (the closest one beyond the last); elsewhere, the closest
        assigned node along the beams. Parts without assigned nodes take
        the closest one in space, or the default """
    res = {}
    for part in _connected_parts(graph):
        mine = [n for n in part if n in assigned]
        if not mine:
            if assigned:
                for n in part:
                    near = min(assigned, key=lambda a: np.linalg.norm(positions[a] - positions[n]))
                    res[n] = assigned[near]
            else:
                for n in part:
                    res[n] = default
            continue
        chain = all(len(graph[n]) <= 2 for n in part) and \
                sum(len(graph[n]) for n in part) == 2*(len(part) - 1)
        if chain:
            start = min(n for n in part if len(graph[n]) <= 1) if len(part) > 1 else part[0]
            s, order, prev, v = {start: 0.}, [start], None, start
            while True:
                nxt = [w for w in graph[v] if w != prev]
                if not nxt:
                    break
                s[nxt[0]] = s[v] + graph[v][nxt[0]]
                prev, v = v, nxt[0]
                order.append(v)
            known = sorted(mine, key=lambda n: s[n])
            ks = np.array([s[n] for n in known])
            for n in part:
                if n in assigned:
                    res[n] = assigned[n]
                    continue
                j = int(np.searchsorted(ks, s[n]))
                if j == 0:
                    res[n] = assigned[known[0]]
                elif j == len(known):
                    res[n] = assigned[known[-1]]
                else:
                    a, b = known[j - 1], known[j]
                    w = (s[n] - s[a])/max(s[b] - s[a], 1e-12)
                    res[n] = (assigned[a][0]*(1. - w) + assigned[b][0]*w,
                              assigned[a][1]*(1. - w) + assigned[b][1]*w)
        else:
            dists = {a: _dijkstra(graph, a) for a in mine}
            for n in part:
                near = min(mine, key=lambda a: dists[a].get(n, np.inf))
                res[n] = assigned[near]
    return res


def beam_reference_geometry(context, comp, elems, rings, sides, warnings):
    """ Reference line points P0 (E, rings, 3), section offsets
        A (E, rings, sides, 3) from them, and direction of each beam along
        the component, in the reference configuration """
    mbs = context.scene.mbdyn
    depsgraph = context.evaluated_depsgraph_get()
    labels, offsets = _beam_layout(mbs, elems)
    uniq = list(dict.fromkeys(label for lab in labels for label in lab))
    node_index = {label: i for i, label in enumerate(uniq)}
    x0, R0 = _reference_nodes(mbs, uniq)
    E = len(elems)
    xis = np.linspace(-1., 1., rings)
    fine = np.linspace(-1., 1., 33)
    P0 = np.empty((E, rings, 3))
    T0 = np.empty((E, rings, 3))
    lengths = []
    for e, (lab, f) in enumerate(zip(labels, offsets)):
        nn = len(lab)
        idx = [node_index[label] for label in lab]
        p = x0[idx] + np.einsum('kij,kj->ki', R0[idx], f)
        N, dN = beam_shape(nn, xis)
        P0[e] = N @ p
        T0[e] = dN @ p
        # arc lengths between the nodes, along the beam
        Nf, _ = beam_shape(nn, fine)
        cum = np.concatenate(([0.], np.cumsum(np.linalg.norm(np.diff(Nf @ p, axis=0), axis=1))))
        if nn == 3:
            lengths.append((cum[16], cum[-1] - cum[16]))
        else:
            lengths.append((cum[-1],))
    T0 /= np.maximum(np.linalg.norm(T0, axis=-1, keepdims=True), 1e-12)
    sigma, U = _traverse([(lab[0], lab[-1]) for lab in labels], T0, R0, node_index)

    # sections at the nodes
    assigned = {}
    for sec in comp.sections:
        if not sec.node or sec.curve is None:
            continue
        node = mbs.nodes.get(sec.node)
        if node is None or node.int_label not in node_index:
            warnings.append("node " + sec.node + " is not a node of the component: section ignored")
            continue
        try:
            assigned[node.int_label] = section_from_object(sec.curve, depsgraph, sides)
        except ValueError as err:
            warnings.append(str(err))
    positions = {label: x0[i] for label, i in node_index.items()}
    stations = station_sections(_station_graph(labels, lengths), positions, assigned,
                                (circle_section(comp.radius, sides), 0.))
    C = np.array([stations[label][0] for label in uniq])
    TH = np.array([stations[label][1] for label in uniq])

    A = np.empty((E, rings, sides, 3))
    for e, lab in enumerate(labels):
        idx = [node_index[label] for label in lab]
        N, _ = beam_shape(len(lab), xis)
        c = np.einsum('rk,ksd->rsd', N, C[idx])
        th = N @ TH[idx]
        ct, st = np.cos(th)[:, None], np.sin(th)[:, None]
        l2 = ct*c[..., 0] - st*c[..., 1]
        l3 = st*c[..., 0] + ct*c[..., 1]
        a1 = sigma[e]*T0[e]
        a2 = U[e]
        a3 = np.cross(a1, a2)
        A[e] = l2[..., None]*a2[:, None, :] + l3[..., None]*a3[:, None, :]
    return P0, A, sigma

# -----------------------------------------------------------
# Meshes

def _elements_collection(context, family):
    name = FAMILIES[family]['collection']
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        context.scene.collection.children.link(col)
    return col


_BUILD_PROPS = ('blendyn_nodes', 'blendyn_elems', 'blendyn_beam3', 'blendyn_beam2',
                'blendyn_rings', 'blendyn_sides')


def _replace_mesh(context, comp, verts, faces):
    mesh = bpy.data.meshes.new(OBJECT_PREFIX + comp.name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = comp.object
    if obj is None:
        obj = bpy.data.objects.new(OBJECT_PREFIX + comp.name, mesh)
        _elements_collection(context, comp.family).objects.link(obj)
        comp.object = obj
    else:
        old = obj.data
        obj.data = mesh
        if old is not None and old.users == 0:
            bpy.data.meshes.remove(old)
        for prop in _BUILD_PROPS:
            if prop in obj:
                del obj[prop]
    fieldlib.set_mesh_material(mesh, fieldlib.get_plain_material())
    obj.mbdyn.type = 'component'
    obj.mbdyn.dkey = comp.name
    obj['blendyn_field_family'] = comp.family
    obj['blendyn_types'] = list(FAMILIES[comp.family]['types'])
    fieldlib.invalidate_object(obj.name)
    _runtime.pop(obj.name, None)
    return obj


def _set_thickness(comp):
    obj = comp.object
    if obj is None:
        return
    mod = obj.modifiers.get('Thickness')
    if comp.family == 'BEAM' or comp.thickness <= 0.:
        if mod is not None:
            obj.modifiers.remove(mod)
        return
    if mod is None:
        mod = obj.modifiers.new('Thickness', 'SOLIDIFY')
        mod.offset = 0.
        mod.use_even_offset = True
    mod.thickness = comp.thickness


def _build_plates(context, comp, elems):
    mbs = context.scene.mbdyn
    node_idx = {}
    faces = []
    for elem in elems:
        faces.append([node_idx.setdefault(elem.nodes[k].int_label, len(node_idx)) for k in range(4)])
    labels = list(node_idx.keys())
    x0, _ = _reference_nodes(mbs, labels)
    obj = _replace_mesh(context, comp, x0.tolist(), faces)
    obj['blendyn_nodes'] = labels
    obj['blendyn_elems'] = [elem.int_label for elem in elems]
    mesh = obj.data
    mesh.attributes.new('blendyn_node', 'INT', 'POINT').data.foreach_set('value', labels)
    mesh.attributes.new('blendyn_elem', 'INT', 'FACE').data.foreach_set('value', obj['blendyn_elems'])
    _set_thickness(comp)
    return obj


def _build_beams(context, comp, elems, warnings):
    # beam3 first, as fieldlib expects
    elems = [elem for elem in elems if elem.type == 'beam3'] + [elem for elem in elems if elem.type == 'beam2']
    rings, sides = comp.rings, comp.sides
    P0, A, sigma = beam_reference_geometry(context, comp, elems, rings, sides, warnings)
    E = len(elems)
    verts = (P0[:, :, None, :] + A).reshape((-1, 3))
    s = np.arange(rings - 1)[:, None]
    m = np.arange(sides)[None, :]
    quads = np.stack((s*sides + m, s*sides + (m + 1) % sides,
                      (s + 1)*sides + (m + 1) % sides, (s + 1)*sides + m), axis=-1).reshape((-1, 4))
    # outward normals: the rings go along the component
    faces = np.where(sigma[:, None, None] > 0., quads[None], quads[None, :, ::-1])
    faces = (faces + (np.arange(E)*rings*sides)[:, None, None]).reshape((-1, 4))
    obj = _replace_mesh(context, comp, verts.tolist(), faces.tolist())
    obj['blendyn_beam3'] = [elem.int_label for elem in elems if elem.type == 'beam3']
    obj['blendyn_beam2'] = [elem.int_label for elem in elems if elem.type == 'beam2']
    obj['blendyn_rings'] = rings
    obj['blendyn_sides'] = sides
    mesh = obj.data
    labels = np.repeat([elem.int_label for elem in elems], (rings - 1)*sides)
    mesh.attributes.new('blendyn_elem', 'INT', 'FACE').data.foreach_set('value', labels.tolist())
    xis = np.tile(np.repeat(np.linspace(-1., 1., rings), sides), E)
    mesh.attributes.new('blendyn_xi', 'FLOAT', 'POINT').data.foreach_set('value', xis.tolist())
    mesh.attributes.new('blendyn_section', 'FLOAT_VECTOR', 'POINT').data.foreach_set(
            'vector', A.reshape(-1).astype(np.float32))
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def build_component(context, comp):
    """ Builds the mesh of the component in the reference configuration.
        Returns the warnings """
    mbs = context.scene.mbdyn
    elems = component_elems(mbs, comp)
    warnings = []
    if not elems:
        _delete_object(comp)
        comp.state = 'DEFINED'
        return ["the component has no elements"]
    if comp.family == 'BEAM':
        _build_beams(context, comp, elems, warnings)
    else:
        _build_plates(context, comp, elems)
    if comp.state == 'DEFINED':
        comp.state = 'PREVIEW'
    for message in warnings:
        logging.warning("BLENDYN::build_component(" + comp.name + "): " + message)
    return warnings

# -----------------------------------------------------------
# Update at each frame

# per mesh: what is needed to move it, rebuilt from the mesh and the
# elements when missing (e.g. after loading a file)
_runtime = {}


def _get_runtime(mbs, comp):
    obj = comp.object
    mesh = obj.data
    key = (mesh.name, len(mesh.vertices))
    rt = _runtime.get(obj.name)
    if rt is not None and rt['key'] == key:
        return rt
    if comp.family == 'BEAM':
        rings, sides = obj['blendyn_rings'], obj['blendyn_sides']
        xis = np.linspace(-1., 1., rings)
        A = np.zeros(len(mesh.vertices)*3, dtype=np.float32)
        mesh.attributes['blendyn_section'].data.foreach_get('vector', A)
        A = A.reshape((-1, rings, sides, 3)).astype(float)
        groups, uniq, start = [], {}, 0
        for etype, nn in (('beam3', 3), ('beam2', 2)):
            elems = [mbs.elems[etype + '_' + str(label)] for label in obj.get('blendyn_' + etype, [])]
            if not elems:
                continue
            labels, offsets = _beam_layout(mbs, elems)
            idx = np.array([[uniq.setdefault(label, len(uniq)) for label in lab] for lab in labels])
            N, _ = beam_shape(nn, xis)
            groups.append({'idx': idx, 'f': np.array(offsets), 'N': N, 'ref': 1 if nn == 3 else 0,
                           'A': A[start:start + len(elems)]})
            start += len(elems)
        labels = list(uniq.keys())
        rt = {'groups': groups}
    else:
        labels = list(obj['blendyn_nodes'])
        rt = {}
    rt['key'] = key
    rt['x0'], rt['R0'] = _reference_nodes(mbs, labels)
    rt['objs'] = _node_objects(mbs, labels)
    for g in rt.get('groups', ()):
        g['R0'] = rt['R0'][g['idx']]
    _runtime[obj.name] = rt
    return rt


def section_rotations(g, R, N):
    """ Rotations of the sections of a group of beams from the reference
        configuration, (beams, points, 3, 3), at the points with shape
        functions N (points, nodes): the rotations of the nodes from the
        reference configuration, interpolated relative to the middle
        (beam3) or first (beam2) node, as MBDyn does for the sections """
    dR = R[g['idx']] @ np.swapaxes(g['R0'], -1, -2)
    dref = dR[:, g['ref']]
    phi = _matrix_to_rotvec(np.einsum('eji,ekjl->ekil', dref, dR))
    return np.einsum('eij,erjk->erik', dref, _rotvec_to_matrix(np.einsum('rk,ekc->erc', N, phi)))


def _beam_vertices(rt, X, R):
    res = []
    for g in rt['groups']:
        idx = g['idx']
        p = X[idx] + np.einsum('ekij,ekj->eki', R[idx], g['f'])
        P = np.einsum('rk,eki->eri', g['N'], p)
        Q = section_rotations(g, R, g['N'])
        V = P[:, :, None, :] + np.einsum('erij,ersj->ersi', Q, g['A'])
        res.append(V.reshape((-1, 3)))
    return np.concatenate(res) if res else np.zeros((0, 3))


def move_component(comp, rt, depsgraph, frame):
    X, R = node_frames(rt['objs'], rt['x0'], rt['R0'], depsgraph, frame)
    verts = _beam_vertices(rt, X, R) if comp.family == 'BEAM' else X
    mesh = comp.object.data
    if len(verts) == len(mesh.vertices):
        mesh.vertices.foreach_set('co', np.asarray(verts, dtype=np.float32).ravel())
        mesh.update()


def update_components(scene, depsgraph=None):
    """ Moves the meshes of the confirmed components with the nodes, and
        colors them """
    mbs = scene.mbdyn
    comps = [comp for comp in mbs.flex_components if comp.state == 'CONFIRMED' and comp.object is not None]
    if not comps:
        fieldlib.update_fields(scene)
        return
    if depsgraph is None:
        depsgraph = bpy.context.evaluated_depsgraph_get()
    frame = scene.frame_current + scene.frame_subframe
    still = set()
    for comp in comps:
        try:
            rt = _get_runtime(mbs, comp)
            move_component(comp, rt, depsgraph, frame)
            if not nodes_animated(rt['objs']):
                still.add(comp.family)
        except (KeyError, IndexError, ValueError, ReferenceError) as err:
            message = "BLENDYN::update_components(): could not update {}: {}".format(comp.name, err)
            print(message)
            logging.error(message)
    # the fields are shown only on components whose nodes move, otherwise
    # the colors would change on meshes that stand still
    fieldlib.update_fields(scene, {fam for fam in FAMILIES if fam not in still})


@persistent
def update_components_handler(scene, depsgraph=None):
    if not hasattr(scene, 'mbdyn'):
        return
    # no need to update the depsgraph: the changed meshes are evaluated
    # before drawing and before rendering the frame
    update_components(scene, depsgraph)


@persistent
def clear_components_cache(*args):
    _runtime.clear()


def _remove_handler(handlers, name):
    for h in [h for h in handlers if getattr(h, '__name__', '') == name]:
        handlers.remove(h)


_remove_handler(bpy.app.handlers.frame_change_post, update_components_handler.__name__)
bpy.app.handlers.frame_change_post.append(update_components_handler)
_remove_handler(bpy.app.handlers.load_post, clear_components_cache.__name__)
bpy.app.handlers.load_post.append(clear_components_cache)

fieldlib.refresh_hook = update_components

# -----------------------------------------------------------
# Settings

def _rebuild(comp, context):
    if comp.object is not None and comp.state != 'DEFINED':
        build_component(context, comp)
        if comp.state == 'CONFIRMED':
            update_components(context.scene)


def _update_geometry(self, context):
    _rebuild(self, context)


def _update_section(self, context):
    comp = _owner_component(self)
    if comp is not None:
        _rebuild(comp, context)


def _update_thickness(self, context):
    _set_thickness(self)


def _section_poll(self, obj):
    if obj.type == 'CURVE':
        return True
    return obj.type == 'MESH' and len(obj.data.polygons) == 0 and len(obj.data.edges) > 0


_enum_items = {}


def _add_type_items(self, context):
    types = FAMILIES[self.family]['types']
    items = [('ALL', "All", "All the " + FAMILIES[self.family]['label'].lower(), 0)] \
            + [(t, t, t + " elements", i + 1) for i, t in enumerate(types)]
    _enum_items[self.family] = items
    return items


class BLENDYN_PG_flex_elem(bpy.types.PropertyGroup):
    """ Element of a flexible component """
    elem: StringProperty(
            name = "Element",
            description = "Key of the element in the MBDyn elements"
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_flex_elem class

bpy.utils.register_class(BLENDYN_PG_flex_elem)


class BLENDYN_PG_flex_section(bpy.types.PropertyGroup):
    """ Section of a beam component at a node """
    node: StringProperty(
            name = "Node",
            description = "Node of the component where the section is given",
            update = _update_section
    )
    curve: PointerProperty(
            type = bpy.types.Object,
            name = "Section",
            description = "Closed curve, or mesh with edges only, drawing the section in its "\
                    + "local X-Y plane: X and Y run along the section axes 2 and 3, and the origin "\
                    + "is on the beam reference line. The object scale applies, and its rotation "\
                    + "about Z turns the section about the beam axis; its location and the other "\
                    + "rotations are ignored",
            poll = _section_poll,
            update = _update_section
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_flex_section class

bpy.utils.register_class(BLENDYN_PG_flex_section)


class BLENDYN_PG_flex_component(bpy.types.PropertyGroup):
    """ Group of flexible elements of the same family drawn by one mesh """
    family: EnumProperty(
            items = FAMILY_ITEMS,
            name = "Family",
            description = "Family of the elements of the component"
    )
    elements: CollectionProperty(
            type = BLENDYN_PG_flex_elem,
            name = "Elements"
    )
    el_index: IntProperty(
            name = "Active element",
            default = 0,
            min = 0
    )
    state: EnumProperty(
            items = [('DEFINED', "Defined", "Elements chosen, mesh not built", 0),
                     ('PREVIEW', "Preview", "Mesh built in the reference configuration", 1),
                     ('CONFIRMED', "Confirmed", "Mesh following the nodes and showing the fields", 2)],
            name = "State",
            default = 'DEFINED'
    )
    object: PointerProperty(
            type = bpy.types.Object,
            name = "Mesh",
            description = "Object drawing the component"
    )
    is_default: BoolProperty(
            name = "Default",
            description = "Default component, holding the elements of its family "\
                    + "that are not in other components",
            default = False
    )
    rings: IntProperty(
            name = "Rings",
            description = "Sections drawn along each beam",
            default = 8,
            min = 2,
            max = 64,
            update = _update_geometry
    )
    sides: IntProperty(
            name = "Sides",
            description = "Points of each section",
            default = 16,
            min = 3,
            max = 256,
            update = _update_geometry
    )
    radius: FloatProperty(
            name = "Radius",
            description = "Radius of the round sections, used when no node of the component "\
                    + "has a section",
            default = 0.05,
            min = 0.,
            precision = 4,
            update = _update_geometry
    )
    sections: CollectionProperty(
            type = BLENDYN_PG_flex_section,
            name = "Sections"
    )
    sec_index: IntProperty(
            name = "Active section",
            default = 0,
            min = 0
    )
    thickness: FloatProperty(
            name = "Thickness",
            description = "Thickness drawn for the plates (Solidify modifier); "\
                    + "0 draws the mid surface only",
            default = 0.,
            min = 0.,
            precision = 4,
            update = _update_thickness
    )
    add_type: EnumProperty(
            items = _add_type_items,
            name = "Type",
            description = "Type of the elements to add"
    )
    add_min: IntProperty(
            name = "From",
            description = "Lowest label of the elements to add",
            default = 0
    )
    add_max: IntProperty(
            name = "To",
            description = "Highest label of the elements to add",
            default = 2**31 - 1
    )
# -----------------------------------------------------------
# end of BLENDYN_PG_flex_component class

bpy.utils.register_class(BLENDYN_PG_flex_component)

# -----------------------------------------------------------
# Operators

def _active_component(context):
    mbs = context.scene.mbdyn
    if 0 <= mbs.fc_index < len(mbs.flex_components):
        return mbs.flex_components[mbs.fc_index]
    return None


def _to_object_mode(context):
    # meshes are replaced: leave Edit Mode first
    if context.mode != 'OBJECT' and context.view_layer.objects.active is not None:
        bpy.ops.object.mode_set(mode = 'OBJECT')


def _report_warnings(op, warnings):
    for message in warnings:
        op.report({'WARNING'}, message)


class BLENDYN_OT_flex_component_add(bpy.types.Operator):
    """ Adds a flexible component """
    bl_idname = "blendyn.flex_component_add"
    bl_label = "Add flexible component"
    bl_options = {'UNDO'}

    family: EnumProperty(
            items = FAMILY_ITEMS,
            name = "Family"
    )

    def execute(self, context):
        new_component(context.scene.mbdyn, self.family)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_component_add class


class BLENDYN_OT_flex_component_remove(bpy.types.Operator):
    """ Removes the active flexible component and its mesh; its elements
        go back to the default component """
    bl_idname = "blendyn.flex_component_remove"
    bl_label = "Remove flexible component"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _active_component(context) is not None

    def execute(self, context):
        _to_object_mode(context)
        remove_component(context, context.scene.mbdyn.fc_index)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_component_remove class


class BLENDYN_OT_flex_component_from_selection(bpy.types.Operator):
    """ Creates a flexible component with the elements of the selected faces
        of the meshes of the flexible components """
    bl_idname = "blendyn.flex_component_from_selection"
    bl_label = "New component from selected faces"
    bl_options = {'UNDO'}

    def execute(self, context):
        keys, families = selected_elem_keys(context)
        if not keys:
            self.report({'ERROR'}, "Select faces of the meshes of the flexible components first")
            return {'CANCELLED'}
        if len(families) > 1:
            self.report({'ERROR'}, "The selected faces draw elements of different families")
            return {'CANCELLED'}
        _to_object_mode(context)
        mbs = context.scene.mbdyn
        comp = new_component(mbs, families.pop())
        n = assign_elements(context, comp, keys)
        warnings = build_component(context, comp)
        _report_warnings(self, warnings)
        mbs.fc_index = list(mbs.flex_components).index(comp)
        self.report({'INFO'}, "Component " + comp.name + " with " + str(n) + " elements")
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_component_from_selection class


class BLENDYN_OT_flex_elems_add_selected(bpy.types.Operator):
    """ Adds the elements of the selected faces of the meshes of the
        flexible components to the active component """
    bl_idname = "blendyn.flex_elems_add_selected"
    bl_label = "Add selected faces"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and not comp.is_default

    def execute(self, context):
        comp = _active_component(context)
        keys, families = selected_elem_keys(context)
        keys = [key for key in keys if context.scene.mbdyn.elems[key].type in FAMILIES[comp.family]['types']]
        if not keys:
            self.report({'ERROR'}, "No selected faces draw " + FAMILIES[comp.family]['label'].lower())
            return {'CANCELLED'}
        _to_object_mode(context)
        n = assign_elements(context, comp, keys)
        self.report({'INFO'}, "Added " + str(n) + " elements")
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_elems_add_selected class


class BLENDYN_OT_flex_elems_add_range(bpy.types.Operator):
    """ Adds the elements of the chosen type and label range to the active
        component """
    bl_idname = "blendyn.flex_elems_add_range"
    bl_label = "Add elements"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and not comp.is_default

    def execute(self, context):
        comp = _active_component(context)
        types = FAMILIES[comp.family]['types'] if comp.add_type == 'ALL' else (comp.add_type,)
        keys = [elem.name for elem in context.scene.mbdyn.elems if elem.type in types
                and comp.add_min <= elem.int_label <= comp.add_max]
        if not keys:
            self.report({'WARNING'}, "No elements of this type in this range")
            return {'CANCELLED'}
        _to_object_mode(context)
        n = assign_elements(context, comp, keys)
        self.report({'INFO'}, "Added " + str(n) + " elements")
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_elems_add_range class


class BLENDYN_OT_flex_elem_remove(bpy.types.Operator):
    """ Removes the active element from the component: it goes back to the
        default component """
    bl_idname = "blendyn.flex_elem_remove"
    bl_label = "Remove element"
    bl_options = {'UNDO'}

    clear: BoolProperty(
            name = "All",
            description = "Remove all the elements",
            default = False
    )

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and not comp.is_default and len(comp.elements)

    def execute(self, context):
        comp = _active_component(context)
        _to_object_mode(context)
        if self.clear:
            comp.elements.clear()
        else:
            comp.elements.remove(min(comp.el_index, len(comp.elements) - 1))
            comp.el_index = max(min(comp.el_index, len(comp.elements) - 1), 0)
        if comp.object is not None:
            build_component(context, comp)
        refresh_default(context, comp.family)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_elem_remove class


class BLENDYN_OT_flex_section_add(bpy.types.Operator):
    """ Adds a section to the active beam component """
    bl_idname = "blendyn.flex_section_add"
    bl_label = "Add section"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and comp.family == 'BEAM'

    def execute(self, context):
        comp = _active_component(context)
        comp.sections.add()
        comp.sec_index = len(comp.sections) - 1
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_section_add class


class BLENDYN_OT_flex_section_remove(bpy.types.Operator):
    """ Removes the active section of the active beam component """
    bl_idname = "blendyn.flex_section_remove"
    bl_label = "Remove section"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and len(comp.sections)

    def execute(self, context):
        comp = _active_component(context)
        comp.sections.remove(min(comp.sec_index, len(comp.sections) - 1))
        comp.sec_index = max(min(comp.sec_index, len(comp.sections) - 1), 0)
        _rebuild(comp, context)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_section_remove class


def _assign_section_object(context, comp, obj):
    """ Uses obj for the active section, or for a new one; places it at the
        node of the section, to find it easily (its location is ignored) """
    if not len(comp.sections):
        comp.sections.add()
        comp.sec_index = 0
    sec = comp.sections[min(comp.sec_index, len(comp.sections) - 1)]
    node = context.scene.mbdyn.nodes.get(sec.node)
    if node is not None:
        obj.location = node.initial_pos
    sec.curve = obj


class BLENDYN_OT_flex_section_circle(bpy.types.Operator):
    """ Creates a circle section for the active section of the component """
    bl_idname = "blendyn.flex_section_circle"
    bl_label = "New circle"
    bl_options = {'UNDO'}

    radius: FloatProperty(
            name = "Radius",
            default = 0.05,
            min = 0.
    )

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and comp.family == 'BEAM'

    def invoke(self, context, event):
        self.radius = _active_component(context).radius
        return self.execute(context)

    def execute(self, context):
        comp = _active_component(context)
        obj = new_section_object(context, 'section.circle', circle_section(self.radius, 32))
        _assign_section_object(context, comp, obj)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_section_circle class


class BLENDYN_OT_flex_section_selig(bpy.types.Operator, ImportHelper):
    """ Loads a profile in Selig format (name, then x y pairs from the
        trailing edge over the upper side to the leading edge and back) as
        the active section of the component """
    bl_idname = "blendyn.flex_section_selig"
    bl_label = "Load Selig profile"
    bl_options = {'UNDO'}

    filter_glob: StringProperty(
            default = "*.dat;*.txt;*.*",
            options = {'HIDDEN'}
    )
    chord: FloatProperty(
            name = "Chord",
            description = "Chord of the section",
            default = 1.,
            min = 0.
    )
    origin: FloatProperty(
            name = "Reference point",
            description = "Position of the beam reference line along the chord, "\
                    + "as a fraction of the chord from the leading edge",
            default = 0.25
    )

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and comp.family == 'BEAM'

    def execute(self, context):
        try:
            with open(self.filepath, 'r') as sf:
                name = sf.readline().strip() or 'section'
                pts = []
                for line in sf:
                    fields = line.split()
                    if len(fields) >= 2:
                        pts.append((float(fields[0]), float(fields[1])))
        except (OSError, ValueError) as err:
            self.report({'ERROR'}, "Could not read the profile: " + str(err))
            return {'CANCELLED'}
        pts = np.array(pts)
        if len(pts) > 1 and np.allclose(pts[0], pts[-1]):
            pts = pts[:-1]
        if len(pts) < 3:
            self.report({'ERROR'}, "The profile has less than three points")
            return {'CANCELLED'}
        pts = np.stack(((pts[:, 0] - self.origin)*self.chord, pts[:, 1]*self.chord), axis=1)
        obj = new_section_object(context, name, pts)
        _assign_section_object(context, _active_component(context), obj)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_section_selig class


class BLENDYN_OT_flex_component_build(bpy.types.Operator):
    """ Builds the mesh of the active component in the reference
        configuration (again, e.g. after editing its sections) """
    bl_idname = "blendyn.flex_component_build"
    bl_label = "Build"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and len(comp.elements)

    def execute(self, context):
        comp = _active_component(context)
        _to_object_mode(context)
        warnings = build_component(context, comp)
        _report_warnings(self, warnings)
        if comp.state == 'CONFIRMED':
            update_components(context.scene)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_component_build class


class BLENDYN_OT_flex_component_confirm(bpy.types.Operator):
    """ Confirms the active component: its mesh follows the nodes and shows
        the fields. The nodes are animated first if they have no keyframes """
    bl_idname = "blendyn.flex_component_confirm"
    bl_label = "Confirm"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and comp.state == 'PREVIEW' and comp.object is not None

    def execute(self, context):
        scene = context.scene
        mbs = scene.mbdyn
        comp = _active_component(context)
        _to_object_mode(context)
        rt = _get_runtime(mbs, comp)
        if mbs.file_basename and not nodes_animated(rt['objs']):
            if bpy.ops.blendyn.set_motion_paths('EXEC_DEFAULT') != {'FINISHED'}:
                self.report({'WARNING'}, "Could not animate the nodes")
        comp.state = 'CONFIRMED'
        _show_fields_of(mbs, comp.family)
        # writing mesh data from a frame change handler while rendering
        # is safe only with a locked interface
        scene.render.use_lock_interface = True
        update_components(scene)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_component_confirm class


class BLENDYN_OT_flex_component_edit(bpy.types.Operator):
    """ Brings the active component back to the reference configuration,
        to edit it """
    bl_idname = "blendyn.flex_component_edit"
    bl_label = "Edit"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        comp = _active_component(context)
        return comp is not None and comp.state == 'CONFIRMED'

    def execute(self, context):
        comp = _active_component(context)
        _to_object_mode(context)
        comp.state = 'PREVIEW'
        _report_warnings(self, build_component(context, comp))
        update_components(context.scene)
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_component_edit class


class BLENDYN_OT_flex_default_components(bpy.types.Operator):
    """ Builds the default flexible components, with the beams and plates
        that are not in other components """
    bl_idname = "blendyn.flex_default_components"
    bl_label = "Build default components"
    bl_options = {'UNDO'}

    def execute(self, context):
        _to_object_mode(context)
        mbs = context.scene.mbdyn
        built = []
        for family in FAMILIES:
            comp = default_component(mbs, family)
            if comp is not None:
                # rebuild it in any case
                _delete_object(comp)
            if refresh_default(context, family) is not None:
                built.append(FAMILIES[family]['label'])
        context.scene.render.use_lock_interface = True
        update_components(context.scene)
        if built:
            self.report({'INFO'}, "Default components: " + ", ".join(built))
        return {'FINISHED'}
# -----------------------------------------------------------
# end of BLENDYN_OT_flex_default_components class

# -----------------------------------------------------------
# Panel

_STATE_ICONS = {'DEFINED': 'MESH_DATA', 'PREVIEW': 'HIDE_OFF', 'CONFIRMED': 'CHECKMARK'}


class BLENDYN_UL_flex_components(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align = True)
        row.prop(item, "name", text = "", emboss = False, icon = _STATE_ICONS[item.state])
        row.label(text = FAMILIES[item.family]['label'] + (", default" if item.is_default else ""))


class BLENDYN_UL_flex_elems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text = item.elem)


class BLENDYN_UL_flex_sections(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align = True)
        row.prop_search(item, "node", context.scene.mbdyn, "nodes", text = "")
        row.prop(item, "curve", text = "")


class BLENDYN_PT_flex_components(bpy.types.Panel):
    """ Flexible components: groups of beams or plates drawn by a mesh - Toolbar Panel """
    bl_idname = "BLENDYN_PT_flex_components"
    bl_label = "Flexible components"
    bl_category = 'Blendyn'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        mbs = context.scene.mbdyn
        return len(mbs.flex_components) or any(elem.type in FLEXIBLE_TYPES for elem in mbs.elems)

    def draw(self, context):
        layout = self.layout
        mbs = context.scene.mbdyn

        row = layout.row()
        row.template_list("BLENDYN_UL_flex_components", "", mbs, "flex_components", mbs, "fc_index",
                          rows = 3)
        col = row.column(align = True)
        col.operator_menu_enum(BLENDYN_OT_flex_component_add.bl_idname, "family", text = "", icon = 'ADD')
        col.operator(BLENDYN_OT_flex_component_remove.bl_idname, text = "", icon = 'REMOVE')
        col = layout.column(align = True)
        col.operator(BLENDYN_OT_flex_component_from_selection.bl_idname, icon = 'FACESEL')
        col.operator(BLENDYN_OT_flex_default_components.bl_idname, icon = 'FILE_REFRESH')

        comp = _active_component(context)
        if comp is None:
            return
        box = layout.box()
        col = box.column()
        col.prop(comp, "name")
        col.label(text = FAMILIES[comp.family]['label'] + ": "
                  + comp.bl_rna.properties['state'].enum_items[comp.state].name.lower(),
                  icon = _STATE_ICONS[comp.state])
        if comp.is_default:
            col.label(text = "Holds the elements not in other components", icon = 'INFO')

        # elements
        col = box.column()
        col.label(text = "Elements: " + str(len(comp.elements)))
        row = col.row()
        row.template_list("BLENDYN_UL_flex_elems", "", comp, "elements", comp, "el_index", rows = 3)
        if not comp.is_default:
            sub = row.column(align = True)
            sub.operator(BLENDYN_OT_flex_elem_remove.bl_idname, text = "", icon = 'REMOVE').clear = False
            sub.operator(BLENDYN_OT_flex_elem_remove.bl_idname, text = "", icon = 'X').clear = True
            sub = col.column(align = True)
            row = sub.row(align = True)
            row.prop(comp, "add_type", text = "")
            row.prop(comp, "add_min")
            row.prop(comp, "add_max")
            row = sub.row(align = True)
            row.operator(BLENDYN_OT_flex_elems_add_range.bl_idname, icon = 'ADD')
            row.operator(BLENDYN_OT_flex_elems_add_selected.bl_idname, icon = 'FACESEL')

        # geometry
        if comp.family == 'BEAM':
            col = box.column(align = True)
            row = col.row(align = True)
            row.prop(comp, "rings")
            row.prop(comp, "sides")
            col.prop(comp, "radius")
            col = box.column()
            col.label(text = "Sections at the nodes:")
            row = col.row()
            row.template_list("BLENDYN_UL_flex_sections", "", comp, "sections", comp, "sec_index", rows = 2)
            sub = row.column(align = True)
            sub.operator(BLENDYN_OT_flex_section_add.bl_idname, text = "", icon = 'ADD')
            sub.operator(BLENDYN_OT_flex_section_remove.bl_idname, text = "", icon = 'REMOVE')
            row = col.row(align = True)
            row.operator(BLENDYN_OT_flex_section_circle.bl_idname, icon = 'MESH_CIRCLE')
            row.operator(BLENDYN_OT_flex_section_selig.bl_idname, icon = 'IMPORT')
        else:
            box.prop(comp, "thickness")

        row = box.row(align = True)
        row.operator(BLENDYN_OT_flex_component_build.bl_idname,
                     text = "Build" if comp.object is None else "Rebuild", icon = 'MOD_BUILD')
        if comp.state == 'PREVIEW':
            row.operator(BLENDYN_OT_flex_component_confirm.bl_idname, icon = 'CHECKMARK')
        elif comp.state == 'CONFIRMED':
            row.operator(BLENDYN_OT_flex_component_edit.bl_idname, icon = 'GREASEPENCIL')
# -----------------------------------------------------------
# end of BLENDYN_PT_flex_components class
