# Bridgeport Control Panel

Arduino Nano sketch that reads the VFD's analog output and displays spindle speed (RPM) on a 4-digit 7-segment LED display.

## Hardware

### Signal chain

The VFD outputs 0–10 V proportional to frequency, with a −5% bias. The maximum operating frequency is 140 Hz (9.5 V); the minimum is 13.8% of maximum (19.32 Hz, ~0.88 V).

A voltage divider and MCP6002 differential op-amp convert the 0–10 V signal to 0–5 V for the Arduino's analog input (A0). The VFD's V+ is at the same potential as digital ground, requiring the differential amplifier configuration. A 1 µF capacitor provides a low-pass filter (cutoff ~1.59 Hz).

```
               ------- 100k ---------------
               |                          |
V- ---- 200k ------------ OPAMP -         |
                                OPAMP out --- A0
V+ ---- 200k ------------ OPAMP +
               |      |
              100k   1uF
               |      |
              GND    GND
```

### Pin assignments

| Pin | Function |
|-----|----------|
| A0  | VFD analog speed signal |
| D2  | TM1637 display CLK |
| D3  | TM1637 display DIO |
| D5  | High/low range toggle button (INPUT_PULLUP) |

### Speed ranges

The Bridgeport has high and low spindle ranges. Low range passes through a backgear with an ~8.3:1 reduction. A button on pin 5 toggles between ranges; the display briefly shows `HI` or `LO` after switching.

## Software

### Dependencies

- [TM1637Display](https://github.com/avishorp/TM1637) library

### Building and uploading

```bash
# Compile
arduino-cli compile --fqbn arduino:avr:nano Bridgeport_control_panel/

# Upload (adjust port as needed)
arduino-cli upload -p /dev/cu.usbserial-* --fqbn arduino:avr:nano Bridgeport_control_panel/
```

Or use the Arduino IDE.

### Calibration constants

Defined at the top of `Bridgeport_control_panel.ino`:

```cpp
const double calibration = 4025.0 / 1023.0;  // ADC reading → RPM scale factor
const double bias = 195.0;                     // Corrects for VFD's −5% bias
```

To recalibrate:
1. Set `calibration = 1.0` and `bias = 0.0` in the sketch and upload.
2. Record ADC readings alongside measured RPM values in `calibration_measurements.csv`.
3. Run `calibration.py` to fit new constants via nonlinear least squares.
4. Update `calibration` and `bias` in the sketch.

### Debug mode

Set `#define DEBUG 1` (or `2` for verbose) to enable serial output at 9600 baud.

## Files

| File | Description |
|------|-------------|
| `Bridgeport_control_panel.ino` | Arduino sketch |
| `calibration.py` | Fits calibration constants from measurement data |
| `calibration_measurements.csv` | ADC readings and measured RPM for calibration |
