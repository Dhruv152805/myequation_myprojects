/*
  =====================================================================
  IoT-Based Weather Station Using ESP32 and Cloud Dashboard
  ---------------------------------------------------------------------
  Reads temperature & humidity from a DHT22 sensor, uploads the data
  to ThingSpeak every UPLOAD_INTERVAL, and triggers an email alert
  (via IFTTT Webhooks) whenever either value crosses a defined
  threshold.

  Hardware:
    - ESP32 Dev Board
    - DHT22 sensor (data pin -> GPIO 4, with a 10k pull-up to 3V3)

  Libraries required (Arduino IDE > Library Manager):
    - "DHT sensor library" by Adafruit
    - "Adafruit Unified Sensor"
    - "WiFi" (bundled with ESP32 board package)
    - "HTTPClient" (bundled with ESP32 board package)
  =====================================================================
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// ---------------------- USER CONFIGURATION -------------------------

// Wi-Fi credentials
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ThingSpeak
const char* TS_API_KEY   = "YOUR_THINGSPEAK_WRITE_API_KEY";
const char* TS_SERVER    = "http://api.thingspeak.com/update";

// IFTTT Webhooks (used for email alerts -- see report Section 5)
const char* IFTTT_EVENT_NAME = "weather_alert";
const char* IFTTT_KEY        = "YOUR_IFTTT_WEBHOOKS_KEY";
const char* IFTTT_SERVER     = "http://maker.ifttt.com/trigger";

// DHT22 sensor
#define DHT_PIN   4
#define DHT_TYPE  DHT22
DHT dht(DHT_PIN, DHT_TYPE);

// Alert thresholds (edit to your requirement)
const float TEMP_HIGH_THRESHOLD  = 38.0;  // deg C
const float TEMP_LOW_THRESHOLD   = 10.0;  // deg C
const float HUM_HIGH_THRESHOLD   = 85.0;  // % RH
const float HUM_LOW_THRESHOLD    = 20.0;  // % RH

// Timing
const unsigned long UPLOAD_INTERVAL = 20000;   // ThingSpeak free tier: >=15s
const unsigned long ALERT_COOLDOWN  = 300000;  // 5 min between repeat alerts

// ---------------------------------------------------------------------

unsigned long lastUploadTime = 0;
unsigned long lastAlertTime  = 0;

void connectWiFi() {
  Serial.print("Connecting to Wi-Fi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected. IP address: ");
  Serial.println(WiFi.localIP());
}

// ---- Question 2: Sensor interfacing -------------------------------
bool readSensor(float &temperature, float &humidity) {
  temperature = dht.readTemperature();   // Celsius
  humidity    = dht.readHumidity();      // % RH

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("ERROR: Failed to read from DHT22 sensor!");
    return false;
  }
  return true;
}

// ---- Question 3: Cloud data upload ---------------------------------
bool uploadToThingSpeak(float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, skipping upload.");
    return false;
  }

  HTTPClient http;
  String url = String(TS_SERVER) + "?api_key=" + TS_API_KEY +
               "&field1=" + String(temperature, 2) +
               "&field2=" + String(humidity, 2);

  http.begin(url);
  int httpCode = http.GET();

  bool success = false;
  if (httpCode > 0) {
    String response = http.getString();
    // ThingSpeak returns the new entry ID (0 = failure, e.g. rate limited)
    if (response.toInt() > 0) {
      Serial.println("ThingSpeak update OK, entry #" + response);
      success = true;
    } else {
      Serial.println("ThingSpeak update failed, response: " + response);
    }
  } else {
    Serial.println("HTTP GET failed, error: " + http.errorToString(httpCode));
  }
  http.end();
  return success;
}

// ---- Question 5: Alert mechanism ------------------------------------
void checkAndSendAlert(float temperature, float humidity) {
  bool tempAlert = (temperature > TEMP_HIGH_THRESHOLD) || (temperature < TEMP_LOW_THRESHOLD);
  bool humAlert  = (humidity > HUM_HIGH_THRESHOLD)   || (humidity < HUM_LOW_THRESHOLD);

  if (!tempAlert && !humAlert) return;

  unsigned long now = millis();
  if (now - lastAlertTime < ALERT_COOLDOWN) {
    return;  // avoid spamming inbox
  }

  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  String url = String(IFTTT_SERVER) + "/" + IFTTT_EVENT_NAME + "/with/key/" + IFTTT_KEY;

  String reason = tempAlert ? "Temperature" : "Humidity";
  String value1 = "Weather Alert: " + reason + " threshold crossed";
  String value2 = "Temp=" + String(temperature, 1) + "C";
  String value3 = "Humidity=" + String(humidity, 1) + "%";

  String payload = "{\"value1\":\"" + value1 + "\",\"value2\":\"" + value2 +
                    "\",\"value3\":\"" + value3 + "\"}";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    Serial.println("Alert triggered: " + payload);
    lastAlertTime = now;
  } else {
    Serial.println("Failed to trigger IFTTT alert.");
  }
  http.end();
}

// ---- Question 1 (reference): system architecture ---------------------
// DHT22 --(digital data pin)--> ESP32 --(Wi-Fi/HTTP)--> ThingSpeak Cloud
//   ESP32 also --(HTTP POST)--> IFTTT Webhooks --> Email alert
// See report Section 1 / block_diagram.png for the full diagram.

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  unsigned long currentTime = millis();
  if (currentTime - lastUploadTime >= UPLOAD_INTERVAL) {
    lastUploadTime = currentTime;

    float temperature, humidity;
    if (readSensor(temperature, humidity)) {
      Serial.printf("Temp: %.2f C  Humidity: %.2f %%\n", temperature, humidity);
      uploadToThingSpeak(temperature, humidity);
      checkAndSendAlert(temperature, humidity);
    }
  }

  delay(100);
}
