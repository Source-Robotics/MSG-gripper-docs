#!/usr/bin/env python3
"""Dimension drawings of the MSG gripper, from the robot model's meshes: front, side, top and coupler views.

    ..\\..\\.venv-cad\\Scripts\\python tools\\dimension_drawings.py [--models PATH] [--step PATH] [--preview DIR]
    ..\\..\\.venv-cad\\Scripts\\python tools\\dimension_drawings.py --measure      # the numbers only
    ..\\..\\.venv-cad\\Scripts\\python tools\\dimension_drawings.py --variants     # what changes per rail and stepper

Writes docs/assets/dimensions/msg_<view>.webp and msg_<view>_dark.webp: a CAD line drawing in the style of the
SSG-48 manual's drawings (thin outlines, no hidden lines, grey dimension lines with arrowheads, millimetres with two
decimals), the light version on white and the dark one on the docs' slate (30, 32, 41), each background made
transparent. The page shows them with #only-light and #only-dark.

The geometry is the assembled gripper of projects/robot_descriptions (urdf/msg_description/msg_solid.urdf: the CAD
exported as STL, the 150 mm rail with the 21.5 mm stepper, solid jaws), posed by the URDF's joints with the jaws
fully open. Every number on a drawing is measured from those meshes here, in the frame of the page "Data for robot
integration": the origin on the coupler axis at the coupler's back face, Z toward the jaw tips, Y along the jaw
travel, X from the rail toward the stepper and the camera. --variants reads the STEP files of the product repository
(projects/MSG-compliant-AI-stepper-gripper) for the parts that change with the rail and the stepper.

The lines are found on the meshes: the creases sharper than CREASE_DEG, the silhouettes and the open edges, kept
where a depth buffer of the view shows them (hidden lines removed). Needs the cadquery environment .venv-cad at the
workspace root (numpy, trimesh, numba, matplotlib, Pillow; cadquery for --variants).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "dimensions"
DESC = Path("urdf") / "msg_description"
URDF = "msg_solid.urdf"
STEP = Path("STEP files")
CREASE_DEG = 30.0          # a mesh edge sharper than this is drawn; the facets of curved faces stay below it
SCALE = 9.0                # px per mm of the drawings (one scale for all four views)
OVERSAMPLE = 2             # the depth buffer is this much finer than the drawing
EPS = 0.3                  # mm: depth tolerance of the visibility test
MIN_CHAIN = 3.0            # mm: a connected group of lines shorter than this is facet noise, not drawn
THEMES = {
    "light": {"bg": (255, 255, 255), "line": "#111111", "dim": "#6b6b6b", "centre": "#9a9a9a"},
    "dark": {"bg": (30, 32, 41), "line": "#e6e8ee", "dim": "#a3a8b5", "centre": "#7d8291"},
}


# ------------------------------------------------------------------------------------------------ the model
def find_dir(arg: str | None, env: str, name: str, probe: Path) -> Path:
    for c in (arg, os.environ.get(env), ROOT.parent / name, ROOT.parent.parent / "projects" / name):
        if c and (Path(c) / probe).exists():
            return Path(c)
    sys.exit(f"dimension_drawings: no clone of {name} with {probe} found; pass the path")


def origin(el) -> np.ndarray:
    m = np.eye(4)
    if el is not None:
        rpy = [float(v) for v in (el.get("rpy") or "0 0 0").split()]
        m = trimesh.transformations.euler_matrix(*rpy, "sxyz")
        m[:3, 3] = [float(v) for v in (el.get("xyz") or "0 0 0").split()]
    return m


def load_assembly(models: Path, opening: float = 1.0) -> dict[str, list[trimesh.Trimesh]]:
    """The URDF's visual meshes posed in its root frame (`flange`), the jaws at `opening` (1 fully open, 0 closed),
    in mm, then moved so that the origin is on the coupler axis at the coupler's back face."""
    pkg = models / DESC
    robot = ET.parse(pkg / URDF).getroot()
    joints = {j.find("child").get("link"): j for j in robot.findall("joint")}
    by_name = {j.get("name"): j for j in robot.findall("joint")}

    def q_of(j) -> float:
        mimic = j.find("mimic")
        if mimic is not None:
            return q_of(by_name[mimic.get("joint")]) * float(mimic.get("multiplier", 1)) + float(mimic.get("offset", 0))
        lim = j.find("limit")
        lo, hi = float(lim.get("lower")), float(lim.get("upper"))
        far = lo if abs(lo) > abs(hi) else hi          # the closed end: the limit away from 0 (0 is open)
        return far * (1.0 - opening)

    def pose(link: str) -> np.ndarray:
        m = np.eye(4)
        while link in joints:
            j = joints[link]
            step = origin(j.find("origin"))
            if j.get("type") == "prismatic":
                slide = np.eye(4)
                slide[:3, 3] = np.array([float(v) for v in j.find("axis").get("xyz").split()]) * q_of(j)
                step = step @ slide
            m = step @ m
            link = j.find("parent").get("link")
        return m

    parts: dict[str, list[trimesh.Trimesh]] = {}
    for link in robot.findall("link"):
        meshes = []
        for vis in link.findall("visual"):
            mesh = trimesh.load(pkg / vis.find("geometry/mesh").get("filename"), force="mesh")
            mesh.apply_transform(pose(link.get("name")) @ origin(vis.find("origin")))
            mesh.apply_scale(1000.0)
            meshes.append(mesh)
        if meshes:
            parts[link.get("name")] = meshes
    back = min(m.bounds[0, 2] for ms in parts.values() for m in ms)
    for ms in parts.values():
        for m in ms:
            m.apply_translation([0, 0, -back])
    parts["_flange_z"] = back                                     # where the URDF's flange frame lies, mm
    return parts


