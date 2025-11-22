# ESP32-CAM Siren/Buzzer Setup Guide

## Hardware Connections

### Option 1: Simple Active Buzzer (3.3V)
```
Active Buzzer (+) → ESP32 GPIO 2
Active Buzzer (-) → ESP32 GND
```
**Pros:** Simple, no extra components
**Cons:** Not very loud, limited range

### Option 2: Relay + High-Power Siren (RECOMMENDED)
```
ESP32 Side:
- GPIO 2 → Relay Module IN
- 3.3V → Relay VCC
- GND → Relay GND

Siren Side (with external 12V power):
- 12V Power (+) → Siren (+)
- Siren (-) → Relay COM
- Relay NO → 12V Power (-)
```
**Pros:** Very loud, long range, suitable for farms
**Cons:** Needs external power supply

### Option 3: Transistor + Buzzer (Medium Power)
```
ESP32 GPIO 2 → 1kΩ Resistor → NPN Transistor Base (2N2222)
Transistor Emitter → GND
Transistor Collector → Buzzer (-)
Buzzer (+) → 5V
```
**Pros:** Louder than direct connection
**Cons:** Needs transistor

## GPIO Pin Recommendations

**Best pins for ESP32-CAM:**
- **GPIO 2** ✅ (Built-in LED, easy to test)
- **GPIO 12** ✅ (Safe to use)
- **GPIO 13** ✅ (Safe to use)
- **GPIO 14** ✅ (Safe to use)
- **GPIO 15** ✅ (Safe to use)

**Avoid these pins:**
- GPIO 0 (Boot mode)
- GPIO 1, 3 (UART)
- GPIO 4 (Flash LED)
- GPIO 16 (PSRAM)

## Arduino Code to Add

Add this to your ESP32-CAM sketch:

```cpp
// Siren pin definition
#define SIREN_PIN 2  // Change to your chosen GPIO

// In setup():
void setup() {
  // ... existing camera setup code ...
  
  // Initialize siren pin
  pinMode(SIREN_PIN, OUTPUT);
  digitalWrite(SIREN_PIN, LOW);  // Start with siren OFF
  Serial.println("Siren initialized on GPIO 2");
}

// Add these functions:
void sirenOn() {
  digitalWrite(SIREN_PIN, HIGH);
  Serial.println("🔊 SIREN ON");
}

void sirenOff() {
  digitalWrite(SIREN_PIN, LOW);
  Serial.println("🔇 SIREN OFF");
}

// Add HTTP endpoint in your web server:
server.on("/siren/on", HTTP_GET, [](AsyncWebServerRequest *request){
  sirenOn();
  request->send(200, "text/plain", "Siren ON");
});

server.on("/siren/off", HTTP_GET, [](AsyncWebServerRequest *request){
  sirenOff();
  request->send(200, "text/plain", "Siren OFF");
});
```

## Testing Steps

1. **Test with Built-in LED first:**
   - Use GPIO 2 (built-in LED)
   - Upload code
   - Visit: `http://YOUR_ESP32_IP/siren/on`
   - LED should turn on
   - Visit: `http://YOUR_ESP32_IP/siren/off`
   - LED should turn off

2. **Connect Buzzer:**
   - Once LED test works, connect buzzer to GPIO 2
   - Test again with URLs above

3. **Upgrade to Relay + Siren:**
   - Connect relay module
   - Connect high-power siren to relay
   - Test with URLs

## Shopping List (for farm use)

1. **5V Relay Module** - $2-5
2. **12V Siren/Alarm** (110dB+) - $10-20
3. **12V Power Supply** - $5-10
4. **Jumper Wires** - $2

**Total: ~$20-35 for loud farm siren**

## Wiring Diagram (Relay Setup)

```
ESP32-CAM          Relay Module        12V Siren
---------          ------------        ---------
GPIO 2 ---------> IN
3.3V -----------> VCC
GND ------------> GND
                  COM <-------------- Siren (-)
                  NO --------------> 12V Power (-)
                                      
12V Power (+) -------------------> Siren (+)
```

## Safety Notes

⚠️ **Important:**
- Don't connect high-power devices directly to ESP32 pins (max 12mA)
- Always use relay for sirens > 5V
- Double-check polarity before powering on
- Test with LED first before connecting siren
- Use external power for siren, not ESP32 power

## Current Backend Configuration

Your backend is already configured to call:
- `http://YOUR_ESP32_IP/siren/on` - Turn siren ON
- `http://YOUR_ESP32_IP/siren/off` - Turn siren OFF

Just add the endpoints to your ESP32 code and it will work!
