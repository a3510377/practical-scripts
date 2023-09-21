#define BTN_PIN 10
#define PERIOD 200
#define START_PIN 2
#define STOP_PIN 9

const unsigned long debounceDelay = 50;

bool modeState = true;  // false: 右至左; true: 左至右
bool buttonState;
bool lastButtonState = false;

unsigned long lastTime = -PERIOD;
unsigned long lastDebounceTime;

int index = START_PIN - 1;

void setup() {
  Serial.begin(9600);

  pinMode(BTN_PIN, INPUT_PULLUP);
  for (uint8_t pin = START_PIN; pin <= STOP_PIN; pin++) {
    pinMode(pin, OUTPUT);
  }
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
      modeState = !modeState;
      Serial.println("--------------------");
    }
  }

  lastButtonState = reading;

  // 以下為
  if (nowTime >= lastTime + PERIOD) {
    lastTime = nowTime;

    digitalWrite(index, LOW);

    Serial.print("LOW: ");
    Serial.println(index);
    if (modeState) {
      if (++index > STOP_PIN) index = START_PIN;
    } else if (--index < START_PIN) index = STOP_PIN;

    digitalWrite(index, HIGH);
    Serial.print("HIGH: ");
    Serial.println(index);
    Serial.println("DELAY");
  }
}