def meshes_of(parts, *names) -> list[trimesh.Trimesh]:
    names = names or [n for n in parts if not n.startswith("_")]
    return [m for n in names for m in parts[n]]


# ------------------------------------------------------------------------------------------------ measurements
def bounds(meshes) -> np.ndarray:
    return np.array([np.min([m.bounds[0] for m in meshes], axis=0), np.max([m.bounds[1] for m in meshes], axis=0)])


def section_bounds(meshes, axis: int, at: float) -> np.ndarray | None:
    normal = np.eye(3)[axis]
    pts = []
    for m in meshes:
        s = m.section(plane_origin=normal * at, plane_normal=normal)
        if s is not None:
            pts.append(s.vertices)
    if not pts:
        return None
    p = np.vstack(pts)
    return np.array([p.min(axis=0), p.max(axis=0)])


def radii(meshes, zmax: float, rmax: float) -> list[tuple[float, float, float]]:
    """Cylinders round the coupler axis (Z) below zmax: (radius, z from, z to) of each, from the vertices of the
    faces whose normals point at the axis (the STL's vertices lie on the CAD's circles)."""
    found = []
    for m in meshes:
        n, c = m.face_normals, m.triangles_center
        r = np.hypot(c[:, 0], c[:, 1])
        radial = np.abs(n[:, 0] * c[:, 0] + n[:, 1] * c[:, 1]) / np.maximum(r, 1e-9)
        sel = (np.abs(n[:, 2]) < 0.05) & (c[:, 2] < zmax) & (r < rmax) & (radial > 0.98)
        v = m.vertices[m.faces[sel]].reshape(-1, 3)
        rv = np.hypot(v[:, 0], v[:, 1])
        order = np.argsort(rv)
        groups = np.split(order, np.where(np.diff(rv[order]) > 0.15)[0] + 1)
        for g in groups:
            if len(g) >= 60:
                found.append((float(np.median(rv[g])), float(v[g, 2].min()), float(v[g, 2].max())))
    return sorted(found)


def main_axis(mesh) -> np.ndarray:
    """The normal of the largest flat face of a mesh (the lens's front: its optical axis), pointing to +Z."""
    agg: dict[tuple, float] = {}
    for n, a in zip(np.round(mesh.face_normals, 3), mesh.area_faces):
        agg[tuple(n)] = agg.get(tuple(n), 0.0) + a
    n = np.array(max(agg, key=agg.get))
    near = mesh.face_normals @ n > 0.9999                         # that face's triangles, unrounded
    n = (mesh.face_normals[near] * mesh.area_faces[near, None]).sum(axis=0)
    n /= np.linalg.norm(n)
    return n if n[2] >= 0 else -n


