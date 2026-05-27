#!/usr/bin/env python3
"""Generate complete KiCad 7 schematic for ESP32 E-Paper Badge.

Circuit blocks:
  A: ESP32-WROOM-32D (MCU) — uses Device:R, Device:C etc from KiCad standard lib
  B: SSD1680 + FPC-26P (E-Paper Driver)
  C: TP4056 + DW01A + FS8205A + HT7333 (Power)
  D: USB-C Connector
  E: Toggle Switch + Status LED
  F: Decoupling caps and pull-up resistors

All custom ICs use esp32-epaper-lib.
Passive components (R, C, L, LED, D) use KiCad standard Device library.
"""
import os, uuid
from kiutils.items.common import Font
from kiutils.schematic import (
    Schematic, SchematicSymbol, Position, Property, Effects,
    Connection, GlobalLabel, LocalLabel, Junction, NoConnect,
    Rectangle, Text, PageSettings, TitleBlock,
)
from kiutils.symbol import SymbolLib

OUT = os.path.dirname(os.path.abspath(__file__))

def uid():
    return str(uuid.uuid4())

# ── Pin position calculator ──────────────────────────────────
# Our symbols use body rectangles and pins at specific offsets.
# When placed at (X,Y), pin positions depend on the symbol's internal geometry.
# We need to track where each pin ends up after placement.

class PinPos:
    """Track pin locations for a placed symbol."""
    def __init__(self, x, y, pins_info):
        """
        x, y: symbol placement position (mm)
        pins_info: dict of pin_name -> (offset_x_mm, offset_y_mm) 
                   relative to symbol origin
        """
        self.x = x
        self.y = y
        self.pins = {}
        for name, (ox, oy) in pins_info.items():
            self.pins[name] = (x + ox, y + oy)
    
    def pin(self, name):
        return self.pins[name]


def wire(sch, x1, y1, x2, y2):
    """Add a wire segment."""
    sch.graphicalItems.append(Connection(
        type='wire',
        points=[Position(X=x1, Y=y1), Position(X=x2, Y=y2)],
        uuid=uid(),
    ))


def label(sch, text, x, y, shape='input'):
    """Add a global label (power net or named net)."""
    sch.globalLabels.append(GlobalLabel(
        text=text,
        shape=shape,
        position=Position(X=x, Y=y),
        effects=Effects(font=Font(height=1.27, width=1.27)),
        uuid=uid(),
    ))


def local_label(sch, text, x, y):
    """Add a local net label."""
    sch.labels.append(LocalLabel(
        text=text,
        position=Position(X=x, Y=y),
        effects=Effects(font=Font(height=1.27, width=1.27)),
        uuid=uid(),
    ))


def junction(sch, x, y):
    """Add a junction (wire node)."""
    sch.junctions.append(Junction(position=Position(X=x, Y=y), uuid=uid()))


def no_connect(sch, x, y):
    """Add a no-connect marker."""
    sch.noConnects.append(NoConnect(position=Position(X=x, Y=y), uuid=uid()))


def place_symbol(sch, lib_nick, entry, ref, value, x, y, rotation=0):
    """Place a component on the schematic."""
    sym = SchematicSymbol(
        libraryNickname=lib_nick,
        entryName=entry,
        position=Position(X=x, Y=y, angle=rotation),
        uuid=uid(),
        properties=[
            Property(key='Reference', value=ref, id=0,
                    position=Position(X=x, Y=y - 5),
                    effects=Effects(font=Font(height=1.27, width=1.27))),
            Property(key='Value', value=value, id=1,
                    position=Position(X=x, Y=y + 5),
                    effects=Effects(font=Font(height=1.27, width=1.27))),
        ],
    )
    sch.schematicSymbols.append(sym)
    return sym


def place_device(sch, ref, value, x, y, rotation=0):
    """Place a standard KiCad Device library component."""
    # Determine library ID from ref prefix
    lib_map = {
        'R':  'Device:R',
        'C':  'Device:C',
        'L':  'Device:L',
        'D':  'Device:D',
        'LED':'Device:LED',
        'Q':  'Device:Q_NMOS_GSD',
        'SW': 'Device:RotarySwitch',  # Will use custom
        'J':  'esp32-epaper-lib:USB-C-16P',
        'BT': 'esp32-epaper-lib:BatteryHolder_18650',
        'F':  'Device:Polyfuse',
    }
    
    # Custom lib parts
    custom = {
        'U3': 'esp32-epaper-lib:TP4056',
        'U4': 'esp32-epaper-lib:DW01A',
        'U5': 'esp32-epaper-lib:FS8205A',
        'U6': 'esp32-epaper-lib:HT7333-1',
        'U2': 'esp32-epaper-lib:SSD1680',
    }
    
    if ref in custom:
        lib_id = custom[ref]
    else:
        prefix = ''.join(c for c in ref if c.isalpha())
        lib_id = lib_map.get(prefix, f'Device:{prefix}')
    
    lib_nick, entry = lib_id.split(':')
    return place_symbol(sch, lib_nick, entry, ref, value, x, y, rotation)


