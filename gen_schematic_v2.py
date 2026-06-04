#!/usr/bin/env python3
"""Generate KiCad 7 schematic for ESP32 E-Paper Badge v1.1.

Uses kiutils but patches output to be fully KiCad 7 compliant.
"""
import os, uuid, re
from kiutils.items.common import Font
from kiutils.schematic import (
    Schematic, SchematicSymbol, Position, Property, Effects,
    Connection, GlobalLabel, LocalLabel, Junction, NoConnect,
    Rectangle, Text, PageSettings, TitleBlock,
    SymbolInstance, SymbolProjectInstance, SymbolProjectPath,
    HierarchicalSheetInstance, ProjectInstance,
)
from kiutils.symbol import SymbolLib

OUT = os.path.dirname(os.path.abspath(__file__))
SCHEMATIC_UUID = str(uuid.uuid4())

def uid():
    return str(uuid.uuid4())

# Track all placed components for the instances block
placed_components = []  # list of (path, ref, unit, value, footprint)

def place_symbol(sch, lib_nick, entry, ref, value, x, y, num_pins=0, footprint=''):
    """Place a component on the schematic with proper KiCad 7 format."""
    pin_uuids = {}
    for i in range(1, num_pins + 1):
        pin_uuids[str(i)] = uid()
    
    sym = SchematicSymbol(
        libraryNickname=lib_nick,
        entryName=entry,
        position=Position(X=x, Y=y, angle=0),
        unit=1,
        inBom=True,
        onBoard=True,
        uuid=uid(),
        properties=[
            Property(key='Reference', value=ref, id=0,
                    position=Position(X=x, Y=y - 5),
                    effects=Effects(font=Font(height=1.27, width=1.27))),
            Property(key='Value', value=value, id=1,
                    position=Position(X=x, Y=y + 5),
                    effects=Effects(font=Font(height=1.27, width=1.27))),
        ],
        pins=pin_uuids,
    )
    sch.schematicSymbols.append(sym)
    
    # Track for instances
    placed_components.append({
        'uuid': sym.uuid,
        'ref': ref,
        'value': value,
        'footprint': footprint,
    })
    
    return sym


def wire(sch, x1, y1, x2, y2):
    sch.graphicalItems.append(Connection(
        type='wire',
        points=[Position(X=x1, Y=y1), Position(X=x2, Y=y2)],
        uuid=uid(),
    ))


def global_label(sch, text, x, y, shape='input'):
    sch.globalLabels.append(GlobalLabel(
        text=text, shape=shape,
        position=Position(X=x, Y=y),
        effects=Effects(font=Font(height=1.27, width=1.27)),
        uuid=uid(),
    ))


def local_label(sch, text, x, y):
    sch.labels.append(LocalLabel(
        text=text,
        position=Position(X=x, Y=y),
        effects=Effects(font=Font(height=1.27, width=1.27)),
        uuid=uid(),
    ))


def section_text(sch, text, x, y):
    sch.graphicalItems.append(Text(
        text=text,
        position=Position(X=x, Y=y),
        effects=Effects(font=Font(height=2.54, width=2.54)),
        uuid=uid(),
    ))