def measure(parts) -> dict[str, float]:
    """Every number the drawings show, in mm, in the frame of the integration page."""
    allm = meshes_of(parts)
    body = parts["msg_gripper_link"]
    jaws = meshes_of(parts, "left_finger_link", "right_finger_link")
    left = parts["left_finger_link"][0]
    a, b, j = bounds(allm), bounds(body), bounds(jaws)
    # the jaw's gripping face: the largest area facing the other jaw, above the carrier
    n, c, area = left.face_normals, left.triangles_center, left.area_faces
    face = (n[:, 1] > 0.99) & (c[:, 2] > 60)
    ys = np.round(c[face, 1], 2)
    y_face = max(set(ys), key=lambda y: area[face][ys == y].sum())
    zf = c[face][ys == y_face][:, 2]
    W2 = a[1, 1]
    blocker = section_bounds(body, 1, W2 - 0.2)                   # the jaw blockers at the rail ends
    rail = section_bounds(body, 1, 0.8 * W2)                      # the body's rail block, outside the stepper
    outer = section_bounds([left], 1, left.bounds[0, 1] + 0.1)    # the jaw's outer face
    tip = left.vertices[left.vertices[:, 2] > j[1, 2] - 0.3]
    top = np.vstack([m.vertices[m.vertices[:, 0] > a[1, 0] - 0.3] for m in body])   # the camera mount's top edge
    cyl = radii(body, zmax=10.0, rmax=30.0)
    ring = max(cyl)
    recess = max([t for t in cyl if t[1] < 0.5 and t[0] < ring[0] - 5])
    lens = bounds(body[1:2])
    axis = main_axis(body[1])
    mv = body[2].vertices
    housing = mv[np.abs(mv[:, 1]) > 20.5]                         # the motor's 42 mm square housing, not its shaft
    return {
        "width": 2 * W2,                                     # over the jaw blockers at the rail ends
        "blocker_x0": float(blocker[0, 0]), "blocker_x1": float(blocker[1, 0]), "blocker_z1": float(blocker[1, 2]),
        "jaws_width": j[1, 1] - j[0, 1],                     # over the jaws, fully open
        "outer_z1": float(outer[1, 2]),                      # the top of the jaw's outer face
        "opening": 2 * abs(y_face),                          # between the solid jaws' faces, fully open
        "face_z0": float(zf.min()), "face_z1": float(zf.max()),
        "jaw_w": left.bounds[1, 1] - left.bounds[0, 1],      # one jaw across Y, at the carrier
        "jaw_x0": j[0, 0], "jaw_x1": j[1, 0],                # the jaws along X
        "jaw_centre_x": float((tip[:, 0].min() + tip[:, 0].max()) / 2),
        "tip_y": float(-tip[:, 1].min()),                    # the outer edge of a jaw's tip
        "tip_z": j[1, 2], "jaw_z0": j[0, 2],
        "height": a[1, 2] - a[0, 2],                         # coupler back face to the jaw tips
        "body_front_z": b[1, 2],                             # the camera mount's front
        "front_x": float(np.vstack([m.vertices[m.vertices[:, 2] > b[1, 2] - 0.3] for m in body])[:, 0].max()),
        "rail_z1": float(rail[1, 2]),
        "x_min": a[0, 0], "x_max": a[1, 0], "depth": a[1, 0] - a[0, 0],
        "top_y0": float(top[:, 1].min()), "top_y1": float(top[:, 1].max()), "top_z": float(top[:, 2].min()),
        "ring_d": 2 * ring[0], "ring_t": ring[2] - ring[1],
        "recess_d": 2 * recess[0], "recess_t": recess[2] - recess[1],
        "motor_length": float(np.ptp(housing[:, 0])),         # the stepper's housing: 20 mm is the 21.5 mm stepper
        "lens_x": float(lens.mean(axis=0)[0]), "lens_z": float(lens.mean(axis=0)[2]),
        "camera_deg": float(np.degrees(np.arctan2(-axis[0], axis[2]))),   # the lens axis, from Z toward -X
        "flange_z": -parts["_flange_z"],                     # the URDF's flange frame, from the back face
    }


# ------------------------------------------------------------------------------------------------ hidden lines
try:
    from numba import njit
except ImportError:                                           # slow, but the same result
    def njit(*a, **k):
        return (lambda f: f) if not (a and callable(a[0])) else a[0]


