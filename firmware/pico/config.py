"""Pin assignments and calibration for the beehive Pico firmware.

Edit values here when you swap sensors or recalibrate.  Nothing in drivers/
should hard-code a pin number.
"""

# ---- I2C buses ----------------------------------------------------------
I2C0_SDA = 20        # SHT41, BME280 (hive-interior + external weather)
I2C0_SCL = 21
I2C0_FREQ = 100_000

I2C1_SDA = 16        # VEML7700, SCD41, SGP40
I2C1_SCL = 17
I2C1_FREQ = 100_000

# ---- 1-Wire (DS18B20 array) ---------------------------------------------
ONEWIRE_PIN = 22

# Populate after enumerating the bus once; see drivers/ds18b20.py.
# ROM addresses are 8-byte bytes objects.
DS18B20_LABELS = {
    # b"\x28\xff\x...": "top_cover",
    # b"\x28\xff\x...": "above_brood",
    # b"\x28\xff\x...": "brood_side",
    # b"\x28\xff\x...": "entrance",
}

# ---- HX711 (weight) -----------------------------------------------------
HX711_DOUT = 18
HX711_SCK = 19
HX711_GAIN = 128     # channel A, gain 128 (highest sensitivity)
HX711_TARE_OFFSET = 0        # set at calibration or via Pi command
HX711_SCALE = 1.0            # kg per raw unit; set at calibration
HX711_SAMPLES = 5            # median-of-N to reject spikes

# ---- Battery voltage divider -------------------------------------------
BATT_ADC_PIN = 28    # ADC2 / GP28
BATT_DIVIDER_RATIO = 5.545   # (100k + 22k) / 22k, refine via calibration
BATT_ADC_VREF = 3.30         # Pico's ADC reference

# Voltage thresholds (pack volts, 3S)
BATT_WARN_V = 11.40
BATT_SHUTDOWN_V = 10.80
BATT_HARD_CUT_V = 9.90

# ---- Bee gate (IR beam array) ------------------------------------------
# 8 tunnels, each with 2 phototransistors A (outward-facing) and B (inward).
BEE_GATE_BEAM_A_PINS = [0, 1, 2, 3, 4, 5, 6, 7]
BEE_GATE_BEAM_B_PINS = [8, 9, 10, 11, 12, 13, 14, 15]
BEE_GATE_DIRECTION_WINDOW_MS = 500   # A then B (or vice versa) within this = 1 event
BEE_GATE_DEBOUNCE_MS = 5
BEE_GATE_STUCK_TIMEOUT_MS = 2000     # beam blocked longer than this: assume loitering

# ---- Publish loop -------------------------------------------------------
PUBLISH_INTERVAL_S = 1               # one JSON packet per second on USB-CDC
SLOW_INTERVAL_S = 5                  # cadence for slow sensors (SCD41 etc.)

# ---- Sensor enable flags -----------------------------------------------
ENABLE_HX711 = True
ENABLE_DS18B20 = True
ENABLE_SHT41 = True
ENABLE_BME280 = True
ENABLE_VEML7700 = True
ENABLE_SCD41 = False                 # opt-in — sensor is $50 and optional
ENABLE_SGP40 = False
ENABLE_BEE_GATE = True
ENABLE_BATTERY_MONITOR = True

# ---- Firmware version --------------------------------------------------
FIRMWARE_VERSION = "0.1.0"
