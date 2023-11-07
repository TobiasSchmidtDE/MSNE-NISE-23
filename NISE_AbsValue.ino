const int analogInPin1 = 26; // analog pin A0 , GPIO 26
const int analogInPin2 = 34; // analog pin A2, GPIO 28

int sensorValue = 0; // value we want to plot
int absValue = 0; // absolute value of the sensor reading

int sensorValue2 = 0; // value we want to plot
int absValue2 = 0; // absolute value of the sensor reading

int numSamples = 200;
int threshold = 100;

bool calibration = false;
int calibValues1 = 0;
int calibValues2 = 0;
int baseline1 = 1720;
int baseline2 = 1730;
int numCalibSamples = 20;


int motorPin1 = 13; // GPIO 13 for vibration motor 1

void setup() {
  Serial.begin(512000); // 512000 bits per second
  pinMode(motorPin1, OUTPUT); // Configure motor pin as an output
}

void loop() {
  long sumSquared = 0;
  long sumSquared2 = 0;
  float rmsValue;
  float rmsValue2;
  int i =0;

/*
  while (calibration == false) {
     for (int i = 0; i < numSamples; i++) {
        sensorValue = analogRead(analogInPin1); // read the analog input
        sumSquared += abs(sensorValue) * abs(sensorValue); // Calculate the sum of squared absolute values
        sensorValue2 = analogRead(analogInPin2); // read the analog input
        sumSquared2 += abs(sensorValue2) * abs(sensorValue2); // Calculate the sum of squared absolute values
     }
    rmsValue = sqrt(sumSquared / (float)numSamples);
    rmsValue2 = sqrt(sumSquared2 / (float)numSamples);

    calibValues1 += rmsValue;
    calibValues2 += rmsValue2;
    i += 1;

    if (i == numCalibSamples) {
      calibration = true; 
      baseline1 = calibValues1 / numCalibSamples;
      baseline2 = calibValues2 / numCalibSamples;
      Serial.println("Calibration complete!");
      Serial.print(" ");
    }
  }
  */

  for (int i = 0; i < numSamples; i++) {
    sensorValue = analogRead(analogInPin1); // read the analog input
    absValue = abs(sensorValue - baseline1); // Calculate the absolute value
    sumSquared += absValue * absValue;
    sensorValue2 = analogRead(analogInPin2); // read the analog input
    absValue2 = abs(sensorValue2 - baseline2); // Calculate the absolute value
    sumSquared2 += absValue2 * absValue2;
  }

  rmsValue = sqrt(sumSquared / (float)numSamples);
  rmsValue2 = sqrt(sumSquared2 / (float)numSamples);
  
  
  // Print out the RMS value
  Serial.println(rmsValue);
  Serial.print(",");
  Serial.println(rmsValue2);


  // Check if RMS value is above the threshold
 if (rmsValue > threshold) {
    // Trigger vibrotactile feedback
    digitalWrite(motorPin1, HIGH);
    Serial.print("Jump!");
    delay(400);
    digitalWrite(motorPin1, LOW);
    Serial.print("Go!");
  }


 if (rmsValue2 > threshold) {
    // Trigger vibrotactile feedback
    digitalWrite(motorPin1, HIGH);
    delay(100); // Vibration duration
    digitalWrite(motorPin1, LOW);
    Serial.print("Sneak! ");
    delay(100);
    digitalWrite(motorPin1, HIGH);
    delay(100); // Vibration duration
    digitalWrite(motorPin1, LOW);
    delay(100);
    Serial.print("Go!");
  }
  
  delay(50);
}
