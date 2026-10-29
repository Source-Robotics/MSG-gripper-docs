"""The reference pages, built at every build from the firmware facts and the hand-written descriptions.

Facts (docs/includes/generated/firmware_facts.json, written by tools/sync_firmware.py from the firmware's release
tag): every CAN command ID, the lengths its handler accepts and the response it sends; every UART command with its
kind, argument type, the mode it enters and what it prints; the defaults. Descriptions (docs/includes/can_commands.yml
and uart_commands.yml): what each command is for, the byte layout of each form, units, ranges, the Python call.

Placeholders, each replaced when the site is built:

    <!-- can-overview -->            every CAN message: ID, name, direction, length, group
    <!-- can-commands: GROUP -->     one section per CAN command of the group, facts strip + byte tables
    <!-- uart-overview -->           every UART command: name, kind, argument, group
    <!-- uart-commands: GROUP -->    the commands of the group as a table
    <!-- defaults-table -->          the defaults of the firmware structures
    <!-- compatibility-table -->     the rows of compatibility.yml

A command the firmware has and the descriptions lack, or the other way round, stops the build (tools/test_tools.py
checks the same before a push). Registered in mkdocs.yml under `hooks:`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from mkdocs.exceptions import PluginError

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "docs" / "includes"

CAN_OVERVIEW = re.compile(r"<!--\s*can-overview\s*-->")
CAN_GROUP = re.compile(r"<!--\s*can-commands:\s*([\w-]+)\s*-->")
UART_OVERVIEW = re.compile(r"<!--\s*uart-overview\s*-->")
UART_GROUP = re.compile(r"<!--\s*uart-commands:\s*([\w-]+)\s*-->")
DEFAULTS = re.compile(r"<!--\s*defaults-table\s*-->")
COMPAT = re.compile(r"<!--\s*compatibility-table\s*-->")
PYTHON = re.compile(r"<!--\s*python-calls\s*-->")

_d: dict = {}


def esc(text) -> str:
    return str(text if text is not None else "").replace("|", r"\|")


def load() -> dict:
    try:
        facts = json.loads((INC / "generated" / "firmware_facts.json").read_text(encoding="utf-8"))
        can = yaml.safe_load((INC / "can_commands.yml").read_text(encoding="utf-8"))
        uart = yaml.safe_load((INC / "uart_commands.yml").read_text(encoding="utf-8"))
        compat = yaml.safe_load((ROOT / "compatibility.yml").read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise PluginError(f"firmware pages: {exc}") from exc
    check(facts, can, uart)
    return {"facts": facts, "can": can, "uart": uart, "compat": compat}


def check(facts: dict, can: dict, uart: dict) -> None:
    """The descriptions and the firmware must name the same commands; a byte layout must fit the frame."""
    fw_can = {e["name"] for e in facts["can"]["ids"]}
    doc_can = set(can["commands"])
    # partial: true -> the site describes a subset (a gripper manual); an unknown command still stops the build
    if fw_can != doc_can and not (can.get("partial") and doc_can <= fw_can):
        raise PluginError(f"can_commands.yml and the firmware disagree: missing {sorted(fw_can - doc_can)}, "
                          f"extra {sorted(doc_can - fw_can)}")
    handlers, tx = facts["can"]["handlers"], facts["can"]["tx"]
    tx_len = {v["id_define"]: v["len"] for v in tx.values()}
    for name, c in can["commands"].items():
        if c.get("group") not in can["groups"]:
            raise PluginError(f"can_commands.yml: {name} has no known group")
        h = handlers.get(name)
        for form in c.get("forms", []):
            size = sum(field_size(f) for f in form["fields"])
            if size != form["length"]:
                raise PluginError(f"can_commands.yml: {name} form of {form['length']} bytes lists {size} bytes of fields")
            if h and h["lengths"] and form["length"] not in h["lengths"]:
                raise PluginError(f"can_commands.yml: {name} has a {form['length']}-byte form, the firmware accepts {h['lengths']}")
        if c.get("response_fields") is not None:
            size = sum(field_size(f) for f in c["response_fields"])
            want = tx_len.get(name)
            if want is not None and size != want:
                raise PluginError(f"can_commands.yml: {name} response lists {size} bytes, the firmware sends {want}")
    fw_uart = {h["name"] for h in facts["uart"]["handlers"]}
    doc_uart = set(uart["commands"])
    if fw_uart != doc_uart and not (uart.get("partial") and doc_uart <= fw_uart):
        raise PluginError(f"uart_commands.yml and the firmware disagree: missing {sorted(fw_uart - doc_uart)}, "
                          f"extra {sorted(doc_uart - fw_uart)}")
    for name, c in uart["commands"].items():
        if c.get("group") not in uart["groups"]:
            raise PluginError(f"uart_commands.yml: {name} has no known group")


def field_size(f: dict) -> int:
    """Bytes a field takes: `bytes: "0-2"` is 3, `bytes: "4"` is 1; bit fields inside a byte count once per byte."""
    spec = str(f["bytes"])
    if "-" in spec:
        a, b = spec.split("-")
        n = int(b) - int(a) + 1
    else:
        n = 1
    return 0 if f.get("bit") is not None and f.get("_shared") else n


def fields_table(fields: list[dict]) -> str:
    rows = ["| Byte | Bit | Field | Type | Meaning |", "|---|---|---|---|---|"]
    for f in fields:
        bit = f.get("bit", "")
        rows.append(f"| {f['bytes']} | {bit} | {esc(f['name'])} | {esc(f.get('type', ''))} | {esc(f.get('meaning', ''))} |")
    return "\n".join(rows)


def direction(name: str) -> str:
    if name.startswith("OUT_IN_"):
        return "host → driver as a remote frame, driver → host as a data frame"
    if name.startswith("OUT_"):
        return "driver → host"
    return "host → driver"


def can_section(name: str, c: dict, d: dict) -> str:
    facts = d["facts"]["can"]
    ident = next(e["id"] for e in facts["ids"] if e["name"] == name)
    h = facts["handlers"].get(name)
    tx_len = {v["id_define"]: v["len"] for v in facts["tx"].values()}
    tx_of_fn = {fn: v["id_define"] for fn, v in facts["tx"].items()}
    chips = [f"ID {ident}", direction(name)]
    if name.startswith("OUT_IN_"):
        chips.append("remote frame, 0 bytes")
    elif name.startswith("OUT_"):
        chips.append(f"{tx_len.get(name, '?')} bytes")
    elif h and h["lengths"]:
        chips.append(" or ".join(str(x) for x in h["lengths"]) + " bytes")
    elif h and not h["empty"]:
        chips.append("0 bytes")
    if c.get("python"):
        chips.append(f"Python: `{c['python']}`")
    reserved = h is None or h["empty"]
    if name.startswith("IN_") and reserved:
        chips.append("not implemented")
    out = [f"### {c['name']}", "", '<div class="cmd-facts" markdown>' + "".join(f'<span class="fact">{x}</span>' for x in chips) + "</div>", ""]
    out.append(c["description"].strip())
    out.append("")
    for form in c.get("forms", []):
        title = f"**{form['length']} bytes**" + (f" — {form['title']}" if form.get("title") else "")
        out += [title, "", fields_table(form["fields"]), ""]
    if c.get("response_fields") is not None:
        length = tx_len.get(name)
        out += [f"**The frame** ({length} bytes)" if length is not None else "**The frame**", "", fields_table(c["response_fields"]), ""]
    responds = [tx_of_fn[fn] for fn in (h["responds"] if h else []) if fn in tx_of_fn]
    if responds:
        names = ", ".join(d["can"]["commands"][r]["name"] for r in responds if r in d["can"]["commands"])
        out += [f"The driver answers with **{names}**.", ""]
    elif name.startswith("IN_") and not reserved:
        out += ["The driver does not answer this command.", ""]
    if c.get("notes"):
        out += [c["notes"].strip(), ""]
    out.append("---")
    return "\n".join(out) + "\n"


def can_overview(d: dict) -> str:
    facts, can = d["facts"]["can"], d["can"]
    tx_len = {v["id_define"]: v["len"] for v in facts["tx"].values()}
    rows = ["| ID | Message | Direction | Length | Group |", "|---|---|---|---|---|"]
    for e in sorted(facts["ids"], key=lambda e: e["id"]):
        if e["name"] not in can["commands"]:
            continue
        c = can["commands"][e["name"]]
        h = facts["handlers"].get(e["name"])
        if e["name"].startswith("OUT_IN_"):
            length = f"0 (remote) / {tx_len.get(e['name'], '?')}"
        elif e["name"].startswith("OUT_"):
            length = str(tx_len.get(e["name"], "—"))
        elif h is None or h["empty"]:
            length = "not implemented"
        else:
            length = ", ".join(str(x) for x in h["lengths"]) or "0"
        g = can["groups"][c["group"]]
        rows.append(f"| {e['id']} | [{c['name']}]({g['page']}#{anchor(c['name'])}) | {direction(e['name'])} | {length} | {g['title']} |")
    return "\n".join(rows) + "\n"


def anchor(title: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", title.lower()).strip("-")


def uart_rows(names: list[str], d: dict) -> str:
    by_name = {h["name"]: h for h in d["facts"]["uart"]["handlers"]}
    rows = ["| Command | Kind | Argument | What it does | Response |", "|---|---|---|---|---|"]
    for n in names:
        h, c = by_name[n], d["uart"]["commands"][n]
        arg = c.get("argument") or (h["arg"] if h["kind"] == "Set/Get" else "")
        if h["kind"] == "Set/Get" and h["arg"] and c.get("argument"):
            arg = f"{h['arg']}: {c['argument']}"
        desc = c["description"].strip()
        if h["mode"]:
            desc += f" Enters **{h['mode']}** mode."
        resp = c.get("response") or (f"`{h['response']}…`" if h["response"] else "—")
        rows.append(f"| `#{n}` | {h['kind']} | {esc(arg)} | {esc(desc)} | {esc(resp)} |")
    return "\n".join(rows) + "\n"


def uart_group(group: str, d: dict) -> str:
    names = [h["name"] for h in d["facts"]["uart"]["handlers"]
             if h["name"] in d["uart"]["commands"] and d["uart"]["commands"][h["name"]]["group"] == group]
    return uart_rows(names, d)


def uart_overview(d: dict) -> str:
    by_name = {h["name"]: h for h in d["facts"]["uart"]["handlers"]}
    rows = ["| Command | Kind | Argument | Group |", "|---|---|---|---|"]
    for n in sorted(by_name, key=str.lower):
        if n not in d["uart"]["commands"]:
            continue
        h, c = by_name[n], d["uart"]["commands"][n]
        g = d["uart"]["groups"][c["group"]]
        rows.append(f"| [`#{n}`]({g['page']}) | {h['kind']} | {h['arg']} | {g['title']} |")
    accepted = set(d["facts"]["uart"]["accepted"])
    orphans = sorted(accepted - set(by_name))
    text = "\n".join(rows) + "\n"
    if orphans and not d["uart"].get("partial"):
        text += ("\nThe parser also accepts " + ", ".join(f"`#{n}`" for n in orphans) +
                 ", which have no handler: the driver answers nothing to them.\n")
    return text


def defaults_table(d: dict) -> str:
    rows = ["| Variable | Default | Firmware comment |", "|---|---|---|"]
    for x in d["facts"]["defaults"]:
        rows.append(f"| `{x['name']}` | {esc(x['value'])} | {esc(x['comment'])} |")
    return "\n".join(rows) + "\n"


def python_calls(d: dict) -> str:
    """Every library call that sends a CAN message, with the message it sends and the page that describes it."""
    rows = ["| Library call | Sends | Answered with | Reference |", "|---|---|---|---|"]
    facts, can = d["facts"]["can"], d["can"]
    tx_of_fn = {fn: v["id_define"] for fn, v in facts["tx"].items()}
    for name, c in can["commands"].items():
        if not c.get("python"):
            continue
        h = facts["handlers"].get(name)
        responds = [tx_of_fn[fn] for fn in (h["responds"] if h else []) if fn in tx_of_fn]
        answer = ", ".join(can["commands"][r]["name"] for r in responds if r in can["commands"])
        if name.startswith("OUT_IN_"):
            answer = c["name"] + " (data frame)"
        g = can["groups"][c["group"]]
        rows.append(f"| `{c['python']}` | {c['name']} (ID {next(e['id'] for e in facts['ids'] if e['name'] == name)}) | {answer or '—'} | [{g['title']}](can/{g['page']}#{anchor(c['name'])}) |")
    return "\n".join(rows) + "\n"


def compat_table(d: dict) -> str:
    cols = d["compat"]["columns"]
    rows = ["| " + " | ".join(c["title"] for c in cols) + " |", "|" + "---|" * len(cols)]
    for r in d["compat"]["rows"]:
        rows.append("| " + " | ".join(esc(r.get(c["key"], "")) for c in cols) + " |")
    return "\n".join(rows) + "\n"


def on_config(config):
    global _d
    _d = load()
    config.extra["firmware_tag"] = _d["facts"]["tag"]
    return config


def on_page_markdown(markdown, page, config, files):
    d = _d
    markdown = CAN_OVERVIEW.sub(lambda m: can_overview(d), markdown)

    def can_group(m):
        g = m.group(1)
        if g not in d["can"]["groups"]:
            raise PluginError(f"{page.file.src_path}: unknown CAN group {g!r}")
        names = [n for n, c in d["can"]["commands"].items() if c["group"] == g]
        return "\n".join(can_section(n, d["can"]["commands"][n], d) for n in names)
    markdown = CAN_GROUP.sub(can_group, markdown)
    markdown = UART_OVERVIEW.sub(lambda m: uart_overview(d), markdown)

    def uart_g(m):
        g = m.group(1)
        if g not in d["uart"]["groups"]:
            raise PluginError(f"{page.file.src_path}: unknown UART group {g!r}")
        return uart_group(g, d)
    markdown = UART_GROUP.sub(uart_g, markdown)
    markdown = DEFAULTS.sub(lambda m: defaults_table(d), markdown)
    markdown = COMPAT.sub(lambda m: compat_table(d), markdown)
    markdown = PYTHON.sub(lambda m: python_calls(d), markdown)
    return markdown
