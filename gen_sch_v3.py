#!/usr/bin/env python3
"""Apply the v1.1 schematic updates to the KiCad project.

This script intentionally updates the already-valid KiCad 7 schematic instead of
regenerating a bare S-expression from scratch, because the checked-in schematic
embeds complete KiCad standard/custom lib_symbols required by KiCad CLI.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script: str) -> None:
    print(f"→ {script}")
    subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)


def main() -> None:
    sch = ROOT / "esp32-epaper.kicad_sch"
    content = sch.read_text(encoding="utf-8")
    if '"R12"' not in content or '"R13"' not in content or '"C21"' not in content:
        run("add_vbat_sense.py")
    else:
        print("✓ VBAT_SENSE components already present")

    content = sch.read_text(encoding="utf-8")
    if '"D3"' not in content or '"D4"' not in content or '"J3"' not in content:
        run("add_power_path_update.py")
    else:
        print("✓ D3/D4/J3 power-path components already present")

    content = sch.read_text(encoding="utf-8")
    print(f"✓ Component instances: {content.count('(symbol (lib_id')}")


if __name__ == "__main__":
    main()
