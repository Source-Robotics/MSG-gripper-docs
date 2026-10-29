"""Write the version facts of versions.yml into the pages (the same hook as Source-Robotics/par6, for a product
that runs another product's firmware).

Two placeholders, each replaced when the site is built:

    <!-- doc-meta: KEY -->      a manual's version box, on its landing page: document number, the gripper release,
                                the driver firmware release (for a document that describes one), revision,
                                publication date, what it applies to
    <!-- documents-table -->    the list of every document, on the About page

The facts live in versions.yml only. docs_version is the gripper release: the product repository's tag without
its V, and the name the site is published under. firmware.version is the driver firmware release the pages and
the generated reference describe; a new firmware release for the same gripper updates the site in place. A
malformed or missing fact, or an unknown manual, stops the build: a version on a page is never guessed.
Registered in mkdocs.yml under `hooks:`.
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

import yaml
from mkdocs.exceptions import PluginError

META_RE = re.compile(r"<!--\s*doc-meta:\s*([A-Za-z0-9_-]+)\s*-->")
TABLE_RE = re.compile(r"<!--\s*documents-table\s*-->")
REQUIRED = ("number", "title", "revision", "status", "covers")

_facts: dict = {}


def load(path) -> dict:
    """versions.yml, checked. Raises PluginError naming what is wrong."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PluginError(f"versions.yml: {exc}") from exc
    if not isinstance(data, dict):
        raise PluginError("versions.yml: not a mapping")
    docs_version = str(data.get("docs_version", ""))
    if not re.fullmatch(r"\d+(\.\d+)*", docs_version):
        raise PluginError(f"versions.yml: docs_version {docs_version!r} is not a gripper release, e.g. \"1.1\"")
    product = data.get("product")
    if not isinstance(product, dict) or not all(product.get(k) for k in ("name", "repository", "tag")):
        raise PluginError("versions.yml: product needs name, repository and tag")
    ptag = str(product["tag"])
    if not re.fullmatch(r"[Vv]\d+(\.\d+)*", ptag):
        raise PluginError(f"versions.yml: product.tag {ptag!r} is not a release tag like V1.1")
    if ptag[1:] != docs_version:
        raise PluginError(f"versions.yml: product.tag {ptag} does not belong to docs_version {docs_version}")
    fw = data.get("firmware")
    if not isinstance(fw, dict) or not all(fw.get(k) for k in ("name", "version", "repository", "tag")):
        raise PluginError("versions.yml: firmware needs name, version, repository and tag")
    fw_version = str(fw["version"])
    if not re.fullmatch(r"\d+", fw_version):
        raise PluginError(f"versions.yml: firmware.version {fw_version!r} is not a firmware release number, e.g. \"108\"")
    tag = str(fw["tag"])
    if not re.fullmatch(r"[Vv]\d+", tag):
        raise PluginError(f"versions.yml: firmware.tag {tag!r} is not a release tag like V108")
    if tag[1:] != fw_version:
        raise PluginError(f"versions.yml: firmware.tag {tag} does not belong to firmware.version {fw_version}")
    manuals = data.get("manuals")
    if not isinstance(manuals, dict) or not manuals:
        raise PluginError("versions.yml: no manuals")
    for key, doc in manuals.items():
        missing = [f for f in REQUIRED if not (doc or {}).get(f)]
        if missing:
            raise PluginError(f"versions.yml: manual {key!r} lacks {', '.join(missing)}")
        if not re.fullmatch(r"\d{4}\.[A-Z]", str(doc["revision"])):
            raise PluginError(f"versions.yml: manual {key!r} revision {doc['revision']!r} is not YEAR.LETTER, e.g. 2026.A")
        if doc["status"] not in ("draft", "published"):
            raise PluginError(f"versions.yml: manual {key!r} status {doc['status']!r} is not draft or published")
        published = doc.get("published")
        if doc["status"] == "published" and not isinstance(published, datetime.date):
            raise PluginError(f"versions.yml: manual {key!r} is published but has no publication date (YYYY-MM-DD)")
    return data


def meta_block(key: str, data: dict) -> str:
    """The version box of manual `key`."""
    doc = data["manuals"].get(key)
    if doc is None:
        raise PluginError(f"doc-meta: no manual {key!r} in versions.yml")
    product, fw = data["product"], data["firmware"]
    draft = doc["status"] == "draft"
    lines = [f"**Document number:** {doc['number']}",
             f"**{product['name']} release:** {data['docs_version']}"]
    if doc.get("firmware"):
        lines.append(f"**Firmware:** {fw['name']} {fw['version']}")
    lines.append(f"**Revision:** {doc['revision']}" + (" (draft)" if draft else ""))
    published = doc.get("published")
    lines.append(f"**Published:** {published.isoformat() if isinstance(published, datetime.date) else '—'}")
    applies = f"{product['name']} release {data['docs_version']}"
    if doc.get("applies_to"):
        applies += f" {doc['applies_to']}"
    if doc.get("firmware"):
        applies += f", {fw['name']} firmware {fw['version']}"
    lines.append(f"**Applies to:** {applies}")
    lines.append("*Original instructions*")
    return '<div class="doc-meta" markdown>\n\n' + "\n\n".join(lines) + "\n\n</div>"


def documents_table(data: dict) -> str:
    """Every document, with its number and what it covers."""
    product, fw = data["product"], data["firmware"]
    rows = [f"| {d['title']} | {d['number']} | {d['covers']} |" for d in data["manuals"].values()]
    return ("| Document | Number | Covers |\n|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"A document marked with a firmware release describes {product['name']} release {data['docs_version']} "
            f"running {fw['name']} firmware {fw['version']}. The version selector in the header switches between "
            "gripper releases; a new firmware release for the same gripper updates the pages in place. The "
            "compatibility table says which firmware, Python library and hardware revisions work together.")


def on_config(config):
    global _facts
    _facts = load(Path(config.config_file_path).parent / "versions.yml")
    config.extra["docs_version"] = _facts["docs_version"]
    config.extra["firmware_version"] = str(_facts["firmware"]["version"])
    return config


def on_page_markdown(markdown, page, config, files):
    markdown = META_RE.sub(lambda m: meta_block(m.group(1), _facts), markdown)
    return TABLE_RE.sub(lambda m: documents_table(_facts), markdown)
