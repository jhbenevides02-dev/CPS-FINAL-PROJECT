#include <Stepper.h>


#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11

const int STEPS_X_REV = 2048; // CX28BYJ48-08 kit motor resolution 2048 pulses to get 1 rev
int speed = 10;

Stepper stepperMotorTest(STEPS_X_REV, IN1, IN3, IN2, IN4);

void setup() {
  Serial.begin(115200);
  stepperMotorTest.setSpeed(speed); // stepper motor speed

}

void loop() {
  Serial.println("Clockwise");
  stepperMotorTest.step(STEPS_X_REV); // one revolution foward
  delay(1000);

  Serial.println("Counter-clockwise");
  stepperMotorTest.step(-STEPS_X_REV); // one revolution back
  delay(1000);
}
