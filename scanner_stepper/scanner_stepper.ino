#include <Stepper.h>

const int stepsPerRevolution = 200;
const int maxRpm = 150;
const int ledPin = 10;
const int forwardSwitchPin = 12;
const int backwardSwitchPin = 8;
const int maxStepsPerDirection = 500;
Stepper stepper(stepsPerRevolution, 2, 4, 5, 6);
const int driverEnablePin = 3; // 490Hz
// http://homepage.cs.uiowa.edu/~jones/step/current.html
// duty-cycle = 0.49 = (0.6 A * 4.1 ohm) / (9.6 V_supply)
const int driverEnablePinValue = 0.6 * 4.1 / 9.6 * 255;
boolean movingForward = true;
int stepCounter = 0;

void setup() {
  Serial.begin(9600);
  pinMode(driverEnablePin, OUTPUT);
  pinMode(forwardSwitchPin, INPUT);
  pinMode(backwardSwitchPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(driverEnablePin, LOW);
  digitalWrite(LED_BUILTIN, LOW);
}

void playNote(int frequency, int duration) {
  float revolutionsPerMinute = frequency * 60.0 / stepsPerRevolution;
  float steps = 1.0 * frequency * duration / 1000.0;

  Serial.print("F: ");
  Serial.println(frequency);
  Serial.print("T: ");
  Serial.println(duration);
  Serial.print("RPM: ");
  Serial.println((int) revolutionsPerMinute);
  Serial.print("s: ");
  Serial.println((int) steps);

  if (revolutionsPerMinute > maxRpm) {
    Serial.println("Max RPM exceeded.");
    Serial.println();
    return;
  }

  Serial.println();

  stepper.setSpeed(revolutionsPerMinute);
  analogWrite(ledPin, map(revolutionsPerMinute, 1, maxRpm, 0, 255));

  analogWrite(driverEnablePin, driverEnablePinValue);

  int stepsLeft = steps;

  while (stepsLeft) {
    int stepsInThisLoop = min(stepsLeft, maxStepsPerDirection - stepCounter);

    if (movingForward) {
      stepper.step(stepsInThisLoop);
    }
    else {
      stepper.step(-stepsInThisLoop);
    }

    stepsLeft -= stepsInThisLoop;

    stepCounter += stepsInThisLoop;

    if (stepCounter >= maxStepsPerDirection) {
      stepCounter = 0;
      movingForward = !movingForward;
    }
  }

  digitalWrite(driverEnablePin, LOW);
  analogWrite(ledPin, 0);
}

int noteNumToFreq(int noteNum) {
  // http://en.wikipedia.org/wiki/Piano_key_frequencies
  return max(0, 440.0 * pow(1.05946, noteNum - 49));
}

void playRange() {
  for (int noteNum = 1; noteNum < 50; noteNum++) {
    playNote(noteNumToFreq(noteNum), 500);
  }
  for (int noteNum = 48; noteNum > 0; noteNum--) {
    playNote(noteNumToFreq(noteNum), 500);
  }
}

void playFromSerial() {
  if (!Serial.available()) {
    return;
  }

  int checkValue = Serial.parseInt();

  if (checkValue != -32) {
    if (checkValue) {
      Serial.println("Play data framing error.");
    }
    return;
  }

  int frequency = Serial.parseInt();

  if (frequency == -1) {
    int duration = Serial.parseInt();

    if (duration < 10 || duration > 10000) {
      Serial.println("Duration out of range.");
      return;
    }

    Serial.print("Silence: ");
    Serial.println(duration);
    delay(duration);
    return; 
  }

  if (frequency < 10 || frequency > 22000) {
    Serial.println("Frequency out of range.");
    return;
  }

  int duration = Serial.parseInt();

  if (duration < 10 || duration > 10000) {
    Serial.println("Duration out of range.");
    return;
  }

  playNote(frequency, duration);
}

void loop() {
  int forwardSwitchState = digitalRead(forwardSwitchPin);
  int backwardSwitchState = digitalRead(backwardSwitchPin);

  if (forwardSwitchState && backwardSwitchState) {
    playRange();
  }
  else if (forwardSwitchState || backwardSwitchState) {
    digitalWrite(LED_BUILTIN, HIGH);
    analogWrite(driverEnablePin, driverEnablePinValue);
    stepper.setSpeed(100);

    if (forwardSwitchState) {
      stepper.step(100);
    } 
    else {
      stepper.step(-100);
    }

    digitalWrite(driverEnablePin, LOW);
    digitalWrite(LED_BUILTIN, LOW);
  } 
  else {
    playFromSerial();
  }
}

















