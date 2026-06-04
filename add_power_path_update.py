#!/usr/bin/env python3
"""Add v1.1 USB/battery power-path components to the valid KiCad schematic.

Adds:
- D3 SS14: USB VBUS -> VCC_RAIL
- D4 SS14: VBAT -> VCC_RAIL
- J3 PH2.0 2P battery connector (uses the existing 2-pin battery symbol geometry)

The schematic remains a placement/intent skeleton; final pin-to-pin wiring is done in KiCad GUI.
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path

SCH_PATH = Path(__file__).with_name("esp32-epaper.kicad_sch")
content = SCH_PATH.read_text(encoding="utf-8")

if '"D3"' in content or '"D4"' in content or '"J3"' in content:
    raise SystemExit("D3/D4/J3 already present; aborting to avoid duplicates")

lines = content.split("\n")

def uid() -> str:
    return str(uuid.uuid4())

# Schematic UUID
sch_uuid = None
for line in lines[:20]:
    m = re.search(r"\(uuid ([^)]+)\)", line)
    if m:
        sch_uuid = m.group(1)
        break
if not sch_uuid:
    raise RuntimeError("schematic uuid not found")

# Boundaries
lib_end = sheet_start = sym_inst_start = None
depth = 0
in_lib = False
for i, line in enumerate(lines):
    if line.strip() == "(lib_symbols":
        in_lib = True
        depth = 1
        continue
    if in_lib:
        for ch in line:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        if depth == 0:
            lib_end = i
            in_lib = False
    if "(sheet_instances" in line and sheet_start is None:
        sheet_start = i
    if "(symbol_instances" in line and sym_inst_start is None:
        sym_inst_start = i

if None in (lib_end, sheet_start, sym_inst_start):
    raise RuntimeError(f"bad boundaries lib_end={lib_end} sheet_start={sheet_start} sym_inst_start={sym_inst_start}")
assert lib_end is not None
assert sheet_start is not None
assert sym_inst_start is not None

# Find last schematic symbol instance before sheet_instances
last_inst = None
for i in range(lib_end, sheet_start):
    if "(symbol (lib_id" in lines[i]:
        last_inst = i
if last_inst is None:
    raise RuntimeError("last symbol not found")

depth = 0
last_inst_end = None
for i in range(last_inst, sheet_start):
    for ch in lines[i]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
    if depth == 0:
        last_inst_end = i
        break
if last_inst_end is None:
    raise RuntimeError("last symbol end not found")


def make_instance(lib_id: str, ref: str, value: str, x: float, y: float, num_pins: int, footprint: str = ""):
    iuuid = uid()
    parts = [
        f'  (symbol (lib_id "{lib_id}") (at {x} {y} 0) (unit 1)',
        "    (in_bom yes) (on_board yes) (dnp no)",
        f"    (uuid {iuuid})",
        f'    (property "Reference" "{ref}" (at {x} {y - 5.08} 0)',
        "      (effects (font (size 1.27 1.27)))",
        "    )",
        f'    (property "Value" "{value}" (at {x} {y + 5.08} 0)',
        "      (effects (font (size 1.27 1.27)))",
        "    )",
    ]
    if footprint:
        parts += [
            f'    (property "Footprint" "{footprint}" (at {x} {y} 0)',
            "      (effects (font (size 1.27 1.27)) hide)",
            "    )",
        ]
    for p in range(1, num_pins + 1):
        parts.append(f'    (pin "{p}" (uuid {uid()}))')
    parts += [
        "    (instances",
        '      (project "esp32-epaper"',
        f'        (path "/{sch_uuid}"',
        f'          (reference "{ref}") (unit 1)',
        "        )",
        "      )",
        "    )",
        "  )",
    ]
    return "\n".join(parts), iuuid

instances = []
sym_paths = []
for lib_id, ref, value, x, y, np, fp in [
    ("Device:D", "D3", "SS14", 105, 235, 2, "Diode_SMD:D_SMA"),
    ("Device:D", "D4", "SS14", 175, 235, 2, "Diode_SMD:D_SMA"),
    # Reuse existing 2-pin battery symbol so no new embedded lib_symbol is required.
    ("esp32-epaper-lib:BatteryHolder_18650", "J3", "PH2.0 2P Battery", 220, 270, 2, "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"),
]:
    inst, iuuid = make_instance(lib_id, ref, value, x, y, np, fp)
    instances.append(inst)
    sym_paths.append((iuuid, ref, value, fp))

wires = f'''  (wire (pts (xy 105 235) (xy 130 235))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )
  (wire (pts (xy 175 235) (xy 190 235))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )
  (wire (pts (xy 130 235) (xy 130 220))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )
  (wire (pts (xy 190 235) (xy 190 220))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )'''

labels = f'''  (global_label "VBUS" (shape input) (at 105 230 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {uid()})
  )
  (global_label "VBAT" (shape input) (at 175 230 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {uid()})
  )
  (global_label "VCC_RAIL" (shape output) (at 190 230 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {uid()})
  )'''

text = f'''  (text "F: USB/Battery Power Path - D3/D4 SS14 OR-ing + J3 PH2.0" (at 100 228 0)
    (effects (font (size 2.54 2.54)) (justify left bottom))
    (uuid {uid()})
  )'''

sym_inst_lines = "\n".join(
    f'    (path "/{sch_uuid}/{iuuid}" (reference "{ref}") (unit 1) (value "{value}") (footprint "{fp}"))'
    for iuuid, ref, value, fp in sym_paths
)

# Insert in a stable order
lines.insert(last_inst_end + 1, "\n" + "\n\n".join(instances))

# Insert wires before first existing wire, labels before first label, text before first text
for predicate, payload in [
    (lambda line: line.strip().startswith("(wire"), wires + "\n"),
    (lambda line: line.strip().startswith("(global_label") or line.strip().startswith("(label"), labels + "\n"),
    (lambda line: line.strip().startswith("(text"), text + "\n"),
]:
    for i in range(lib_end, sheet_start + 1):
        if predicate(lines[i]):
            lines.insert(i, payload)
            break
    else:
        raise RuntimeError("insertion point not found")

for i, line in enumerate(lines):
    if "(symbol_instances" in line:
        lines.insert(i + 1, sym_inst_lines + "\n")
        break

content = "\n".join(lines)
content = content.replace('(title "ESP32 E-Paper Badge v1.0")', '(title "ESP32 E-Paper Badge v1.1")')
content = content.replace('(date "2025-05-27")', '(date "2026-06-04")')
content = content.replace('(rev "1.0")', '(rev "1.1")')
content = content.replace('2.13\\" Tri-color E-Paper, USB-C Charging', '2.13\\" Tri-color E-Paper, USB-C Charging + USB Direct Power')

# Balance check
balance = 0
for ch in content:
    if ch == "(":
        balance += 1
    elif ch == ")":
        balance -= 1
if balance != 0:
    raise RuntimeError(f"unbalanced parentheses: {balance}")

SCH_PATH.write_text(content, encoding="utf-8")
print(f"✓ Updated {SCH_PATH}")
print(f"  Added: D3, D4, J3")
print(f"  Component instances: {content.count('(symbol (lib_id')}")
