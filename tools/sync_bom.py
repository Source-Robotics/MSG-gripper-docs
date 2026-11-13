#!/usr/bin/env python3
"""Copy the gripper repository's bill of materials into the docs, as it is.

    python tools/sync_bom.py [--repo PATH] [--check]

Reads the BOM from a clone of the product repository named in versions.yml (product.repository): --repo, else
$GRIPPER_REPO_DIR, else a sibling folder of this repository or ../../projects/<name>. Writes
docs/build/bill-of-materials.md and docs/assets/bom/. The page is the repository's file with these changes only:

  - a header that names the original and the commit it was copied from
  - GitHub's `> [!NOTE]` / `> [!TIP]` blocks and `> **Note:**` quotes become admonitions
  - links to images in the repository become small inline pictures (click to enlarge), scaled to 400 px and
    stored as WebP
  - links to other files of the repository become absolute, PCrnjak/ paths become Source-Robotics/, and an
    empty link ("coming soon") becomes plain text
  - a list right after a line of text gets the blank line before it that Python-Markdown needs (GitHub renders
    the list without it)

Everything else, the parts, the quantities, the purchase links, is left untouched: a wrong part is fixed in the
repository's file, then this tool is run again. --check exits 1 when the page is out of date.

When docs/includes/bom-variants.yml exists (the MSG: which rows each version needs), the tool writes it into the
page for the version selector (docs/javascripts/bom-variants.js) and stops when an entry finds no row, finds more
than one, or names an option the file does not offer.
"""
from __future__ import annotations

import argparse
import html
import json
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
VARIANTS = ROOT / "docs" / "includes" / "bom-variants.yml"
BOM_PATH = {"MSG-compliant-AI-stepper-gripper": "BOM.md", "SSG-48-adaptive-electric-gripper": "BOM/README.md"}
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
    stem = os.path.splitext(name)[0]
    return re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_") + ".webp"


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
    # a list right after a line of text: Python-Markdown needs a blank line between them, GitHub does not
    text = re.sub(r"(?m)^(?!\s|[-*+] |\d+\. |[>|!#<])(.+)\n(?=[-*+] |\d+\. )", r"\1\n\n", text)

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
            im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
            im.thumbnail((STORED, STORED))
            im.save(IMG_DIR / safe, "WEBP", quality=82, method=6)
    return text.strip() + "\n"


def bom_rows(text: str) -> list[tuple[str, list[str]]]:
    """(section, cells) of every row of every table: the section is the ## heading above the table."""
    rows, section, header = [], "", False
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith("## "):
            section = line[3:].strip()
        if not line.startswith("|"):
            header = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header:
            header = True                                   # the first line of a table is its header
        elif not set("".join(cells)) <= set(":- "):
            rows.append((section, cells))
    return rows


def found_rows(entry: dict, rows: list[tuple[str, list[str]]]) -> list[int]:
    """The rows a bom-variants.yml entry names: its section, its first cell, and its `has` text if it gives one."""
    return [i for i, (section, cells) in enumerate(rows)
            if section == entry.get("section") and cells and cells[0] == entry.get("first")
            and (not entry.get("has") or entry["has"] in " | ".join(cells))]


def variant_problems(data: dict, rows: list[tuple[str, list[str]]]) -> list[str]:
    """Every entry finds exactly one row, and names only choices and options the file offers."""
    problems, choices = [], data.get("choices") or {}
    for e in data.get("rows") or []:
        name = f"{e.get('section')} / {e.get('first')}" + (f" ({e['has']})" if e.get("has") else "")
        hits = len(found_rows(e, rows))
        if hits != 1:
            problems.append(f"{name} finds {hits} rows, not one")
        for key in ("only", "note"):
            for choice, values in (e.get(key) or {}).items():
                offered = (choices.get(choice) or {}).get("options") or {}
                if choice not in choices or not set(values) <= set(offered):
                    problems.append(f"{name}: {key} names an unknown choice or option: {choice} {list(values)}")
    for choice in ("rail", "stepper"):
        offered = set(((choices.get(choice) or {}).get("options") or {}))
        if set(((data.get("print") or {}).get(choice) or {})) != offered:
            problems.append(f"print.{choice} does not cover exactly the {choice} options")
    return problems


def variant_box(body: str) -> str:
    """The element the version selector fills, with bom-variants.yml in it; empty when there is no such file."""
    if not VARIANTS.exists():
        return ""
    data = yaml.safe_load(VARIANTS.read_text(encoding="utf-8"))
    problems = variant_problems(data, bom_rows(body))
    if problems:
        sys.exit("sync_bom: the BOM and docs/includes/bom-variants.yml disagree:\n  " + "\n  ".join(problems))
    payload = html.escape(json.dumps(data, ensure_ascii=False, separators=(",", ":")), quote=True)
    return f'<div class="bom-variants" data-variants="{payload}"></div>\n\n'


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
    page = (HEADER.format(bom=bom, bom_url=bom.replace(" ", "%20"), url=url, when=when, commit=commit)
            + variant_box(body) + body).replace("\n", "\r\n")
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
