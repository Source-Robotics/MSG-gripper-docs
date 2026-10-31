#!/usr/bin/env python3
"""Build the 3D model the landing page's configurator shows, from the repository's URDF.

    python tools/build_model.py [--repo PATH]

Writes docs/assets/models/msg/: body.glb (the gripper body), jaws_printed.glb (the two printed jaws of the URDF,
at the closed position with their joint transforms baked in) and viewer.json: the jaw options, the direction and
travel of each jaw's opening, the colour swatches and the default opening. docs/javascripts/gripper-viewer.js
reads them. The URDF models the 150 mm rail variant. The scene stands as the gripper does in its photos (glTF is
Y-up): the stepper upright with the camera on top, the fingers pointing forward along +X; it is centred, and the
body mesh is decimated for the web. Needs trimesh (with fast-simplification), numpy and pyyaml.
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
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "models" / "msg"
DESC = Path("MSG_gripper_description") / "URDF" / "msg_gripper"
URDF = DESC / "urdf" / "PAR6_MSG.urdf"
BODY = DESC / "meshes" / "gripper.STL"
OPTIONS = [  # key, label, folder under DESC holding jaw1.STL and jaw2.STL
    ("printed", "Printed jaws", Path("meshes")),
]
COLOURS = {
    "body": {"Grey": "#d2d2cf", "Black": "#1a1a1a", "White": "#f2f2f0"},
    "jaws": {"Black": "#1a1a1a", "Grey": "#9a9a98", "Yellow": "#f2c230"},
}
MAX_FACES = 30000          # the body mesh of the URDF has 64 000 faces: too many for a landing page
Y_UP = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
# The URDF's fingers point along its Z (Y once turned Y-up) with the stepper lying along -X; a quarter turn about
# the rail's axis stands the stepper up and points the fingers forward, as the gripper stands on a table.
UPRIGHT = trimesh.transformations.rotation_matrix(-np.pi / 2, [0, 0, 1]) @ Y_UP


def find_repo(arg: str | None) -> Path:
    name = str(yaml.safe_load((ROOT / "versions.yml").read_text(encoding="utf-8"))["product"]["repository"]).rstrip("/").rsplit("/", 1)[-1]
    for c in (arg, os.environ.get("GRIPPER_REPO_DIR"), ROOT.parent / name, ROOT.parent.parent / "projects" / name):
        if c and (Path(c) / URDF).exists():
            return Path(c)
    sys.exit(f"build_model: no clone of {name} with {URDF} found; pass --repo PATH")


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


def material(hex_colour: str):
    rgb = [int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)]
    return trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=rgb + [255], metallicFactor=0.0, roughnessFactor=0.65, doubleSided=True))


def export(meshes: dict[str, trimesh.Trimesh], path: Path, colour: str):
    scene = trimesh.Scene()
    for name, mesh in meshes.items():
        mesh.visual = material(colour)
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.export(path)
    return path.stat().st_size // 1024


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
    ap.add_argument("--repo", help="the clone of the gripper repository")
    args = ap.parse_args(argv)
    repo = find_repo(args.repo)
    robot = ET.parse(repo / URDF).getroot()
    joints = {j.find("child").get("link"): j for j in robot.findall("joint")}
    links = {l.get("name"): l for l in robot.findall("link")}

    # each jaw's pose at a joint value q (prismatic: the joint origin, then the slide along the axis), the two ends
    # of its travel, and which end is closed: the one where the two default jaw meshes are nearest each other
    def pose(jaw, q):
        j = joints[jaw]
        axis = np.array([float(v) for v in j.find("axis").get("xyz").split()])
        slide = np.eye(4)
        slide[:3, 3] = axis * q
        return UPRIGHT @ origin_matrix(j.find("origin")) @ slide @ origin_matrix(links[jaw].find("visual/origin"))

    def far_end(jaw):                                # the limit away from 0; a mimic joint follows its source
        j = joints[jaw]
        mimic = j.find("mimic")
        if mimic is not None:
            src = [c for c, jj in joints.items() if jj.get("name") == mimic.get("joint")][0]
            return far_end(src) * float(mimic.get("multiplier", 1)) + float(mimic.get("offset", 0))
        lim = j.find("limit")
        lo, hi = float(lim.get("lower", 0)), float(lim.get("upper", 0))
        return lo if abs(lo) > abs(hi) else hi

    default = {jaw: load_mesh(repo / DESC / OPTIONS[0][2] / f"{jaw}.STL") for jaw in ("jaw1", "jaw2")}
    ends = {jaw: (0.0, far_end(jaw)) for jaw in default}

    def gap(i):                                      # distance between the jaw meshes with both at end i
        c = [pose(jaw, ends[jaw][i]) @ np.append(default[jaw].centroid, 1) for jaw in default]
        return float(np.linalg.norm(c[0][:3] - c[1][:3]))

    closed = 0 if gap(0) <= gap(1) else 1
    jaw_world, jaw_dir, travel = {}, {}, 0.0
    for jaw in default:
        q_closed, q_open = ends[jaw][closed], ends[jaw][1 - closed]
        jaw_world[jaw] = pose(jaw, q_closed)
        d = pose(jaw, q_open)[:3, 3] - jaw_world[jaw][:3, 3]
        travel = float(np.linalg.norm(d))
        jaw_dir[jaw] = (d / travel).round(6).tolist()
    body_m = UPRIGHT @ origin_matrix(links["gripper"].find("visual/origin"))

    body = load_mesh(repo / BODY)
    body.apply_transform(body_m)
    for jaw, mesh in default.items():
        mesh.apply_transform(jaw_world[jaw])
    centre = np.vstack([body.bounds] + [m.bounds for m in default.values()])
    offset = -(centre.min(axis=0) + centre.max(axis=0)) / 2
    body.apply_translation(offset)
    if OUT.exists():
        for old in OUT.iterdir():
            old.unlink()
    sizes = {"body.glb": export({"gripper": body}, OUT / "body.glb", COLOURS["body"]["Grey"])}
    options = []
    for key, label, folder in OPTIONS:
        meshes = {}
        for jaw in jaw_world:
            mesh = load_mesh(repo / DESC / folder / f"{jaw}.STL")
            mesh.apply_transform(jaw_world[jaw])
            mesh.apply_translation(offset)
            meshes[jaw] = mesh
        sizes[f"jaws_{key}.glb"] = export(meshes, OUT / f"jaws_{key}.glb", COLOURS["jaws"]["Black"])
        options.append({"key": key, "label": label, "file": f"jaws_{key}.glb"})
    config = {
        "body": "body.glb", "jaws": options, "travel_m": round(travel, 6), "dir": jaw_dir,
        "colors": COLOURS, "default": {"jaws": OPTIONS[0][0], "opening": 0.5, "body": "#d2d2cf", "jaws_color": "#1a1a1a"},
        "camera": {"azimuth_deg": 55, "polar_deg": 68, "fill": 1.0},     # in front of the fingers, to one side, a little above
    }
    packed = {f.name: compress(f) for f in sorted(OUT.glob("*.glb"))}
    sizes_after = {f.name: f.stat().st_size // 1024 for f in sorted(OUT.glob("*.glb"))}
    (OUT / "viewer.json").write_text(json.dumps(config, indent=1) + "\n", encoding="utf-8")
    for m in default.values():
        m.apply_translation(offset)
    allb = np.vstack([body.bounds] + [m.bounds for m in default.values()])
    ext = (allb.max(axis=0) - allb.min(axis=0)) * 1000
    print(f"wrote {OUT.relative_to(ROOT)}: " + ", ".join(f"{k} {v} KB" for k, v in sizes.items())
          + f"; travel {travel * 1000:.0f} mm, model {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm")
    print("after compression: " + ", ".join(f"{k} {v} KB ({packed[k]})" for k, v in sizes_after.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
