#!/usr/bin/env python3
"""Read the firmware at a release tag and write the generated files the reference pages are built from (the
same idea as par6's tools/sync_runtime.py: facts come from the TAGGED code, never from uncommitted work).

    python tools/sync_firmware.py                      write docs/includes/generated/ from firmware.tag in versions.yml
    python tools/sync_firmware.py --check              exit 1 when a generated file differs from what the tag gives
    python tools/sync_firmware.py --firmware PATH --tag V108
    python tools/sync_firmware.py --print uart|can|defaults [--tag V103]   print one table instead of writing
    python tools/sync_firmware.py --no-network         keep the release notes that are there (no GitHub API call)

It reads the firmware repository with `git show <tag>:<file>` and writes, into docs/includes/generated/:

    firmware_facts.json         what the code says: FIRMWARE_VERSION, every CAN command ID with the lengths its
                                handler accepts and the response it sends, every frame the driver transmits with
                                its length, every UART command the parser accepts and every UART handler with its
                                kind (Set/Get, Get, Action), argument type, the mode it enters and the response it
                                prints, the defaults of the controller and PID structures
    firmware_release_notes.md   the GitHub Release notes of every release up to docs_version (the release body is
                                the firmware's changelog, see the firmware repository's release_guide.md)

hooks/firmware_pages.py turns the facts and the hand-written descriptions (docs/includes/can_commands.yml,
uart_commands.yml) into the reference pages at build time, and tools/test_tools.py checks that the two agree.

The firmware repository (the last part of firmware.repository in versions.yml) is --firmware, else $FIRMWARE_DIR, else a
folder of that name next to this repository, next to its parent, or under ../../projects; firmware.src names its
source folder. Python 3.11+, PyYAML (installed with MkDocs).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "includes" / "generated"
SRC = "STEPFOC firmware/src"            # overridden by firmware.src in versions.yml
REPO_NAME = "STEPFOC-stepper-controller"   # overridden by the last part of firmware.repository in versions.yml


class SyncError(Exception):
    pass


def find_firmware(arg: str | None) -> Path:
    candidates = [arg, os.environ.get("FIRMWARE_DIR"), ROOT.parent / REPO_NAME, ROOT.parent.parent / REPO_NAME,
                  ROOT.parent.parent / "projects" / REPO_NAME]
    for c in candidates:
        if c and (Path(c) / ".git").exists():
            return Path(c)
    raise SyncError(f"no {REPO_NAME} repository found: pass --firmware PATH or set FIRMWARE_DIR")


def git_show(repo: Path, tag: str, path: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), "show", f"{tag}:{path}"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SyncError(f"{tag}:{path} not readable in {repo}: {r.stderr.strip()} (are the tags fetched?)")
    return r.stdout


# ---------------------------------------------------------------- UART

STRCMP = re.compile(r'strcmp\(\s*command\s*,\s*"(\w+)"\s*\)\s*==\s*0')
PRINT = re.compile(r'Serialport\.print(?:ln)?\(\s*"([^"]*)"')
MODE = re.compile(r"Controller_mode\s*=\s*(\d+)")
ASSIGN = re.compile(r"^\s*(?:controller|PID|Gripper|FOC|parser)\.\w+\s*=\s*[^=]", re.M)
# Controller_mode number -> name, from firmware.modes in versions.yml (the numbering differs between firmwares).
MODE_NAMES: dict[int, str] = {}


def uart_whitelist(parser_cpp: str) -> list[str]:
    """The command names the serial parser accepts (anything else is dropped before a handler sees it)."""
    return list(dict.fromkeys(STRCMP.findall(parser_cpp)))


def uart_handlers(communication_cpp: str) -> list[dict]:
    """One entry per UART handler, in source order."""
    text = communication_cpp
    matches = list(STRCMP.finditer(text))
    out = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        # the firmware's own comment lines right above the handler
        before = text[:start].rstrip()
        comments = []
        for line in reversed(before.splitlines()):
            s = line.strip()
            if s.startswith("//"):
                comments.append(s[2:].strip())
            elif s in ("", "{", "}") or s.startswith(("else", "if")):
                if comments or s in ("", "{", "}"):
                    break
            else:
                break
        comments.reverse()
        prints = [p for p in PRINT.findall(block) if p.strip()]
        has_arg = "strlen(argument)" in block
        arg_type = "float" if "atof(argument)" in block else "int" if "atoi(argument)" in block else ""
        mode = MODE.search(block)
        # a handler that changes state is an action: it enters a mode, assigns a variable, or calls a function
        # (Write_config(), Set_Default_config(), Bootloader_ResetIntoBootloader(), ...; prints do not count)
        calls = [c for c in re.findall(r"\b([A-Z]\w+)\s*\(", block) if c not in ("Serialport",)]
        changes = bool(mode) or bool(ASSIGN.search(block)) or bool(calls)
        kind = "Set/Get" if has_arg else ("Action" if changes else "Get")
        out.append({"name": m.group(1), "kind": kind, "arg": arg_type if has_arg else "",
                    "mode": MODE_NAMES.get(int(mode.group(1)), mode.group(1)) if mode else "",
                    "response": (prints[0].strip() if prints else ""), "comment": " ".join(comments)})
    return out


# ---------------------------------------------------------------- CAN

DEFINE = re.compile(r"^#define[ \t]+((?:IN_|OUT_|OUT_IN_)[A-Z0-9_]+|HEARTBEAT_SETUP)[ \t]+(\d+)[ \t]*(?://[ \t]*(.*))?$", re.M)
CASE = re.compile(r"case\s+([A-Z0-9_]+)\s*:")
LEN = re.compile(r"CAN_RX_msg\.len\s*==\s*(\d+)")
RESPONSE_FN = re.compile(r"\b([A-Z][A-Za-z_0-9]*(?:_CAN|_response|_pack))\(\)\s*;")
TX_FN = re.compile(r"^void\s+(\w+)\s*\(\s*\)\s*\{", re.M)
TX_LEN = re.compile(r"CAN_TX_msg\.len\s*=\s*(\d+)")
TX_ID = re.compile(r"Combine_2_CAN_ID\([^,]+,\s*([A-Z0-9_]+)")


def can_ids(constants_h: str) -> list[dict]:
    return [{"name": n, "id": int(v), "comment": (c or "").strip()} for n, v, c in DEFINE.findall(constants_h)]


def can_handlers(communication_can_cpp: str) -> dict[str, dict]:
    """For every `case IN_X:` of the receive switch: the frame lengths it accepts and the response functions it calls."""
    text = communication_can_cpp
    matches = list(CASE.finditer(text))
    out = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[m.start():end]
        body = block.split("break;")[0]
        out[m.group(1)] = {"lengths": sorted({int(x) for x in LEN.findall(body)}),
                           "responds": list(dict.fromkeys(RESPONSE_FN.findall(body))),
                           "empty": body.strip().count("\n") <= 1}
    return out


def can_tx(communication_can_cpp: str) -> dict[str, dict]:
    """Every frame the driver transmits: the function name -> its command ID define and length."""
    text = communication_can_cpp
    matches = list(TX_FN.finditer(text))
    out = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[m.start():end]
        length, ident = TX_LEN.search(block), TX_ID.search(block)
        if length and ident:
            out[m.group(1)] = {"len": int(length.group(1)), "id_define": ident.group(1)}
    return out


def firmware_version(constants_h: str, tag: str) -> str:
    m = re.search(r"^#define\s+FIRMWARE_VERSION\s+(\d+)", constants_h, re.M)
    if m:
        if f"V{m.group(1)}" != tag:
            raise SyncError(f"constants.h at {tag} says FIRMWARE_VERSION {m.group(1)}")
        return m.group(1)
    return tag.lstrip("V")       # V104 and older: the version came from EEPROM


# ---------------------------------------------------------------- defaults and errors

FIELD = re.compile(r"^[ \t]*volatile[ \t]+(?:unsigned[ \t]+)?(?:int|float|bool|uint\d+_t|int\d+_t)[ \t]+(\w+)[ \t]*=[ \t]*([^;]+);[ \t]*(?://[ \t]*(.*))?$", re.M)


def defaults(common_h: str) -> list[dict]:
    return [{"name": n, "value": v.strip(), "comment": (c or "").strip()} for n, v, c in FIELD.findall(common_h)]


# ---------------------------------------------------------------- tables (--print)

def esc(text) -> str:
    return str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", r"\|")


def table_uart(facts: dict) -> str:
    rows = ["| Command | Kind | Argument | Enters mode | Response starts with | Firmware comment |", "|---|---|---|---|---|---|"]
    for h in facts["uart"]["handlers"]:
        rows.append(f"| `{h['name']}` | {h['kind']} | {h['arg']} | {h['mode']} | {esc(h['response'])} | {esc(h['comment'])} |")
    return "\n".join(rows) + "\n"


def table_can(facts: dict) -> str:
    rows = ["| ID | Name | Direction | Handled | Accepted lengths | Driver answers with | Firmware comment |", "|---|---|---|---|---|---|---|"]
    handlers = facts["can"]["handlers"]
    for e in sorted(facts["can"]["ids"], key=lambda e: e["id"]):
        n = e["name"]
        direction = "host → driver" if n.startswith("IN_") or n == "HEARTBEAT_SETUP" else "driver → host"
        if n.startswith("OUT_IN"):
            direction = "host → driver (remote frame), driver → host"
        h = handlers.get(n)
        handled = "no" if h is None or h["empty"] else "yes"
        lengths = ", ".join(str(x) for x in h["lengths"]) if h and h["lengths"] else ("—" if h else "")
        rows.append(f"| {e['id']} | `{n}` | {direction} | {handled} | {lengths} | {esc(', '.join(h['responds']) if h else '')} | {esc(e['comment'])} |")
    return "\n".join(rows) + "\n"


def table_defaults(facts: dict) -> str:
    rows = ["| Variable | Default | Firmware comment |", "|---|---|---|"]
    for d in facts["defaults"]:
        rows.append(f"| `{d['name']}` | {esc(d['value'])} | {esc(d['comment'])} |")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------- release notes

def release_notes(docs_version: str) -> str:
    """Every GitHub Release up to docs_version, newest first: `## V108 (2026-08-26)` + the release body."""
    api = f"https://api.github.com/repos/Source-Robotics/{REPO_NAME}/releases?per_page=100"
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": "Source-Robotics-docs"}), timeout=30) as r:
            releases = json.load(r)
    except Exception as exc:
        raise SyncError(f"GitHub releases not readable: {exc} (use --no-network to keep the file that is there)")
    parts = []
    for rel in sorted(releases, key=lambda x: int(re.sub(r"\D", "", x["tag_name"]) or 0), reverse=True):
        number = int(re.sub(r"\D", "", rel["tag_name"]) or 0)
        if number > int(docs_version):
            continue
        body = (rel.get("body") or "").strip().replace("\r", "")
        body = re.sub(r"^### ", "#### ", body, flags=re.M)
        parts.append(f"## {rel['tag_name']} ({rel['published_at'][:10]})\n\n{body or '*No release notes.*'}\n")
    if not parts:
        raise SyncError("no release found")
    return "\n".join(parts)


# ---------------------------------------------------------------- build

def facts_for(repo: Path, tag: str) -> dict:
    read = lambda name: git_show(repo, tag, f"{SRC}/{name}")
    constants, can_cpp, comm_cpp = read("constants.h"), read("communication_CAN.cpp"), read("communication.cpp")
    commit = subprocess.run(["git", "-C", str(repo), "rev-list", "-n", "1", tag], capture_output=True, text=True).stdout.strip()
    return {
        "tag": tag, "version": firmware_version(constants, tag), "commit": commit[:12],
        "can": {"ids": can_ids(constants), "handlers": can_handlers(can_cpp), "tx": can_tx(can_cpp)},
        "uart": {"accepted": uart_whitelist(read("SerialPacketParser.cpp")), "handlers": uart_handlers(comm_cpp)},
        "defaults": defaults(read("common.h")),
    }


def build(repo: Path, tag: str, docs_version: str, network: bool) -> dict[str, str]:
    facts = facts_for(repo, tag)
    if facts["version"] != docs_version:
        raise SyncError(f"release {tag} is firmware {facts['version']}, docs_version is {docs_version} (versions.yml)")
    head = (f"<!-- Generated by tools/sync_firmware.py from {REPO_NAME} {tag} ({facts['commit']}). Do not "
            f"edit: change the firmware, release it, then run the tool again. -->\n")
    files = {"firmware_facts.json": json.dumps(facts, indent=1, sort_keys=True) + "\n"}
    if network:
        files["firmware_release_notes.md"] = head + "\n" + release_notes(docs_version)
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--firmware", help="the firmware repository (default: next to this repository, or $FIRMWARE_DIR)")
    ap.add_argument("--tag", help="the release tag (default: firmware.tag in versions.yml)")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when a generated file is out of date")
    ap.add_argument("--no-network", action="store_true", help="do not fetch the release notes from GitHub")
    ap.add_argument("--print", choices=["uart", "can", "defaults"], help="print one table and exit")
    args = ap.parse_args(argv)
    facts_yml = yaml.safe_load((ROOT / "versions.yml").read_text(encoding="utf-8"))
    tag = args.tag or facts_yml["firmware"]["tag"]
    global SRC, REPO_NAME
    SRC = facts_yml["firmware"].get("src", SRC)
    REPO_NAME = facts_yml["firmware"]["repository"].rstrip("/").rsplit("/", 1)[-1]
    MODE_NAMES.update({int(k): str(v) for k, v in (facts_yml["firmware"].get("modes") or {}).items()})
    if not MODE_NAMES:
        print("sync_firmware: versions.yml lacks firmware.modes (Controller_mode number -> name)", file=sys.stderr)
        return 2
    try:
        repo = find_firmware(args.firmware)
        if args.print:
            facts = facts_for(repo, tag)
            sys.stdout.write({"uart": table_uart, "can": table_can, "defaults": table_defaults}[args.print](facts))
            return 0
        files = build(repo, tag, str(facts_yml["docs_version"]), network=not args.no_network)
    except SyncError as exc:
        print(f"sync_firmware: {exc}", file=sys.stderr)
        return 2
    stale = [n for n, text in files.items() if not (OUT / n).exists() or (OUT / n).read_text(encoding="utf-8") != text]
    if args.check:
        for n in stale:
            print(f"out of date: docs/includes/generated/{n}")
        print("generated files up to date" if not stale else f"{len(stale)} out of date: run tools/sync_firmware.py")
        return 1 if stale else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for n in stale:
        (OUT / n).write_text(files[n], encoding="utf-8")
    print(f"from {REPO_NAME} {tag}: {len(stale)} generated file(s) written, {len(files) - len(stale)} unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
