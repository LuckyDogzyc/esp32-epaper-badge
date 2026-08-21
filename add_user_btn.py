#!/usr/bin/env python3
"""Incrementally add the v1.2 next-PCB USER_BTN circuit to the valid KiCad schematic.

Circuit: GPIO33 / USER_BTN_N --+-- SW2 (normally-open tactile) -- GND
                                +-- C22 100nF ------------------ GND
                                +-- R14 10k -------------------- 3V3

GPIO33 is a non-strapping, unused GPIO in the checked-in reference schematic.
EN remains exclusively the ESP32 reset/enable network. This changes the next PCB
reference schematic only; it does not claim to rewire an external prototype.
"""
from pathlib import Path

SCH = Path(__file__).with_name("esp32-epaper.kicad_sch")
text = SCH.read_text(encoding="utf-8")

# Idempotence prevents accidental duplicated symbols/nets.
if 'USER_BTN_N' in text or '(reference "SW2")' in text:
    raise SystemExit('USER_BTN patch already present; refusing to duplicate it')

# Keep generated revision metadata synchronized with the editable schematic.
text = text.replace('(title "ESP32 E-Paper Badge v1.1")', '(title "ESP32 E-Paper Badge v1.2")', 1)
text = text.replace('(rev "1.1")', '(rev "1.2")', 1)
text = text.replace('(date "2026-06-04")', '(date "2026-08-22")', 1)

# Embed the stock two-pin normally-open pushbutton symbol, preserving the existing
# valid lib_symbols section rather than regenerating the schematic.
switch_lib = '''    (symbol "Switch:SW_Push" (pin_numbers hide) (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "SW" (at 1.27 2.54 0)
        (effects (font (size 1.27 1.27)) (justify left))
      )
      (property "Value" "SW_Push" (at 0 -1.524 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 5.08 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "SW_Push_0_1"
        (circle (center -2.032 0) (radius 0.508)
          (stroke (width 0) (type default)) (fill (type none))
        )
        (polyline (pts (xy 0 1.27) (xy 0 3.048))
          (stroke (width 0) (type default)) (fill (type none))
        )
        (polyline (pts (xy 2.54 1.27) (xy -2.54 1.27))
          (stroke (width 0) (type default)) (fill (type none))
        )
        (circle (center 2.032 0) (radius 0.508)
          (stroke (width 0) (type default)) (fill (type none))
        )
        (pin passive line (at -5.08 0 0) (length 2.54)
          (name "1" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 5.08 0 180) (length 2.54)
          (name "2" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
'''
needle = '  )\n\n  (text "F: USB/Battery Power Path - D3/D4 SS14 OR-ing + J3 PH2.0"'
if needle not in text:
    raise SystemExit('lib_symbols insertion point not found')
text = text.replace(needle, switch_lib + needle, 1)

# The ESP32 instance is centered at (75,65); IO33 electrical pin endpoint is
# exactly (96.59,44.68). All USER_BTN wire endpoints deliberately meet pins.
annotations = '''  (text "G: USER_BTN - GPIO33, active-low (NEXT PCB / reference schematic only)" (at 105 60 0)
    (effects (font (size 1.8 1.8)) (justify left bottom))
    (uuid d778e5c0-9d52-43b5-bb13-ae4d29643020)
  )

'''
needle = '  (text "F: USB/Battery Power Path - D3/D4 SS14 OR-ing + J3 PH2.0"'
text = text.replace(needle, annotations + needle, 1)

wires = '''  (wire (pts (xy 96.59 44.68) (xy 120 44.68))
    (stroke (width 0) (type default))
    (uuid 2a9dfb7e-7d0a-453d-a47f-807490a02cdc)
  )
  (wire (pts (xy 120 44.68) (xy 130 44.68))
    (stroke (width 0) (type default))
    (uuid 0f0b87a6-2df5-4d38-bf4d-bfc5f67e13d3)
  )
  (wire (pts (xy 130 44.68) (xy 140.08 44.68))
    (stroke (width 0) (type default))
    (uuid d00b0b74-ae04-41ed-917d-5a80c84f457b)
  )

'''
needle = '  (wire (pts (xy 105 235) (xy 130 235))'
text = text.replace(needle, wires + needle, 1)

