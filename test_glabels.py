#!/usr/bin/env python3
"""Test each global_label individually to find the broken one."""
import uuid, subprocess

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

# Extract instances and glabels
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
glabel_elems = [e for e in elements if e.strip().startswith('(global_label')]

print(f'Testing {len(glabel_elems)} global_labels individually:')

for idx, gl in enumerate(glabel_elems):
    # Extract label name
    name = gl.split('"')[1] if '"' in gl else '?'
    SCH = str(uuid.uuid4())
    test = f'''(kicad_sch (version 20221206) (generator eeschema)
  (uuid {SCH})
  (paper "A3" portrait)
{lib_section}
{chr(10).join(inst_elems)}
{gl}
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''
    path = f'/tmp/test_gl_{idx}.kicad_sch'
    with open(path, 'w') as f:
        f.write(test)
    r = subprocess.run(
        ['kicad-cli', 'sch', 'export', 'netlist', '--output', f'/tmp/t_gl_{idx}.net', path],
        capture_output=True, text=True
    )
    status = "PASS" if r.returncode == 0 else "FAIL"
    print(f'  {status} [{idx}] {name}')
    if r.returncode != 0:
        print(f'       {repr(gl[:150])}')
