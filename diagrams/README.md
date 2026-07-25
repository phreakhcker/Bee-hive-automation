# Wiring Diagrams

Four SVG diagrams — open any of them in a web browser, or view them inline on GitHub (SVG renders natively there).

| File | What it shows |
|---|---|
| [`system-overview.svg`](system-overview.svg) | Top-level block diagram: solar → BMS → Pi 5 + Pico → all sensors. Wire-color legend included. Start here. |
| [`pico-wiring.svg`](pico-wiring.svg) | Every pin on the Pi Pico 2 with its wire color, function, and destination sensor. Includes HX711, bee-gate, I²C0/I²C1 sensor buses, DS18B20, and the pack-voltage ADC divider. |
| [`power-system.svg`](power-system.svg) | Solar panel through MPPT, ANL fuse, Daly BMS, 3S4P pack, ATO fuse, and 12→5 V buck to Pi. Fuse ratings and wire gauges called out. |
| [`bee-gate.svg`](bee-gate.svg) | Top view of the 8-tunnel entrance gate showing paired ITR9606 beam sensors, plus a per-sensor schematic and the channel→GPIO map. |

## Wire color convention

Same across all four diagrams (and matches [`../docs/hardware.md`](../docs/hardware.md)):

| Signal | Color |
|---|---|
| +5 V | **Red** |
| +3.3 V | **Orange** |
| GND | **Black** |
| I²C SDA | **Yellow** |
| I²C SCL | **Green** |
| 1-Wire | **Purple** |
| UART / USB data | **Blue** |
| GPIO / interrupt | **White** |
| PWM / clock (HX711 SCK) | **Grey** |
| Analog / ADC | **Brown** |
| I²S / CSI ribbon | **Pink** |

## If you want raster copies (PNG)

The SVGs are the authoritative source. To export to PNG for presentations:

```bash
# Any of these work; pick what you have.
inkscape system-overview.svg --export-type=png --export-dpi=200
rsvg-convert -o system-overview.png system-overview.svg
# Or open in a browser and screenshot.
```

## If you want to redraw / modify

The diagrams are hand-coded SVG (no editor lock-in). Open in any editor (Inkscape, Figma, Illustrator, or a text editor if you're comfortable with SVG XML). The `<style>` block at the top of each file defines the color/font tokens.
