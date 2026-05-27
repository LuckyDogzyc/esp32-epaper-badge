#!/usr/bin/env python3
"""Generate an interactive HTML visual schematic for review."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ESP32 E-Paper Badge — Schematic v1.0</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { 
    font-family: 'Courier New', monospace; 
    background: #1a1a2e; 
    color: #e0e0e0;
    padding: 20px;
  }
  h1 { text-align: center; color: #00d4ff; font-size: 24px; margin-bottom: 5px; }
  h2 { color: #00d4ff; font-size: 14px; margin-bottom: 3px; border-bottom: 1px solid #333; padding-bottom: 3px; }
  .subtitle { text-align: center; color: #888; font-size: 12px; margin-bottom: 20px; }
  
  .schematic { 
    position: relative; 
    width: 1100px; height: 800px; 
    margin: 0 auto;
    background: #0d1117;
    border: 2px solid #333;
    border-radius: 8px;
  }
  
  .section {
    position: absolute;
    border: 1px dashed #444;
    border-radius: 6px;
    padding: 8px;
  }
  .section-title {
    color: #ff6b6b;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 6px;
  }
  
  .ic {
    background: #16213e;
    border: 2px solid #4a90d9;
    border-radius: 4px;
    padding: 8px;
    text-align: center;
    position: absolute;
    min-width: 120px;
  }
  .ic .ref { color: #ff6b6b; font-size: 11px; }
  .ic .name { color: #4a90d9; font-size: 12px; font-weight: bold; }
  .ic .pins { color: #888; font-size: 9px; margin-top: 4px; }
  
  .passive {
    background: #1a1a2e;
    border: 1px solid #666;
    border-radius: 3px;
    padding: 3px 6px;
    text-align: center;
    position: absolute;
    font-size: 10px;
  }
  
  .power-label {
    color: #ff4444;
    font-size: 10px;
    font-weight: bold;
    position: absolute;
  }
  .net-label {
    color: #00ff88;
    font-size: 9px;
    position: absolute;
  }
  
  .wire {
    position: absolute;
    background: #666;
  }
  .wire.h { height: 1px; }
  .wire.v { width: 1px; }
  
  .connector {
    background: #2d1b4e;
    border: 2px solid #9b59b6;
    border-radius: 4px;
    padding: 6px;
    text-align: center;
    position: absolute;
  }

  .info-box {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: #16213e;
    border: 1px solid #4a90d9;
    border-radius: 4px;
    padding: 10px;
    font-size: 10px;
    max-width: 250px;
  }
  .info-box h3 { color: #4a90d9; font-size: 11px; margin-bottom: 5px; }
  .info-box p { color: #888; margin: 2px 0; }

  /* Power flow arrows */
  .flow-arrow {
    color: #ff4444;
    font-size: 16px;
    position: absolute;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    font-size: 11px;
  }
  th { background: #16213e; color: #4a90d9; padding: 6px; text-align: left; }
  td { padding: 4px 6px; border-bottom: 1px solid #333; }
  tr:hover { background: #1e2a3a; }
</style>
</head>
<body>

<h1>⚡ ESP32 E-Paper Badge — Schematic v1.0</h1>
<div class="subtitle">ESP32-WROOM-32D + SSD1680 + TP4056 + DW01A + HT7333 | 2.13" Tri-color E-Paper | USB-C Charging</div>

<div class="schematic">

  <!-- Section A: ESP32 MCU -->
  <div class="section" style="left:15px; top:15px; width:440px; height:280px;">
    <div class="section-title">A: ESP32-WROOM-32D MCU</div>
    
    <div class="ic" style="left:120px; top:40px; width:200px; height:180px;">
      <div class="ref">U1</div>
      <div class="name">ESP32-WROOM-32D</div>
      <div class="pins" style="text-align:left;">
        <div>IO23 (MOSI) → EPD_DIN</div>
        <div>IO18 (CLK) → EPD_CLK</div>
        <div>IO5 → EPD_RST</div>
        <div>IO17 → EPD_DC</div>
        <div>IO16 → EPD_CS</div>
        <div>IO4 ← EPD_BUSY</div>
        <div>IO2 ← DEBUG_SW</div>
        <div>IO19 → LED</div>
        <div>EN ← R1(10k) → 3V3</div>
        <div>3V3 / GND</div>
      </div>
    </div>
    
    <div class="passive" style="left:10px; top:50px;">C1 10µF</div>
    <div class="passive" style="left:10px; top:75px;">C2 100nF</div>
    <div class="passive" style="left:345px; top:50px;">C3 10µF</div>
    <div class="passive" style="left:345px; top:75px;">R1 10kΩ</div>
    <div class="passive" style="left:345px; top:100px;">R2 10kΩ</div>
    <div class="passive" style="left:10px; top:230px;">R3 10kΩ</div>
    
    <div class="power-label" style="left:10px; top:35px;">3V3 ━</div>
    <div class="power-label" style="left:10px; top:220px;">GND ━</div>
  </div>

  <!-- Section B: SSD1680 + FPC -->
  <div class="section" style="left:475px; top:15px; width:600px; height:360px;">
    <div class="section-title">B: SSD1680 E-Paper Driver + FPC Display Connector</div>
    
    <div class="ic" style="left:15px; top:40px; width:180px; height:230px;">
      <div class="ref">U2</div>
      <div class="name">SSD1680</div>
      <div class="pins" style="text-align:left;">
        <div>VDD → 3V3</div>
        <div>VSS → GND</div>
        <div>BS → GND (SPI mode)</div>
        <div>CLK ← EPD_CLK</div>
        <div>DIN ← EPD_MOSI</div>
        <div>DC ← EPD_DC</div>
        <div>CS ← EPD_CS</div>
        <div>RST ← EPD_RST</div>
        <div>BUSY → EPD_BUSY</div>
        <div style="color:#ff6b6b;">GDR → L1 → Q1</div>
        <div style="color:#ff6b6b;">RESE → R8(0.47Ω)</div>
        <div style="color:#ff6b6b;">PREVGH → charge pump</div>
        <div style="color:#ff6b6b;">PREVGL → charge pump</div>
      </div>
    </div>
    
    <div class="connector" style="left:260px; top:40px; width:160px; height:230px;">
      <div class="ref" style="color:#9b59b6;">J2</div>
      <div class="name" style="color:#9b59b6;">FPC-26P 0.5mm</div>
      <div class="pins" style="text-align:left; color:#888;">
        <div>1-2: GND</div>
        <div>3-4,9-10: GDR</div>
        <div>5-6,15-16: PREVGL</div>
        <div>7-8,13-14: PREVGH</div>
        <div>11-12,17-18: RESE</div>
        <div>19-20: VDD (3V3)</div>
        <div>21: CLK</div>
        <div>22: DIN</div>
        <div>23: RST</div>
        <div>24: DC</div>
        <div>25: CS</div>
        <div>26: BUSY</div>
      </div>
    </div>
    
    <div class="passive" style="left:440px; top:50px;">L1 68µH</div>
    <div class="passive" style="left:440px; top:75px;">Q1 AO3400A</div>
    <div class="passive" style="left:500px; top:50px;">D6 MBR0530</div>
    <div class="passive" style="left:500px; top:75px;">D7 MBR0530</div>
    <div class="passive" style="left:500px; top:100px;">D8 MBR0530</div>
    <div class="passive" style="left:440px; top:110px;">R7 10kΩ</div>
    <div class="passive" style="left:440px; top:135px;">R8 0.47Ω</div>
    
    <div style="position:absolute; left:15px; top:285px; font-size:9px; color:#666;">
      C7-C15: 9× 1µF (charge pump caps) | C16,C17: 100nF | C18: 4.7µF
    </div>
  </div>

  <!-- Section C: Power -->
  <div class="section" style="left:15px; top:320px; width:700px; height:250px;">
    <div class="section-title">C: Power — USB-C → TP4056 → DW01A+FS8205A → HT7333 → 3V3</div>
    
    <!-- Power flow: USB-C → TP4056 → Battery → DW01A → HT7333 → 3V3 -->
    
    <div class="connector" style="left:10px; top:40px; width:90px; height:100px;">
      <div class="ref" style="color:#9b59b6;">J1</div>
      <div class="name" style="color:#9b59b6;">USB-C</div>
      <div class="pins">VBUS=5V<br>CC1→R9<br>CC2→R10<br>GND</div>
    </div>
    
    <div class="flow-arrow" style="left:105px; top:80px;">→</div>
    
    <div class="ic" style="left:120px; top:40px; width:110px; height:100px;">
      <div class="ref">U3</div>
      <div class="name">TP4056</div>
      <div class="pins" style="font-size:8px;">
        <div>VCC ← VBUS</div>
        <div>PROG → R4(1.2k)</div>
        <div>GND</div>
        <div>BAT → VBAT</div>
        <div>CE → VBUS</div>
      </div>
    </div>
    
    <div class="passive" style="left:120px; top:150px;">R4 1.2kΩ (500mA)</div>
    <div class="passive" style="left:120px; top:170px;">C4,C5: 10µF</div>
    <div class="passive" style="left:10px; top:150px;">R9 5.1kΩ</div>
    <div class="passive" style="left:10px; top:170px;">R10 5.1kΩ</div>
    
    <div class="flow-arrow" style="left:240px; top:80px;">→</div>
    
    <div class="ic" style="left:260px; top:40px; width:100px; height:60px;">
      <div class="ref">U4</div>
      <div class="name">DW01A</div>
      <div class="pins" style="font-size:8px;">CS,OD,OC,TD,VCC,GND</div>
    </div>
    
    <div class="ic" style="left:260px; top:120px; width:100px; height:50px;">
      <div class="ref">U5</div>
      <div class="name">FS8205A</div>
      <div class="pins" style="font-size:8px;">S1,G1,S2,G2,D1,D2</div>
    </div>
    
    <div class="passive" style="left:370px; top:60px;">R5 100Ω</div>
    <div class="passive" style="left:370px; top:80px;">C6 100nF</div>
    
    <div class="flow-arrow" style="left:375px; top:160px;">→ VBAT →</div>
    
    <div class="ic" style="left:450px; top:40px; width:100px; height:60px;">
      <div class="ref">U6</div>
      <div class="name">HT7333-1</div>
      <div class="pins" style="font-size:8px;">VIN ← VBAT<br>VOUT → 3V3<br>GND</div>
    </div>
    
    <div class="passive" style="left:450px; top:110px;">C19 10µF</div>
    <div class="passive" style="left:520px; top:110px;">C20 10µF</div>
    
    <div class="flow-arrow" style="left:555px; top:60px;">→ 3V3</div>
    
    <div class="connector" style="left:450px; top:150px; width:80px; height:40px;">
      <div class="ref" style="color:#9b59b6;">BT1</div>
      <div class="name" style="color:#9b59b6; font-size:10px;">18650</div>
    </div>
    
    <div style="position:absolute; left:10px; top:220px; font-size:9px; color:#666;">
      VBUS(5V) → TP4056 → VBAT(3.0-4.2V) → DW01A保护 → HT7333(3.3V) → 系统供电
    </div>
  </div>

  <!-- Section D: Switch + LED -->
  <div class="section" style="left:735px; top:320px; width:340px; height:250px;">
    <div class="section-title">D: Debug Switch + Status LED</div>
    
    <div class="ic" style="left:15px; top:40px; width:120px; height:60px;">
      <div class="ref">SW1</div>
      <div class="name">Toggle SW</div>
      <div class="pins" style="font-size:8px;">COM→GND, NO→IO2, NC</div>
    </div>
    
    <div class="passive" style="left:160px; top:55px;">R3 10kΩ (IO2上拉)</div>
    
    <div style="position:absolute; left:15px; top:120px; font-size:9px; color:#888;">
      <div>LOW (GND) = 调试模式 (WiFi常开)</div>
      <div>HIGH (10k上拉) = 正常模式 (24h sleep)</div>
    </div>
    
    <div class="passive" style="left:15px; top:170px;">R11 1kΩ</div>
    <div class="passive" style="left:80px; top:170px;">D5 LED Green</div>
    <div style="position:absolute; left:15px; top:195px; font-size:9px; color:#888;">
      GPIO19 → R11 → LED → GND (刷新时亮)
    </div>
  </div>

  <!-- Net connections legend -->
  <div class="info-box">
    <h3>📋 SPI Bus (ESP32 ↔ SSD1680)</h3>
    <p>EPD_CLK: GPIO18 → CLK</p>
    <p>EPD_MOSI: GPIO23 → DIN</p>
    <p>EPD_CS: GPIO16 → CS</p>
    <p>EPD_DC: GPIO17 → DC</p>
    <p>EPD_RST: GPIO5 → RST</p>
    <p>EPD_BUSY: GPIO4 ← BUSY</p>
    <hr style="border-color:#333; margin:5px 0;">
    <h3>📋 Power Nets</h3>
    <p style="color:#ff4444;">VBUS: USB 5V</p>
    <p style="color:#ff8800;">VBAT: Battery 3.0-4.2V</p>
    <p style="color:#00ff88;">3V3: System 3.3V</p>
    <p style="color:#888;">GND: Common Ground</p>
    <hr style="border-color:#333; margin:5px 0;">
    <p style="color:#888;">Source refs:</p>
    <p style="color:#666;">• ESP32 HWDG v4.4</p>
    <p style="color:#666;">• SSD1680 DS v1.2</p>
    <p style="color:#666;">• Driver Board v1.3</p>
    <p style="color:#666;">• TP4056 DS Rev 1.05</p>
  </div>

</div>

<h2 style="margin-top:30px;">📊 Complete BOM</h2>
<table>
  <tr><th>Ref</th><th>Value</th><th>Package</th><th>Function</th><th>Source</th></tr>
  <tr><td>U1</td><td>ESP32-WROOM-32D</td><td>Module</td><td>MCU + WiFi</td><td>Espressif</td></tr>
  <tr><td>U2</td><td>SSD1680</td><td>QFN-48</td><td>E-Paper Driver IC</td><td>SSD1680 DS v1.2</td></tr>
  <tr><td>U3</td><td>TP4056</td><td>SOP-8</td><td>Li-Ion Charger (500mA)</td><td>TP4056 DS</td></tr>
  <tr><td>U4</td><td>DW01A</td><td>SOT-23-6</td><td>Battery Protection</td><td>DW01A DS</td></tr>
  <tr><td>U5</td><td>FS8205A</td><td>TSSOP-8</td><td>Dual N-MOSFET</td><td>FS8205A DS</td></tr>
  <tr><td>U6</td><td>HT7333-1</td><td>SOT-89</td><td>LDO (Iq=1µA)</td><td>HT7333 DS</td></tr>
  <tr><td>Q1</td><td>AO3400A</td><td>SOT-23</td><td>N-MOSFET (gate drive)</td><td>Driver Board v1.3</td></tr>
  <tr><td>D5</td><td>LED Green</td><td>0805</td><td>Status indicator</td><td>-</td></tr>
  <tr><td>D6,D7,D8</td><td>MBR0530</td><td>SOD-123</td><td>Charge pump diodes</td><td>Driver Board v1.3</td></tr>
  <tr><td>L1</td><td>68µH</td><td>4×4mm</td><td>Charge pump inductor</td><td>Driver Board v1.3</td></tr>
  <tr><td>R1,R2,R3</td><td>10kΩ</td><td>0805</td><td>Pull-ups (EN, IO0, IO2)</td><td>ESP32 HWDG</td></tr>
  <tr><td>R4</td><td>1.2kΩ</td><td>0805</td><td>PROG (500mA charge)</td><td>TP4056 DS</td></tr>
  <tr><td>R5</td><td>100Ω</td><td>0805</td><td>DW01A CS resistor</td><td>DW01A DS</td></tr>
  <tr><td>R7</td><td>10kΩ</td><td>0805</td><td>SSD1680 pull-down</td><td>Driver Board v1.3</td></tr>
  <tr><td>R8</td><td>0.47Ω</td><td>0805</td><td>SSD1680 current sense</td><td>Driver Board v1.3</td></tr>
  <tr><td>R9,R10</td><td>5.1kΩ</td><td>0805</td><td>USB-C CC pull-down</td><td>USB-C Spec</td></tr>
  <tr><td>R11</td><td>1kΩ</td><td>0805</td><td>LED current limit</td><td>-</td></tr>
  <tr><td>C1,C3,C4,C5,C19,C20</td><td>10µF</td><td>0805</td><td>Power decoupling</td><td>-</td></tr>
  <tr><td>C2,C6,C16,C17</td><td>100nF</td><td>0805</td><td>HF decoupling</td><td>-</td></tr>
  <tr><td>C7-C15</td><td>1µF ×9</td><td>0805</td><td>SSD1680 charge pump</td><td>Driver Board v1.3</td></tr>
  <tr><td>C18</td><td>4.7µF</td><td>0805</td><td>SSD1680 bulk cap</td><td>Driver Board v1.3</td></tr>
  <tr><td>J1</td><td>USB-C 16P</td><td>SMD</td><td>Charging port</td><td>USB-C Spec</td></tr>
  <tr><td>J2</td><td>FPC-26P 0.5mm</td><td>SMD</td><td>E-Paper display connector</td><td>DEPG0213RWS DS</td></tr>
  <tr><td>SW1</td><td>Toggle SPDT</td><td>SMD</td><td>Debug/Normal switch</td><td>-</td></tr>
  <tr><td>BT1</td><td>18650 holder</td><td>Through-hole</td><td>Battery holder</td><td>-</td></tr>
</table>

<h2 style="margin-top:20px;">📋 GPIO Pin Map</h2>
<table>
  <tr><th>GPIO</th><th>Function</th><th>Direction</th><th>Target</th></tr>
  <tr><td>GPIO18</td><td>SPI CLK (VSPI)</td><td>OUT</td><td>SSD1680.CLK / FPC.21</td></tr>
  <tr><td>GPIO23</td><td>SPI MOSI (VSPI)</td><td>OUT</td><td>SSD1680.DIN / FPC.22</td></tr>
  <tr><td>GPIO5</td><td>E-Paper Reset</td><td>OUT</td><td>SSD1680.RST / FPC.23</td></tr>
  <tr><td>GPIO17</td><td>Data/Command</td><td>OUT</td><td>SSD1680.DC / FPC.24</td></tr>
  <tr><td>GPIO16</td><td>SPI Chip Select</td><td>OUT</td><td>SSD1680.CS / FPC.25</td></tr>
  <tr><td>GPIO4</td><td>Busy Status</td><td>IN</td><td>SSD1680.BUSY / FPC.26</td></tr>
  <tr><td>GPIO2</td><td>Debug Switch</td><td>IN</td><td>SW1.NO (LOW=debug)</td></tr>
  <tr><td>GPIO19</td><td>Status LED</td><td>OUT</td><td>R11 → D5 → GND</td></tr>
</table>

<div style="text-align:center; margin-top:20px; color:#666; font-size:10px;">
  ESP32 E-Paper Badge v1.0 | Generated 2025-05-27 | KiCad 7 Format | 
  Open esp32-epaper.kicad_pro in KiCad to edit and run ERC
</div>

</body>
</html>
"""

path = os.path.join(OUT, 'schematic-preview.html')
with open(path, 'w') as f:
    f.write(html)
print(f"✓ HTML preview saved: {path}")
print(f"  Size: {len(html)} bytes")
