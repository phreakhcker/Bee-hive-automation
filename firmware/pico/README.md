# Pico Firmware

MicroPython firmware that reads all sensors and emits one JSON packet per second on USB-CDC.

## Flashing

See [`../../scripts/flash_pico.md`](../../scripts/flash_pico.md).

## Files

| File | Role |
|---|---|
| `main.py` | boot entry point; sensor scheduler; JSON emitter; command handler |
| `config.py` | pin assignments, calibration constants, feature flags |
| `drivers/hx711.py` | bit-banged HX711 load-cell driver |
| `drivers/ds18b20.py` | multi-probe DS18B20 array on 1-Wire |
| `drivers/sht4x.py` | Sensirion SHT41/SHT45 (I²C 0x44) |
| `drivers/bme280.py` | Bosch BME280 (I²C 0x76/0x77) |
| `drivers/veml7700.py` | Vishay VEML7700 lux sensor (I²C 0x10) |
| `drivers/scd41.py` | Sensirion SCD41 CO₂ sensor (I²C 0x62) |
| `drivers/sgp40.py` | Sensirion SGP40 VOC sensor (I²C 0x59) |
| `drivers/battery_monitor.py` | ADC pack-voltage read via divider |
| `drivers/bee_gate.py` | 8-channel IR beam-break counter with direction |

## Packet format

Newline-delimited JSON on USB-CDC. One packet per second. Example:

```json
{"t": 1721830000, "w_kg": 42.31, "t_in": 34.1, "rh_in": 62.4,
 "t_out": 24.1, "rh_out": 55.0, "p_hpa": 1012.3, "lux": 14300,
 "co2_ppm": 780, "voc_idx": 25123, "bees_in": 12, "bees_out": 8,
 "bees_ambiguous": 1, "v_pack": 12.14,
 "t_probes": {"top_cover": 34.2, "above_brood": 35.1, ...}}
```

Lines starting with `#` are human-readable logs; ingest ignores them.

## Commands (Pi → Pico)

Send newline-terminated JSON:

- `{"cmd":"ping"}` — Pico replies `# pong v=0.1.0`.
- `{"cmd":"tare"}` — reset HX711 zero to current reading.
- `{"cmd":"calibrate","cal":0.000428}` — set weight scale factor (kg/raw).

## Enumerating DS18B20 addresses

The first time you connect DS18B20 probes, get their ROM addresses so you can label each probe (top cover / above brood / etc.):

```python
from drivers.ds18b20 import DS18B20Array
d = DS18B20Array(22)
print(d.rom_list())
```

Copy those addresses into `config.DS18B20_LABELS`.

## Weight calibration procedure

1. Physically build the load-cell stand with the top platform empty.
2. Send `{"cmd":"tare"}` — this becomes zero.
3. Place a known weight (10 kg is convenient) on the platform.
4. Read the reported weight from the next JSON packet — it will be wrong.
5. Compute new scale: `new_cal = 10.0 / (reported_kg / current_cal)`.
6. Send `{"cmd":"calibrate","cal":<new_cal>}`.
7. Save the value to `config.HX711_SCALE` so it persists across reboots.

## Development on the bench

```bash
# From your laptop, after flashing MicroPython and copying files:
mpremote connect /dev/ttyACM0 repl        # interactive
mpremote connect /dev/ttyACM0 run main.py # non-persistent run
mpremote connect /dev/ttyACM0 cp *.py :   # copy files
```
