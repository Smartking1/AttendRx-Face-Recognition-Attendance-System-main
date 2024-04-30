#include <Arduino.h>
#include <WiFi.h>
#include "WifiCam.hpp"

static const char* WIFI_SSID = "Attendance";
static const char* WIFI_PASS = "12345678";

esp32cam::Resolution initialResolution;

void setup() {
  Serial.begin(9600);
  Serial.println();
  delay(2000);

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("WiFi connection failed");
    delay(5000);
    ESP.restart();
  }
  Serial.println("WiFi connected");

  using namespace esp32cam;
  initialResolution = Resolution::find(1024, 768);
  Config cfg;
  cfg.setPins(pins::AiThinker);
  cfg.setResolution(initialResolution);
  cfg.setJpeg(80);

  bool camera_ok = Camera.begin(cfg);
  if (!camera_ok) {
    Serial.println("Camera initialization failed");
    ESP.restart();
  }
  Serial.println("Camera initialized");

  Serial.print("Local IP Address: ");
  Serial.println(WiFi.localIP());

  // You can add additional camera-related setup or operations here
}

void loop() {
  // You can add camera-related operations in the loop function
}
