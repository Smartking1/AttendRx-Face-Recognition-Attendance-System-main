#include "WifiCam.hpp"
#include <WiFi.h>
#include <Wire.h>             
#include "images.h"
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,20,4);  // set the LCD address to 0x27 for a 16 chars and 2 line display
 
int demoMode = 0;
int counter = 0;

static const char* WIFI_SSID = "Attendance";
static const char* WIFI_PASS = "12345678";

esp32cam::Resolution initialResolution;

WebServer server(80);
 

 
void setup()
{
    lcd.init();
  // Print a message to the LCD.
  lcd.backlight();
  Serial.begin(9600);
  Serial.println();
  delay(2000);

  lcd.setCursor(0,0);
  lcd.print("ATTENDANCE ");
  lcd.setCursor(1,0);
  lcd.print("STARTED ");
  delay(2500);
  lcd.clear();
  
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("WiFi failure");
     
    delay(5000);
    ESP.restart();
  }
  Serial.println("WiFi connected");
//  write("Wifi\nConnected!", "left", 24);
  delay(1000);
  {
    using namespace esp32cam;

    initialResolution = Resolution::find(1024, 768);

    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(initialResolution);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    if (!ok) {
      Serial.println("camera initialize failure");
       lcd.print("CAMERA ");
  lcd.setCursor(1,0);
    lcd.print("FAILED ");
    delay(2500);
    lcd.clear();
      ESP.restart();
    }
    Serial.println("camera initialize success");
    lcd.setCursor(0,0);
  lcd.print("Connected");
  
    delay(2000);
    lcd.clear();
  }

  Serial.println("camera starting");
   lcd.setCursor(0,0);
  lcd.print("CAMERA ");
  lcd.setCursor(1,0);
    lcd.print("STARTING ");
    delay(2500);
    lcd.clear();
    
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  lcd.setCursor(0,0);
  lcd.print("Connected");
  delay(2500);
lcd.clear();

  addRequestHandlers();
  server.begin();
}

void
loop()
{
  server.handleClient();
}
