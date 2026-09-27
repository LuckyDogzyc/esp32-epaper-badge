# ESP32 E-Paper Badge

> ⚠️ **当前有效需求为 V2：《[改板需求说明-V2-ESP32C6](改板需求说明-V2-ESP32C6.md)》**（Word 版：`改板需求说明-V2-ESP32C6.docx`）
> V2 要点：主控换 **ESP32-C6-MINI-1-N4**（原生 USB，删除 CH340N/烧录按键/拨动开关）、板 **67×28×0.6mm**（屏区 59.2 + 尾部区 8）、**不设安装孔**、堆叠为"屏朝外 → 电芯 → PCB（元件面朝背面）"、电芯 **≤4mm**、两个**侧按**实体键、电池分压修正到 IO2 + 新增 VBUS 检测、整机总厚 **≈9.1–9.6mm**。
> **本文档以下内容描述的是 V1 版本，仅作对照，冲突处以 V2 为准。**

## 文档索引

| 文件 | 版本 | 用途 |
|------|------|------|
| `改板需求说明-V2-ESP32C6.md` / `.docx` | **V2（当前有效）** | 给设计方的改板制造说明：删除/替换/新增位号、引脚映射、电池与堆叠、侧按键、验收清单 |
| `外包需求文档.md` | V1（历史） | 初版外包需求，V2 未提及处仍沿用其画法与工艺 |

低功耗 ESP32 + 2.13" 三色电子纸显示器，用于每日自动更新数据展示。当前参考原理图版本为 v1.2：已补充 USB-C 直供电、电池自动切换、103040 软包电池 PH2.0 接口、电池电量检测，以及独立的 USER_BTN 用户按键。**本版本仅用于下一版 PCB/reference schematic；现有外部原型 GPIO 映射不同，不能据此改线或直接刷写。**

## 硬件方案

| 模块 | 方案 | 说明 |
|------|------|------|
| MCU | ESP32-WROOM-32D | WiFi + BLE，deep sleep 10µA |
| 屏幕 | DEPG0213RWS 2.13" | 三色(黑白红)，SSD1680 驱动 |
| 充电/直供电 | TP4056 + D3/D4 SS14 | USB-C 充电，支持无电池 USB 直供电 |
| 保护 | DW01A + FS8205A | 过充/过放/过流保护 |
| LDO | HT7333-1 | 超低 Iq=1µA |
| 电池 | 103040 软包锂电池 PH2.0 | 1200mAh，外接插头，deep sleep 续航目标 >1 年 |

## 电路模块

1. **ESP32 最小系统** — 抄 Espressif 官方设计指南 v4.4
2. **SSD1680 驱动电路** — 抄已验证驱动板 v1.3 原理图
3. **TP4056 充电 + D3/D4 电源路径切换** — USB-C VBUS 与 VBAT 通过 SS14 汇聚到 VCC_RAIL
4. **DW01A+FS8205A 保护** — 抄数据手册参考设计
5. **HT7333 LDO** — VCC_RAIL 转 3.3V 系统电源
6. **VBAT_SENSE 电量检测** — R12/R13 100k 分压 + C21 100nF 滤波 → GPIO34
7. **USER_BTN 独立用户按键** — SW2 常开按键把 `USER_BTN_N` 拉低；R14 10k 外部上拉至 3V3，C22 100nF 去抖；连接 GPIO33，绝不接 ESP32 EN/RST

## GPIO 分配

| GPIO | 功能 | 目标 |
|------|------|------|
| 18 | SPI CLK | SSD1680.CLK |
| 23 | SPI MOSI | SSD1680.DIN |
| 5 | Reset | SSD1680.RST |
| 17 | D/C | SSD1680.DC |
| 16 | CS | SSD1680.CS |
| 4 | Busy | SSD1680.BUSY |
| 2 | Debug Switch | SW1 (LOW=调试) |
| 19 | LED | D5 状态指示 |
| 33 | USER_BTN | `USER_BTN_N`，独立 active-low 用户按键（短按状态；按住 ≥5 秒网络配网） |
| 34 | ADC | VBAT_SENSE 电池电量检测 |

### USER_BTN firmware contract (next PCB)

- Configure GPIO33 as an input; `USER_BTN_N` is **active-low** and has the fitted external R14 10k pull-up, so firmware must not rely on an internal pull-up.
- Apply a ≥20 ms software debounce; on a debounced press/release shorter than 5 seconds, show the device status.
- On a continuous debounced low level of **at least 5 seconds**, enter/keep awake for network provisioning. It is not a reset action.
- ESP32 EN/RST remains the normal reset/enable circuit only; do not connect USER_BTN firmware or PCB wiring to EN.

## 文件说明

| 文件 | 说明 |
|------|------|
| `esp32-epaper.kicad_pro` | KiCad 7 项目文件 |
| `esp32-epaper.kicad_sch` | v1.2 下一版 PCB 参考原理图，55 个组件已放置（含 GPIO33 USER_BTN） |
| `esp32-epaper-lib.kicad_sym` | 自定义符号库 |
| `DESIGN.md` | 完整设计文档 (BOM/网络表/引脚定义) |
| `schematic-preview.html` | 浏览器可查看的可视化原理图 |
| `gen_symbols.py` | 符号库生成脚本 (kiutils) |
| `gen_schematic.py` | 原理图生成脚本 (kiutils) |

## 使用方法

1. 安装 [KiCad 7+](https://www.kicad.org/)
2. 打开 `esp32-epaper.kicad_pro`
3. 运行 ERC 检查
4. 审查所有连线，重点检查 D3/D4 电源路径、J3 电池接口和 VBAT_SENSE
5. 分配封装 (footprints)
6. 进入 PCB 布局


## 设计原则

- 每块电路抄原厂参考设计，不发明电路
- 所有被动件值严格遵循数据手册
- HT7333 (Iq=1µA) 是续航关键，不用 AMS1117 (Iq=5mA)
- SSD1680 外围电路完全复制已验证的驱动板 v1.3
