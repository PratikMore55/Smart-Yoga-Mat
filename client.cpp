#include <WiFi.h>
#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

const char* ssid = "abc";
const char* password = "xyz";
const char* serverIP = "192.168.1.68";  
const uint16_t serverPort = 5000;

WiFiClient client;
MAX30105 particleSensor;
#define BUFFER_SIZE 100

uint32_t irBuffer[BUFFER_SIZE];  
uint32_t redBuffer[BUFFER_SIZE];  

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found. Please check wiring.");
    while (1);
  }

  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
}

void loop() {
  if (!client.connected()) {
    Serial.println("Connecting to server...");
    if (client.connect(serverIP, serverPort)) {
      Serial.println("Connected!");
    } else {
      Serial.println("Connection failed");
      delay(5000);
      return;
    }
  }

  float heartRate = 0, spo2 = 0;
  int32_t spo2Temp, heartRateTemp;
  int8_t spo2Valid, hrValid;

  for (int i = 0; i < BUFFER_SIZE; i++) {
    while (particleSensor.available() == false)
      particleSensor.check();

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample();
  }

  maxim_heart_rate_and_oxygen_saturation(irBuffer, BUFFER_SIZE, redBuffer, &spo2Temp, &spo2Valid, &heartRateTemp, &hrValid);

  heartRate = hrValid ? heartRateTemp : 0;
  spo2 = spo2Valid ? spo2Temp : 0;

  String data = String(heartRate) + "," + String(spo2);
  Serial.println("Sending: " + data);
  client.println(data);

  delay(1000);  
}
