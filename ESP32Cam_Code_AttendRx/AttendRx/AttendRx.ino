#include <Arduino.h>
#include <WiFi.h>
#include "WifiCam.hpp"

static const char* WIFI_SSID = "Attendance";
static const char* WIFI_PASS = "12345678";
esp32cam::Resolution initialResolution;

void setup() {
  Serial.begin(115200);
  delay(2000);  // Delay to allow serial monitor to initialize

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("WiFi connected, IP address: ");
  Serial.println(WiFi.localIP());

  // Initialize camera
  using namespace esp32cam;
  initialResolution = Resolution::find(1024, 768);  // Set desired resolution
  Config cfg;
  cfg.setPins(pins::AiThinker);  // Set camera module type
  cfg.setResolution(initialResolution);
  cfg.setJpeg(80);  // Set JPEG quality (0-100)

  bool camera_ok = Camera.begin(cfg);
  if (!camera_ok) {
    Serial.println("Camera initialization failed!");
    while (1);  // Halt program if camera fails to initialize
  }

  Serial.println("Camera initialized");
}

void loop() {
  // Your camera-related code or operations can go here
  // Example: capturing images, performing face recognition, streaming video, etc.
  delay(1000);  // Add a delay between operations
}
