
#include <ESP32Servo.h>

// MOTOR L298N
#define IN1 26
#define IN2 27
#define ENA 14

// IR SENSOR
#define IR_SENSOR_1 17
#define IR_SENSOR_2 13

// SERVO
#define SERVO_PIN_1 19
#define SERVO_PIN_2 18

Servo servo1;
Servo servo2;

// Mau YOLO nhan duoc
String currentColor = "NONE";

int previousIR1 = HIGH;
int previousIR2 = HIGH;

// Thoi gian giu servo tai goc gat
const unsigned long SERVO_HOLD_MS = 700;

// Toc do gat ra cho ca hai servo
const unsigned long SERVO_STEP_MS = 2;
const int SERVO_STEP_DEG = 4;

// SERVO 1 - GREEN
int servo1Angle = 130;
unsigned long servo1MoveTime = 0;
unsigned long servo1HoldStart = 0;
bool servo1Active = false;
bool servo1Holding = false;

// SERVO 2 - RED
int servo2Angle = 130;
unsigned long servo2MoveTime = 0;
unsigned long servo2HoldStart = 0;
bool servo2Active = false;
bool servo2Holding = false;


// Nhan mau tu Python qua Serial
void readSerialColor() {
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();

    if (command == "GREEN" ||
        command == "RED" ||
        command == "BLUE") {

      currentColor = command;

      Serial.print("Nhan mau YOLO: ");
      Serial.println(currentColor);
    }
  }
}


// Dieu khien servo GREEN
void controlGreenServo() {
  if (!servo1Active) {
    return;
  }

  unsigned long now = millis();

  // Gat ra nhanh tu 130 do den 40 do
  if (servo1Angle > 40) {
    if (now - servo1MoveTime >= SERVO_STEP_MS) {
      servo1MoveTime = now;

      servo1Angle -= SERVO_STEP_DEG;

      if (servo1Angle < 40) {
        servo1Angle = 40;
      }

      servo1.write(servo1Angle);
    }
  }

  // Giu tai goc gat 700 ms
  if (servo1Angle == 40) {
    if (!servo1Holding) {
      servo1Holding = true;
      servo1HoldStart = now;
    }

    if (now - servo1HoldStart >= SERVO_HOLD_MS) {
      // Quay ve vi tri ban dau ngay
      servo1.write(130);
      servo1Angle = 130;
      servo1Active = false;
      servo1Holding = false;

      Serial.println("Servo GREEN da quay ve 130 do");
    }
  }
}


// Dieu khien servo RED
void controlRedServo() {
  if (!servo2Active) {
    return;
  }

  unsigned long now = millis();

  // Gat ra nhanh tu 130 do den 40 do
  if (servo2Angle > 40) {
    if (now - servo2MoveTime >= SERVO_STEP_MS) {
      servo2MoveTime = now;

      servo2Angle -= SERVO_STEP_DEG;

      if (servo2Angle < 40) {
        servo2Angle = 40;
      }

      servo2.write(servo2Angle);
    }
  }

  // Giu tai goc gat 700 ms
  if (servo2Angle == 40) {
    if (!servo2Holding) {
      servo2Holding = true;
      servo2HoldStart = now;
    }

    if (now - servo2HoldStart >= SERVO_HOLD_MS) {
      // Quay ve vi tri ban dau ngay
      servo2.write(130);
      servo2Angle = 130;
      servo2Active = false;
      servo2Holding = false;

      Serial.println("Servo RED da quay ve 130 do");
    }
  }
}


void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);

  pinMode(IR_SENSOR_1, INPUT);
  pinMode(IR_SENSOR_2, INPUT);

  servo1.attach(SERVO_PIN_1);
  servo2.attach(SERVO_PIN_2);

  servo1.write(130);
  servo2.write(130);

  // Motor chay tien
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 150);

  Serial.println("Color sorting ready");
}


void loop() {
  readSerialColor();

  int sensor1 = digitalRead(IR_SENSOR_1);
  int sensor2 = digitalRead(IR_SENSOR_2);

  // ==========================================
  // CUM 1: GREEN + IR1 -> SERVO1
  // ==========================================
  if (previousIR1 == HIGH && sensor1 == LOW) {
    Serial.println("IR1 phat hien vat");

    if (currentColor == "GREEN" && !servo1Active) {
      Serial.println("GREEN + IR1 -> SERVO1");

      servo1Active = true;
      servo1Holding = false;
      servo1MoveTime = millis();
      servo1HoldStart = 0;

      currentColor = "NONE";
    } else {
      Serial.println("IR1: Sai mau hoac servo dang hoat dong");
    }
  }

  // ==========================================
  // CUM 2: RED + IR2 -> SERVO2
  // ==========================================
  if (previousIR2 == HIGH && sensor2 == LOW) {
    Serial.println("IR2 phat hien vat");

    if (currentColor == "RED" && !servo2Active) {
      Serial.println("RED + IR2 -> SERVO2");
      delay(250);
      servo2Active = true;
      servo2Holding = false;
      servo2MoveTime = millis();
      servo2HoldStart = 0;

      currentColor = "NONE";
    } else {
      Serial.println("IR2: Sai mau hoac servo dang hoat dong");
    }
  }

  previousIR1 = sensor1;
  previousIR2 = sensor2;

  // Cap nhat hai servo doc lap
  controlGreenServo();
  controlRedServo();

  delay(1);
}