@njit(cache=True)
def _raster(P, Z, W, H):
    zb = np.full((H, W), -1e9)
    for t in range(P.shape[0]):
        x0, y0, x1, y1, x2, y2 = P[t, 0, 0], P[t, 0, 1], P[t, 1, 0], P[t, 1, 1], P[t, 2, 0], P[t, 2, 1]
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-12:
            continue
        minx = max(int(np.floor(min(x0, x1, x2))), 0)
        maxx = min(int(np.ceil(max(x0, x1, x2))), W - 1)
        miny = max(int(np.floor(min(y0, y1, y2))), 0)
        maxy = min(int(np.ceil(max(y0, y1, y2))), H - 1)
        for py in range(miny, maxy + 1):
            for px in range(minx, maxx + 1):
                cx, cy = px + 0.5, py + 0.5
                w0 = ((x1 - cx) * (y2 - cy) - (x2 - cx) * (y1 - cy)) / area
                w1 = ((x2 - cx) * (y0 - cy) - (x0 - cx) * (y2 - cy)) / area
                w2 = 1.0 - w0 - w1
                if w0 >= -1e-6 and w1 >= -1e-6 and w2 >= -1e-6:
                    z = w0 * Z[t, 0] + w1 * Z[t, 1] + w2 * Z[t, 2]
                    if z > zb[py, px]:
                        zb[py, px] = z
    return zb


def visible_lines(meshes, right, up) -> np.ndarray:
    """The visible edges of the view as segments (n, 2, 2) in view millimetres (u along `right`, v along `up`)."""
    right, up = np.asarray(right, float), np.asarray(up, float)
    toward = np.cross(right, up)                                   # from the object to the viewer
    s = SCALE * OVERSAMPLE
    allv = np.vstack([m.vertices for m in meshes])
    u0, v0 = (allv @ right).min() - 2, (allv @ up).min() - 2
    W = int(((allv @ right).max() + 2 - u0) * s) + 1
    H = int(((allv @ up).max() + 2 - v0) * s) + 1

    def px(p):
        return np.stack([(p @ right - u0) * s, (p @ up - v0) * s], -1)

    tris = np.concatenate([px(m.vertices)[m.faces] for m in meshes])
    deps = np.concatenate([(m.vertices @ toward)[m.faces] for m in meshes])
    zb = _raster(tris, deps, W, H)
    # the farthest surface in each 3 x 3 neighbourhood: an edge on a silhouette or next to its own face passes
    pad = np.pad(zb, 1, constant_values=-1e9)
    zmin = np.min([pad[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)], axis=0)
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    segs = []
    for m in meshes:
        d = m.face_normals @ toward
        fa, e = m.face_adjacency, m.face_adjacency_edges
        crease = (m.face_adjacency_angles > math.radians(CREASE_DEG)) & ((d[fa[:, 0]] > 0) | (d[fa[:, 1]] > 0))
        silhouette = (d[fa[:, 0]] > 0) != (d[fa[:, 1]] > 0)
        uniq, count = np.unique(m.edges_sorted, axis=0, return_counts=True)
        edges = np.vstack([e[crease | silhouette], uniq[count == 1]])
        a, b = m.vertices[edges[:, 0]], m.vertices[edges[:, 1]]
        pa, pb = px(a), px(b)
        za, zbe = a @ toward, b @ toward
        runs = []                                                  # (edge, start point, end point) of each visible run
        for i in range(len(edges)):
            k = max(int(np.linalg.norm(pb[i] - pa[i]) / 0.5), 1)
            t = np.linspace(0, 1, k + 1)
            pts = pa[i] + (pb[i] - pa[i]) * t[:, None]
            z = za[i] + (zbe[i] - za[i]) * t
            ix = np.clip(pts[:, 0].astype(int), 0, W - 1)
            iy = np.clip(pts[:, 1].astype(int), 0, H - 1)
            vis = z >= zmin[iy, ix] - EPS
            j = 0
            while j <= k:
                if not vis[j]:
                    j += 1
                    continue
                start = j
                while j + 1 <= k and vis[j + 1]:
                    j += 1
                if j > start:
                    runs.append((i, pts[start], pts[j]))
                j += 1
        if not runs:
            continue
        # drop specks: connected groups of edges with less than MIN_CHAIN mm of visible line (facet noise on
        # curved faces); real outlines are long connected chains
        n = len(m.vertices)
        graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n, n))
        _, label = connected_components(graph, directed=False)
        length = np.zeros(label.max() + 1)
        for i, p0, p1 in runs:
            length[label[edges[i, 0]]] += np.linalg.norm(p1 - p0) / s
        segs += [(p0, p1) for i, p0, p1 in runs if length[label[edges[i, 0]]] >= MIN_CHAIN]
    out = np.array(segs) / s
    out[..., 0] += u0
    out[..., 1] += v0
    return out