# ── Section rectangles for visual grouping ──
def section_box(sch, x1, y1, x2, y2, title, x_title=0, y_title=0):
    """Draw a dashed rectangle around a schematic section."""
    sch.graphicalItems.append(Rectangle(
        start=Position(X=x1, Y=y1),
        end=Position(X=x2, Y=y2),
        stroke=Stroke(width=0.3, type='dash'),
        fill=Fill(type='none'),
        uuid=uid(),
    ))
    sch.graphicalItems.append(Text(
        text=title,
        position=Position(X=x_title or x1 + 5, Y=y_title or y1 - 3),
        effects=Effects(font=Font(height=2.54, width=2.54)),
        uuid=uid(),
    ))


# ══════════════════════════════════════════════════════════════
# Main schematic builder
# ══════════════════════════════════════════════════════════════

def build_schematic():
    from kiutils.schematic import Stroke as SchStroke, Fill as SchFill
    
    # Load custom symbol library
    lib = SymbolLib.from_file(os.path.join(OUT, 'esp32-epaper-lib.kicad_sym'))
    
    sch = Schematic(
        version='20230121',
        generator='kiutils',
        uuid=uid(),
        paper=PageSettings(paperSize='A3', portrait=True),
        titleBlock=TitleBlock(
            title='ESP32 E-Paper Badge v1.0',
            date='2025-05-27',
            revision='1.0',
            company='LuckyDog',
            comments={
                1: 'ESP32-WROOM-32D + SSD1680 + TP4056 + HT7333',
                2: '2.13" Tri-color E-Paper, USB-C Charging',
                3: 'Source: ESP32 HWDG v4.4 + SSD1680 DS v1.2 + Driver Board v1.3',
                4: 'NOT FOR PRODUCTION - Verify with ERC before PCB layout',
            },
        ),
    )
    
    # Embed custom symbols
    sch.libSymbols = lib.symbols
    
    # ──────────────────────────────────────────────────────────
    # Layout coordinates (mm)
    # A3 portrait: ~280mm wide × 400mm tall usable area
    #
    #  ┌──────────────────────────────────────────────────┐
    #  │  Title Block                                      │
    #  ├──────────────────────────────────────────────────┤
    #  │                    │                              │
    #  │   ESP32-WROOM-32D  │     SSD1680 + FPC Connector  │
    #  │   (Section A)       │     (Section B)              │
    #  │   x=20..130         │     x=160..270               │
    #  │   y=15..110         │     y=15..160                │
    #  │                    │                              │
    #  ├──────────────────────────────────────────────────┤
    #  │  USB-C  TP4056  DW01A FS8205A  HT7333  Batt  SW LED│
    #  │  (Section C: Power + Peripherals, y=170..360)     │
    #  │                                                    │
    #  └──────────────────────────────────────────────────┘
    #
    
    # ═══════════════════════════════════════════════════════════
    # SECTION A: ESP32-WROOM-32D
    # ═══════════════════════════════════════════════════════════
    # Place at (75, 65) - center of MCU section
    place_symbol(sch, 'RF_Module', 'ESP32-WROOM-32D', 'U1', 'ESP32-WROOM-32D', 75, 65)
    
    # Decoupling caps for ESP32
    # C1: 10µF on 3V3
    place_symbol(sch, 'Device', 'C', 'C1', '10µF', 35, 20)
    # C2: 100nF on 3V3  
    place_symbol(sch, 'Device', 'C', 'C2', '100nF', 45, 20)
    # C3: 10µF on EN
    place_symbol(sch, 'Device', 'C', 'C3', '10µF', 115, 20)
    
    # Pull-ups
    # R1: 10k EN
    place_symbol(sch, 'Device', 'R', 'R1', '10kΩ', 115, 35)
    # R2: 10k IO0
    place_symbol(sch, 'Device', 'R', 'R2', '10kΩ', 115, 45)
    # R3: 10k IO2 (debug switch)
    place_symbol(sch, 'Device', 'R', 'R3', '10kΩ', 20, 100)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION B: SSD1680 E-Paper Driver
    # ═══════════════════════════════════════════════════════════
    place_symbol(sch, 'esp32-epaper-lib', 'SSD1680', 'U2', 'SSD1680', 195, 80)
    
    # FPC connector
    place_symbol(sch, 'esp32-epaper-lib', 'FPC-26P-Epaper', 'J2', 'FPC-26P 0.5mm', 255, 80)
    
    # SSD1680 peripheral components
    # L1: 68µH inductor (charge pump)
    place_symbol(sch, 'Device', 'L', 'L1', '68µH', 195, 15)
    # Q1: AO3400A N-MOSFET
    place_symbol(sch, 'Device', 'Q_NMOS_GSD', 'Q1', 'AO3400A', 210, 15)
    
    # Diodes D6, D7, D8
    place_symbol(sch, 'Device', 'D', 'D6', 'MBR0530', 175, 25)
    place_symbol(sch, 'Device', 'D', 'D7', 'MBR0530', 185, 25)
    place_symbol(sch, 'Device', 'D', 'D8', 'MBR0530', 195, 25)
    
    # R7: 10k, R8: 0.47Ω
    place_symbol(sch, 'Device', 'R', 'R7', '10kΩ', 225, 25)
    place_symbol(sch, 'Device', 'R', 'R8', '0.47Ω', 235, 25)
    
    # Caps C7-C15 (1µF × 9) for charge pump
    for i, ref in enumerate(['C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15']):
        place_symbol(sch, 'Device', 'C', ref, '1µF', 165 + (i % 5) * 12, 140 + (i // 5) * 12)
    
    # C16, C17: 100nF
    place_symbol(sch, 'Device', 'C', 'C16', '100nF', 225, 35)
    place_symbol(sch, 'Device', 'C', 'C17', '100nF', 235, 35)
    
    # C18: 4.7µF
    place_symbol(sch, 'Device', 'C', 'C18', '4.7µF', 225, 45)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION C: Power Management
    # ═══════════════════════════════════════════════════════════
    
    # USB-C connector
    place_symbol(sch, 'esp32-epaper-lib', 'USB-C-16P', 'J1', 'USB-C 16P', 20, 210)
    
    # CC pull-downs
    place_symbol(sch, 'Device', 'R', 'R9', '5.1kΩ', 20, 240)
    place_symbol(sch, 'Device', 'R', 'R10', '5.1kΩ', 30, 240)
    
    # TP4056 charger
    place_symbol(sch, 'esp32-epaper-lib', 'TP4056', 'U3', 'TP4056', 75, 210)
    
    # R4: 1.2kΩ (PROG → 500mA charge current)
    place_symbol(sch, 'Device', 'R', 'R4', '1.2kΩ', 60, 225)
    
    # C4, C5: 10µF
    place_symbol(sch, 'Device', 'C', 'C4', '10µF', 55, 210)
    place_symbol(sch, 'Device', 'C', 'C5', '10µF', 95, 210)
    
    # DW01A battery protection
    place_symbol(sch, 'esp32-epaper-lib', 'DW01A', 'U4', 'DW01A', 140, 210)
    
    # FS8205A dual MOSFET
    place_symbol(sch, 'esp32-epaper-lib', 'FS8205A', 'U5', 'FS8205A', 140, 260)
    
    # R5: 100Ω (DW01A CS)
    place_symbol(sch, 'Device', 'R', 'R5', '100Ω', 155, 240)
    # C6: 100nF
    place_symbol(sch, 'Device', 'C', 'C6', '100nF', 155, 250)
    
    # HT7333 LDO
    place_symbol(sch, 'esp32-epaper-lib', 'HT7333-1', 'U6', 'HT7333-1', 200, 210)
    
    # C19, C20: 10µF
    place_symbol(sch, 'Device', 'C', 'C19', '10µF', 185, 210)
    place_symbol(sch, 'Device', 'C', 'C20', '10µF', 215, 210)
    
    # Battery holder
    place_symbol(sch, 'esp32-epaper-lib', 'BatteryHolder_18650', 'BT1', '18650', 200, 270)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION D: Peripherals (Switch + LED)
    # ═══════════════════════════════════════════════════════════
    
    # Toggle switch
    place_symbol(sch, 'esp32-epaper-lib', 'ToggleSwitch_SPDT', 'SW1', 'SW SPDT', 255, 210)
    
    # LED + Resistor
    place_symbol(sch, 'Device', 'LED', 'D5', 'Green', 255, 250)
    place_symbol(sch, 'Device', 'R', 'R11', '1kΩ', 255, 240)
    
    # ═══════════════════════════════════════════════════════════
    # Power Labels
    # ═══════════════════════════════════════════════════════════
    
    # VBUS (USB 5V)
    label(sch, 'VBUS', 20, 195, 'input')
    
    # 3V3 system power
    label(sch, '3V3', 140, 175, 'power_out')  # From HT7333 output
    label(sch, '3V3', 40, 10, 'input')        # ESP32 VDD
    label(sch, '3V3', 175, 10, 'input')       # SSD1680 VDD
    
    # VBAT (battery voltage)
    label(sch, 'VBAT', 120, 220, 'output')    # TP4056 BAT
    label(sch, 'VBAT', 195, 200, 'input')     # HT7333 VIN
    
    # GND
    label(sch, 'GND', 20, 180, 'input')
    label(sch, 'GND', 75, 180, 'input')
    label(sch, 'GND', 140, 180, 'input')
    label(sch, 'GND', 200, 180, 'input')
    
    # ═══════════════════════════════════════════════════════════
    # Net Labels (Signal connections)
    # ═══════════════════════════════════════════════════════════
    
    # SPI bus
    local_label(sch, 'EPD_CLK', 135, 65)
    local_label(sch, 'EPD_MOSI', 135, 70)
    local_label(sch, 'EPD_CS', 135, 60)
    local_label(sch, 'EPD_DC', 135, 55)
    local_label(sch, 'EPD_RST', 135, 50)
    local_label(sch, 'EPD_BUSY', 135, 75)
    
    # SSD1680 side
    local_label(sch, 'EPD_CLK', 160, 80)
    local_label(sch, 'EPD_MOSI', 160, 85)
    local_label(sch, 'EPD_CS', 160, 75)
    local_label(sch, 'EPD_DC', 160, 70)
    local_label(sch, 'EPD_RST', 160, 65)
    local_label(sch, 'EPD_BUSY', 160, 90)
    
    # Debug switch
    local_label(sch, 'DEBUG_SW', 15, 100)
    local_label(sch, 'DEBUG_SW', 240, 215)
    
    # Status LED
    local_label(sch, 'LED', 135, 80)
    local_label(sch, 'LED', 245, 250)
    
    # ═══════════════════════════════════════════════════════════
    # Section Labels (text annotations)
    # ═══════════════════════════════════════════════════════════
    sch.graphicalItems.append(Text(
        text='A: ESP32-WROOM-32D MCU',
        position=Position(X=20, Y=13),
        effects=Effects(font=Font(height=2.54, width=2.54)),
        uuid=uid(),
    ))
    sch.graphicalItems.append(Text(
        text='B: SSD1680 E-Paper Driver + FPC',
        position=Position(X=160, Y=8),
        effects=Effects(font=Font(height=2.54, width=2.54)),
        uuid=uid(),
    ))
    sch.graphicalItems.append(Text(
        text='C: Power Management (USB-C → TP4056 → DW01A → HT7333)',
        position=Position(X=15, Y=170),
        effects=Effects(font=Font(height=2.54, width=2.54)),
        uuid=uid(),
    ))
    sch.graphicalItems.append(Text(
        text='D: Debug Switch + Status LED',
        position=Position(X=240, Y=170),
        effects=Effects(font=Font(height=2.54, width=2.54)),
        uuid=uid(),
    ))
    
    # ═══════════════════════════════════════════════════════════
    # Key wiring connections (power rails)
    # ═══════════════════════════════════════════════════════════
    
    # USB VBUS → TP4056 VCC
    wire(sch, 35, 200, 60, 200)   # USB-C VBUS → wire → TP4056 VCC
    wire(sch, 60, 200, 60, 210)   # down to TP4056
    
    # TP4056 BAT → VBAT net
    wire(sch, 90, 215, 120, 215)  # TP4056 BAT out → VBAT
    wire(sch, 120, 215, 120, 220) # → VBAT label
    
    # VBAT → HT7333 VIN
    wire(sch, 120, 220, 190, 220)
    wire(sch, 190, 220, 190, 210)
    
    # HT7333 VOUT → 3V3
    wire(sch, 210, 210, 215, 210)
    wire(sch, 215, 210, 215, 175)
    wire(sch, 140, 175, 215, 175)  # 3V3 bus
    
    # 3V3 → ESP32 VDD
    wire(sch, 40, 175, 40, 10)
    wire(sch, 40, 10, 40, 20)      # to C1
    
    # GND connections (simplified - in real KiCad, use power symbols)
    # We use global labels for GND, so explicit wires aren't strictly needed
    # KiCad's ERC will connect all same-named power labels
    
    # ═══════════════════════════════════════════════════════════
    # Save
    # ═══════════════════════════════════════════════════════════
    path = os.path.join(OUT, 'esp32-epaper.kicad_sch')
    sch.to_file(path, encoding='utf-8')
    print(f"✓ Schematic saved: {path}")
    
    # Count items
    n_syms = len(sch.schematicSymbols)
    n_wires = sum(1 for g in sch.graphicalItems if isinstance(g, Connection))
    n_labels = len(sch.globalLabels) + len(sch.labels)
    print(f"  Components: {n_syms}")
    print(f"  Wires: {n_wires}")
    print(f"  Labels: {n_labels}")
    
    return sch


if __name__ == '__main__':
    build_schematic()
