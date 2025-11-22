# ESP32-CAM Siren Control Code

## Add these lines to your CameraWebServer.ino:

### 1. Add at the top (after includes):
```cpp
#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>  // Add this line

// Siren pin definition
#define SIREN_PIN 2
```

### 2. Add after WiFi connection (in setup() function):
```cpp
void setup() {
  // ... existing camera and WiFi setup code ...
  
  // Initialize Siren GPIO pin
  pinMode(SIREN_PIN, OUTPUT);
  digitalWrite(SIREN_PIN, LOW);
  Serial.println("🔊 Siren GPIO initialized on pin 2");

  WiFi.begin(ssid, password);
  // ... WiFi connection code ...

  startCameraServer();
  
  // Add siren web server
  setupSirenServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}
```

### 3. Add these functions before setup():
```cpp
// Create web server instance
WebServer server(80);

// Siren control functions
void sirenOn() {
  digitalWrite(SIREN_PIN, HIGH);
  Serial.println("🔊 SIREN ACTIVATED via ESP32 (GPIO 2)");
}

void sirenOff() {
  digitalWrite(SIREN_PIN, LOW);
  Serial.println("🔇 SIREN DEACTIVATED via ESP32 (GPIO 2)");
}

// Web server handlers
void handleSirenOn() {
  sirenOn();
  server.send(200, "text/plain", "Siren ON");
}

void handleSirenOff() {
  sirenOff();
  server.send(200, "text/plain", "Siren OFF");
}

void handleSirenStatus() {
  int sirenState = digitalRead(SIREN_PIN);
  String status = sirenState ? "ON" : "OFF";
  server.send(200, "text/plain", "Siren: " + status);
}

// Setup siren web server
void setupSirenServer() {
  server.on("/siren/on", HTTP_GET, handleSirenOn);
  server.on("/siren/off", HTTP_GET, handleSirenOff);
  server.on("/siren/status", HTTP_GET, handleSirenStatus);
  
  server.begin();
  Serial.println("Siren web server started");
  Serial.println("Endpoints:");
  Serial.println("  /siren/on - Turn siren ON");
  Serial.println("  /siren/off - Turn siren OFF");
  Serial.println("  /siren/status - Check siren status");
}
```

### 4. Add to loop() function:
```cpp
void loop() {
  server.handleClient();  // Add this line
  delay(10000);
}
```

## Complete Modified CameraWebServer.ino:

```cpp
#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// ===================
// Select camera model
// ===================
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// ===========================
// Enter your WiFi credentials
// ===========================
const char *ssid = "R";
const char *password = "123456789";

// Siren pin definition
#define SIREN_PIN 2

// Create web server instance
WebServer server(80);

void startCameraServer();
void setupLedFlash(int pin);

// Siren control functions
void sirenOn() {
  digitalWrite(SIREN_PIN, HIGH);
  Serial.println("🔊 SIREN ACTIVATED via ESP32 (GPIO 2)");
}

void sirenOff() {
  digitalWrite(SIREN_PIN, LOW);
  Serial.println("🔇 SIREN DEACTIVATED via ESP32 (GPIO 2)");
}

// Web server handlers
void handleSirenOn() {
  sirenOn();
  server.send(200, "text/plain", "Siren ON");
}

void handleSirenOff() {
  sirenOff();
  server.send(200, "text/plain", "Siren OFF");
}

void handleSirenStatus() {
  int sirenState = digitalRead(SIREN_PIN);
  String status = sirenState ? "ON" : "OFF";
  server.send(200, "text/plain", "Siren: " + status);
}

// Setup siren web server
void setupSirenServer() {
  server.on("/siren/on", HTTP_GET, handleSirenOn);
  server.on("/siren/off", HTTP_GET, handleSirenOff);
  server.on("/siren/status", HTTP_GET, handleSirenStatus);
  
  server.begin();
  Serial.println("Siren web server started");
  Serial.println("Endpoints:");
  Serial.println("  /siren/on - Turn siren ON");
  Serial.println("  /siren/off - Turn siren OFF");
  Serial.println("  /siren/status - Check siren status");
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // ... (keep all your existing camera config code) ...

  // Initialize Siren GPIO pin
  pinMode(SIREN_PIN, OUTPUT);
  digitalWrite(SIREN_PIN, LOW);
  Serial.println("🔊 Siren GPIO initialized on pin 2");

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();
  setupSirenServer();  // Add this line

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void loop() {
  server.handleClient();  // Add this line
  delay(10000);
}
```

## Test URLs (after upload):

- `http://YOUR_ESP32_IP/siren/on` - Turn siren ON
- `http://YOUR_ESP32_IP/siren/off` - Turn siren OFF  
- `http://YOUR_ESP32_IP/siren/status` - Check status

Your backend is already configured to call these endpoints!