def true_circles(segs: np.ndarray, rs: list[float], tol: float = 0.08) -> np.ndarray:
    """Seen along the coupler axis, the facets of its cylinders show as polygons: every chord whose two ends lie on
    one of the circles `rs` (centred on the axis, the view's origin) becomes an arc of that circle."""
    out = []
    for a, b in segs:
        ra, rb = np.hypot(*a), np.hypot(*b)
        r = next((r for r in rs if abs(ra - r) < tol and abs(rb - r) < tol), None)
        if r is None or np.linalg.norm(b - a) > r:
            out.append((a, b))
            continue
        t0, t1 = math.atan2(a[1], a[0]), math.atan2(b[1], b[0])
        t1 = t0 + (t1 - t0 + math.pi) % (2 * math.pi) - math.pi
        t = np.linspace(t0, t1, max(int(abs(t1 - t0) * r / 0.3), 1) + 1)
        p = r * np.stack([np.cos(t), np.sin(t)], -1)
        out += list(zip(p[:-1], p[1:]))
    return np.array(out)


# ------------------------------------------------------------------------------------------------ the drawing
class Sheet:
    """One view: the lines and the dimensions in view millimetres, drawn with matplotlib for both themes."""

    def __init__(self, segs, theme):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection
        self.plt, self.T = plt, THEMES[theme]
        lo, hi = segs.reshape(-1, 2).min(axis=0), segs.reshape(-1, 2).max(axis=0)
        self.lo, self.hi = lo - 60, hi + 60                       # room for the dimensions; cropped afterwards
        w, h = (self.hi - self.lo) * SCALE / 100
        self.fig = plt.figure(figsize=(w, h), dpi=100, facecolor=np.array(self.T["bg"]) / 255)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(self.lo[0], self.hi[0])
        self.ax.set_ylim(self.lo[1], self.hi[1])
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.pt = SCALE * 72 / 100                                # points per mm on this sheet
        self.ax.add_collection(LineCollection(segs, colors=self.T["line"], linewidths=0.17 * self.pt,
                                              capstyle="round", joinstyle="round"))
        self.font = font()
        self.text_mm = 3.8

    def _line(self, pts, colour=None, lw=0.12, **kw):
        p = np.asarray(pts, float)
        self.ax.plot(p[:, 0], p[:, 1], color=colour or self.T["dim"], lw=lw * self.pt, solid_capstyle="butt", **kw)

    def _arrow(self, tip, direction):
        d = np.asarray(direction, float) / np.linalg.norm(direction)
        n = np.array([-d[1], d[0]])
        tip = np.asarray(tip, float)
        base = tip - d * 2.6
        self.ax.fill(*np.array([tip, base + n * 0.42, base - n * 0.42]).T, color=self.T["dim"], lw=0)

    def _text(self, xy, label, rotation=0, ha="center", va="bottom"):
        self.ax.text(*xy, label, rotation=rotation, ha=ha, va=va, color=self.T["dim"], fontproperties=self.font,
                     fontsize=self.text_mm * self.pt, rotation_mode="anchor")

    def dim(self, p1, p2, at: float, horizontal: bool, value: float | None = None, text_side: int = 1,
            text_shift: float = 0.0):
        """A linear dimension between the feature points p1 and p2, its line at `at` (v for a horizontal one, u for
        a vertical one), extension lines from the features with a small gap, arrows inside (outside if short)."""
        p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
        i, k = (0, 1) if horizontal else (1, 0)                    # i: the measured axis, k: the offset axis
        value = abs(p2[i] - p1[i]) if value is None else value
        for p in (p1, p2):
            sgn = np.sign(at - p[k]) or 1
            a, b = p.copy(), p.copy()
            a[k] = p[k] + sgn * 1.2
            b[k] = at + sgn * 2.0
            if abs(at - p[k]) > 1.3:
                self._line([a, b])
        s1, s2 = p1.copy(), p2.copy()
        s1[k] = s2[k] = at
        lo, hi = (s1, s2) if s1[i] < s2[i] else (s2, s1)
        unit = np.eye(2)[i]
        if hi[i] - lo[i] > 8:
            self._line([lo, hi])
            self._arrow(lo, -unit)
            self._arrow(hi, unit)
        else:                                                      # short: arrows outside, pointing in
            self._line([lo - unit * 6, hi + unit * 6])
            self._arrow(lo, unit)
            self._arrow(hi, -unit)
        mid = (lo + hi) / 2
        mid[i] += text_shift
        label = f"{value:.2f}"
        if horizontal:
            mid[1] += 0.8 * text_side
            self._text(mid, label, va="bottom" if text_side > 0 else "top")
        else:
            mid[0] -= 0.8 * text_side
            self._text(mid, label, rotation=90, va="bottom" if text_side > 0 else "top")

    def diameter(self, centre, radius, angle_deg, length, value=None, prefix="Ø"):
        """A leader from outside to the circle, the arrow touching it, the value at the leader's end."""
        a = math.radians(angle_deg)
        d = np.array([math.cos(a), math.sin(a)])
        c = np.asarray(centre, float)
        on = c + d * radius
        out = c + d * (radius + length)
        self._line([on, out])
        self._arrow(on, -d)
        shoulder = out + np.array([5.0 * np.sign(d[0] or 1), 0])
        self._line([out, shoulder])
        label = f"{prefix}{(2 * radius if value is None else value):.2f}"
        self._text(shoulder + np.array([0.8 * np.sign(d[0] or 1), 0]), label, ha="left" if d[0] >= 0 else "right",
                   va="center")

    def centre_line(self, p1, p2):
        self._line([p1, p2], colour=self.T["centre"], lw=0.1, dashes=(12, 3, 2, 3))

    def angle(self, centre, a1_deg, a2_deg, radius, value=None):
        """An angle between two directions from `centre` (degrees, counter-clockwise from +u): an arc with arrows,
        the value outside its middle."""
        c = np.asarray(centre, float)
        t = np.radians(np.linspace(a1_deg, a2_deg, 60))
        self._line(c + radius * np.stack([np.cos(t), np.sin(t)], -1))
        for a, sgn in ((a1_deg, -1), (a2_deg, 1)):
            r = math.radians(a)
            tip = c + radius * np.array([math.cos(r), math.sin(r)])
            self._arrow(tip, sgn * np.array([-math.sin(r), math.cos(r)]) * (1 if a2_deg > a1_deg else -1))
        mid = math.radians((a1_deg + a2_deg) / 2)
        d = np.array([math.cos(mid), math.sin(mid)])
        label = f"{abs(a2_deg - a1_deg) if value is None else value:.2f}°"
        self._text(c + d * (radius + 1.5), label, ha="left" if d[0] >= 0 else "right", va="bottom")

    def save(self, path: Path, preview: Path | None = None):
        from PIL import Image
        tmp = path.with_suffix(".tmp.png")
        self.fig.savefig(tmp, dpi=100, facecolor=self.fig.get_facecolor())
        self.plt.close(self.fig)
        img = Image.open(tmp).convert("RGB")
        tmp.unlink()
        a = np.asarray(img)
        bg = np.array(self.T["bg"])
        ink = np.any(a != bg, axis=2)
        rows, cols = np.where(ink.any(axis=1))[0], np.where(ink.any(axis=0))[0]
        pad = int(3 * SCALE)
        box = (max(cols[0] - pad, 0), max(rows[0] - pad, 0), min(cols[-1] + pad, a.shape[1]), min(rows[-1] + pad, a.shape[0]))
        img = img.crop(box)
        if preview:
            preview.mkdir(parents=True, exist_ok=True)
            img.save(preview / (path.stem + ".png"))
        a = np.asarray(img)
        alpha = np.where(np.all(a == bg, axis=2), 0, 255).astype(np.uint8)
        out = img.convert("RGBA")
        out.putalpha(Image.fromarray(alpha))
        assert max(out.size) <= 2400, out.size
        out.save(path, "WEBP", quality=90, method=6)
        return out.size


