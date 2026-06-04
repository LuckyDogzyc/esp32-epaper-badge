#!/usr/bin/env python3
"""Add battery voltage sensing divider to ESP32 E-Paper Badge v1.1.

Circuit: BAT+ -> R12(100k) -> [VBAT_SENSE] -> R13(100k) -> GND
         C21(100nF) from VBAT_SENSE to GND (filter)
         GPIO34 reads VBAT_SENSE (ADC1_CH6)

Pin geometry (KiCad Device:R, vertical):
  pin1 at (0, +3.81) angle 270, length 1.27 -> connects at (0, +5.08) = BOTTOM
  pin2 at (0, -3.81) angle 90,  length 1.27 -> connects at (0, -5.08) = TOP
Device:C same geometry.
"""
import uuid, re

SCH_PATH = '/root/projects/esp32-epaper-badge/esp32-epaper.kicad_sch'

with open(SCH_PATH, 'r') as f:
    content = f.read()

lines = content.split('\n')

# Find schematic UUID
SCH_UUID = None
for line in lines[:10]:
    m = re.search(r'\(uuid ([^)]+)\)', line)
    if m:
        SCH_UUID = m.group(1)
        break

# Find section boundaries
lib_start = lib_end = None
depth = 0
for i, line in enumerate(lines):
    if line.strip() == '(lib_symbols':
        lib_start = i
        depth = 1
    elif depth > 0:
        for ch in line:
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
        if depth == 0:
            lib_end = i
            break

sheet_start = sym_start = None
for i, line in enumerate(lines):
    if '(sheet_instances' in line:
        sheet_start = i
    if '(symbol_instances' in line:
        sym_start = i

# Find last instance
last_inst = None
for i in range(lib_end, sheet_start):
    if '(symbol (lib_id' in lines[i]:
        last_inst = i

depth = 0
last_inst_end = None
for i in range(last_inst, sheet_start):
    for ch in lines[i]:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
    if depth == 0:
        last_inst_end = i
        break

print(f"SCH_UUID: {SCH_UUID}")
print(f"lib: {lib_start}-{lib_end}, last_inst: {last_inst}-{last_inst_end}")

# ══════════ Helper ══════════
def uid():
    return str(uuid.uuid4())

def make_instance(lib_id, ref, value, x, y, num_pins, footprint=''):
    iuuid = uid()
    parts = [
        f'  (symbol (lib_id "{lib_id}") (at {x} {y} 0) (unit 1)',
        f'    (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid {iuuid})',
        f'    (property "Reference" "{ref}" (at {x} {y - 5.08} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
        f'    (property "Value" "{value}" (at {x} {y + 5.08} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
    ]
    if footprint:
        parts.append(f'    (property "Footprint" "{footprint}" (at {x} {y} 0)')
        parts.append(f'      (effects (font (size 1.27 1.27)) hide)')
        parts.append(f'    )')
    for p in range(1, num_pins + 1):
        parts.append(f'    (pin "{p}" (uuid {uid()}))')
    parts += [
        f'    (instances',
        f'      (project "esp32-epaper"',
        f'        (path "/{SCH_UUID}"',
        f'          (reference "{ref}") (unit 1)',
        f'        )',
        f'      )',
        f'    )',
        f'  )',
    ]
    return '\n'.join(parts), iuuid, ref

# ══════════ Component positions ══════════
# Midpoint Y = 265.0 (VBAT_SENSE node)
# R12 center at Y = 265.0 - 5.08 = 259.92
# R13 center at Y = 265.0 + 5.08 = 270.08
# C21 center at Y = 270.08 (same as R13, to the right)

R12_X, R12_Y = 230, 259.92
R13_X, R13_Y = 230, 270.08
C21_X, C21_Y = 245, 270.08

MID_Y = 265.0
GND_Y = 275.16
VBAT_Y = 254.84  # R12 pin2 (TOP)

r12_inst, r12_uuid, _ = make_instance('Device:R', 'R12', '100k', R12_X, R12_Y, 2)
r13_inst, r13_uuid, _ = make_instance('Device:R', 'R13', '100k', R13_X, R13_Y, 2)
c21_inst, c21_uuid, _ = make_instance('Device:C', 'C21', '100nF', C21_X, C21_Y, 2)

