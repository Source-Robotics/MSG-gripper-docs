"""Build versioned CAN downloads and the offline frame tool from the reference's data.

Kept identical in the four driver/gripper sites. The firmware hook validates the source
facts first. Reserved commands are excluded; RTR requests remain distinct from replies.
DBC cannot distinguish a command's forms by DLC, so each motion layout gets its own file.
"""
from __future__ import annotations

import json
import posixpath
import re
from pathlib import Path

import yaml
from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File

_schema: dict = {}
_assets: dict[str, str] = {}


def signal(field: dict) -> dict:
    first, _, last = str(field["bytes"]).partition("-")
    byte = int(first)
    count = int(last or first) - byte + 1
    kind = field["type"]
    bits = [int(x) for x in str(field["bit"]).split("-")] if "bit" in field else None
    width = len(bits) if bits else count * 8
    if bits and (max(bits) > 7 or min(bits) < 0 or count != 1):
        raise PluginError(f"CAN tool: invalid bit field {field['name']}")
    return {
        "name": field["name"], "byte": byte, "size": count, "bits": bits,
        "width": width, "signed": kind.startswith("signed"), "float": kind == "float 32",
        "lsb_first": field.get("bit_order") == "lsb_first", "meaning": field.get("meaning", ""),
    }


def protocol(docs: Path, title: str) -> dict:
    facts = json.loads((docs / "includes/generated/firmware_facts.json").read_text(encoding="utf-8"))
    descriptions = yaml.safe_load((docs / "includes/can_commands.yml").read_text(encoding="utf-8"))
    ids = {x["name"]: x["id"] for x in facts["can"]["ids"]}
    tx = {x["id_define"]: x["len"] for x in facts["can"]["tx"].values()}
    commands = []
    for key, item in descriptions["commands"].items():
        if item["description"].strip().startswith("Reserved"):
            continue
        forms = []
        handler = facts["can"]["handlers"].get(key)
        for form in item.get("forms", []):
            forms.append({"direction": "host", "length": form["length"], "remote": False,
                          "title": form.get("title", "command"),
                          "fields": [signal(f) for f in form["fields"]]})
        if key.startswith("OUT_IN_"):
            forms.append({"direction": "host", "length": 0, "remote": True,
                          "title": "status request (RTR)", "fields": []})
        elif handler and not forms:
            forms.append({"direction": "host", "length": 0, "remote": False,
                          "title": "command", "fields": []})
        if handler and 0 in handler["lengths"] and not any(f["length"] == 0 for f in forms):
            forms.append({"direction": "host", "length": 0, "remote": False,
                          "title": "status poll", "fields": []})
        if key in tx:
            forms.append({"direction": "driver", "length": tx[key], "remote": False,
                          "title": "reply" if handler else "driver feedback",
                          "fields": [signal(f) for f in item.get("response_fields", [])]})
        if forms:
            commands.append({"key": key, "id": ids[key], "name": item["name"],
                             "description": item["description"].strip(), "forms": forms})
    for command in commands:
        for form in command["forms"]:
            occupied = set()
            for f in form["fields"]:
                positions = [f["byte"] * 8 + b for b in f["bits"]] if f["bits"] else list(
                    range(f["byte"] * 8, (f["byte"] + f["size"]) * 8))
                if any(b >= form["length"] * 8 or b in occupied for b in positions):
                    raise PluginError(f"CAN tool: overlapping/out-of-frame fields in {command['name']}")
                occupied.update(positions)
    return {"product": title, "firmware": facts["tag"], "commit": facts["commit"],
            "byte_order": "big-endian", "bitrate": 1000000, "commands": commands}


