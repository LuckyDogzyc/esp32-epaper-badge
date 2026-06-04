# ESP32 E-Paper Badge

低功耗 ESP32 + 2.13" 三色电子纸显示器，用于每日自动更新数据展示。当前版本为 v1.1，已按外包需求补充 USB-C 直供电、电池自动切换、103040 软包电池 PH2.0 接口和电池电量检测。

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
| 34 | ADC | VBAT_SENSE 电池电量检测 |

## 文件说明

| 文件 | 说明 |
|------|------|
| `esp32-epaper.kicad_pro` | KiCad 7 项目文件 |
| `esp32-epaper.kicad_sch` | 原理图，52 个组件已放置 |
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

## 成本估算

- **不含屏幕/电池**: ~¥15
- **含屏幕(¥9) + 103040 电池(¥12)**: ~¥36/台
- 打样 5 片 PCB: ~¥15 (嘉立创)

## 设计原则

- 每块电路抄原厂参考设计，不发明电路
- 所有被动件值严格遵循数据手册
- HT7333 (Iq=1µA) 是续航关键，不用 AMS1117 (Iq=5mA)
- SSD1680 外围电路完全复制已验证的驱动板 v1.3
