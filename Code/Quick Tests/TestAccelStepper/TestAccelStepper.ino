// Accel Stepper

#include <AccelStepper.h>

#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11

const int STEPS_X_REV = 2048;

int maxSpeed = 500; // steps per second
int acceleration = 200; // steps per second

/******************************************************************************************************
  How to find your motor’s limit

    Set setAcceleration() to about 200 and keep it fixed.
    Raise setMaxSpeed() by 100 each time: 600, 700, 800 and so on.
    When it starts to buzz, skip steps or stall, go back about 20% below that value.
    Check that the position after a round trip still matches by looking at the shaft marking.
********************************************************************************************************/

AccelStepper motStepper(AccelStepper::FULL4WIRE, IN1, IN3, IN2, IN4); //4 control pins in full-step mode, the same as Stepper.h.

void setup() {

  Serial.begin(115200);

  motStepper.setMaxSpeed(maxSpeed);       // steps per second (not RPM)
  motStepper.setAcceleration(acceleration);   // steps per second squared
  motStepper.moveTo(STEPS_X_REV);    // target: one revolution
}

void loop() {

  if (motStepper.distanceToGo() == 0) {   // reached target
    delay(1000);
    motStepper.moveTo(-motStepper.currentPosition());   // go to the opposite side
    Serial.println(motStepper.currentPosition());

    /* Use move() when you want “N steps from here” and moveTo() when you want “go to position X”. */
  }
  /* To fix the two revolution issue using the code above
    if (motStepper.currentPosition() == 0) {
      motStepper.moveTo(STEPS_X_REV);   // at the start: go one revolution forward
    } else {
      motStepper.moveTo(0);             // at the far end: go back to the start
    }
  */

  motStepper.run();   // must be called as often as possible
}
