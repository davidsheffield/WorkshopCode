/*******************************************************************************
**
** Arduino Nano in my Bridgeport's control panel. It takes the signal from
** the VFD and provides the spindle speed on an LED display.
**
** The VFD provides a 0-10 V signal that is linearly proportional to
** the supplied frequency. The maximum operation frequency is 140 Hz (10 V).
** That signal is converted to 0-5V by using a voltage divider
** and an MCP6002 op-amp. The cutoff frequency of the low-pass filter
** is 15.9 Hz.
**
** Vin --- 100k ------------------ OPAMP +
**                |     |                   OPAMP out --- VFD_PIN
**               100k  0.1uF   --- OPAMP -             |
**                |     |      |                       |
**               GND   GND     -------------------------
**
** The Bridgeport has a high speed range and a low speed range, which goes
** throught a backgear with approximation a 8.3:1 reduction in speed. A button
** on the control panel allows the user to select the high or low speed range.
** By default, the panel displays the high speed range.
**
** The speed is displayed on a 4-digit 7-segment LED display. The display has
** pins VCC, GND, CLK, and DIO. It uses the protocol defined by the TM1637 chip.
**
*******************************************************************************/

// Constant for the backgear ratio
const float BACKGEAR_RATIO = 8.3;

// Analogue pin for the VFD speed signal
#define VFD_PIN A0

// Pin for the low/high speed range button
#define RANGE_BUTTON_PIN 5
// Pin 4 wasn't working

// Pins for CLK and DIO
#define CLK 2
#define DIO 3

// Set frequency range
bool high_range = true;
bool last_button_state = false;

void setup() {
    // Set pin modes
    pinMode(VFD_PIN, INPUT);
    pinMode(RANGE_BUTTON_PIN, INPUT_PULLUP);
    pinMode(CLK, OUTPUT);
    pinMode(DIO, OUTPUT);

    // initialize serial communication at 9600 bits per second:
    Serial.begin(9600);
}

void loop() {
    delay(10); // Low pass filter has a cutoff period of 63 ms

    int range_button = digitalRead(RANGE_BUTTON_PIN);
    // Check the range button and change the range if it is a new press
    if (range_button == LOW && !last_button_state) {
        high_range = !high_range;
        last_button_state = true;
    } else if (range_button == HIGH) {
        last_button_state = false;
    }

    // Read the VFD signal
    int vfd_value = analogRead(VFD_PIN);
    // Convert to speed [RPM]
    float fspeed = (vfd_value / 1023.0) * 4025.0;
    fspeed = high_range ? fspeed : fspeed / BACKGEAR_RATIO;
    int speed = (int)fspeed;

    // Write to serial for debugging
    Serial.print("RANGE BUTTON: ");
    Serial.print(range_button);
    Serial.print("  last_button_state: ");
    Serial.print(last_button_state);
    Serial.print("  Range: ");
    Serial.print(high_range ? "High" : "Low");
    Serial.print("  VFD: ");
    Serial.print(vfd_value);
    Serial.print("  Speed: ");
    Serial.println(speed);
}
