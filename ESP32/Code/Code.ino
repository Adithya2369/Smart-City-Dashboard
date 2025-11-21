#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASS";

String accessToken = "YOUR_ACCESS_TOKEN"; // Valid for 1 hour!

String spreadsheetId = "YOUR_SPREADSHEET_ID";

// Google requires TLS root certificate
const char* rootCACertificate =
"-----BEGIN CERTIFICATE-----\n"
"MIID..."
"-----END CERTIFICATE-----\n";

float randf(float a, float b) { return a + ((float)rand() / RAND_MAX) * (b - a); }

String getISODate() {
  time_t now = time(nullptr);
  struct tm *p = localtime(&now);
  char buf[20];
  strftime(buf, sizeof(buf), "%Y-%m-%d", p);
  return String(buf);
}

String getISOTime() {
  time_t now = time(nullptr);
  struct tm *p = localtime(&now);
  char buf[20];
  strftime(buf, sizeof(buf), "%H:%M:%S", p);
  return String(buf);
}

void sendToSheet(String sheetName, String rowDataJSON) {
  WiFiClientSecure client;
  client.setCACert(rootCACertificate);

  HTTPClient https;

  String url = "https://sheets.googleapis.com/v4/spreadsheets/" + spreadsheetId +
               "/values/" + sheetName + "!A1:append?valueInputOption=USER_ENTERED";

  Serial.println(url);

  if (https.begin(client, url)) {
    https.addHeader("Authorization", "Bearer " + accessToken);
    https.addHeader("Content-Type", "application/json");

    int httpCode = https.POST(rowDataJSON);

    Serial.print("Response code: ");
    Serial.println(httpCode);
    Serial.println(https.getString());

    https.end();
  } else {
    Serial.println("Connection failed!");
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("\nConnected.");
}

void loop() {

  String date = getISODate();
  String time = getISOTime();

  // ---------- WEATHER RANDOM ----------
  float temp = randf(25, 35);
  float hum = randf(40, 80);
  float press = randf(1005, 1015);
  float wind = randf(0.5, 8.0);
  float cloud = randf(0, 100);
  float sun = randf(200, 1100);

  String weatherJSON = "{\"values\": [[\"" + date + "\",\"" + time + "\"," +
                       temp + "," + hum + "," + press + "," + wind + "," +
                       cloud + "," + sun + "]]}";
  sendToSheet("Weather", weatherJSON);

  // ---------- NOISE RANDOM ----------
  float L1 = randf(40, 80);
  float L2 = randf(40, 80);
  float L3 = randf(40, 80);
  float L4 = randf(40, 80);

  String noiseJSON = "{\"values\": [[\"" + date + "\",\"" + time + "\"," +
                     L1 + "," + L2 + "," + L3 + "," + L4 + "]]}";
  sendToSheet("Noise", noiseJSON);

  // ---------- WASTE RANDOM ----------
  int B1 = rand() % 100;
  int B2 = rand() % 100;
  int B3 = rand() % 100;
  int B4 = rand() % 100;
  int B5 = rand() % 100;

  String wasteJSON = "{\"values\": [[\"" + date + "\",\"" + time + "\"," +
                     B1 + "," + B2 + "," + B3 + "," + B4 + "," + B5 + "]]}";
  sendToSheet("Waste", wasteJSON);

  // ---------- AIR QUALITY RANDOM ----------
  float AQI = randf(50, 150);
  float CO2 = randf(400, 900);
  float PM25 = randf(10, 60);
  float PM10 = randf(20, 90);
  float NO2 = randf(5, 30);
  float O3 = randf(5, 25);

  String airJSON = "{\"values\": [[\"" + date + "\",\"" + time + "\"," +
                   AQI + "," + CO2 + "," + PM25 + "," + PM10 + "," +
                   NO2 + "," + O3 + "]]}";
  sendToSheet("AirQuality", airJSON);

  Serial.println("Uploaded all rows.\n");

  delay(15000); // send every 15 seconds
}