new_instances = '\n\n'.join([r12_inst, r13_inst, c21_inst])

# ══════════ Wires ══════════
# R12.pin1 = (230, 265.0) = midpoint, R13.pin2 = (230, 265.0) = same! No wire needed.
# Wire 1: midpoint to C21.pin2: (230, 265.0) -> (245, 265.0)
# Wire 2: R13.pin1 to C21.pin1 (GND bus): (230, 275.16) -> (245, 275.16)

new_wires = f'''  (wire (pts (xy {R12_X} {MID_Y}) (xy {C21_X} {MID_Y}))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )
  (wire (pts (xy {R13_X} {GND_Y}) (xy {C21_X} {GND_Y}))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )'''

# ══════════ Labels ══════════
new_labels = f'''  (global_label "VBAT" (shape output) (at {R12_X} {VBAT_Y} 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {uid()})
  )
  (label "VBAT_SENSE" (at {R12_X + 5} {MID_Y} 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {uid()})
  )
  (global_label "GND" (shape input) (at {R13_X} {GND_Y} 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {uid()})
  )
  (label "VBAT_SENSE" (at 100 90 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {uid()})
  )'''

# ══════════ Text annotation ══════════
new_text = f'''  (text "E: Battery Voltage Sensing (GPIO34)" (at 225 248 0)
    (effects (font (size 2.54 2.54)) (justify left bottom))
    (uuid {uid()})
  )'''

# ══════════ Symbol instances ══════════
new_sym_insts = f'''    (path "/{SCH_UUID}/{r12_uuid}" (reference "R12") (unit 1) (value "100k") (footprint ""))
    (path "/{SCH_UUID}/{r13_uuid}" (reference "R13") (unit 1) (value "100k") (footprint ""))
    (path "/{SCH_UUID}/{c21_uuid}" (reference "C21") (unit 1) (value "100nF") (footprint ""))'''

# ══════════ Apply ══════════
# Insert instances after last instance
lines.insert(last_inst_end + 1, '\n' + new_instances)

# Find wire section and add wires
first_wire = None
for i in range(lib_end, sheet_start + 1):
    if lines[i].strip().startswith('(wire'):
        first_wire = i
        break
if first_wire:
    lines.insert(first_wire, new_wires + '\n')

# Find label section
first_label = None
for i in range(lib_end, sheet_start + 2):
    if lines[i].strip().startswith('(global_label') or lines[i].strip().startswith('(label'):
        first_label = i
        break
if first_label:
    lines.insert(first_label, new_labels + '\n')

# Find text section
first_text = None
for i in range(lib_end, sheet_start + 3):
    if lines[i].strip().startswith('(text'):
        first_text = i
        break
if first_text:
    lines.insert(first_text, new_text + '\n')

# Add symbol instances
for i, line in enumerate(lines):
    if '(symbol_instances' in line:
        lines.insert(i + 1, new_sym_insts + '\n')
        break

# Write
content = '\n'.join(lines)
with open(SCH_PATH, 'w') as f:
    f.write(content)

# Verify
depth = 0
for i, line in enumerate(lines):
    for ch in line:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if depth < 0:
            print(f"ERROR: Unbalanced at line {i+1}")
            break
    if depth < 0:
        break

comp_count = sum(1 for l in lines if '(symbol (lib_id' in l)
print(f"✓ Written: {len(lines)} lines, {comp_count} instances, balance={depth}")

# Show new component positions
print(f"\nPin positions:")
print(f"  R12 at ({R12_X},{R12_Y}): pin2(TOP=VBAT)=({R12_X},{VBAT_Y}), pin1(BOT=MID)=({R12_X},{MID_Y})")
print(f"  R13 at ({R13_X},{R13_Y}): pin2(TOP=MID)=({R13_X},{MID_Y}), pin1(BOT=GND)=({R13_X},{GND_Y})")
print(f"  C21 at ({C21_X},{C21_Y}): pin2(TOP=MID)=({C21_X},{MID_Y}), pin1(BOT=GND)=({C21_X},{GND_Y})")
