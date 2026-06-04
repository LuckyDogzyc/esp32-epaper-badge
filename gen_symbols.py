#!/usr/bin/env python3
"""Generate KiCad 7 symbol library for ESP32 E-Paper Badge.

Custom parts: TP4056, DW01A, FS8205A, HT7333-1, SSD1680, USB-C-16P, FPC-26P,
PH2.0 battery connector, ToggleSwitch
"""
import os, sys
from kiutils.symbol import (
    SymbolLib, Symbol as SySymbol, SymbolPin,
    SyRect, Stroke, Fill, Effects, Font, Property,
    Position as SyPos,
)

OUT = os.path.dirname(os.path.abspath(__file__))

def make_sym(name, ref_prefix, left_pins, right_pins, body_w=600, body_h=None):
    """Create an IC symbol.
    
    left_pins/right_pins: list of (number, name, electrical_type)
    """
    pin_spacing = 100  # mil between pins
    pin_length = 200   # mil (0.2 inches)
    
    max_pins = max(len(left_pins), len(right_pins), 1)
    if body_h is None:
        body_h = (max_pins + 1) * pin_spacing
    
    half_w = body_w // 2
    half_h = body_h // 2
    
    # Body rectangle (kiutils uses inches)
    graphics = [
        SyRect(
            start=SyPos(X=-half_w/1000, Y=-half_h/1000),
            end=SyPos(X=half_w/1000, Y=half_h/1000),
            stroke=Stroke(width=0.254),
            fill=Fill(type='background'),
        )
    ]
    
    pins = []
    
    # Left pins (pin extends LEFT, position at left body edge)
    for i, (num, pname, etype) in enumerate(left_pins):
        y = (-half_h + (i + 1) * pin_spacing) / 1000
        pins.append(SymbolPin(
            electricalType=etype,
            graphicalStyle='line',
            position=SyPos(X=-half_w/1000, Y=y),
            length=pin_length/1000,
            name=pname,
            nameEffects=Effects(font=Font(height=0.762, width=0.762)),
            number=str(num),
            numberEffects=Effects(font=Font(height=0.762, width=0.762)),
        ))
    
    # Right pins (pin extends RIGHT, position at right body edge)
    for i, (num, pname, etype) in enumerate(right_pins):
        y = (-half_h + (i + 1) * pin_spacing) / 1000
        pins.append(SymbolPin(
            electricalType=etype,
            graphicalStyle='line',
            position=SyPos(X=half_w/1000, Y=y),
            length=pin_length/1000,
            name=pname,
            nameEffects=Effects(font=Font(height=0.762, width=0.762)),
            number=str(num),
            numberEffects=Effects(font=Font(height=0.762, width=0.762)),
        ))
    
    return SySymbol(
        libraryNickname='esp32-epaper-lib',
        entryName=name,
        properties=[
            Property(key='Reference', value=ref_prefix, id=0,
                    position=SyPos(X=0, Y=(-half_h - 60)/1000),
                    effects=Effects(font=Font(height=1.0, width=1.0))),
            Property(key='Value', value=name, id=1,
                    position=SyPos(X=0, Y=(half_h + 60)/1000),
                    effects=Effects(font=Font(height=1.0, width=1.0))),
            Property(key='Footprint', value='', id=2,
                    position=SyPos(X=0, Y=(half_h + 160)/1000),
                    effects=Effects(font=Font(height=0.635, width=0.635), hide=True)),
        ],
        graphicItems=graphics,
        pins=pins,
    )


