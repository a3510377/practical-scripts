#include <Arduino.h>

#define BTN_PIN 10
#define PERIOD 200

#define DATA_PIN 2
#define LATCH_PIN 3
#define CLOCK_PIN 4

const unsigned long debounceDelay = 50;

enum Mode {
  RIGHT_TO_LEFT,
  LEFT_TO_RIGHT,
  LEFT_SPACING_3,
  LEFT_SPACING_4,
};

uint8_t mode = RIGHT_TO_LEFT;
// 24       16       8      0
// 11111111_11111111_11111111
uint32_t ledCache;
bool buttonState;
bool lastButtonState = false;

unsigned long lastTime = -PERIOD;
unsigned long lastDebounceTime;

void update();

void setup() {
  Serial.begin(9600);

  pinMode(BTN_PIN, INPUT_PULLUP);

  pinMode(DATA_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
}

void loop() {
  // 以下為去抖動範例的
  unsigned long nowTime = millis();
  bool reading = digitalRead(BTN_PIN);

  if (reading != lastButtonState) {
    lastDebounceTime = nowTime;
  }
  if ((nowTime - lastDebounceTime) > debounceDelay && reading != buttonState) {
    buttonState = reading;

    if (buttonState) {
      if (++mode > LEFT_SPACING_4) mode = 0;

      switch (mode) {
        case RIGHT_TO_LEFT:
        case LEFT_TO_RIGHT:
          ledCache = 0;
          break;
          // RIGHT_TO_LEFT
        case LEFT_SPACING_3:
          ledCache = 0x808080;
          break;
        case LEFT_SPACING_4:
          ledCache = 0x20820;
          break;
      }

      Serial.println("--------------------");
    }
  }
  lastButtonState = reading;

  if (nowTime >= lastTime + PERIOD) {
    lastTime = nowTime;
    switch (mode) {
      case RIGHT_TO_LEFT:
        ledCache >>= 1;
        if (ledCache <= 0) {
          ledCache = 0x800000;  // 0b100000000000000000000000
        }
        break;
      case LEFT_TO_RIGHT:
        ledCache <<= 1;
        if (ledCache > 0xffffff || ledCache <= 0) {
          ledCache = 1;
        }
        break;
      case LEFT_SPACING_3:
        ledCache <<= 1;
        if (!(ledCache & 0xff)) {
          ledCache |= 1;
        }
        break;
      case LEFT_SPACING_4:
        ledCache <<= 1;
        if (!(ledCache & 0x3f)) {
          ledCache |= 1;
        }
        break;
    }

    update();
  }

  Serial.println("--------");
}

void update() {
  digitalWrite(LATCH_PIN, LOW);
  uint32_t tmpLedCache = ~ledCache;
  for (uint8_t i = 0; i <= 2; i++) {
    Serial.print(i);
    Serial.print(". ");
    Serial.println(tmpLedCache & 0xff, 2);
    shiftOut(DATA_PIN, CLOCK_PIN, LSBFIRST, tmpLedCache & 0xff);
    tmpLedCache >>= 8;
  }
  digitalWrite(LATCH_PIN, HIGH);
}
