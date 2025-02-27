#include <WiFi.h>
#include <HTTPClient.h>
const char* ssid = "Pratik_2.4G";
const char* password = "Ganesh@348";
const char* server_url = "http://192.168.1.45:5000/";  // Update with Flask server IP

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi.");
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(server_url);
        http.addHeader("Content-Type", "application/json");

        // Example data: Replace with actual sensor values
        String jsonData = "{\"features\": [80, 97, 22, 36.5]}";  

        int httpResponseCode = http.POST(jsonData);
        
        Serial.print("HTTP Response Code: ");
        Serial.println(httpResponseCode);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("Response: " + response);
        } else {
            Serial.println("Error in HTTP request.");
        }

        http.end();
    }
    delay(5000);  // Send request every 5 seconds
}
