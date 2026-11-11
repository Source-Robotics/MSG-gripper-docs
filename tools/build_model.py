#!/usr/bin/env python3
"""Build the 3D model the landing page's configurator shows, from the robot model in robot_descriptions.

    ..\\..\\.venv-cad\\Scripts\\python tools\\build_model.py [--models PATH]

Reads projects/robot_descriptions (urdf/msg_description: msg_solid.urdf and msg_soft_tpu.urdf, the assembled
gripper with the 150 mm rail and the 21.5 mm stepper) and writes docs/assets/models/msg/: body.glb (the body: the
printed structure, the motor and the camera lens), jaws_solid.glb and jaws_soft_tpu.glb (the two jaw options of the
model, each jaw at the closed position with its joint transform baked in) and viewer.json: the jaw options, the
direction and travel of each jaw's opening, the colour swatches and the default opening.
docs/javascripts/gripper-viewer.js reads them.

The colour pickers repaint the printed parts only. Parts with a colour of their own in the model (the motor, the
camera lens, the TPU pads) are exported under a name starting with `fixed_`, which the viewer leaves as it is.

The scene stands as the gripper does in its photos (glTF is Y-up): the stepper upright with the camera on top, the
fingers pointing forward along +X; it is centred, and large meshes are decimated for the web. Needs trimesh (with
fast-simplification), numpy and pyyaml: the cadquery environment .venv-cad at the workspace root has them.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "models" / "msg"
PKG = Path("urdf") / "msg_description"
OPTIONS = [  # key, label, the URDF of that jaw option
    ("solid", "Solid jaws", "msg_solid.urdf"),
    ("soft_tpu", "TPU jaws", "msg_soft_tpu.urdf"),
]
BODY_LINK = "msg_gripper_link"
JAWS = {"left_finger_link": "jaw1", "right_finger_link": "jaw2"}    # the viewer moves the nodes jaw1 and jaw2
FIXED = {"msg_camera_lens_black", "msg_gripper_motor_black", "msg_jaw_yellow"}   # URDF materials kept as they are
COLOURS = {
    "body": {"Grey": "#d2d2cf", "Black": "#1a1a1a", "White": "#f2f2f0"},
    "jaws": {"Black": "#1a1a1a", "Grey": "#9a9a98", "Yellow": "#f2c230"},
}
MAX_FACES = 30000          # per mesh: enough for a landing page
# The URDF's link frame has the fingers along -Z, the stepper and the camera along -X and the jaw travel along Y.
# This turns -X up (+Y), -Z forward (+X) and Y to +Z: the stepper stands up and the fingers point forward.
UPRIGHT = np.array([[0, 0, -1, 0], [-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float)


def find_models(arg: str | None) -> Path:
    for c in (arg, os.environ.get("ROBOT_DESCRIPTIONS_DIR"), ROOT.parent / "robot_descriptions",
              ROOT.parent.parent / "projects" / "robot_descriptions"):
        if c and (Path(c) / PKG / OPTIONS[0][2]).exists():
            return Path(c)
    sys.exit(f"build_model: no clone of robot_descriptions with {PKG / OPTIONS[0][2]} found; pass --models PATH")


def origin_matrix(el) -> np.ndarray:
    if el is None:
        return np.eye(4)
    xyz = [float(v) for v in (el.get("xyz") or "0 0 0").split()]
    rpy = [float(v) for v in (el.get("rpy") or "0 0 0").split()]
    m = trimesh.transformations.euler_matrix(rpy[0], rpy[1], rpy[2], "sxyz")
    m[:3, 3] = xyz
    return m


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh")
    if len(mesh.faces) > MAX_FACES:
        mesh = mesh.simplify_quadric_decimation(face_count=MAX_FACES)
    return mesh


def visuals(link, pkg: Path):
    """(mesh, its colour as #rrggbb, fixed?) for every visual of a URDF link, in the link's frame."""
    out = []
    for v in link.findall("visual"):
        g = v.find("geometry/mesh")
        if g is None:
            continue
        mesh = load_mesh(pkg / g.get("filename"))
        if g.get("scale"):
            mesh.apply_scale([float(s) for s in g.get("scale").split()])
        mesh.apply_transform(origin_matrix(v.find("origin")))
        mat = v.find("material")
        rgba = mat.find("color").get("rgba").split() if mat is not None and mat.find("color") is not None else "1 1 1 1".split()
        colour = "#" + "".join(f"{round(float(c) * 255):02x}" for c in rgba[:3])
        out.append((mesh, colour, (mat.get("name") if mat is not None else "") in FIXED))
    return out


def material(hex_colour: str):
    rgb = [int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)]
    return trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=rgb + [255], metallicFactor=0.0, roughnessFactor=0.65, doubleSided=True))


