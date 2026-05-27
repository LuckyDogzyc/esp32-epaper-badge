#!/usr/bin/env python3
"""Generate complete KiCad 7 schematic for ESP32 E-Paper Badge v1.0.
Writes the file directly in correct KiCad 7 S-expression format."""
import os, uuid

OUT = os.path.dirname(os.path.abspath(__file__))
SCH_UUID = str(uuid.uuid4())

def uid():
    return str(uuid.uuid4())

def make_symbol_def(name, ref_prefix, left_pins, right_pins):
    lines = []
    ps = 2.54  # pin spacing mm
    pl = 3.81  # pin length mm
    nl, nr = len(left_pins), len(right_pins)
    mx = max(nl, nr, 1)
    hh = (mx + 1) * ps / 2
    hw = 5.08
    lines.append(f'    (symbol "{name}" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "{ref_prefix}" (at 0 {hh+1.27:.2f} 0)')
    lines.append(f'        (effects (font (size 1.27 1.27)))')
    lines.append(f'      )')
    lines.append(f'      (property "Value" "{name.split(":")[-1]}" (at 0 {-hh-1.27:.2f} 0)')
    lines.append(f'        (effects (font (size 1.27 1.27)))')
    lines.append(f'      )')
    lines.append(f'      (property "Footprint" "" (at 0 0 0)')
    lines.append(f'        (effects (font (size 1.27 1.27)) hide)')
    lines.append(f'      )')
    lines.append(f'      (rectangle (start {-hw:.2f} {hh:.2f}) (end {hw:.2f} {-hh:.2f})')
    lines.append(f'        (stroke (width 0.254))')
    lines.append(f'        (fill (type background))')
    lines.append(f'      )')
    for i, (num, pn, et) in enumerate(left_pins):
        y = hh - (i+1)*ps
        lines.append(f'      (pin {et} line (at {-hw-pl:.2f} {y:.2f} 0) (length {pl})')
        lines.append(f'        (name "{pn}" (effects (font (size 1.27 1.27))))')
        lines.append(f'        (number "{num}" (effects (font (size 1.27 1.27))))')
        lines.append(f'      )')
    for i, (num, pn, et) in enumerate(right_pins):
        y = hh - (i+1)*ps
        lines.append(f'      (pin {et} line (at {hw+pl:.2f} {y:.2f} 180) (length {pl})')
        lines.append(f'        (name "{pn}" (effects (font (size 1.27 1.27))))')
        lines.append(f'        (number "{num}" (effects (font (size 1.27 1.27))))')
        lines.append(f'      )')
    lines.append(f'    )')
    return '\n'.join(lines)

def make_instance(lib_id, ref, value, x, y, num_pins, footprint=''):
    lines = []
    iuuid = uid()
    lines.append(f'  (symbol (lib_id "{lib_id}") (at {x} {y} 0) (unit 1)')
    lines.append(f'    (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid {iuuid})')
    lines.append(f'    (property "Reference" "{ref}" (at {x} {y-5.08} 0)')
    lines.append(f'      (effects (font (size 1.27 1.27)))')
    lines.append(f'    )')
    lines.append(f'    (property "Value" "{value}" (at {x} {y+5.08} 0)')
    lines.append(f'      (effects (font (size 1.27 1.27)))')
    lines.append(f'    )')
    if footprint:
        lines.append(f'    (property "Footprint" "{footprint}" (at {x} {y} 0)')
        lines.append(f'      (effects (font (size 1.27 1.27)) hide)')
        lines.append(f'    )')
    for p in range(1, num_pins+1):
        lines.append(f'    (pin "{p}" (uuid {uid()}))')
    lines.append(f'    (instances')
    lines.append(f'      (project "esp32-epaper"')
    lines.append(f'        (path "/{SCH_UUID}"')
    lines.append(f'          (reference "{ref}") (unit 1)')
    lines.append(f'        )')
    lines.append(f'      )')
    lines.append(f'    )')
    lines.append(f'  )')
    return '\n'.join(lines), iuuid, ref

