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

page = hook.URL_RE.sub(lambda m: hook.version_url(m.group(1), m.group(2), data),
                      "[f](<!-- version-url: firmware -->/src) <!-- version-link: product -->")
check("A10 version-url is the files at the tag, version-link a link to them with the version as its text",
      page == "[f](x/tree/V108/src) [1.1](x/tree/V1.1)", page)
dated, _ = load_text(GOOD.replace("tag: V1.1}", "tag: V1.1, released: 2026-02-19}"))
check("A11 version-link adds the release date when there is one",
      dated is not None and hook.version_url("link", "product", dated) == "[1.1](x/tree/V1.1) (2026-02-19)")
try:
    hook.version_url("url", "python", data)
    check("A12 a version-url of an unknown component stops the build", False, "no error")
except PluginError:
    check("A12 a version-url of an unknown component stops the build", True)
check("A13 every version-url and version-link placeholder in the docs names product or firmware",
      all(m[1] in ("product", "firmware")
          for p in (ROOT / "docs").rglob("*.md") for m in hook.URL_RE.findall(p.read_text(encoding="utf-8"))))

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

# ---------------------------------------------------------------- E. the figures hook
fig = load_module("figures_hook", ROOT / "hooks" / "figures.py")
pair = "\n".join(["Text.", "", '![A gripper](a.webp#only-light){ width="9" }',
                  '![A gripper](a_dark.webp#only-dark){ width="9" }', "", "More."])
out, n = fig.transform(pair, 1, "3.")
check("E1 a light and a dark picture are one figure, numbered on from the chapter's count, alt text as caption",
      n == 1 and out.count("<figure") == 1 and "<figcaption>Figure 3.2: A gripper.</figcaption>" in out, out)
inline = "\n".join(["A line of text", "![A gripper](a.webp)", "", "![Hero](h.webp){ .hero }", ""])
out, n = fig.transform(inline, 0, "")
check("E2 a picture inside a paragraph and a hero picture are left alone", n == 0 and "<figure" not in out, out)
check("E3 numbered chapters count across pages, other pages on their own",
      fig.chapter("03-technical-data/dimensions.md") == ("03-technical-data", "3.")
      and fig.chapter("07-maintenance.md") == ("07-maintenance.md", "7.")
      and fig.chapter("build/printing.md") == ("build/printing.md", ""))
handmade = "\n".join(['<figure class="gui-shot" markdown="1">', '<div markdown="1">', "", "![A screenshot](s.jpg)", "",
                      "</div>", "<figcaption>1. A mark.</figcaption>", "</figure>", "", "![After it](b.webp)", ""])
out, n = fig.transform(handmade, 0, "")
check("E4 a picture inside a hand-made <figure> is left alone, the next standalone one is numbered",
      n == 1 and out.count("<figure") == 2 and "Figure 1: After it." in out, out)
numbered = [str(p.relative_to(ROOT / "docs")) for p in (ROOT / "docs").rglob("*.md")
            if "<figcaption>Figure " in p.read_text(encoding="utf-8")]
check("E5 no caption is numbered by hand: the hook numbers them", not numbered, "; ".join(numbered))

# ---------------------------------------------------------------- F. the known issues hook
ki = load_module("known_issues_hook", ROOT / "hooks" / "known_issues.py")
DOCS = ROOT / "docs"
try:
    shipped_ki, err = ki.load(ROOT / "known_issues.yml", DOCS), None
except PluginError as exc:
    shipped_ki, err = None, str(exc)
check("F1 known_issues.yml loads, and every issue's page exists", shipped_ki is not None, err)
check("F2 an issue's link is relative to the page it lands on",
      ki.link({"page": "06-operation/errors.md#clearing", "title": "T"}, "09-troubleshooting/known-issues.md")
      == "[T](../06-operation/errors.md#clearing)")
ISSUE = {"id": "KI-1", "component": "c", "summary": "s", "workaround": "w", "page": "index.md", "title": "t",
         "status": "open", "since": "2026-11-02"}


def load_issues(issues):
    text = yaml.safe_dump({"components": {"c": {"name": "C", "version": "1"}}, "issues": issues})
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(text.replace("'2026-11-02'", "2026-11-02"))
    try:
        return ki.load(f.name, DOCS), None
    except PluginError as exc:
        return None, str(exc)
    finally:
        Path(f.name).unlink()


_, err = load_issues([dict(ISSUE, component="x")])
check("F3 an unknown component stops the build", err is not None and "not under components" in err, err)
_, err = load_issues([ISSUE, dict(ISSUE)])
check("F4 a repeated id stops the build", err is not None and "twice" in err, err)
kdata, err = load_issues([ISSUE, dict(ISSUE, id="KI-2", status="fixed", fixed_in="1.1")])
out = ki.all_issues(kdata, "09-troubleshooting/known-issues.md") if kdata else ""
check("F5 open issues are listed by component, fixed ones under Fixed with their version",
      "### C" in out and "### Fixed" in out and "| KI-2 | s | 1.1 |" in out and "| KI-1 | s | w |" in out, err or out)

print(f"\n{len(fails)} failure(s)" if fails else "\nall checks passed")
sys.exit(1 if fails else 0)
