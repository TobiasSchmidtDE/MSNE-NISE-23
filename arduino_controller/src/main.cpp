#include <Arduino.h>

// Constants for the analog input pins
const int analogInPin1 = 26;  // Analog pin A0, GPIO 26
const int analogInPin2 = 34;  // Analog pin A2, GPIO 28

// Variables for sensor values and their absolute values
int sensorValue = 0;        // Value from sensor 1
int absValue = 0;           // Absolute value for sensor 1
int sensorValue2 = 0;       // Value from sensor 2
int absValue2 = 0;          // Absolute value for sensor 2

// Sampling parameters
int numSamples = 200;

// int sum_baseline = 0;     // Sum of sensor 1 values for baseline calculation
// int sum_baseline2 = 0;    // Sum of sensor 2 values for baseline calculation
// int baseline1 = 0;       // Preset baseline for sensor 1
// int baseline2 = 0;       // Preset baseline for sensor 2
// long baselineCount = 0;     // Counter for baseline calculation
// int max_baseline_count = 1000;  // Number of loops for baseline calculation

int baseline1 = 1700;       // Preset baseline for sensor 1
int baseline2 = 1700;       // Preset baseline for sensor 2

// Motor control pin
// 12 and 13
int motorPin1 = 13;  // GPIO 13 for vibration motor 1
int motorPin2 = 12;  // GPIO 12 for vibration motor 2
bool motorOn = true; // Flag for motor use (for debug purposes)

void setup() {
  Serial.begin(512000);  // Start serial communication at 512000 bps
  pinMode(motorPin1, OUTPUT);  // Configure the motor pin as an output
  pinMode(motorPin2, OUTPUT);
}

void loop() {
  // Variables for calculating RMS values
  long sumSquared = 0;
  long sumSquared2 = 0;
  float rmsValue;
  float rmsValue2;
  long sum = 0;
  long sum2 = 0;
   // Read and process sensor data
  for (int i = 0; i < numSamples; i++) {
    sensorValue = analogRead(analogInPin1);  // Read the analog input from sensor 1
    absValue = abs(sensorValue - baseline1);  // Calculate the absolute value
    sumSquared += absValue * absValue;        // Accumulate the sum of squares

    sensorValue2 = analogRead(analogInPin2);  // Read the analog input from sensor 2
    absValue2 = abs(sensorValue2 - baseline2);  // Calculate the absolute value
    sumSquared2 += absValue2 * absValue2;      // Accumulate the sum of squares

    sum += sensorValue;  // Accumulate the sum of sensor 1 values
    sum2 += sensorValue2;  // Accumulate the sum of sensor 2 values

  }

  // // Calculate the baseline values
  // // first calculate the average of the sensor values
  // float avg = sum / (float)numSamples;
  // float avg2 = sum2 / (float)numSamples;
  // // if the baselineCount is smaller than the max_baseline_count value add to sum
  // if (baselineCount < max_baseline_count) {
  //   sum_baseline += avg;
  //   sum_baseline2 += avg2;
  //   baselineCount++;
  //   // update the baseline values
  //   baseline1 = (int)(sum_baseline / (float)baselineCount);
  //   baseline2 = (int)(sum_baseline2 / (float)baselineCount);
  // } else {
  //   // if the baselineCount is equal to the max_baseline_count value calculate the baseline
  //   baseline1 = (int)(sum_baseline / (float)max_baseline_count);
  //   baseline2 = (int)(sum_baseline2 / (float)max_baseline_count);
  // }

  // Calculate the RMS values
  rmsValue = sqrt(sumSquared / (float)numSamples);
  rmsValue2 = sqrt(sumSquared2 / (float)numSamples);

  
  // Print out the RMS values
  Serial.print(rmsValue2);
  Serial.print(",");
  Serial.println(rmsValue);


  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the incoming command

    // Check the command and act accordingly
    if (command == "vibrate_single") {
      if (motorOn) {
        digitalWrite(motorPin1, HIGH);  // Activate motor
        delay(400);  // Wait for 400 ms
        digitalWrite(motorPin1, LOW);   // Deactivate motor
      }
    } else if (command == "vibrate_double") {
      if (motorOn) {
        digitalWrite(motorPin2, HIGH);  // Activate motor
        delay(100);  // Vibration duration
        digitalWrite(motorPin2, LOW);   // Deactivate motor
        delay(100);
        digitalWrite(motorPin2, HIGH);  // Activate motor again
        delay(100);  // Vibration duration
        digitalWrite(motorPin2, LOW);   // Deactivate motor
      }
    } else if (command == "motor_on"){
      motorOn = true;
    } else if (command == "motor_off"){
      motorOn = false;
    }

  }

  // Short delay before the next loop iteration
  delay(50);
}