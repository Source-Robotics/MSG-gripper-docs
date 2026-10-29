#!/usr/bin/env python3
"""Tests for hooks/versions.py, hooks/firmware_pages.py and the shipped data files. No network, no firmware
repository: fixtures and the files in the repository. Run: python tools/test_tools.py (the build check runs it on
every push)."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
fails = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (f"   [{detail}]" if detail and not cond else ""))
    if not cond:
        fails.append(name)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hook = load_module("versions_hook", ROOT / "hooks" / "versions.py")
pages = load_module("firmware_pages", ROOT / "hooks" / "firmware_pages.py")
from mkdocs.exceptions import PluginError  # noqa: E402

# ---------------------------------------------------------------- the version hook
GOOD = """docs_version: "1.1"
product: {name: MSG gripper, repository: x, tag: V1.1}
firmware: {name: STEPFOC, version: "108", repository: x, tag: V108}
manuals:
  msg: {number: SR-5003, title: MSG Gripper Manual, revision: 2026.A, status: draft, published: null, firmware: true,
            applies_to: "with the STEPFOC driver PCB v1", covers: the driver}
  guide: {number: SR-5101, title: Some Guide, revision: 2026.B, status: published, published: 2026-11-02,
          applies_to: "", covers: a guide}
"""


def load_text(text):
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(text)
    try:
        return hook.load(f.name), None
    except PluginError as exc:
        return None, str(exc)
    finally:
        Path(f.name).unlink()


data, err = load_text(GOOD)
check("A1 a valid versions.yml loads", data is not None, err)
d, e = load_text(GOOD.replace("tag: V108", "tag: v108"))
check("A1b a lowercase tag loads (the v101 tag of the Spectral firmware)", d is not None, e)
for label, bad, word in (
        ("docs_version not a release", GOOD.replace('"1.1"', '"x"'), "docs_version"),
        ("a product tag of another release", GOOD.replace("tag: V1.1", "tag: V1.0"), "does not belong"),
        ("a firmware tag of another release", GOOD.replace("tag: V108", "tag: V107"), "does not belong"),
        ("a malformed firmware tag", GOOD.replace("tag: V108", "tag: 108"), "firmware.tag"),
        ("a product without a tag", GOOD.replace("tag: V1.1", "tag: ''"), "product needs"),
        ("a revision not YEAR.LETTER", GOOD.replace("2026.A", "A"), "YEAR.LETTER"),
        ("an unknown status", GOOD.replace("status: draft", "status: final"), "status"),
        ("published without a date", GOOD.replace("published: 2026-11-02", "published: null"), "publication date"),
        ("a missing field", GOOD.replace("covers: the driver", "covers: ''"), "lacks covers")):
    d, e = load_text(bad)
    check(f"A2 refused: {label}", d is None and word in (e or ""), e)
meta = hook.meta_block("msg", data)
check("A3 a firmware document's box: number, gripper release, firmware, revision (draft), applies to both",
      "SR-5003" in meta and "**MSG gripper release:** 1.1" in meta and "**Firmware:** STEPFOC 108" in meta
      and "2026.A (draft)" in meta
      and "**Applies to:** MSG gripper release 1.1 with the STEPFOC driver PCB v1, STEPFOC firmware 108" in meta, meta)
meta = hook.meta_block("guide", data)
check("A4 a published document's box: no firmware line, the gripper release, the date, no (draft)",
      "**Firmware:**" not in meta and "release:** 1.1" in meta and "2026-11-02" in meta and "(draft)" not in meta, meta)
try:
    hook.meta_block("nope", data)
    raised = False
except PluginError:
    raised = True
check("A5 an unknown manual stops the build", raised)
table = hook.documents_table(data)
check("A6 the documents table: one row per manual, the gripper release and the firmware named",
      table.count("| SR-") == 2 and "release 1.1" in table and "108" in table, table)
hook._facts = data
page = hook.on_page_markdown("x\n<!-- doc-meta: msg -->\ny\n<!-- documents-table -->\n", None, None, None)
check("A7 both placeholders are replaced", "doc-meta:" not in page and "documents-table" not in page and "SR-5101" in page)
shipped = hook.load(ROOT / "versions.yml")
check("A8 the shipped versions.yml loads", bool(shipped["docs_version"]))
check("A9 every placeholder in the docs names a manual of versions.yml",
      all(k in shipped["manuals"]
          for p in (ROOT / "docs").rglob("*.md") for k in hook.META_RE.findall(p.read_text(encoding="utf-8"))))

# ---------------------------------------------------------------- the firmware pages
try:
    d = pages.load()
    loaded, load_err = True, ""
except PluginError as exc:
    d, loaded, load_err = None, False, str(exc)
check("B1 the shipped facts and descriptions load and agree (every command described, layouts fit the frames)", loaded, load_err)
if loaded:
    facts = d["facts"]
    check("B2 the generated facts are from the firmware release versions.yml names", facts["tag"] == shipped["firmware"]["tag"]
          and facts["version"] == str(shipped["firmware"]["version"]), f"{facts['tag']} vs {shipped['firmware']['tag']}")
    missing = [g["page"] for src in (d["can"], d["uart"]) for g in src["groups"].values()]
    missing = [p for p, base in zip(missing, ["can"] * len(d["can"]["groups"]) + ["uart"] * len(d["uart"]["groups"]))
               if not (ROOT / "docs" / "reference" / base / p).exists()]
    check("B3 every command group has its reference page", not missing, str(missing))
    check("B4 the compatibility table has a row for this firmware release, and names this docs version",
          any(str(r.get("firmware")) == str(shipped["firmware"]["version"]) for r in d["compat"]["rows"])
          and any(str(r.get("docs")) == shipped["docs_version"] for r in d["compat"]["rows"]))
    check("B5 every column of the compatibility table has a key and a title",
          all("key" in c and "title" in c for c in d["compat"]["columns"]))
    gen = ROOT / "docs" / "includes" / "generated" / "firmware_release_notes.md"
    check("B6 the release notes cover the release this site describes",
          gen.exists() and f"## {shipped['firmware']['tag']} (" in gen.read_text(encoding="utf-8"))
    # the hook refuses a description file that drifts from the facts
    bad_can = json.loads(json.dumps(d["can"]))
    if d["can"].get("partial"):   # a partial reference may leave commands out, but not invent one
        bad_can["commands"]["IN_NOPE"] = {"name": "Nope", "group": next(iter(bad_can["groups"])), "description": "x"}
    else:
        bad_can["commands"].pop("IN_ESTOP")
    try:
        pages.check(facts, bad_can, d["uart"])
        refused = False
    except PluginError:
        refused = True
    check("B7 a CAN command the firmware has but the descriptions lack (or one it does not have) stops the build", refused)
    bad_can = json.loads(json.dumps(d["can"]))
    first_form = next(n for n, c in bad_can["commands"].items() if c.get("forms"))
    bad_can["commands"][first_form]["forms"][0]["fields"][0]["bytes"] = "0-7"
    try:
        pages.check(facts, bad_can, d["uart"])
        refused = False
    except PluginError:
        refused = True
    check("B8 a byte layout that does not fit the frame stops the build", refused)
    bad_uart = json.loads(json.dumps(d["uart"]))
    bad_uart["commands"]["Nope"] = {"group": next(iter(bad_uart["groups"])), "description": "x"}
    try:
        pages.check(facts, d["can"], bad_uart)
        refused = False
    except PluginError:
        refused = True
    check("B9 a UART command the firmware lacks stops the build", refused)
    # the rendered tables name every command
    over = pages.can_overview(d)
    check("B10 the CAN overview lists every described command ID",
          all(f"| {e['id']} |" in over for e in facts["can"]["ids"] if e["name"] in d["can"]["commands"]))
    uo = pages.uart_overview(d)
    check("B11 the UART overview lists every described handler",
          all(f"`#{h['name']}`" in uo for h in facts["uart"]["handlers"] if h["name"] in d["uart"]["commands"]))
    with_forms = [n for n, c in d["can"]["commands"].items() if c.get("forms")]
    answered = next((n for n in with_forms if facts["can"]["handlers"].get(n, {}).get("responds")), with_forms[0])
    sec = pages.can_section(answered, d["can"]["commands"][answered], d)
    check("B12 a command section: facts strip, the accepted lengths, the answer",
          "cmd-facts" in sec and "bytes" in sec and ("Respond_" in sec or not facts["can"]["handlers"].get(answered, {}).get("responds")), sec[:200])

print(f"\n{len(fails)} failure(s)" if fails else "\nall checks passed")
sys.exit(1 if fails else 0)