def main():
    symbols = []
    
    # ── TP4056 (SOP-8, Battery Charger) ──
    # Source: TP4056 Datasheet Rev 1.05
    symbols.append(make_sym('TP4056', 'U',
        left_pins=[
            (1, 'CHRG',  'open_collector'),  # Charge status output
            (2, 'PROG',  'input'),            # Charge current set
            (3, 'GND',   'power_in'),
            (4, 'VCC',   'power_in'),         # Input supply
        ],
        right_pins=[
            (8, 'CE',    'input'),            # Chip enable
            (7, 'NC',    'no_connect'),
            (6, 'STDBY', 'open_collector'),   # Standby status
            (5, 'BAT',   'power_out'),        # Battery
        ],
        body_w=600, body_h=500,
    ))
    
    # ── DW01A (SOT-23-6, Battery Protection) ──
    # Source: DW01A Datasheet
    symbols.append(make_sym('DW01A', 'U',
        left_pins=[
            (1, 'CS',  'bidirectional'),
            (2, 'GND', 'power_in'),
            (3, 'OD',  'output'),
        ],
        right_pins=[
            (4, 'OC',  'output'),
            (5, 'VCC', 'power_in'),
            (6, 'TD',  'input'),
        ],
        body_w=500, body_h=500,
    ))
    
    # ── FS8205A (TSSOP-8, Dual N-MOSFET) ──
    # Source: FS8205A Datasheet
    symbols.append(make_sym('FS8205A', 'U',
        left_pins=[
            (1, 'S1', 'passive'),
            (2, 'G1', 'input'),
            (3, 'S2', 'passive'),
            (4, 'G2', 'input'),
        ],
        right_pins=[
            (8, 'D1', 'passive'),
            (7, 'D1', 'passive'),
            (6, 'D2', 'passive'),
            (5, 'D2', 'passive'),
        ],
        body_w=500, body_h=500,
    ))
    
    # ── HT7333-1 (SOT-89, LDO) ──
    # Source: HT7333 Datasheet
    symbols.append(make_sym('HT7333-1', 'U',
        left_pins=[
            (1, 'VIN',  'power_in'),
            (2, 'GND',  'power_in'),
        ],
        right_pins=[
            (3, 'VOUT', 'power_out'),
        ],
        body_w=400, body_h=300,
    ))
    
    # ── SSD1680 (QFN-48, E-Paper Driver IC) ──
    # Source: SSD1680 Datasheet v1.2 + Driver Board v1.3 Schematic
    # Simplified symbol showing only key pins (not all 48)
    symbols.append(make_sym('SSD1680', 'U',
        left_pins=[
            (1,  'VDD',    'power_in'),
            (2,  'VSS',    'power_in'),
            (3,  'BS',     'input'),       # Bus select: 0=SPI
            (4,  'CLK',    'input'),       # SPI clock
            (5,  'DIN',    'input'),       # SPI data in
            (6,  'DC',     'input'),       # Data/Command
            (7,  'CS',     'input'),       # Chip select
            (8,  'RST',    'input'),       # Reset
            (9,  'BUSY',   'output'),      # Busy status
        ],
        right_pins=[
            (10, 'GDR',    'output'),      # Gate drive
            (11, 'RESE',   'passive'),     # Current sense
            (12, 'PREVGH', 'passive'),     # Positive gate voltage
            (13, 'PREVGL', 'passive'),     # Negative gate voltage
            (14, 'VDH',    'passive'),     # Positive driving voltage
            (15, 'VDL',    'passive'),     # Negative driving voltage
            (16, 'VGH',    'passive'),     # Gate high
            (17, 'VGL',    'passive'),     # Gate low
            (18, 'VCOM',   'passive'),     # Common mode voltage
        ],
        body_w=700, body_h=1900,
    ))
    
    # ── USB-C 16Pin Receptacle ──
    # Source: USB Type-C Spec R2.1
    symbols.append(make_sym('USB-C-16P', 'J',
        left_pins=[
            (1,  'GND',  'power_in'),
            (2,  'VBUS', 'power_out'),
            (3,  'CC1',  'bidirectional'),
            (4,  'SBU1', 'bidirectional'),
            (5,  'DP1',  'bidirectional'),
            (6,  'DN1',  'bidirectional'),
            (7,  'DP2',  'bidirectional'),
            (8,  'DN2',  'bidirectional'),
        ],
        right_pins=[
            (9,  'SH',   'passive'),   # Shield
        ],
        body_w=600, body_h=900,
    ))
    
    # ── FPC 26P 0.5mm Connector (E-Paper Display) ──
    # Source: DEPG0213RWS FPC pinout
    symbols.append(make_sym('FPC-26P-Epaper', 'J',
        left_pins=[
            (1,  'GND',    'power_in'),
            (2,  'GND',    'power_in'),
            (3,  'GDR',    'passive'),
            (4,  'GDR',    'passive'),
            (5,  'PREVGL', 'passive'),
            (6,  'PREVGL', 'passive'),
            (7,  'PREVGH', 'passive'),
            (8,  'PREVGH', 'passive'),
            (9,  'GDR',    'passive'),
            (10, 'GDR',    'passive'),
            (11, 'RESE',   'passive'),
            (12, 'RESE',   'passive'),
            (13, 'PREVGH', 'passive'),
        ],
        right_pins=[
            (14, 'PREVGH', 'passive'),
            (15, 'PREVGL', 'passive'),
            (16, 'PREVGL', 'passive'),
            (17, 'RESE',   'passive'),
            (18, 'RESE',   'passive'),
            (19, 'VDD',    'power_in'),
            (20, 'VDD',    'power_in'),
            (21, 'CLK',    'input'),
            (22, 'DIN',    'input'),
            (23, 'RST',    'input'),
            (24, 'DC',     'input'),
            (25, 'CS',     'input'),
            (26, 'BUSY',   'output'),
        ],
        body_w=700, body_h=1500,
    ))
    
    # ── Battery Holder (18650) ──
    symbols.append(make_sym('BatteryHolder_18650', 'BT',
        left_pins=[
            (1, 'NEG', 'power_in'),
        ],
        right_pins=[
            (2, 'POS', 'power_out'),
        ],
        body_w=800, body_h=300,
    ))
    
    # ── PH2.0 2-pin connector for 103040 LiPo battery ──
    symbols.append(make_sym('PH2_0-2P-Battery', 'J',
        left_pins=[
            (1, 'BAT+', 'power_out'),
        ],
        right_pins=[
            (2, 'BAT-', 'power_in'),
        ],
        body_w=500, body_h=300,
    ))

    # ── Toggle Switch SPDT ──
    symbols.append(make_sym('ToggleSwitch_SPDT', 'SW',
        left_pins=[
            (1, 'COM', 'passive'),
        ],
        right_pins=[
            (2, 'NO',  'passive'),
            (3, 'NC',  'passive'),
        ],
        body_w=400, body_h=400,
    ))
    
    # Build library
    lib = SymbolLib(
        version='20211014',
        generator='kiutils',
        symbols=symbols,
    )
    
    path = os.path.join(OUT, 'esp32-epaper-lib.kicad_sym')
    lib.to_file(path, encoding='utf-8')
    print(f"✓ Symbol library saved: {path}")
    print(f"  Symbols: {len(symbols)}")
    for s in symbols:
        print(f"    - {s.entryName} ({len(s.pins)} pins)")
    return lib


if __name__ == '__main__':
    main()