def build_schematic():
    lib = SymbolLib.from_file(os.path.join(OUT, 'esp32-epaper-lib.kicad_sym'))
    
    sch = Schematic(
        version='20221206',
        generator='eeschema',
        uuid=SCHEMATIC_UUID,
        paper=PageSettings(paperSize='A3', portrait=True),
        titleBlock=TitleBlock(
            title='ESP32 E-Paper Badge v1.1',
            date='2026-06-04',
            revision='1.1',
            company='LuckyDog',
            comments={
                1: 'ESP32-WROOM-32D + SSD1680 + TP4056 + HT7333',
                2: '2.13" Tri-color E-Paper, USB-C Charging',
                3: 'Source: ESP32 HWDG v4.4 + SSD1680 DS v1.2 + Driver Board v1.3',
            },
        ),
    )
    
    # Embed custom symbols
    sch.libSymbols = lib.symbols
    
    # ═══════════════════════════════════════════════════════════
    # SECTION A: ESP32-WROOM-32D
    # ═══════════════════════════════════════════════════════════
    place_symbol(sch, 'RF_Module', 'ESP32-WROOM-32D', 'U1', 'ESP32-WROOM-32D',
                 75, 65, num_pins=39, footprint='RF_Module:ESP32-WROOM-32D')
    
    place_symbol(sch, 'Device', 'C', 'C1', '10µF', 35, 20, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C2', '100nF', 45, 20, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C3', '10µF', 115, 20, num_pins=2)
    place_symbol(sch, 'Device', 'R', 'R1', '10kΩ', 115, 35, num_pins=2)
    place_symbol(sch, 'Device', 'R', 'R2', '10kΩ', 115, 45, num_pins=2)
    place_symbol(sch, 'Device', 'R', 'R3', '10kΩ', 20, 100, num_pins=2)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION B: SSD1680 + FPC
    # ═══════════════════════════════════════════════════════════
    place_symbol(sch, 'esp32-epaper-lib', 'SSD1680', 'U2', 'SSD1680',
                 195, 80, num_pins=18)
    place_symbol(sch, 'esp32-epaper-lib', 'FPC-26P-Epaper', 'J2', 'FPC-26P 0.5mm',
                 255, 80, num_pins=26)
    place_symbol(sch, 'Device', 'L', 'L1', '68µH', 195, 15, num_pins=2)
    place_symbol(sch, 'Device', 'Q_NMOS_GSD', 'Q1', 'AO3400A', 210, 15, num_pins=3)
    
    place_symbol(sch, 'Device', 'D', 'D6', 'MBR0530', 175, 25, num_pins=2)
    place_symbol(sch, 'Device', 'D', 'D7', 'MBR0530', 185, 25, num_pins=2)
    place_symbol(sch, 'Device', 'D', 'D8', 'MBR0530', 195, 25, num_pins=2)
    
    place_symbol(sch, 'Device', 'R', 'R7', '10kΩ', 225, 25, num_pins=2)
    place_symbol(sch, 'Device', 'R', 'R8', '0.47Ω', 235, 25, num_pins=2)
    
    for i, ref in enumerate(['C7','C8','C9','C10','C11','C12','C13','C14','C15']):
        place_symbol(sch, 'Device', 'C', ref, '1µF',
                     165 + (i % 5) * 12, 140 + (i // 5) * 12, num_pins=2)
    
    place_symbol(sch, 'Device', 'C', 'C16', '100nF', 225, 35, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C17', '100nF', 235, 35, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C18', '4.7µF', 225, 45, num_pins=2)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION C: Power
    # ═══════════════════════════════════════════════════════════
    place_symbol(sch, 'esp32-epaper-lib', 'USB-C-16P', 'J1', 'USB-C 16P',
                 20, 210, num_pins=9)
    place_symbol(sch, 'Device', 'R', 'R9', '5.1kΩ', 20, 240, num_pins=2)
    place_symbol(sch, 'Device', 'R', 'R10', '5.1kΩ', 30, 240, num_pins=2)
    
    place_symbol(sch, 'esp32-epaper-lib', 'TP4056', 'U3', 'TP4056',
                 75, 210, num_pins=8)
    place_symbol(sch, 'Device', 'R', 'R4', '1.2kΩ', 60, 225, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C4', '10µF', 55, 210, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C5', '10µF', 95, 210, num_pins=2)
    
    place_symbol(sch, 'esp32-epaper-lib', 'DW01A', 'U4', 'DW01A',
                 140, 210, num_pins=6)
    place_symbol(sch, 'esp32-epaper-lib', 'FS8205A', 'U5', 'FS8205A',
                 140, 260, num_pins=8)
    place_symbol(sch, 'Device', 'R', 'R5', '100Ω', 155, 240, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C6', '100nF', 155, 250, num_pins=2)
    
    place_symbol(sch, 'esp32-epaper-lib', 'HT7333-1', 'U6', 'HT7333-1',
                 200, 210, num_pins=3)
    place_symbol(sch, 'Device', 'C', 'C19', '10µF', 185, 210, num_pins=2)
    place_symbol(sch, 'Device', 'C', 'C20', '10µF', 215, 210, num_pins=2)
    
    place_symbol(sch, 'esp32-epaper-lib', 'BatteryHolder_18650', 'BT1', '103040 LiPo',
                 200, 270, num_pins=2)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION D: Switch + LED
    # ═══════════════════════════════════════════════════════════
    place_symbol(sch, 'esp32-epaper-lib', 'ToggleSwitch_SPDT', 'SW1', 'SW SPDT',
                 255, 210, num_pins=3)
    place_symbol(sch, 'Device', 'LED', 'D5', 'Green', 255, 250, num_pins=2)
    place_symbol(sch, 'Device', 'R', 'R11', '1kΩ', 255, 240, num_pins=2)
    
    # ═══════════════════════════════════════════════════════════
    # Power Labels
    # ═══════════════════════════════════════════════════════════
    global_label(sch, 'VBUS', 20, 195, 'input')
    global_label(sch, '3V3', 140, 175, 'power_out')
    global_label(sch, '3V3', 40, 10, 'input')
    global_label(sch, '3V3', 175, 10, 'input')
    global_label(sch, 'VBAT', 120, 220, 'output')
    global_label(sch, 'VBAT', 195, 200, 'input')
    global_label(sch, 'GND', 20, 180, 'input')
    global_label(sch, 'GND', 75, 180, 'input')
    global_label(sch, 'GND', 140, 180, 'input')
    global_label(sch, 'GND', 200, 180, 'input')
    
    # ═══════════════════════════════════════════════════════════
    # Net Labels (SPI + Debug)
    # ═══════════════════════════════════════════════════════════
    for name, xy in [
        ('EPD_CLK',  (135, 65)), ('EPD_CLK',  (160, 80)),
        ('EPD_MOSI', (135, 70)), ('EPD_MOSI', (160, 85)),
        ('EPD_CS',   (135, 60)), ('EPD_CS',   (160, 75)),
        ('EPD_DC',   (135, 55)), ('EPD_DC',   (160, 70)),
        ('EPD_RST',  (135, 50)), ('EPD_RST',  (160, 65)),
        ('EPD_BUSY', (135, 75)), ('EPD_BUSY', (160, 90)),
        ('DEBUG_SW', (15, 100)), ('DEBUG_SW', (240, 215)),
        ('LED',      (135, 80)), ('LED',      (245, 250)),
    ]:
        local_label(sch, name, xy[0], xy[1])
    
    # ═══════════════════════════════════════════════════════════
    # Section labels
    # ═══════════════════════════════════════════════════════════
    section_text(sch, 'A: ESP32-WROOM-32D MCU', 20, 13)
    section_text(sch, 'B: SSD1680 E-Paper Driver + FPC', 160, 8)
    section_text(sch, 'C: Power Management', 15, 170)
    section_text(sch, 'D: Debug Switch + Status LED', 240, 170)
    
    # ═══════════════════════════════════════════════════════════
    # Wires (power rails)
    # ═══════════════════════════════════════════════════════════
    wire(sch, 35, 200, 60, 200)
    wire(sch, 60, 200, 60, 210)
    wire(sch, 90, 215, 120, 215)
    wire(sch, 120, 215, 120, 220)
    wire(sch, 120, 220, 190, 220)
    wire(sch, 190, 220, 190, 210)
    wire(sch, 210, 210, 215, 210)
    wire(sch, 215, 210, 215, 175)
    wire(sch, 140, 175, 215, 175)
    wire(sch, 40, 175, 40, 20)
    wire(sch, 40, 10, 40, 20)
    
    # ═══════════════════════════════════════════════════════════
    # Build instances block
    # ═══════════════════════════════════════════════════════════
    project_name = 'esp32-epaper'
    
    # Sheet instances
    sch.sheetInstances = [
        HierarchicalSheetInstance(instancePath='/', page='1')
    ]
    
    # Symbol instances
    sch.symbolInstances = [
        SymbolInstance(
            path=f'/{SCHEMATIC_UUID}/{comp["uuid"]}',
            reference=comp['ref'],
            unit=1,
            value=comp['value'],
            footprint=comp['footprint'],
        )
        for comp in placed_components
    ]
    
    # Project instances for each symbol
    for sym in sch.schematicSymbols:
        sym.instances = [
            SymbolProjectInstance(
                name=project_name,
                paths=[
                    SymbolProjectPath(
                        sheetInstancePath='/',
                        reference=get_ref_for_sym(sym),
                        unit=1,
                    )
                ],
            )
        ]
    
    # ═══════════════════════════════════════════════════════════
    # Save raw output then fix format issues
    # ═══════════════════════════════════════════════════════════
    raw_path = os.path.join(OUT, 'esp32-epaper-raw.kicad_sch')
    sch.to_file(raw_path, encoding='utf-8')
    
    # Read and fix the output
    with open(raw_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Properties should NOT have (id N) in symbol instances
    # The (id N) is only valid in lib_symbols definition
    # In instances, properties should be: (property "Reference" "U1" (at x y 0))
    content = re.sub(
        r'(\(symbol \(lib_id "[^"]*"\) \(at [^)]*\)(?:\n\s+\(in_bom[^)]*\))?(?:\n\s+\(on_board[^)]*\))?(?:\n\s+\(dnp[^)]*\))?\n\s+\(uuid[^)]*\)\n\s+)\(property "Reference" "([^"]*)" \(id 0\) \(at ([^)]*)\)',
        r'\1(property "Reference" "\2" (at \3 0)',
        content
    )
    content = re.sub(
        r'(\(symbol \(lib_id "[^"]*"\) .+?\n\s+\(uuid[^)]*\)\n\s+(?:.*\n)*?\s+)\(property "Value" "([^"]*)" \(id 1\) \(at ([^)]*)\)',
        r'\1(property "Value" "\2" (at \3 0)',
        content
    )
    
    # Fix 2: Ensure (dnp no) is present after (in_bom yes) (on_board yes)
    content = content.replace('(in_bom yes) (on_board yes)', '(in_bom yes) (on_board yes) (dnp no)')
    
    # Fix 3: Ensure version is correct
    content = content.replace('(version 20230121)', '(version 20221206)')
    
    # Save final version
    final_path = os.path.join(OUT, 'esp32-epaper.kicad_sch')
    with open(final_path, 'w') as f:
        f.write(content)
    
    # Clean up
    os.remove(raw_path)
    
    print(f"✓ Schematic saved: {final_path}")
    print(f"  Components: {len(sch.schematicSymbols)}")
    print(f"  Wires: {sum(1 for g in sch.graphicalItems if isinstance(g, Connection))}")
    print(f"  Global labels: {len(sch.globalLabels)}")
    print(f"  Local labels: {len(sch.labels)}")
    print(f"  Symbol instances: {len(sch.symbolInstances)}")


def get_ref_for_sym(sym):
    """Get reference from symbol properties."""
    for prop in sym.properties:
        if prop.key == 'Reference':
            return prop.value
    return '?'


if __name__ == '__main__':
    build_schematic()
