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
  LEFT_SPACING_2_3,
  LEFT_CUMULATIVE_3,
  LEFT_CUMULATIVE_3_LOOP,
};

uint8_t mode;
bool modeNodeMode = true;
// 24       16       8      0
// 11111111_11111111_11111111
uint32_t ledCache;
bool buttonState = false;
bool lastButtonState = false;

unsigned long lastTime = -PERIOD;
unsigned long lastDebounceTime;

void update(void);
void setMod(uint8_t mode);

void setup() {
  Serial.begin(9600);

  pinMode(BTN_PIN, INPUT_PULLUP);

  pinMode(DATA_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);

  setMod(LEFT_SPACING_2_3);
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
      if (++mode > LEFT_CUMULATIVE_3_LOOP) mode = 0;

      setMod(mode);

      Serial.println("--------------------");
    }
  }
  lastButtonState = reading;

  if (nowTime >= lastTime + PERIOD) {
    lastTime = nowTime;
    switch (mode) {
      case LEFT_TO_RIGHT:
      case LEFT_SPACING_3:
      case LEFT_SPACING_4:
      case LEFT_SPACING_2_3:
        ledCache <<= 1;
        if (ledCache >> 24 || ledCache <= 0) {
          ledCache &= 0xffffff;
          ledCache |= 1;
        }
        break;
      case RIGHT_TO_LEFT:
        ledCache >>= 1;
        if (ledCache <= 0) {
          ledCache = 0x800000;  // 0b100000000000000000000000
        }
        break;
      case LEFT_CUMULATIVE_3:
        ledCache <<= 1;
        ledCache |= 0x10101;
        if (ledCache >> 24) {
          ledCache = 0x10101;
        }
        break;
      case LEFT_CUMULATIVE_3_LOOP:
        if (modeNodeMode) {
          ledCache <<= 1;
          ledCache |= 0x10101;
          if (ledCache >> 24) {
            modeNodeMode = false;
          }
        } else {
          uint8_t tmp = ledCache & ((ledCache & 0xff) >> 1);

          ledCache = tmp;
          for (uint8_t i = 0; i < 2; i++) {
            ledCache <<= 8;
            ledCache |= tmp;
          }
          if (ledCache <= 0) {
            ledCache = 0x10101;
            modeNodeMode = true;
          }
        }
        break;
    }

    update();
  }
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
  Serial.println("--------");
}

void setMod(uint8_t _mode) {
  switch (_mode) {
    case RIGHT_TO_LEFT:
    case LEFT_TO_RIGHT:
      ledCache = 0;
      break;
      // RIGHT_TO_LEFT
    case LEFT_SPACING_4:
      ledCache = 0x820820;
      break;
    case LEFT_SPACING_2_3:
      ledCache = 0xe00e00;
      break;
    case LEFT_SPACING_3:
    case LEFT_CUMULATIVE_3:
    case LEFT_CUMULATIVE_3_LOOP:
      ledCache = 0x10101;
      break;
  }

  mode = _mode;
  modeNodeMode = true;
  Serial.print("setMode: ");
  Serial.println(mode);
}
