#!/usr/bin/env python3
"""Copy the gripper repository's bill of materials into the docs, as it is.

    python tools/sync_bom.py [--repo PATH] [--check]

Reads the BOM from a clone of the product repository named in versions.yml (product.repository): --repo, else
$GRIPPER_REPO_DIR, else a sibling folder of this repository or ../../projects/<name>. Writes
docs/build/bill-of-materials.md and docs/assets/bom/. The page is the repository's file with these changes only:

  - a header that names the original and the commit it was copied from
  - GitHub's `> [!NOTE]` / `> [!TIP]` blocks and `> **Note:**` quotes become admonitions
  - links to images in the repository become small inline pictures (click to enlarge), scaled to 400 px
  - links to other files of the repository become absolute, PCrnjak/ paths become Source-Robotics/, and an
    empty link ("coming soon") becomes plain text

Everything else, the parts, the quantities, the purchase links, is left untouched: a wrong part is fixed in the
repository's file, then this tool is run again. --check exits 1 when the page is out of date.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "build" / "bill-of-materials.md"
IMG_DIR = ROOT / "docs" / "assets" / "bom"
BOM_PATH = {"MSG-compliant-AI-stepper-gripper": "BOM.md", "SSG-48-adaptive-electric-gripper": "BOM/BOM.md"}
THUMB = 120
STORED = 400

HEADER = """# Bill of materials

!!! note "This is a copy"
    The original is [{bom}]({url}/blob/main/{bom_url}) in the gripper's repository; this page is that file as of
    {when} (commit `{commit}`), with the reference images shown inline. If a link is broken or a part is wrong,
    [open an issue]({url}/issues/new) there, and the fix lands here with the next sync. The shop's
    [starter kit](index.md#kits-and-the-shop) covers the driver and everything its setup needs.

"""


def product() -> tuple[str, str]:
    data = yaml.safe_load((ROOT / "versions.yml").read_text(encoding="utf-8"))
    url = str(data["product"]["repository"]).rstrip("/")
    return url, url.rsplit("/", 1)[-1]


def find_repo(arg: str | None, name: str, bom: str) -> Path:
    for c in (arg, os.environ.get("GRIPPER_REPO_DIR"), ROOT.parent / name, ROOT.parent.parent / "projects" / name):
        if c and (Path(c) / bom).exists():
            return Path(c)
    sys.exit(f"sync_bom: no clone of {name} found; pass --repo PATH")


def safe_name(name: str) -> str:
    stem, ext = os.path.splitext(name)
    return re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_") + ext.lower()


def convert(text: str, repo: Path, bom: str, url: str, write_images: bool) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\A# .*\n+", "", text)                      # the title: ours
    text = re.sub(r"\n---\n", "\n", text)                       # the headings separate the sections
    text = text.replace("github.com/PCrnjak/", "github.com/Source-Robotics/")

    def admonition(m):
        kind = (m.group(1) or "note").lower()
        body = " ".join(line.lstrip("> ").strip() for line in m.group(2).split("\n") if line.strip())
        return f"!!! {kind}\n    {body}\n"
    text = re.sub(r"> \[!(NOTE|TIP|WARNING|IMPORTANT)\]\n((?:>.*\n?)+)", admonition, text)
    text = re.sub(r"> \*\*Note:\*\* (.*)\n", lambda m: f"!!! note\n    {m.group(1)}\n", text)
    text = re.sub(r"\[([^\]]+)\]\(\)", r"\1", text)             # an empty link: plain text

    bom_dir = (repo / bom).parent
    img_src_used: dict[Path, str] = {}

    def link(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|#)", target):
            return m.group(0)
        rel = unquote(target)
        local = (bom_dir / rel).resolve()
        if local.suffix.lower() in (".png", ".jpg", ".jpeg"):
            if not local.exists():
                sys.exit(f"sync_bom: the BOM refers to a missing image: {rel}")
            safe = safe_name(local.name)
            img_src_used[local] = safe
            return f'![{local.stem}](../assets/bom/{safe}){{ width="{THUMB}" }}'
        try:
            inside = local.relative_to(repo.resolve()).as_posix()
        except ValueError:
            return m.group(0)
        kind = "tree" if local.is_dir() else "blob"
        return f"[{label}]({url}/{kind}/main/{inside.replace(' ', '%20')})"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    if write_images:
        from PIL import Image
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        for old in IMG_DIR.iterdir():
            if old.name not in img_src_used.values():
                old.unlink()
        for src, safe in img_src_used.items():
            im = Image.open(src)
            im = im.convert("RGB") if safe.endswith(".jpg") else im.convert("RGBA")
            im.thumbnail((STORED, STORED))
            im.save(IMG_DIR / safe, optimize=True)
    return text.strip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="the clone of the gripper repository")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the page is out of date")
    args = ap.parse_args(argv)
    url, name = product()
    bom = BOM_PATH.get(name, "BOM.md")
    repo = find_repo(args.repo, name, bom)
    try:
        commit, when = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h %cs", "--", bom],
                                      capture_output=True, text=True, check=True).stdout.split()
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        commit, when = "unknown", "today"
    body = convert((repo / bom).read_text(encoding="utf-8"), repo, bom, url, write_images=not args.check)
    page = (HEADER.format(bom=bom, bom_url=bom.replace(" ", "%20"), url=url, when=when, commit=commit) + body).replace("\n", "\r\n")
    if args.check:
        current = PAGE.read_bytes().decode("utf-8") if PAGE.exists() else ""
        same = current.split("\r\n\r\n", 2)[-1:] == page.split("\r\n\r\n", 2)[-1:]
        print("bill-of-materials.md is " + ("up to date" if same else "OUT OF DATE: run tools/sync_bom.py"))
        return 0 if same else 1
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_bytes(page.encode("utf-8"))
    print(f"wrote {PAGE.relative_to(ROOT)} from {repo} ({commit}, {when}); {len(list(IMG_DIR.iterdir()))} reference images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
