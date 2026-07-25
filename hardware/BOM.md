# Bill of Materials

All prices approximate (USD, late-2026 street prices). Every item has 2–3 purchase links: Amazon search, AliExpress search, and a **manufacturer / specialty reseller** link where it exists. Direct-link products (Adafruit #, Pololu, DigiKey part pages, Renogy, Hydreon, etc.) have been verified live at the time of writing.

## Reading the links

- **Direct** links point to specific verified product pages (checked live).
- **Amazon / AliExpress** links are stable **search URLs** — they land you on a current list of matching items so you can pick a listing with good reviews and the current price. Marketplace product listings rot too fast to hard-code.
- Some items should **not** be bought from marketplaces at all (Victron, Hydreon, Sensirion sensors) — the counterfeit rate is too high. Those items link only to authorized sources.

## Counterfeit warnings — read once

| Item | Risk | What to do |
|---|---|---|
| **Raspberry Pi 5 / Camera 3 / official PSU** | AliExpress commonly ships grey-market or clones with fake serials | Buy from [Approved Resellers](https://www.raspberrypi.com/resellers/) only (Adafruit, PiShop, CanaKit, DigiKey) |
| **SanDisk microSD** | AliExpress counterfeit rate on flash is notorious | Amazon "sold and shipped by Amazon.com" or WD direct |
| **BME280 breakout** | Cheap "GY-BME280" boards on AliExpress frequently ship with BMP280 (no humidity) | Buy Adafruit or SparkFun |
| **SCD41 breakout** | AliExpress "SCD41" often ships SCD40 (less accurate, no low-power mode) | Buy Adafruit or Sensirion via DigiKey |
| **Victron SmartSolar MPPT** | Documented AliExpress counterfeits since 2019 — fake Bluetooth, no protections | Authorized US dealers only |
| **Opus BT-C3100** | Many clones with ±15 % capacity errors | US Amazon seller with hundreds of recent reviews, or specialty battery retailer |
| **"Pure nickel" strip** | Often nickel-plated steel (4× the resistance) | Magnet test on arrival; pure nickel is only weakly magnetic |
| **Silicone wire** | Often copper-clad aluminum (CCA) with silicone-flavored PVC | BNTECHGO brand on Amazon; feel for high-strand-count soft insulation |
| **MG Chemicals 419D** | Amazon third-party 419D often diluted / dead propellant | DigiKey, Mouser, or MG Chemicals direct |
| **Cable glands** | Cheap PG glands often have wrong metric threads | Heyco / Sealcon via McMaster if IP66 matters |

---

## Compute

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **Raspberry Pi 5 (4 GB)** — Pi 4 works if you already have one | 1 | $60 | [Direct (approved resellers)](https://www.raspberrypi.com/products/raspberry-pi-5/) · [Amazon](https://www.amazon.com/s?k=raspberry+pi+5+4gb) · avoid AliExpress |
| **Official Pi 5 27 W USB-C PSU** (bench setup only) | 1 | $12 | [Direct](https://www.raspberrypi.com/products/27w-power-supply/) · [Amazon](https://www.amazon.com/s?k=raspberry+pi+5+27w+usb-c+power+supply+official) |
| **SanDisk High Endurance 64 GB microSD** — endurance grade | 1 | $12 | [Amazon (SanDisk only)](https://www.amazon.com/s?k=sandisk+high+endurance+microsd+64gb) · avoid AliExpress |
| **Raspberry Pi Pico 2 (RP2350)** | 1 | $6.25 | [Adafruit #6006](https://www.adafruit.com/product/6006) · [Direct](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) · [Amazon](https://www.amazon.com/s?k=raspberry+pi+pico+2+rp2350) |
| **Hailo-8L HAT** (optional — multi-stream ML acceleration) | 1 | $70 | [Approved resellers via Pi](https://www.raspberrypi.com/products/ai-hat/) · [Amazon](https://www.amazon.com/s?k=raspberry+pi+ai+hat+hailo-8l) |

## Sensors — I²C / 1-Wire

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **4× 50 kg load cell + HX711 kit** (Wheatstone-bridge assembly) | 1 | $10 | [SparkFun HX711 #13879](https://www.sparkfun.com/products/13879) (breakout) · [Amazon (full kit)](https://www.amazon.com/s?k=4x+50kg+load+cell+HX711+kit) · [AliExpress](https://www.aliexpress.us/w/wholesale-4x+50kg+load+cell+hx711.html) |
| **DS18B20 waterproof stainless probe, 1 m** | 4 | $10 ea | [Adafruit #381](https://www.adafruit.com/product/381) · [Amazon multipack](https://www.amazon.com/s?k=DS18B20+waterproof+probe+1m) · [AliExpress](https://www.aliexpress.us/w/wholesale-ds18b20+waterproof+probe+1m.html) |
| **4.7 kΩ 1/4 W resistor** (1-Wire pull-up) | 1 | — | Included in resistor kit below |
| **Sensirion SHT41 / SHT45 breakout** — outside weather | 1 | $12.50 | [Adafruit #5665 (now SHT45)](https://www.adafruit.com/product/5665) · [Amazon](https://www.amazon.com/s?k=adafruit+sht41+breakout) · [AliExpress](https://www.aliexpress.us/w/wholesale-SHT41+breakout.html) |
| **Sensirion SHT31-DIS-F w/ PTFE membrane** — hive interior (propolis-resistant) | 1 | $14 | [DigiKey](https://www.digikey.com/en/products/detail/sensirion-ag/SHT31-DIS-F2-5KS/6194392) · [Adafruit SHT31](https://www.adafruit.com/product/2857) |
| **Bosch BME280 breakout** — outdoor T/RH/pressure | 1 | $14.95 | [Adafruit #2652](https://www.adafruit.com/product/2652) · [Amazon (Adafruit/SparkFun only)](https://www.amazon.com/s?k=bme280+breakout+adafruit) · avoid GY-BME280 clones |
| **Vishay VEML7700 lux breakout** | 1 | $4.95 | [Adafruit #4162](https://www.adafruit.com/product/4162) · [Amazon](https://www.amazon.com/s?k=veml7700+lux+breakout) · [AliExpress](https://www.aliexpress.us/w/wholesale-veml7700+breakout.html) |
| **Sensirion SCD41 CO₂ breakout** (optional) | 1 | $49.95 | [Adafruit #5190](https://www.adafruit.com/product/5190) · [DigiKey SCD41](https://www.digikey.com/en/products/detail/sensirion-ag/SCD41-D-R2/13684498) · avoid AliExpress "SCD41" |
| **Sensirion SGP40 VOC breakout** (optional) | 1 | $14.95 | [Adafruit #4829](https://www.adafruit.com/product/4829) · [Amazon](https://www.amazon.com/s?k=sgp40+voc+breakout+adafruit) |
| **MCP23017 I²C GPIO expander** (only if GPIO count runs short) | 1 | $5 | [Adafruit #5346](https://www.adafruit.com/product/5346) · [Amazon](https://www.amazon.com/s?k=MCP23017+I2C+GPIO+expander+breakout) · [AliExpress](https://www.aliexpress.us/w/wholesale-MCP23017+breakout.html) |

## Sensors — cameras, audio, entrance

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **Raspberry Pi Camera Module 3** (standard, autofocus) — entrance | 1 | $29.25 | [Adafruit #5657](https://www.adafruit.com/product/5657) · [Direct](https://www.raspberrypi.com/products/camera-module-3/) · [Amazon (approved resellers)](https://www.amazon.com/s?k=raspberry+pi+camera+module+3) |
| **Raspberry Pi Camera Module 3 NoIR** — inside hive | 1 | $29+ | [Adafruit #5659](https://www.adafruit.com/product/5659) · [Direct](https://www.raspberrypi.com/products/camera-module-3/) |
| **CSI 22-pin (mini) camera cable for Pi 5** — standard-to-mini | 2 | $5 ea | [Direct — Pi camera cable](https://www.raspberrypi.com/products/camera-cable/) · [Amazon](https://www.amazon.com/s?k=raspberry+pi+5+camera+cable+15+to+22+pin) |
| **Adafruit SPH0645LM4H I²S MEMS mic breakout** | 1 | $6.95 | [Adafruit #3421](https://www.adafruit.com/product/3421) · [Amazon](https://www.amazon.com/s?k=SPH0645LM4H+I2S+microphone+breakout) · [AliExpress](https://www.aliexpress.us/w/wholesale-SPH0645LM4H+i2s+mic.html) |
| **850 nm IR LED strip, 5 m, 12 V** — inside-hive illumination | 0.5 m | $10 (reel) | [Amazon "850nm IR LED strip"](https://www.amazon.com/s?k=850nm+infrared+led+strip+5m+12v) · [AliExpress](https://www.aliexpress.us/w/wholesale-850nm+ir+led+strip+5m+12v.html) — verify **850 nm not 940 nm** |
| **Everlight ITR9606-F slotted opto-interrupter** — bee gate | 16 | $0.65 ea | [DigiKey ITR9606-F](https://www.digikey.com/en/products/detail/everlight-electronics-co-ltd/ITR9606-F/2693864) · [Mouser](https://www.mouser.com/c/?q=ITR9606) · avoid AliExpress unbranded knockoffs |
| **Hydreon RG-9 optical rain sensor** | 1 | $49 | [Direct — rainsensors.com](https://rainsensors.com/products/rg-9/) — genuine only |
| **FT232RL / CH340 USB-serial breakout** — for RG-9 (or use Pi UART instead) | 1 | $8 | [Amazon 2-pack](https://www.amazon.com/s?k=FT232RL+USB+TTL+serial+converter+type-C) · [AliExpress](https://www.aliexpress.us/w/wholesale-FT232RL+USB+TTL.html) |

## Power system — cells & testing

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **Opus BT-C3100 V2.2** — 4-bay Li-ion tester (capacity + IR) | 1 | $55 | [Amazon (US seller, 100+ reviews)](https://www.amazon.com/s?k=Opus+BT-C3100+V2.2+charger+analyzer) · avoid cheap clones |
| **18650 cells** — salvaged from laptop packs or purchased | 12 matched (test ~40) | free–$40 | Salvage from laptop packs; new Samsung 25R / LG HG2 from [liionwholesale.com](https://liionwholesale.com/) if buying |
| **Keystone 1042 4-cell 18650 holder with solder tabs** | 3 | $3 ea | [DigiKey #1042](https://www.digikey.com/en/products/detail/keystone-electronics/1042/2137907) · [Mouser #1042](https://www.mouser.com/ProductDetail/Keystone-Electronics/1042) · [Amazon](https://www.amazon.com/s?k=Keystone+1042+18650+4-cell+holder) |
| **Pure nickel strip 0.15 × 8 mm, 1 m** — parallel-group interconnects | 1 | $8 | [Vruzend](https://vruzend.com/product/pure-nickel-strip/) · [Amazon (magnet test on arrival)](https://www.amazon.com/s?k=pure+nickel+strip+0.15+8mm) |

## Power system — protection & charging

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **Daly 3S 20 A smart BMS w/ Bluetooth** | 1 | $28 | [Overkill Solar (US, firmware-vetted)](https://www.overkillsolar.com/) · [Amazon](https://www.amazon.com/s?k=Daly+3S+20A+Smart+BMS+Bluetooth+12V) · [AliExpress Daly Official Store](https://www.aliexpress.us/w/wholesale-Daly-3S-20A-Smart-BMS-Bluetooth.html) |
| **SEFUSE SF77E thermal fuse (77 °C, one-shot)** | 1 | $2 | [Mouser (search SF77E)](https://www.mouser.com/c/?q=SEFUSE%20SF77E) · [DigiKey](https://www.digikey.com/en/products/result?keywords=SF77E) |
| **10 kΩ NTC thermistor, potted probe** — battery temp sense | 1 | $3 | [Amazon](https://www.amazon.com/s?k=10K+NTC+thermistor+potted+probe+waterproof) · [AliExpress](https://www.aliexpress.us/w/wholesale-10K-NTC-thermistor-waterproof-probe.html) |
| **Renogy 100 W 12 V monocrystalline rigid panel** | 1 | $80 | [Renogy direct](https://www.renogy.com/pages/100w-monocrystalline-solar-rigid-panels-compact-design-rng-100d-ss-html) · [Amazon (Renogy storefront)](https://www.amazon.com/s?k=Renogy+100W+12V+monocrystalline+rigid+solar+panel) |
| **10 AWG MC4 solar cable pair, 3 m** | 1 | $12 | [Renogy MC4 kits](https://www.renogy.com/solar-adaptor-kit-mc4/) · [Amazon (UL-4703 marking)](https://www.amazon.com/s?k=10+AWG+MC4+solar+cable+3m+pair) |
| **Victron SmartSolar MPPT 75/15** — CRITICAL: authorized dealers only | 1 | $110 | [EcoDirect](https://www.ecodirect.com/Victron-Energy-SmartSolar-75-15-Charge-Controller-p/victron-energy-ss-mppt-75-15.htm) · [Dakota Lithium](https://dakotalithium.com/product/victron-smartsolar-mppt-75-15-solar-charge-controller/) · [EXPLORIST.life](https://shop.explorist.life/shop/all-products/victron-smartsolar-mppt-7515/) · **NEVER AliExpress** |
| **Pololu D36V50F5** (5 V, 5.5 A synchronous buck) — main 5 V rail | 1 | $30 | [Pololu #4091](https://www.pololu.com/product/4091) |
| **ANL 15 A fuse + inline holder** | 1 | $10 | [Amazon](https://www.amazon.com/s?k=ANL+15A+fuse+holder+inline) · [AliExpress](https://www.aliexpress.us/w/wholesale-ANL-15A-fuse-holder.html) |
| **ATO/ATC 10 A fuse + inline holder** — load-side | 1 | $5 | [DigiKey (Littelfuse ATO)](https://www.digikey.com/en/products/filter/automotive-fuses/141) · [Amazon](https://www.amazon.com/s?k=ATO+ATC+10A+fuse+inline+holder+12AWG) |

## Wiring

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **14 AWG silicone stranded (red + black), 5 m ea** — main power | 2 | $10 | [Amazon BNTECHGO](https://www.amazon.com/s?k=BNTECHGO+14AWG+silicone+wire+red+black) · [AliExpress](https://www.aliexpress.us/w/wholesale-14AWG-silicone-wire-red-black.html) |
| **22 AWG silicone stranded (multi-color)** — sensor runs, BMS balance | 5 m | $8 | [Amazon BNTECHGO 22AWG](https://www.amazon.com/s?k=BNTECHGO+22AWG+silicone+wire+kit) · [AliExpress](https://www.aliexpress.us/w/wholesale-22AWG-silicone-wire.html) |
| **CAT6 F/UTP (foiled + drain wire)** — HX711 shielded run | ~2 m | $5–15 | [Monoprice CAT6 shielded](https://www.monoprice.com/category/cables/networking/cat6-cables) · [Amazon](https://www.amazon.com/s?k=CAT6+FTP+shielded+cable+solid+copper) |
| **ALLECIN 50-value resistor kit** — includes 220 Ω, 4.7 k, 10 k, 22 k, 100 k | 1 | $12 | [Amazon](https://www.amazon.com/s?k=ALLECIN+50+value+resistor+kit) · verify ≥ 16 per value |

## Enclosures & mounting

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **Bud NBF-32026 IP66 polycarbonate box** (~400 × 300 × 160 mm) | 1 | $43 | [DigiKey](https://www.digikey.com/en/products/detail/bud-industries/NBF-32026/2328539) · [Bud direct](https://www.budind.com/product/nema-ip-rated-boxes/nbf-series-fiberglass-enclosure/nbf-32026/) |
| **Vented battery box** (~200 × 120 × 80 mm, IP54, ABS) | 1 | $25 | [Amazon (marine battery box, add vent plugs)](https://www.amazon.com/s?k=vented+ABS+marine+battery+box+12V) · [AliExpress](https://www.aliexpress.us/w/wholesale-vented+lithium+battery+box+12V.html) |
| **Ceramic fiber blanket, 300 × 300 × 6 mm** — intumescent liner | 1 | $10 | [McMaster](https://www.mcmaster.com/products/ceramic-fiber-insulation/) · [Amazon](https://www.amazon.com/s?k=ceramic+fiber+blanket+6mm+300x300) |
| **PG9 + PG13 nylon cable gland assortment** | 1 | $8 | [McMaster (Heyco/Sealcon)](https://www.mcmaster.com/products/cable-glands/) · [Amazon](https://www.amazon.com/s?k=PG9+PG13+nylon+cable+gland+waterproof+assortment) |
| **35 mm × 200 mm DIN rail** (optional layout) | 1 | $5 | [AutomationDirect](https://www.automationdirect.com/adc/shopping/catalog/terminal_blocks_-a-_accessories/din_rail) · [Amazon (1 m stick, cut down)](https://www.amazon.com/s?k=35mm+DIN+rail+200mm+slotted) |
| **Adjustable pole mount** for 100 W panel | 1 | $30 | [Renogy pole mounts](https://www.renogy.com/mounts-brackets/) · [Amazon](https://www.amazon.com/s?k=adjustable+pole+mount+100W+solar+panel) |
| **3D-printed bee-gate + radiation shield** — ASA or PETG only (no PLA) | — | print | Your own printer (see [`docs/hardware.md`](../docs/hardware.md)) |

## Chemistry & desiccant

| Item | Qty | ~Price | Buy from |
|---|---:|---:|---|
| **MG Chemicals 419D conformal acrylic** — coat every hive-side PCB | 1 | $15 | [MG Chemicals](https://mgchemicals.com/products/conformal-coatings/acrylic-conformal-coating/acrylic-lacquer-419d/) · [DigiKey (MG 419D)](https://www.digikey.com/en/products/result?keywords=MG+419D) — avoid Amazon third-party |
| **Silica gel packs (orange-to-green indicating, cobalt-free)** | 4 | $5 | [McMaster](https://www.mcmaster.com/products/desiccants/) · [Amazon](https://www.amazon.com/s?k=indicating+silica+gel+packets+rechargeable+orange) |
| **Neutral-cure silicone RTV sealant** — cable strain relief inside hive (**NOT acetoxy**) | 1 tube | $8 | [Amazon (neutral-cure only)](https://www.amazon.com/s?k=neutral+cure+silicone+sealant+RTV) |

## Tools (skip anything you already have)

| Tool | ~Price | Buy from |
|---|---:|---|
| Auto-ranging multimeter | $30 | [Amazon](https://www.amazon.com/s?k=auto+ranging+multimeter) · [AliExpress (ANENG AN8008)](https://www.aliexpress.us/w/wholesale-ANENG+AN8008.html) |
| Temp-controlled soldering iron (Pinecil V2) | $30–50 | [Pine Store (genuine)](https://pine64.com/product/pinecil-smart-mini-portable-soldering-iron/) · [Amazon](https://www.amazon.com/s?k=Pinecil+V2+soldering+iron) |
| Wire strippers + flush cutters | $20 | [Amazon](https://www.amazon.com/s?k=self+adjusting+wire+stripper+flush+cutter+set) |
| Heatshrink assortment (3:1 adhesive-lined) | $10 | [Amazon](https://www.amazon.com/s?k=heat+shrink+tubing+kit+3%3A1+adhesive) |
| JST-XH crimp kit + Engineer PA-09 crimper | $30 | [Amazon Engineer PA-09](https://www.amazon.com/s?k=Engineer+PA-09+crimper) · [Amazon JST-XH kit](https://www.amazon.com/s?k=JST+XH+connector+crimp+kit) |
| Hot glue gun (any) | $15 | [Amazon](https://www.amazon.com/s?k=hot+glue+gun) |

## Totals (order-of-magnitude)

| Bucket | ~$ |
|---|---:|
| Compute (Pi 5 + Pico + SD + PSU) | $95 |
| Sensors (excluding optional CO₂/VOC/rain) | $200 |
| Sensors (all optional included) | $330 |
| Power system (incl. cell tester) | $400 |
| Enclosures + wiring + chemistry | $150 |
| **Base total (minimum viable)** | **~$800** |
| **Fully loaded** | **~$1,000** |

The two components where I'd never cut costs: **Victron MPPT** (a fake will cook cells or fail dangerously) and **Opus BT-C3100** (clones over-report capacity, letting bad cells through the testing pipeline).
