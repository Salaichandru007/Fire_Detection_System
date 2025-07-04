#include "esp_camera.h"
#include <WiFi.h>

#include <Arduino.h>
#include <WiFiClientSecure.h>
#include <FirebaseClient.h>

#define CAMERA_MODEL_AI_THINKER // Has PSRAM
#include "camera_pins.h"
#include "config.h"


void startCameraServer();
void setupLedFlash(int pin);
const int flameSensorPin = 14;
const int mq135SensorPin = 13;
const int buzzerPin= 12;
static bool alertSent = false;


// Firebase setup
void processData(AsyncResult &aResult);
UserAuth user_auth(WEB_API_KEY, USER_EMAIL, USER_PASS);
FirebaseApp app;
WiFiClientSecure ssl_client;
using AsyncClient = AsyncClientClass;
AsyncClient aClient(ssl_client);
RealtimeDatabase Database;

// Timing
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 10000; // 10 seconds

// Data variables
int flameSensorValue = 1;
int mq135SensorValue = 1;
String fireStatus = "No Fire";

void setup() {
  Serial.begin(115200);
  pinMode(flameSensorPin,INPUT);
  pinMode(mq135SensorPin,INPUT);
  pinMode(buzzerPin,OUTPUT);
  Serial.setDebugOutput(true);
  Serial.println();

  // Start with off
  digitalWrite(buzzerPin, LOW);

  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash(LED_GPIO_NUM);
#endif

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  WiFi.setSleep(false);

  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

    // Firebase
  ssl_client.setInsecure();
  ssl_client.setConnectionTimeout(1000);
  ssl_client.setHandshakeTimeout(5);
  initializeApp(aClient, app, getAuth(user_auth), processData, "🔐 authTask");
  app.getApp<RealtimeDatabase>(Database);
  Database.url(DATABASE_URL);
}

void loop() {
  app.loop();

  if (app.ready()) {
    unsigned long currentTime = millis();
    if (currentTime - lastSendTime >= sendInterval) {
      lastSendTime = currentTime;

      // Read sensor
      flameSensorValue = digitalRead(flameSensorPin);  // 0 = flame detected, 1 = no flame
      mq135SensorValue = digitalRead(mq135SensorPin);  // 0 = smoke detected, 1 = no smoke

       // --- Fire Detection Logic ---
      if (flameSensorValue == 0 || mq135SensorValue == 0) {
        fireStatus = "Fire Detected";
        if(!alertSent){
          for(int i=0;i<5;i++){
           digitalWrite(buzzerPin, HIGH); // Activate buzzer
           delay(500);
           digitalWrite(buzzerPin, LOW); // Deactivate buzzer
           delay(500);
          }
          alertSent=true;
        }       
      } else {
        fireStatus = "No Fire";
        alertSent = false;
      }
      // --- END Fire Detection Logic ---

      // Log to Serial
      Serial.print("Flame Sensor Value: ");
      Serial.println(flameSensorValue);
      Serial.print("MQ135 Sensor Value: ");
      Serial.println(mq135SensorValue);
      Serial.print("Fire Status: ");
      Serial.println(fireStatus);

      // Send to Firebase
      Database.set<int>(aClient, "/sensor/flame", flameSensorValue, processData, "Send_Flame_Value");
      Database.set<int>(aClient, "/sensor/mq135", mq135SensorValue, processData, "Send_MQ135_Value");
      Database.set<String>(aClient, "/sensor/status", fireStatus, processData, "Send_Fire_Status");

    }
  }

  
  // Do nothing. Everything is done in another task by the web server
//  delay(10000);
}

void processData(AsyncResult &aResult) {
  if (!aResult.isResult()) return;

  if (aResult.isEvent())
    Firebase.printf("Event task: %s, msg: %s, code: %d\n", aResult.uid().c_str(), aResult.eventLog().message().c_str(), aResult.eventLog().code());

  if (aResult.isDebug())
    Firebase.printf("Debug task: %s, msg: %s\n", aResult.uid().c_str(), aResult.debug().c_str());

  if (aResult.isError())
    Firebase.printf("Error task: %s, msg: %s, code: %d\n", aResult.uid().c_str(), aResult.error().message().c_str(), aResult.error().code());

  if (aResult.available())
    Firebase.printf("task: %s, payload: %s\n", aResult.uid().c_str(), aResult.c_str());
}
