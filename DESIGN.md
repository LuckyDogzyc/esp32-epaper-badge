# ESP32 电子纸显示器 — 硬件设计文档

## 项目概述
- 每日自动唤醒、WiFi连接、更新数据、刷新屏幕、deep sleep
- 拨动开关切调试/正常模式
- USB-C 充电 + USB 直供电 + 103040 软包电池 PH2.0 接口供电
- 2.13" 三色电子纸 (DEPG0213RWS, SSD1680)

## 方案确认
- MCU: ESP32-WROOM-32D (经典款，与用户现有开发板一致)
- 屏幕: DEPG0213RWS (2.13" 黑白红三色, SSD1680驱动)
- 供电: USB-C VBUS / 103040 VBAT → D3/D4 SS14 自动切换 → VCC_RAIL → HT7333 → 3.3V

---

## 1. GPIO 分配表

| 功能       | ESP32 GPIO | 方向   | 说明                |
|-----------|------------|--------|---------------------|
| SPI CLK   | GPIO18     | OUTPUT | VSPI CLK            |
| SPI MOSI  | GPIO23     | OUTPUT | VSPI MOSI           |
| EPD_RST   | GPIO5      | OUTPUT | 屏幕复位             |
| EPD_DC    | GPIO17     | OUTPUT | 数据/命令选择         |
| EPD_CS    | GPIO16     | OUTPUT | SPI 片选             |
| EPD_BUSY  | GPIO4      | INPUT  | 屏幕忙状态            |
| DEBUG_SW  | GPIO2      | INPUT  | LOW=调试模式, HIGH=正常|
| LED       | GPIO19     | OUTPUT | 状态指示灯(刷新时亮)    |
| VBAT_SENSE| GPIO34     | INPUT  | 电池电量 ADC1_CH6       |

## 2. 电路模块

### 模块A: ESP32-WROOM-32 最小系统
来源: ESP32 Hardware Design Guidelines v4.4

组件:
- U1: ESP32-WROOM-32D 模组
- C1: 10μF 0805 (3.3V退耦)
- C2: 100nF 0805 (3.3V高频退耦)
- C3: 10μF 0805 (EN脚滤波)
- R1: 10kΩ 0805 (EN上拉)
- R2: 10kΩ 0805 (IO0上拉)
- R3: 10kΩ 0805 (IO2上拉, 调试开关)

连接:
- VDD (Pin 2) → 3V3
- GND (Pin 1,15,38,39) → GND
- EN (Pin 3) → R1上拉到3V3, C3到GND
- IO0 (Pin 25) → R2上拉到3V3
- IO2 (Pin 24) → R3上拉到3V3, 拨动开关到GND

### 模块B: SSD1680 电子纸驱动电路
来源: 用户提供的墨水屏驱动板v1.3原理图 (已验证可用)

组件:
- U2: SSD1680 (EPD驱动IC)
- L1: 68μH (电荷泵电感, 贴片功率电感)
- Q1: AO3400A (N-MOSFET SOT-23)
- D6, D7, D8: MBR0530 (肖特基二极管 SOD-123)
- R7: 10kΩ 0805
- R8: 0.47Ω (470mΩ) 0805
- C7~C15: 9× 1μF 0805
- C16: 100nF 0805
- C17: 100nF 0805
- C18: 4.7μF 0805
- FPC1: 26P 0.5mm FPC座 (下接或双侧触点)

SSD1680 SPI连接:
- CLK ← GPIO18
- DIN (SDA) ← GPIO23 (MOSI)
- CS ← GPIO16
- DC ← GPIO17
- RST ← GPIO5
- BUSY → GPIO4

### 模块C: TP4056 充电电路
来源: TP4056 Datasheet Rev 1.05 Typical Application

组件:
- U3: TP4056 (SOP-8)
- R4: 1.2kΩ 0805 (PROG, 设定充电电流500mA)
- C4: 10μF 0805 (BAT滤波)
- C5: 10μF 0805 (IN滤波)

连接:
- VCC (Pin 4) ← USB-C 5V (VBUS)
- GND (Pin 3) → GND
- BAT (Pin 5) → VBAT → 103040软包电池正极/J3 pin1
- PROG (Pin 2) → R4到GND
- CHRG (Pin 1) → 悬空或接LED指示
- STDBY (Pin 6) → 悬空或接LED指示
- CE (Pin 8) → VBUS (有USB时自动使能)

### 模块D: DW01A + FS8205A 电池保护电路
来源: DW01A Datasheet Typical Application

组件:
- U4: DW01A (SOT-23-6)
- U5: FS8205A (双N-MOSFET, TSSOP-8)
- R5: 100Ω 0805 (CS电阻)
- C6: 100nF 0805 (滤波)

连接: 标准DW01A+FS8205A参考设计

### 模块E: D3/D4 电源路径切换 + HT7333-1 超低功耗LDO
来源: HT7333 Datasheet

组件:
- U6: HT7333-1 (SOT-89)
- C19: 10μF 0805 (输入滤波)
- C20: 10μF 0805 (输出滤波)

连接:
- VIN ← VCC_RAIL（D3/D4 汇聚后的 USB 或电池输入）
- VOUT → 3V3 系统电源
- GND → GND

电源路径:
- USB-C VBUS → D3(SS14) → VCC_RAIL
- VBAT/J3 pin1 → D4(SS14) → VCC_RAIL
- USB 插入且无电池时，VBUS 经 D3 直接给 HT7333 供电，系统可运行
- USB 拔掉且有电池时，VBAT 经 D4 给 HT7333 供电

### 模块F: USB-C 母座
组件:
- J1: USB-C 16pin 母座 (沉板式)
- R9: 5.1kΩ 0805 (CC1下拉)
- R10: 5.1kΩ 0805 (CC2下拉)

连接:
- VBUS → TP4056 VCC
- CC1 → R9 → GND
- CC2 → R10 → GND
- GND → GND
- D+/D- → 预留给 USB 转串口/调试，如不贴 CH340 可悬空

### 模块H: 103040 电池接口 + 电量检测
组件:
- J3: PH2.0 2pin 电池接口
- R12/R13: 100kΩ/100kΩ 电池分压
- C21: 100nF 滤波

连接:
- J3 pin1 BAT+ → VBAT
- J3 pin2 BAT- → GND
- VBAT → R12 → VBAT_SENSE → R13 → GND
- C21 与 R13 并联到 GND
- VBAT_SENSE → ESP32 GPIO34 (ADC1_CH6)

### 模块G: 调试开关 + 状态LED
组件:
- SW1: 拨动开关 (3pin贴片)
- R11: 1kΩ 0805 (LED限流)
- D5: LED 0805 (绿色)

连接:
- SW1 COM → GND
- SW1 NO → GPIO2
- D5正极 → R11 → GPIO19
- D5负极 → GND

---

## 3. 完整 BOM

| Ref   | 值/型号              | 封装     | 数量 | 参考单价(¥) |
|-------|---------------------|----------|------|------------|
| U1    | ESP32-WROOM-32D     | 模组     | 1    | 7.00       |
| U2    | SSD1680             | QFN-48   | 1    | 1.50       |
| U3    | TP4056              | SOP-8    | 1    | 0.50       |
| U4    | DW01A               | SOT-23-6 | 1    | 0.20       |
| U5    | FS8205A             | TSSOP-8  | 1    | 0.30       |
| U6    | HT7333-1            | SOT-89   | 1    | 0.30       |
| L1    | 68μH                | 4×4mm    | 1    | 0.50       |
| Q1    | AO3400A             | SOT-23   | 1    | 0.15       |
| D5    | LED 0805            | 0805     | 1    | 0.05       |
| D6    | MBR0530             | SOD-123  | 1    | 0.10       |
| D7    | MBR0530             | SOD-123  | 1    | 0.10       |
| D8    | MBR0530             | SOD-123  | 1    | 0.10       |
| C1~C5 | 10μF 0805           | 0805     | 5    | 0.25       |
| C6    | 100nF 0805          | 0805     | 1    | 0.05       |
| C7~C15| 1μF 0805            | 0805     | 9    | 0.45       |
| C16~C17| 100nF 0805         | 0805     | 2    | 0.10       |
| C18   | 4.7μF 0805          | 0805     | 1    | 0.05       |
| C19~C20| 10μF 0805          | 0805     | 2    | 0.10       |
| R1~R3 | 10kΩ 0805           | 0805     | 3    | 0.06       |
| R4    | 1.2kΩ 0805          | 0805     | 1    | 0.02       |
| R5    | 100Ω 0805           | 0805     | 1    | 0.02       |
| R7    | 10kΩ 0805           | 0805     | 1    | 0.02       |
| R8    | 0.47Ω 0805          | 0805     | 1    | 0.05       |
| R9~R10| 5.1kΩ 0805          | 0805     | 2    | 0.04       |
| R11   | 1kΩ 0805            | 0805     | 1    | 0.02       |
| J1    | USB-C 16pin母座     | 沉板式    | 1    | 0.30       |
| FPC1  | 26P 0.5mm FPC座     | 下接     | 1    | 0.50       |
| SW1   | 拨动开关 3pin        | 贴片     | 1    | 0.20       |
| BT1   | 103040软包电池标注   | 外购      | 1    | -          |
| J3    | PH2.0 2P电池接口     | 卧式/贴片 | 1    | 0.10       |
| D3,D4 | SS14肖特基二极管     | SMA       | 2    | 0.10       |
| R12,R13| 100kΩ              | 0402/0805 | 2    | 0.02       |
| C21   | 100nF               | 0402/0805 | 1    | 0.01       |

**BOM总计(不含屏幕电池): ~¥15**
**含屏幕(¥9) + 103040电池(¥12): ~¥36**

---

## 4. 网络连接表 (Netlist)

### 电源网络
- VBUS: USB-C 5V → TP4056 VCC → D3 阳极
- VBAT: TP4056 BAT / DW01A+FS8205A / J3 BAT+ / D4 阳极 / R12 上端
- VCC_RAIL: D3/D4 阴极汇聚 → HT7333 VIN
- 3V3: HT7333 VOUT / ESP32 VDD / SSD1680 VDD / 所有上拉电阻
- GND: 公共地
- VBAT_SENSE: R12/R13 中点 + C21 → ESP32 GPIO34

### SPI 总线
- EPD_CLK:  GPIO18 → SSD1680 CLK → FPC1
- EPD_MOSI: GPIO23 → SSD1680 DIN → FPC1
- EPD_CS:   GPIO16 → SSD1680 CS
- EPD_DC:   GPIO17 → SSD1680 DC
- EPD_RST:  GPIO5  → SSD1680 RST
- EPD_BUSY: GPIO4  ← SSD1680 BUSY

### SSD1680 电荷泵
- GDR:   SSD1680 → L1 → D6/D7/D8 → PREVGH/PREVGL
- RESE:  SSD1680 → R8
- PREVGH: D6/D7 → C10/C11/C12 → SSD1680
- PREVGL: D8 → C13/C14/C15 → SSD1680

### 其他
- DEBUG: GPIO2 ← SW1 (开关到GND)
- LED:   GPIO19 → R11 → D5 → GND
- CC1:   J1 CC1 → R9 → GND
- CC2:   J1 CC2 → R10 → GND

---

## 5. 参考文档
1. ESP32 Hardware Design Guidelines v4.4 — 模组最小系统
2. SSD1680 Datasheet v1.2 — 驱动IC参考设计
3. 墨水屏驱动板 v1.3 原理图 (用户提供, 已验证) — SSD1680外围电路
4. TP4056 Datasheet Rev 1.05 — 充电电路
5. DW01A+FS8205A Datasheet — 电池保护
6. HT7333 Datasheet — LDO

---

## 6. SSD1680 FPC 26P 引脚定义 (DEPG0213RWS)

| Pin | 名称     | 连接到          |
|-----|---------|----------------|
| 1   | GND     | GND            |
| 2   | GND     | GND            |
| 3   | GDR     | Q1 Gate, L1    |
| 4   | GDR     | Q1 Gate, L1    |
| 5   | PREVGL  | D8, C13-C15    |
| 6   | PREVGL  | D8, C13-C15    |
| 7   | PREVGH  | D6-D7, C10-C12 |
| 8   | PREVGH  | D6-D7, C10-C12 |
| 9   | GDR     | Q1 Gate        |
| 10  | GDR     | Q1 Gate        |
| 11  | RESE    | R8             |
| 12  | RESE    | R8             |
| 13  | PREVGH  | D6-D7          |
| 14  | PREVGH  | D6-D7          |
| 15  | PREVGL  | D8             |
| 16  | PREVGL  | D8             |
| 17  | RESE    | R8             |
| 18  | RESE    | R8             |
| 19  | 3V3     | 3V3            |
| 20  | 3V3     | 3V3            |
| 21  | EPD_CLK | SSD1680 CLK   |
| 22  | EPD_DIN | SSD1680 DIN   |
| 23  | EPD_RST | SSD1680 RST   |
| 24  | EPD_DC  | SSD1680 DC    |
| 25  | EPD_CS1 | SSD1680 CS    |
| 26  | EPD_BUSY| SSD1680 BUSY  |

注: 实际引脚顺序以DEPG0213RWS数据手册为准，此处基于常见2.13寸三色屏FPC定义。
