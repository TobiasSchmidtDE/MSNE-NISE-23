#include <Arduino.h>

// Constants for the analog input pins
const int analogInPin1 = 26;  // Analog pin A0, GPIO 26
const int analogInPin2 = 34;  // Analog pin A2, GPIO 28

// Variables for sensor values and their absolute values
int sensorValue1 = 0;        // Value from sensor 1
int sensorValue2 = 0;       // Value from sensor 2

// Sampling and thresholding parameters
int buffersize = 300;
int rmssize = 50;
int baseline1 = 0;
int baseline2 = 0;
int rms1 = 0;
int rms2 = 0;
int threshold = 0;


// Motor control pin
int motorPin1 = 13;  // GPIO 13 for vibration motor 1
bool motorOn = false; // Flag for motor use (for debug purposes)

void setup() {
  Serial.begin(512000);  // Start serial communication at 512000 bps
  pinMode(motorPin1, OUTPUT);  // Configure the motor pin as an output
}

void loop() {
  // Variables for calculating RMS values
  float rmsValue;
  float rmsValue2;


  // Print out the RMS values
  // Serial.print(rmsValue2);
  Serial.print(analogRead(analogInPin1));   // Gleichfarbige Kabel = Jump
  Serial.print(",");
  Serial.print(analogRead(analogInPin2));   // Andersfarbige Kabel = Duck
  // Serial.println(rmsValue);


  // Trigger vibrotactile feedback if RMS value is above the threshold for sensor 1
  if (rmsValue > threshold) {
    // Serial.print("Jump!");
    if (motorOn) {
      digitalWrite(motorPin1, HIGH);  // Activate motor
      delay(400);  // Wait for 400 ms
      digitalWrite(motorPin1, LOW);   // Deactivate motor
    }
    // Serial.print("Go!");
  }

  // Trigger a different pattern of vibrotactile feedback for sensor 2
  if (rmsValue2 > threshold) {
    // Serial.print("Sneak! ");
    if (motorOn) {
      digitalWrite(motorPin1, HIGH);  // Activate motor
      delay(100);  // Vibration duration
      digitalWrite(motorPin1, LOW);   // Deactivate motor
      delay(100);
      digitalWrite(motorPin1, HIGH);  // Activate motor again
      delay(100);  // Vibration duration
      digitalWrite(motorPin1, LOW);   // Deactivate motor
    }
    // Serial.print("Go!");
  }

  // Short delay before the next loop iteration
  delay(72);
}