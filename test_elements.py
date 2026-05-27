#!/usr/bin/env python3
"""Incrementally test schematic elements to find what breaks."""
import uuid, subprocess, sys

with open('/root/projects/esp32-epaper-badge/esp32-epaper.kicad_sch', 'r') as f:
    content = f.read()

lines = content.split('\n')

# Find boundaries
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

sheet_start = None
for i, line in enumerate(lines):
    if '(sheet_instances' in line:
        sheet_start = i
        break

lib_section = '\n'.join(lines[lib_start:lib_end+1])

# Extract all top-level elements
elements = []
i = lib_end + 1
while i < sheet_start:
    line = lines[i]
    if line.startswith('  (') and not line.startswith('    '):
        elem_start = i
        elem_depth = 0
        for j in range(i, sheet_start):
            for ch in lines[j]:
                if ch == '(': elem_depth += 1
                elif ch == ')': elem_depth -= 1
            if elem_depth == 0:
                elements.append('\n'.join(lines[elem_start:j+1]))
                i = j + 1
                break
        else:
            i += 1
    else:
        i += 1

inst_elems = [e for e in elements if '(symbol (lib_id' in e]
wire_elems = [e for e in elements if e.strip().startswith('(wire')]
text_elems = [e for e in elements if e.strip().startswith('(text')]
glabel_elems = [e for e in elements if e.strip().startswith('(global_label')]
llabel_elems = [e for e in elements if e.strip().startswith('(label')]

print(f'inst={len(inst_elems)} wires={len(wire_elems)} texts={len(text_elems)} glabels={len(glabel_elems)} llabels={len(llabel_elems)}')

# Show samples
print(f'\nWire: {repr(wire_elems[0][:200])}')
print(f'GLabel: {repr(glabel_elems[0][:200])}')
print(f'LLabel: {repr(llabel_elems[0][:200])}')
print(f'Text: {repr(text_elems[0][:200])}')

def test(label, elems):
    SCH = str(uuid.uuid4())
    test = f'''(kicad_sch (version 20221206) (generator eeschema)
  (uuid {SCH})
  (paper "A3" portrait)
{lib_section}
{chr(10).join(elems)}
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''
    path = f'/tmp/test_{label}.kicad_sch'
    with open(path, 'w') as f:
        f.write(test)
    r = subprocess.run(
        ['kicad-cli', 'sch', 'export', 'netlist', '--output', f'/tmp/t_{label}.net', path],
        capture_output=True, text=True
    )
    status = "PASS" if r.returncode == 0 else "FAIL"
    print(f'  {status} {label} ({len(elems)} elems)')
    return r.returncode == 0

print('\n--- Individual element types ---')
test('inst_only', inst_elems)
test('wires_only', inst_elems + wire_elems)
test('texts_only', inst_elems + text_elems)
test('glabels_only', inst_elems + glabel_elems)
test('llabels_only', inst_elems + llabel_elems)

print('\n--- Combinations ---')
test('wires+text', inst_elems + wire_elems + text_elems)
test('wires+glabel', inst_elems + wire_elems + glabel_elems)
test('wires+llabel', inst_elems + wire_elems + llabel_elems)
test('all_no_sym_inst', inst_elems + wire_elems + text_elems + glabel_elems + llabel_elems)