labels = '''  (global_label "3V3" (shape input) (at 120 37.06 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid 71f6c376-15cc-49c5-9be6-67f6b33bc1d8)
  )
  (global_label "GND" (shape input) (at 130 52.3 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid 742cc360-1e52-465e-99d9-2b0c1fce5ae3)
  )
  (global_label "GND" (shape input) (at 150.24 44.68 0) (fields_autoplaced)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid 2544dd6c-ed6b-479e-9495-750e079c6e9e)
  )
  (label "USER_BTN_N" (at 105 44.68 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid b2119923-e262-4f4a-9099-773284b4fe53)
  )

'''
needle = '  (global_label "VBUS" (shape input) (at 105 230 0)'
text = text.replace(needle, labels + needle, 1)

instances = '''  (symbol (lib_id "Device:R") (at 120 40.87 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid 0dd9dc0d-8963-4a01-942c-5410becc1dc0)
    (property "Reference" "R14" (at 120 37.06 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "10k" (at 120 44.68 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 120 40.87 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid 25bdb496-f61b-49ca-bb66-7a10652878f1))
    (pin "2" (uuid cf2d64fa-3a3b-4869-bf0d-5ce32c1f4b68))
    (instances
      (project "esp32-epaper"
        (path "/6281fcfa-6553-4706-b287-236232e6465c"
          (reference "R14") (unit 1)
        )
      )
    )
  )
  (symbol (lib_id "Device:C") (at 130 48.49 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid b25f8a6b-1b70-4fde-bf80-dc818a410306)
    (property "Reference" "C22" (at 130 44.68 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "100nF" (at 130 52.3 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 130 48.49 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid e533936d-4779-444d-beba-f4a3191f6e74))
    (pin "2" (uuid 2f7b6aee-ef74-4ff4-8586-a24f2d30b0f2))
    (instances
      (project "esp32-epaper"
        (path "/6281fcfa-6553-4706-b287-236232e6465c"
          (reference "C22") (unit 1)
        )
      )
    )
  )
  (symbol (lib_id "Switch:SW_Push") (at 145.16 44.68 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid 1d5a7f72-ee96-4a89-b7f5-5f4c693fb09e)
    (property "Reference" "SW2" (at 146.43 47.22 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "USER_BTN (NO)" (at 145.16 41.632 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Button_Switch_SMD:SW_SPST_TL3301AN" (at 145.16 44.68 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid 5cc36074-4a43-4e81-b1af-d2c7cd5ddbfe))
    (pin "2" (uuid f9521c83-62d7-4dd9-8c48-03cf442dd7ce))
    (instances
      (project "esp32-epaper"
        (path "/6281fcfa-6553-4706-b287-236232e6465c"
          (reference "SW2") (unit 1)
        )
      )
    )
  )

'''
needle = '  (symbol (lib_id "RF_Module:ESP32-WROOM-32D")'
text = text.replace(needle, instances + needle, 1)

symbol_instances = '''    (path "/6281fcfa-6553-4706-b287-236232e6465c/0dd9dc0d-8963-4a01-942c-5410becc1dc0" (reference "R14") (unit 1) (value "10k") (footprint "Resistor_SMD:R_0603_1608Metric"))
    (path "/6281fcfa-6553-4706-b287-236232e6465c/b25f8a6b-1b70-4fde-bf80-dc818a410306" (reference "C22") (unit 1) (value "100nF") (footprint "Capacitor_SMD:C_0603_1608Metric"))
    (path "/6281fcfa-6553-4706-b287-236232e6465c/1d5a7f72-ee96-4a89-b7f5-5f4c693fb09e" (reference "SW2") (unit 1) (value "USER_BTN (NO)") (footprint "Button_Switch_SMD:SW_SPST_TL3301AN"))
'''
needle = '  )\n)\n'
if text.count(needle) != 1:
    raise SystemExit('symbol_instances insertion point not unique')
text = text.replace(needle, symbol_instances + needle, 1)

SCH.write_text(text, encoding="utf-8")
print(f'Patched {SCH.name}: v1.2 USER_BTN_N on GPIO33 with R14/C22/SW2')