# ══════════ lib_symbols ══════════
lib_syms = []
lib_syms.append(make_symbol_def('esp32-epaper-lib:TP4056', 'U',
    [(1,'CHRG','open_collector'),(2,'PROG','input'),(3,'GND','power_in'),(4,'VCC','power_in')],
    [(8,'CE','input'),(7,'NC','no_connect'),(6,'STDBY','open_collector'),(5,'BAT','power_out')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:DW01A', 'U',
    [(1,'CS','bidirectional'),(2,'GND','power_in'),(3,'OD','output')],
    [(4,'OC','output'),(5,'VCC','power_in'),(6,'TD','input')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:FS8205A', 'U',
    [(1,'S1','passive'),(2,'G1','input'),(3,'S2','passive'),(4,'G2','input')],
    [(8,'D1','passive'),(7,'D1','passive'),(6,'D2','passive'),(5,'D2','passive')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:HT7333-1', 'U',
    [(1,'VIN','power_in'),(2,'GND','power_in')],
    [(3,'VOUT','power_out')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:SSD1680', 'U',
    [(1,'VDD','power_in'),(2,'VSS','power_in'),(3,'BS','input'),
     (4,'CLK','input'),(5,'DIN','input'),(6,'DC','input'),
     (7,'CS','input'),(8,'RST','input'),(9,'BUSY','output')],
    [(10,'GDR','output'),(11,'RESE','passive'),(12,'PREVGH','passive'),
     (13,'PREVGL','passive'),(14,'VDH','passive'),(15,'VDL','passive'),
     (16,'VGH','passive'),(17,'VGL','passive'),(18,'VCOM','passive')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:USB-C-16P', 'J',
    [(1,'GND','power_in'),(2,'VBUS','power_out'),(3,'CC1','bidirectional'),
     (4,'SBU1','bidirectional'),(5,'DP1','bidirectional'),(6,'DN1','bidirectional'),
     (7,'DP2','bidirectional'),(8,'DN2','bidirectional')],
    [(9,'SH','passive')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:FPC-26P-Epaper', 'J',
    [(1,'GND','power_in'),(2,'GND','power_in'),(3,'GDR','passive'),
     (4,'GDR','passive'),(5,'PREVGL','passive'),(6,'PREVGL','passive'),
     (7,'PREVGH','passive'),(8,'PREVGH','passive'),(9,'GDR','passive'),
     (10,'GDR','passive'),(11,'RESE','passive'),(12,'RESE','passive'),
     (13,'PREVGH','passive')],
    [(14,'PREVGH','passive'),(15,'PREVGL','passive'),(16,'PREVGL','passive'),
     (17,'RESE','passive'),(18,'RESE','passive'),(19,'VDD','power_in'),
     (20,'VDD','power_in'),(21,'CLK','input'),(22,'DIN','input'),
     (23,'RST','input'),(24,'DC','input'),(25,'CS','input'),(26,'BUSY','output')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:BatteryHolder_18650', 'BT',
    [(1,'NEG','power_in')], [(2,'POS','power_out')]))
lib_syms.append(make_symbol_def('esp32-epaper-lib:ToggleSwitch_SPDT', 'SW',
    [(1,'COM','passive')], [(2,'NO','passive'),(3,'NC','passive')]))

# ══════════ Instances ══════════
insts = []
irefs = []

def P(lib_id, ref, value, x, y, np, fp=''):
    inst, iu, ir = make_instance(lib_id, ref, value, x, y, np, fp)
    insts.append(inst)
    irefs.append((iu, ir, value, fp))

# A: MCU
P('RF_Module:ESP32-WROOM-32D','U1','ESP32-WROOM-32D',75,65,39,'RF_Module:ESP32-WROOM-32D')
P('Device:C','C1','10µF',35,20,2); P('Device:C','C2','100nF',45,20,2)
P('Device:C','C3','10µF',115,20,2); P('Device:R','R1','10kΩ',115,35,2)
P('Device:R','R2','10kΩ',115,45,2); P('Device:R','R3','10kΩ',20,100,2)
# B: EPD
P('esp32-epaper-lib:SSD1680','U2','SSD1680',195,80,18)
P('esp32-epaper-lib:FPC-26P-Epaper','J2','FPC-26P',255,80,26)
P('Device:L','L1','68µH',195,15,2); P('Device:Q_NMOS_GSD','Q1','AO3400A',210,15,3)
P('Device:D','D6','MBR0530',175,25,2); P('Device:D','D7','MBR0530',185,25,2)
P('Device:D','D8','MBR0530',195,25,2)
P('Device:R','R7','10kΩ',225,25,2); P('Device:R','R8','0.47Ω',235,25,2)
for i,r in enumerate(['C7','C8','C9','C10','C11','C12','C13','C14','C15']):
    P('Device:C',r,'1µF',165+(i%5)*12,140+(i//5)*12,2)
P('Device:C','C16','100nF',225,35,2); P('Device:C','C17','100nF',235,35,2)
P('Device:C','C18','4.7µF',225,45,2)
# C: Power
P('esp32-epaper-lib:USB-C-16P','J1','USB-C 16P',20,210,9)
P('Device:R','R9','5.1kΩ',20,240,2); P('Device:R','R10','5.1kΩ',30,240,2)
P('esp32-epaper-lib:TP4056','U3','TP4056',75,210,8)
P('Device:R','R4','1.2kΩ',60,225,2); P('Device:C','C4','10µF',55,210,2)
P('Device:C','C5','10µF',95,210,2)
P('esp32-epaper-lib:DW01A','U4','DW01A',140,210,6)
P('esp32-epaper-lib:FS8205A','U5','FS8205A',140,260,8)
P('Device:R','R5','100Ω',155,240,2); P('Device:C','C6','100nF',155,250,2)
P('esp32-epaper-lib:HT7333-1','U6','HT7333-1',200,210,3)
P('Device:C','C19','10µF',185,210,2); P('Device:C','C20','10µF',215,210,2)
P('esp32-epaper-lib:BatteryHolder_18650','BT1','18650',200,270,2)
# D: Switch + LED
P('esp32-epaper-lib:ToggleSwitch_SPDT','SW1','SW SPDT',255,210,3)
P('Device:LED','D5','Green',255,250,2); P('Device:R','R11','1kΩ',255,240,2)

# Wires
wires_data = [(35,200,60,200),(60,200,60,210),(90,215,120,215),(120,215,120,220),
              (120,220,190,220),(190,220,190,210),(210,210,215,210),(215,210,215,175),
              (140,175,215,175),(40,175,40,20),(40,10,40,20)]

wire_blocks = []
for x1,y1,x2,y2 in wires_data:
    wire_blocks.append(f'''  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )''')

# Global labels
gl_data = [('VBUS',20,195,'input'),('3V3',140,175,'power_out'),('3V3',40,10,'input'),
           ('3V3',175,10,'input'),('VBAT',120,220,'output'),('VBAT',195,200,'input'),
           ('GND',20,180,'input'),('GND',75,180,'input'),('GND',140,180,'input'),('GND',200,180,'input')]
gl_blocks = []
for t,x,y,s in gl_data:
    gl_blocks.append(f'''  (global_label "{t}" (shape {s}) (at {x} {y} 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {uid()})
  )''')

# Local labels
ll_data = [('EPD_CLK',135,65),('EPD_CLK',160,80),('EPD_MOSI',135,70),('EPD_MOSI',160,85),
           ('EPD_CS',135,60),('EPD_CS',160,75),('EPD_DC',135,55),('EPD_DC',160,70),
           ('EPD_RST',135,50),('EPD_RST',160,65),('EPD_BUSY',135,75),('EPD_BUSY',160,90),
           ('DEBUG_SW',15,100),('DEBUG_SW',240,215),('LED',135,80),('LED',245,250)]
ll_blocks = []
for t,x,y in ll_data:
    ll_blocks.append(f'''  (label "{t}" (at {x} {y} 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {uid()})
  )''')

# Text annotations
txt_data = [('A: ESP32-WROOM-32D MCU',20,13),('B: SSD1680 E-Paper Driver + FPC',160,8),
            ('C: Power Management',15,170),('D: Debug Switch + Status LED',240,170)]
txt_blocks = []
for t,x,y in txt_data:
    txt_blocks.append(f'''  (text "{t}" (at {x} {y} 0)
    (effects (font (size 2.54 2.54)) (justify left bottom))
    (uuid {uid()})
  )''')

# symbol_instances
si_lines = []
for iu,ir,val,fp in irefs:
    si_lines.append(f'    (path "/{SCH_UUID}/{iu}" (reference "{ir}") (unit 1) (value "{val}") (footprint "{fp}"))')

# ══════════ Assemble ══════════
sch = f'''(kicad_sch (version 20221206) (generator eeschema)

  (uuid {SCH_UUID})

  (paper "A3" portrait)

  (title_block
    (title "ESP32 E-Paper Badge v1.0")
    (date "2025-05-27")
    (rev "1.0")
    (company "LuckyDog")
    (comment 1 "ESP32-WROOM-32D + SSD1680 + TP4056 + HT7333")
    (comment 2 "2.13\\" Tri-color E-Paper, USB-C Charging")
  )

  (lib_symbols
{chr(10).join(lib_syms)}
  )

{chr(10).join(txt_blocks)}

{chr(10).join(wire_blocks)}

{chr(10).join(gl_blocks)}

{chr(10).join(ll_blocks)}

{chr(10).join(insts)}

  (sheet_instances
    (path "/" (page "1"))
  )

  (symbol_instances
{chr(10).join(si_lines)}
  )
)
'''

path = os.path.join(OUT, 'esp32-epaper.kicad_sch')
with open(path, 'w') as f:
    f.write(sch)
print(f"✓ Schematic saved: {path}")
print(f"  Size: {len(sch)} bytes")
print(f"  Components: {len(insts)}")
print(f"  Wires: {len(wire_blocks)}")
print(f"  Labels: {len(gl_blocks) + len(ll_blocks)}")