def font():
    """Roboto, the docs' font, from a docs site's social-card cache when there is one; else matplotlib's DejaVu."""
    from matplotlib.font_manager import FontProperties
    for site in [ROOT] + sorted(ROOT.parent.glob("*")):
        f = site / ".cache" / "plugin" / "social" / "fonts" / "Roboto" / "Regular.ttf"
        if f.exists():
            return FontProperties(fname=str(f))
    return FontProperties(family="DejaVu Sans")


# ------------------------------------------------------------------------------------------------ the four views
# right, up: the view's axes in the gripper's frame (X up to the camera, Y along the jaw travel, Z to the jaw tips),
# third-angle projection round the front view
VIEWS = {
    "front": ([0, 1, 0], [0, 0, 1]),       # from the camera side (+X): the jaws up, the travel across
    "side": ([-1, 0, 0], [0, 0, 1]),       # from +Y, the right of the front view: the camera on the left
    "top": ([0, 1, 0], [-1, 0, 0]),        # from the jaw tips (+Z)
    "coupler": ([0, 1, 0], [1, 0, 0]),     # from the robot (-Z): the coupler
}


def annotate(view: str, sh: Sheet, M: dict[str, float]):
    """The dimensions of each view. Feature points are given in the gripper's frame (x, y, z) and projected."""
    right, up = (np.array(v, float) for v in VIEWS[view])

    def P(x, y, z):
        p = np.array([x, y, z], float)
        return np.array([p @ right, p @ up])

    W2, top, cx = M["width"] / 2, M["tip_z"], M["jaw_centre_x"]
    J2 = M["jaws_width"] / 2
    if view == "front":                     # u = y, v = z
        sh.dim(P(0, -W2, M["blocker_z1"]), P(0, W2, M["blocker_z1"]), top + 16, True)           # overall width
        sh.dim(P(0, -J2, M["outer_z1"]), P(0, J2, M["outer_z1"]), top + 8, True)                # over the jaws
        zf = (M["face_z0"] + M["face_z1"]) / 2
        sh.dim(P(0, -M["opening"] / 2, zf), P(0, M["opening"] / 2, zf), zf, True)               # between the faces
        sh.dim(P(0, -M["ring_d"] / 2, 0), P(0, -M["tip_y"], top), -W2 - 12, False)               # overall height
        sh.dim(P(0, J2, M["rail_z1"]), P(0, M["tip_y"], top), W2 + 10, False, text_side=-1)
    elif view == "side":                    # u = -x, v = z
        sh.dim(P(M["x_max"], 0, M["top_z"]), P(M["x_min"], 0, M["face_z0"]), top + 14, True)     # overall depth
        sh.centre_line(P(0, 0, -16), P(0, 0, M["ring_t"] + 6))                                   # the coupler axis
        sh.centre_line(P(cx, 0, M["jaw_z0"] - 4), P(cx, 0, top + 4))                             # the jaws' centre
        sh.dim(P(0, 0, -1), P(cx, 0, M["jaw_z0"]), -12, True, text_side=-1)                      # axis to the jaws
        sh.dim(P(-M["ring_d"] / 2, 0, 0), P(-M["ring_d"] / 2, 0, M["ring_t"]), -M["x_min"] + 10, False,
               text_side=-1)                                                                     # the coupler ring
        sh.dim(P(M["front_x"], 0, M["body_front_z"]), P(M["x_max"], 0, 0), -M["x_max"] - 10, False)  # to the mount's front
        # the camera's optical axis, from the lens toward the jaws, and its angle to Z
        lens = P(M["lens_x"], 0, M["lens_z"])
        a = math.radians(M["camera_deg"])
        d = np.array([math.sin(a), math.cos(a)])                                                 # in (u, v): -x is +u
        sh.centre_line(lens - d * 6, lens + d * ((M["lens_x"] - cx) / math.sin(a)))
        sh.centre_line(lens, lens + np.array([0, 40]))
        sh.angle(lens, 90 - M["camera_deg"], 90, 32)
    elif view == "top":                     # u = y, v = -x
        vt = -M["x_min"]
        sh.dim(P(M["blocker_x0"], -W2, 0), P(M["blocker_x0"], W2, 0), vt + 16, True)             # overall width
        sh.dim(P(M["x_min"], J2 - M["jaw_w"], 0), P(M["x_min"], J2, 0), vt + 6, True)            # a jaw across
        sh.dim(P(M["jaw_x0"], J2, 0), P(M["jaw_x1"], J2, 0), W2 + 10, False, text_side=-1)       # a jaw along X
        sh.dim(P(M["x_min"], -J2, 0), P(M["x_max"], M["top_y0"], 0), -W2 - 12, False)           # overall depth
    elif view == "coupler":                 # u = y, v = x
        sh.diameter((0, 0), M["ring_d"] / 2, 35, 22)
        sh.diameter((0, 0), M["recess_d"] / 2, 150, 32)
        sh.centre_line(P(0, -M["ring_d"] / 2 - 6, 0), P(0, W2 + 12, 0))                          # the coupler axis
        sh.centre_line(P(-M["ring_d"] / 2 - 6, 0, 0), P(M["ring_d"] / 2 + 6, 0, 0))
        sh.centre_line(P(cx, -W2 - 4, 0), P(cx, W2 + 12, 0))                                     # the jaws' centre
        sh.dim(P(0, W2 + 2, 0), P(cx, W2 + 2, 0), W2 + 10, False, text_side=-1)                  # axis to the jaws
        sh.dim(P(0, W2 + 2, 0), P(M["x_max"], M["top_y1"], 0), W2 + 10, False, text_side=-1)     # axis to the mount top
        sh.dim(P(M["blocker_x0"], -W2, 0), P(M["blocker_x0"], W2, 0), M["x_min"] - 10, True, text_side=-1)


