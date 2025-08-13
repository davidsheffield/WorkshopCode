/*******************************************************************************
**
** Arduino Nano in my Bridgeport's control panel. It takes the signal from
** the VFD and provides the spindle speed on an LED display.
**
** The VFD provides a 0-10 V signal that is linearly proportional to
** the supplied frequency. The maximum operation frequency is 140 Hz (10 V).
** That signal is converted to 0-5V by using a voltage divider
** and an MCP6002 op-amp. The cutoff frequency of the low-pass filter
** is 1.59 Hz (a period of 629 ms).
**
** Vin --- 100k ------------------ OPAMP +
**                |     |                   OPAMP out --- VFD_PIN
**               100k  1uF     --- OPAMP -             |
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

#include <TM1637Display.h>

// 1 to enable debug output to serial
#define DEBUG 0

// Constant for the backgear ratio
const double BACKGEAR_RATIO = 8.3;

// Analogue pin for the VFD speed signal
#define VFD_PIN A0

// Pin for the low/high speed range button
#define RANGE_BUTTON_PIN 5
// Pin 4 wasn't working

// Pins for CLK and DIO
#define CLK 2
#define DIO 3

// Create display object
TM1637Display display(CLK, DIO);
const uint8_t HI_segments[] = {
    0,
	0b01110110, // H
	0b00110000, // I
    0};
const uint8_t LO_segments[] = {
	0,
	0b00111000, // L
	0b00111111, // O
    0};

// Set frequency range
bool high_range = true;
bool last_button_state = false;

// Check for button presses every 10 ms but the display only needs to be updated
// every 1 s. Empirically determined such that
// num_of_checks * button_check_interval ~= 1 s
int button_check_interval = 10; // check for button press every 10 ms
int num_of_checks = 95; // Number of checks before updating display
int num_of_checks_done = num_of_checks; // Number of checks left
double sum_of_speeds = 0.0; // Sum up num_of_checks speeds to get the average


void setup() {
    // Set pin modes
    pinMode(VFD_PIN, INPUT);
    pinMode(RANGE_BUTTON_PIN, INPUT_PULLUP);
    pinMode(CLK, OUTPUT);
    pinMode(DIO, OUTPUT);

    // Set display brightness (0-7)
    display.setBrightness(5);

    // initialize serial communication at 9600 bits per second:
    Serial.begin(9600);
}


void loop() {
    delay(10); // Low pass filter has a cutoff period of 63 ms

    // Check the range button and change the range if it is a new press
    int range_button = digitalRead(RANGE_BUTTON_PIN);
    if (range_button == LOW && !last_button_state) {
        high_range = !high_range;
        last_button_state = true;
        display.setSegments(high_range ? HI_segments : LO_segments);
    } else if (range_button == HIGH) {
        last_button_state = false;
    }

    // Read the VFD signal
    int vfd_value = analogRead(VFD_PIN);
    // Convert to speed [RPM]
    double speed = ((double)vfd_value / 1023.0) * 4025.0;
    speed = high_range ? speed : speed / BACKGEAR_RATIO;
    sum_of_speeds += speed;

    if (num_of_checks_done-- == 0) {
        double average_speed = sum_of_speeds / (double)num_of_checks;
        sum_of_speeds = 0.0;
        num_of_checks_done = num_of_checks;
        int display_speed = (int)average_speed;
        display.showNumberDec(display_speed);

        // Write to serial for debugging
        if (DEBUG) {
            Serial.print("Speed: ");
            Serial.print(average_speed);
            Serial.print(" Display Speed: ");
            Serial.println(display_speed);
        }
    }

    // Write to serial for debugging
    if (DEBUG) {
        Serial.print("Range: ");
        Serial.print(high_range);
        Serial.print(" RANGE BUTTON: ");
        Serial.print(range_button);
        Serial.print(" last_button_state: ");
        Serial.print(last_button_state);
        Serial.print(" VFD: ");
        Serial.print(vfd_value);
        Serial.print(" Speed: ");
        Serial.print(speed);
        Serial.print(" Sum of Speeds: ");
        Serial.println(sum_of_speeds);
    }
}
