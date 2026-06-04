#!/usr/bin/env python3
"""Generate an interactive HTML visual schematic for review.

Preview is intentionally high-level: it mirrors the v1.1 requirement document and
KiCad component set, while final pin-to-pin electrical verification remains in KiCad.
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

COMPONENT_GROUPS = [
    ("MCU", "U1 ESP32-WROOM-32D", "C1/C2/C3, R1/R2/R3, GPIO34 VBAT_SENSE"),
    ("E-Paper", "U2 SSD1680 + J2 FPC-26P", "L1, Q1, D6-D8, R7/R8, C7-C18"),
    ("USB/Charge", "J1 USB-C + U3 TP4056", "R4, C4/C5, R9/R10 CC pull-down"),
    ("Power Path", "D3/D4 SS14 OR-ing", "VBUS/VBAT -> VCC_RAIL -> U6 HT7333 -> 3V3"),
    ("Battery", "J3 PH2.0 + BT1 103040 LiPo", "R12/R13 100k divider + C21 filter -> GPIO34"),
    ("Protection", "U4 DW01A + U5 FS8205A", "Li-ion overcharge/overdischarge/overcurrent protection"),
    ("User IO", "SW1 Debug switch + D5 LED", "R11 LED limit, DEBUG_SW mode select"),
]

BOM_ROWS = [
    ("U1", "ESP32-WROOM-32D", "Module", "MCU + WiFi/BLE"),
    ("U2", "SSD1680", "QFN", "E-paper driver"),
    ("U3", "TP4056", "SOP-8", "Li-ion charger"),
    ("U4", "DW01A", "SOT-23-6", "Battery protection controller"),
    ("U5", "FS8205A", "TSSOP-8", "Dual N-MOSFET protection switch"),
    ("U6", "HT7333-1", "SOT-89", "Low-Iq 3.3V LDO"),
    ("J1", "USB-C 16P", "SMD", "Charging/power input"),
    ("J2", "FPC-26P", "0.5mm", "E-paper display connector"),
    ("J3", "PH2.0 2P", "Connector", "103040 LiPo battery input"),
    ("BT1", "103040 LiPo", "External", "Battery placeholder/marking"),
    ("D3,D4", "SS14", "SMA", "USB/Battery power-path OR-ing"),
    ("D5", "Green LED", "SMD", "Status indicator"),
    ("D6,D7,D8", "MBR0530", "SOD-123", "SSD1680 charge pump"),
    ("R1-R13", "10k/1.2k/100R/0.47R/5.1k/1k/100k", "SMD", "Pull-up, charge, CC, LED, VBAT sense"),
    ("C1-C21", "10uF/1uF/100nF/4.7uF", "SMD", "Decoupling, charge pump, VBAT filter"),
    ("L1", "68uH", "Power inductor", "SSD1680 charge pump"),
    ("Q1", "AO3400A", "SOT-23", "SSD1680 gate drive"),
    ("SW1", "SPDT switch", "SMD", "Debug/normal mode"),
]

cards = "\n".join(
    f"""<section class=\"card\"><h2>{title}</h2><h3>{main}</h3><p>{detail}</p></section>"""
    for title, main, detail in COMPONENT_GROUPS
)
rows = "\n".join(
    f"<tr><td>{ref}</td><td>{value}</td><td>{pkg}</td><td>{fn}</td></tr>"
    for ref, value, pkg, fn in BOM_ROWS
)

html = f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>ESP32 E-Paper Badge — Schematic v1.1</title>
<style>
  body {{ margin:0; padding:28px; font-family: Inter, 'Microsoft YaHei', Arial, sans-serif; background:#0d1117; color:#e6edf3; }}
  h1 {{ color:#58a6ff; text-align:center; margin-bottom:6px; }}
  .subtitle {{ text-align:center; color:#8b949e; margin-bottom:26px; }}
  .flow {{ max-width:1180px; margin:0 auto 24px; background:#161b22; border:1px solid #30363d; border-radius:14px; padding:18px; }}
  .rail {{ display:flex; align-items:center; justify-content:center; gap:14px; flex-wrap:wrap; font-family:'Courier New', monospace; }}
  .node {{ padding:10px 14px; border-radius:10px; border:1px solid #3b82f6; background:#0b2447; color:#bfdbfe; }}
  .arrow {{ color:#f97316; font-size:24px; }}
  .grid {{ max-width:1180px; margin:0 auto; display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:14px; }}
  .card {{ background:#161b22; border:1px solid #30363d; border-radius:14px; padding:16px; min-height:120px; }}
  .card h2 {{ color:#ff7b72; font-size:15px; margin:0 0 8px; }}
  .card h3 {{ color:#7ee787; font-size:16px; margin:0 0 8px; }}
  .card p {{ color:#8b949e; margin:0; line-height:1.5; }}
  table {{ max-width:1180px; width:100%; margin:26px auto; border-collapse:collapse; background:#161b22; border:1px solid #30363d; }}
  th, td {{ padding:9px 11px; border-bottom:1px solid #30363d; text-align:left; }}
  th {{ color:#58a6ff; background:#0b2447; }}
  .note {{ max-width:1180px; margin:0 auto; color:#f2cc60; background:#332b00; border:1px solid #8a6d00; border-radius:10px; padding:12px; line-height:1.5; }}
</style>
</head>
<body>
<h1>ESP32 E-Paper Badge — Schematic Preview v1.1</h1>
<div class=\"subtitle\">52 components placed | USB-C charging + USB direct power | D3/D4 SS14 power-path OR-ing | 103040 LiPo PH2.0 | VBAT_SENSE</div>

<div class=\"flow\">
  <div class=\"rail\">
    <span class=\"node\">USB-C VBUS 5V</span><span class=\"arrow\">→</span><span class=\"node\">D3 SS14</span>
    <span class=\"arrow\">↘</span><span class=\"node\">VCC_RAIL</span><span class=\"arrow\">→</span><span class=\"node\">HT7333</span><span class=\"arrow\">→</span><span class=\"node\">3V3 System</span>
    <span class=\"node\">103040 VBAT</span><span class=\"arrow\">→</span><span class=\"node\">D4 SS14</span><span class=\"arrow\">↗</span>
  </div>
</div>

<div class=\"grid\">{cards}</div>

<table>
<thead><tr><th>Ref</th><th>Value</th><th>Package</th><th>Function</th></tr></thead>
<tbody>{rows}</tbody>
</table>

<div class=\"note\">注意：该 HTML 是需求/组件/网络意图预览；KiCad 原理图文件已同步到 52 个组件并通过 netlist 导出验证，但最终 PCB 前仍需在 KiCad GUI 中完成全量 pin-to-pin 连线和 ERC/DRC。</div>
</body>
</html>
"""

path = os.path.join(OUT, 'schematic-preview.html')
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"✓ HTML preview saved: {path}")
print(f"  Size: {len(html)} bytes")