def draw(parts, M, preview: Path | None, out: Path = OUT):
    out.mkdir(parents=True, exist_ok=True)
    allm = meshes_of(parts)
    for view, (right, up) in VIEWS.items():
        segs = visible_lines(allm, right, up)
        if abs(np.cross(right, up)[2]) > 0.99:                     # seen along the coupler axis
            segs = true_circles(segs, [r for r, _, _ in radii(parts["msg_gripper_link"], zmax=20.0, rmax=30.0)])
        for theme in THEMES:
            sh = Sheet(segs, theme)
            annotate(view, sh, M)
            name = f"msg_{view}" + ("_dark" if theme == "dark" else "")
            size = sh.save(out / f"{name}.webp", preview)
            print(f"wrote {(out / name).relative_to(ROOT)}.webp, {size[0]} x {size[1]} px, {len(segs)} line segments")


# ------------------------------------------------------------------------------------------------ the variants
def variants(step_repo: Path, M: dict[str, float] | None):
    """The parts that change with the rail and the stepper, measured in their STEP files; with the drawn variant's
    measurements M, the overall sizes of the other steppers (the cover's outer end carries the camera mount)."""
    import cadquery as cq

    def box(rel):
        bb = cq.importers.importStep(str(step_repo / STEP / rel)).val().BoundingBox()
        return bb
    print("Rail | body length | jaw blocker thickness | width over the jaw blockers")
    blocker = box("Common parts/jaw_blocker.STEP").zlen
    for rail in (100, 150, 200):
        body = box(f"Linear rail dependant parts/{rail}mm rail/MSG_Gripper_body_{rail}mm.STEP").xlen
        print(f"{rail} mm | {body:.2f} | {blocker:.2f} | {body + 2 * blocker:.2f}")
    print("Stepper | cover length | cover's outer end, from the 21.5 mm one | depth along X | axis to the mount's top")
    ref = None
    for name in ("21_5", "40", "60"):
        bb = box(f"Stepper dependant parts/{name}mm stepper/Stepper_cover_{name}mm.STEP")
        ref = bb.zmin if ref is None else ref
        shift = ref - bb.zmin
        sizes = f" | {M['depth'] + shift:.2f} | {M['x_max'] + shift:.2f}" if M else ""
        print(f"{name.replace('_', '.')} mm | {bb.zlen:.2f} | {shift:+.2f}{sizes}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", help="the clone of robot_descriptions")
    ap.add_argument("--step", help="the clone of MSG-compliant-AI-stepper-gripper (for --variants)")
    ap.add_argument("--preview", help="also write each drawing as PNG into this folder")
    ap.add_argument("--measure", action="store_true", help="print the numbers, draw nothing")
    ap.add_argument("--variants", action="store_true", help="print what changes per rail and stepper")
    args = ap.parse_args(argv)
    models = find_dir(args.models, "ROBOT_DESCRIPTIONS_DIR", "robot_descriptions", DESC / URDF)
    parts = load_assembly(models)
    M = measure(parts)
    if args.variants:
        variants(find_dir(args.step, "GRIPPER_REPO_DIR", "MSG-compliant-AI-stepper-gripper", STEP), M)
        return 0
    for k, v in M.items():
        print(f"  {k:14s} {v:8.2f} mm")
    if not args.measure:
        draw(parts, M, Path(args.preview) if args.preview else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
