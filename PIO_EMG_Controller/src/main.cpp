#include <Arduino.h>

// Constants for the analog input pins
const int analogInPin1 = 26;  // Analog pin A0, GPIO 26
const int analogInPin2 = 34;  // Analog pin A2, GPIO 28

// Variables for sensor values and their absolute values
int sensorValue = 0;        // Value from sensor 1
int absValue = 0;           // Absolute value for sensor 1
int sensorValue2 = 0;       // Value from sensor 2
int absValue2 = 0;          // Absolute value for sensor 2

// Sampling and thresholding parameters
int numSamples = 200;
int threshold = 100;

// Calibration parameters (unused in the current code)
bool calibration = false;
int calibValues1 = 0;
int calibValues2 = 0;
int baseline1 = 1720;       // Preset baseline for sensor 1
int baseline2 = 1730;       // Preset baseline for sensor 2
int numCalibSamples = 20;

// Motor control pin
int motorPin1 = 13;  // GPIO 13 for vibration motor 1
bool motorOn = false; // Flag for motor use (for debug purposes)

void setup() {
  Serial.begin(512000);  // Start serial communication at 512000 bps
  pinMode(motorPin1, OUTPUT);  // Configure the motor pin as an output
}

void loop() {
  // Variables for calculating RMS values
  long sumSquared = 0;
  long sumSquared2 = 0;
  float rmsValue;
  float rmsValue2;

  // Read and process sensor data
  for (int i = 0; i < numSamples; i++) {
    sensorValue = analogRead(analogInPin1);  // Read the analog input from sensor 1
    absValue = abs(sensorValue - baseline1);  // Calculate the absolute value
    sumSquared += absValue * absValue;        // Accumulate the sum of squares

    sensorValue2 = analogRead(analogInPin2);  // Read the analog input from sensor 2
    absValue2 = abs(sensorValue2 - baseline2);  // Calculate the absolute value
    sumSquared2 += absValue2 * absValue2;      // Accumulate the sum of squares
  }

  // Calculate the RMS values
  rmsValue = sqrt(sumSquared / (float)numSamples);
  rmsValue2 = sqrt(sumSquared2 / (float)numSamples);
  
  // Print out the RMS values
  Serial.println(rmsValue2);
  Serial.print(",");
  Serial.println(rmsValue);

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
  delay(50);
}