def identifier(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", text)


def dbc(schema: dict, motion_length: int = 8) -> str:
    lines = [f'VERSION "{schema["product"]} {schema["firmware"]}"',
             "", "NS_ :", "    CM_", "    VAL_", "    SIG_VALTYPE_", "", "BS_:", "",
             "BU_: Host " + " ".join(f"Driver{i}" for i in range(14)), ""]
    comments = [f'CM_ "Source commit {schema["commit"]}. Combined clean/fault reply IDs; nodes 0-13. '
                f'Send_data_pack_1 uses DLC {motion_length}. RTR requests and the empty gripper poll have no signal layout.";']
    value_types, choices = [], []
    for node in range(14):
        for command in schema["commands"]:
            for form in command["forms"]:
                if form["remote"]:
                    continue  # DBC describes the data reply, not an RTR flag.
                if command["key"] == "IN_GRIPPER_DATA_PACK" and form["length"] == 0:
                    continue  # Same identifier as the five-byte move, no payload to decode.
                if command["key"] == "IN_DATA_PACK_1" and form["length"] != motion_length:
                    continue
                for error in ([0, 1] if form["direction"] == "driver" else [0]):
                    can_id = (node << 7) | (command["id"] << 1) | error
                    suffix = f"_N{node}" + ("_Fault" if error else "")
                    name = identifier(command["name"])[:32-len(suffix)] + suffix
                    sender, receiver = (f"Driver{node}", "Host") if form["direction"] == "driver" else ("Host", f"Driver{node}")
                    lines.append(f"BO_ {can_id} {name}: {form['length']} {sender}")
                    for f in form["fields"]:
                        raw = f["lsb_first"] and f["width"] > 1
                        sn = identifier(f["name"] + ("_raw" if raw else ""))[:32]
                        start = f["byte"] * 8 + (max(f["bits"]) if f["bits"] else 7)
                        minimum = -(2 ** (f["width"] - 1)) if f["signed"] else 0
                        maximum = 2 ** (f["width"] - int(f["signed"])) - 1
                        if f["float"]:
                            minimum, maximum = -3.402823466e38, 3.402823466e38
                        sign = "-" if f["signed"] else "+"
                        lines.append(f' SG_ {sn} : {start}|{f["width"]}@0{sign} (1,0) [{minimum}|{maximum}] "" {receiver}')
                        meaning = f["meaning"] + ("; raw bit pair, see value labels (wire order differs from numeric status)" if raw else "")
                        comments.append(f"CM_ SG_ {can_id} {sn} {json.dumps(meaning, ensure_ascii=True)};")
                        if f["float"]:
                            value_types.append(f"SIG_VALTYPE_ {can_id} {sn} : 1;")
                        if raw and f["name"] == "gripper_object_detection":
                            choices.append(f'VAL_ {can_id} {sn} 0 "moving" 1 "object while opening" 2 "object while closing" 3 "at position";')
                    lines.append("")
    return "\n".join(lines + comments + value_types + choices) + "\n"


def on_files(files, config):
    global _schema, _assets
    _schema = protocol(Path(config.docs_dir), config.site_name)
    stem = "assets/can/protocol-" + _schema["firmware"]
    _assets = {"json": stem + ".json"}
    files.append(File.generated(config, _assets["json"], content=json.dumps(_schema, ensure_ascii=True, indent=2) + "\n"))
    layouts = [("position", 8), ("velocity", 5), ("current", 2)] if any(
        c["key"] == "IN_DATA_PACK_1" for c in _schema["commands"]) else [("gripper", 8)]
    for name, length in layouts:
        _assets[name] = stem + "-" + name + ".dbc"
        files.append(File.generated(config, _assets[name], content=dbc(_schema, length)))
    return files


def on_page_markdown(markdown, page, config, files):
    if "<!-- can-downloads -->" in markdown:
        links = [f"[{'Command definitions (JSON)' if name == 'json' else name.title() + ' DBC'}]({posixpath.relpath(path, posixpath.dirname(page.file.src_uri))})"
                 for name, path in _assets.items()]
        markdown = markdown.replace("<!-- can-downloads -->", " · ".join(links))
    if "<!-- can-tool -->" in markdown:
        url = posixpath.relpath(_assets["json"], page.url or ".")
        markup = f'''<div class="can-tool" data-schema="{url}" markdown="0">
  <p class="can-tool__status" role="status">Loading the firmware's command definitions…</p>
  <fieldset><legend>Build a frame</legend>
    <label for="ct-node">Node ID (0–13)</label><input id="ct-node" name="node" type="number" min="0" max="13" step="1" value="0">
    <label for="ct-command">Message and layout</label><select id="ct-command" name="command"></select>
    <label><input name="error" type="checkbox"> Driver reply has an active fault (error bit 1)</label>
    <div class="can-tool__fields"></div>
    <button type="button" name="build" class="md-button md-button--primary">Build frame</button>
    <pre class="can-tool__built" aria-live="polite"></pre>
    <button type="button" name="use" class="md-button">Use this frame in the decoder</button>
  </fieldset>
  <fieldset><legend>Decode a frame</legend>
    <label for="ct-id">CAN identifier (hex)</label><input id="ct-id" name="identifier" type="text" value="0x07A" spellcheck="false">
    <label for="ct-data">Data bytes (hex, up to eight)</label><input id="ct-data" name="data" type="text" value="C8 1E 01 2C C0" spellcheck="false">
    <label><input name="remote" type="checkbox"> Remote request (RTR; no payload)</label>
    <button type="button" name="decode" class="md-button md-button--primary">Decode frame</button>
    <div class="can-tool__decoded" aria-live="polite"></div>
  </fieldset>
  <noscript>Enable JavaScript for the frame tool, or use the reference tables and downloads above.</noscript>
</div>'''
        markdown = markdown.replace("<!-- can-tool -->", markup)
    return markdown