def compress(path: Path) -> str:
    """Meshopt compression with gltfpack (Node.js): the file shrinks to a fraction, the browser decodes it with
    three.js's MeshoptDecoder. Named nodes are kept (-kn). Without Node.js the file stays as trimesh wrote it,
    which the viewer reads as well."""
    exe = os.environ.get("GLTFPACK") or shutil.which("gltfpack")
    npx = shutil.which("npx")
    cmd = [exe] if exe else ([npx, "--yes", "gltfpack@1.3.0"] if npx else None)
    if not cmd:
        print(f"note: no gltfpack (Node.js); {path.name} left uncompressed")
        return "uncompressed"
    packed = path.with_name(path.stem + ".packed.glb")
    subprocess.run(cmd + ["-i", str(path), "-o", str(packed), "-cc", "-kn"], check=True, capture_output=True)
    packed.replace(path)
    return "meshopt"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", help="the clone of robot_descriptions")
    args = ap.parse_args(argv)
    models = find_models(args.models)
    pkg = models / PKG
    commit = subprocess.run(["git", "-C", str(models), "describe", "--tags", "--always"], capture_output=True,
                            text=True).stdout.strip() or "unknown"

    def parse(urdf):
        robot = ET.parse(pkg / urdf).getroot()
        return ({j.find("child").get("link"): j for j in robot.findall("joint")},
                {l.get("name"): l for l in robot.findall("link")})

    joints, links = parse(OPTIONS[0][2])

    def pose(jaw, q):                                 # a jaw's frame at joint value q, in the body's link frame
        j = joints[jaw]
        axis = np.array([float(v) for v in j.find("axis").get("xyz").split()])
        slide = np.eye(4)
        slide[:3, 3] = axis * q
        return origin_matrix(j.find("origin")) @ slide

    def far_end(jaw):                                # the limit away from 0; a mimic joint follows its source
        j = joints[jaw]
        mimic = j.find("mimic")
        if mimic is not None:
            src = [c for c, jj in joints.items() if jj.get("name") == mimic.get("joint")][0]
            return far_end(src) * float(mimic.get("multiplier", 1)) + float(mimic.get("offset", 0))
        lim = j.find("limit")
        lo, hi = float(lim.get("lower", 0)), float(lim.get("upper", 0))
        return lo if abs(lo) > abs(hi) else hi

    # which end of the travel is closed: the one where the two jaws of the first option are nearest each other
    first = {jaw: trimesh.util.concatenate([m for m, _, _ in visuals(links[jaw], pkg)]) for jaw in JAWS}
    ends = {jaw: (0.0, far_end(jaw)) for jaw in JAWS}

    def gap(i):
        c = [pose(jaw, ends[jaw][i]) @ np.append(first[jaw].centroid, 1) for jaw in JAWS]
        return float(np.linalg.norm(c[0][:3] - c[1][:3]))

    closed = 0 if gap(0) <= gap(1) else 1
    jaw_frame, jaw_dir, travel = {}, {}, 0.0
    for jaw, name in JAWS.items():
        q_closed, q_open = ends[jaw][closed], ends[jaw][1 - closed]
        jaw_frame[jaw] = UPRIGHT @ pose(jaw, q_closed)
        d = (UPRIGHT @ pose(jaw, q_open))[:3, 3] - jaw_frame[jaw][:3, 3]
        travel = float(np.linalg.norm(d))
        jaw_dir[name] = (d / travel).round(6).tolist()

    body = visuals(links[BODY_LINK], pkg)
    for mesh, _, _ in body:
        mesh.apply_transform(UPRIGHT)
    closed_jaws = []
    for jaw in JAWS:
        m = first[jaw].copy()
        m.apply_transform(jaw_frame[jaw])
        closed_jaws.append(m)
    allb = np.vstack([m.bounds for m, _, _ in body] + [m.bounds for m in closed_jaws])
    offset = -(allb.min(axis=0) + allb.max(axis=0)) / 2

    if OUT.exists():
        for old in OUT.iterdir():
            old.unlink()
    OUT.mkdir(parents=True, exist_ok=True)

    scene = trimesh.Scene()
    for i, (mesh, colour, fixed) in enumerate(body):
        mesh.apply_translation(offset)
        name = f"fixed_body_{i}" if fixed else f"body_{i}"
        mesh.visual = material(colour if fixed else COLOURS["body"]["Grey"])
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    scene.export(OUT / "body.glb")
    sizes = {"body.glb": (OUT / "body.glb").stat().st_size // 1024}

    options = []
    for key, label, urdf in OPTIONS:
        _, olinks = parse(urdf)
        scene = trimesh.Scene()
        for jaw, name in JAWS.items():
            frame = jaw_frame[jaw].copy()
            frame[:3, 3] += offset
            scene.graph.update(frame_from=scene.graph.base_frame, frame_to=name, matrix=frame)
            for i, (mesh, colour, fixed) in enumerate(visuals(olinks[jaw], pkg)):
                part = f"fixed_{name}_{i}" if fixed else f"{name}_{i}"
                mesh.visual = material(colour if fixed else COLOURS["jaws"]["Black"])
                scene.add_geometry(mesh, node_name=part, geom_name=part, parent_node_name=name)
        scene.export(OUT / f"jaws_{key}.glb")
        sizes[f"jaws_{key}.glb"] = (OUT / f"jaws_{key}.glb").stat().st_size // 1024
        options.append({"key": key, "label": label, "file": f"jaws_{key}.glb"})

    config = {
        "body": "body.glb", "jaws": options, "travel_m": round(travel, 6), "dir": jaw_dir,
        "colors": COLOURS, "default": {"jaws": OPTIONS[0][0], "opening": 0.5, "body": "#d2d2cf", "jaws_color": "#1a1a1a"},
        "camera": {"azimuth_deg": 55, "polar_deg": 68, "fill": 1.0},     # in front of the fingers, to one side, a little above
        "source": f"robot_descriptions {commit}, {PKG.as_posix()}",
    }
    packed = {f.name: compress(f) for f in sorted(OUT.glob("*.glb"))}
    sizes_after = {f.name: f.stat().st_size // 1024 for f in sorted(OUT.glob("*.glb"))}
    (OUT / "viewer.json").write_text(json.dumps(config, indent=1) + "\n", encoding="utf-8")
    ext = (allb.max(axis=0) - allb.min(axis=0)) * 1000
    print(f"wrote {OUT.relative_to(ROOT)} from robot_descriptions {commit}: "
          + ", ".join(f"{k} {v} KB" for k, v in sizes.items())
          + f"; travel {travel * 1000:.1f} mm, model {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm")
    print("after compression: " + ", ".join(f"{k} {v} KB ({packed[k]})" for k, v in sizes_after.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
