#!/usr/bin/env python3
"""Test schematic with incremental instances to find what breaks."""
import os, uuid

def uid():
    return str(uuid.uuid4())

SCH = str(uuid.uuid4())

# Read schematic
with open('/root/projects/esp32-epaper-badge/esp32-epaper.kicad_sch', 'r') as f:
    content = f.read()

lines = content.split('\n')

# Find lib_symbols boundaries
lib_start = None
lib_end = None
depth = 0
for i, line in enumerate(lines):
    if line.strip() == '(lib_symbols':
        lib_start = i
        depth = 1
    elif lib_start and depth > 0:
        for ch in line:
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
        if depth == 0:
            lib_end = i
            break

# Extract each lib symbol
symbols = {}
sym_start = None
sym_depth = 0
sym_name = None
for i in range(lib_start+1, lib_end):
    line = lines[i]
    if line.strip().startswith('(symbol "') and sym_start is None:
        sym_start = i
        sym_name = line.strip().split('"')[1]
        sym_depth = 1
    elif sym_start is not None:
        for ch in line:
            if ch == '(': sym_depth += 1
            elif ch == ')': sym_depth -= 1
        if sym_depth == 0:
            symbols[sym_name] = '\n'.join(lines[sym_start:i+1])
            sym_start = None
            sym_name = None

# Extract all instances
instances = []
inst_start = None
inst_depth = 0
for i in range(lib_end+1, len(lines)):
    line = lines[i]
    if '(symbol (lib_id' in line:
        inst_start = i
        inst_depth = 1
    elif inst_start is not None:
        for ch in line:
            if ch == '(': inst_depth += 1
            elif ch == ')': inst_depth -= 1
        if inst_depth == 0:
            instances.append('\n'.join(lines[inst_start:i+1]))
            inst_start = None

print(f"Symbols: {len(symbols)}, Instances: {len(instances)}")

# Take just the first instance of each unique lib_id
unique_insts = {}
for inst in instances:
    lid = inst.split('"')[1]
    if lid not in unique_insts:
        unique_insts[lid] = inst

needed_syms = {lid: symbols[lid] for lid in unique_insts if lid in symbols}

# Build test schematic
lib_sec = '\n'.join(needed_syms.values())
inst_sec = '\n'.join(unique_insts.values())

test_sch = f'''(kicad_sch (version 20221206) (generator eeschema)

  (uuid {SCH})

  (paper "A3" portrait)

  (lib_symbols
{lib_sec}
  )

{inst_sec}

  (sheet_instances
    (path "/" (page "1"))
  )
)
'''

with open('/tmp/test_unique.kicad_sch', 'w') as f:
    f.write(test_sch)

print(f"Test schematic: {len(needed_syms)} symbols, {len(unique_insts)} instances")
print(f"Missing syms: {set(unique_insts.keys()) - set(symbols.keys())}")
