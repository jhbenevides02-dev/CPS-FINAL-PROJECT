// TestPuppetScene
// One scene, two actors, each on its own stepper rail. Follows the state machine diagram:
// IDLE -> (HOMING first time) -> Showing: MOVE_12 -> MOVE_21 -> HOLD -> (DANCE) -> ... -> EXIT -> IDLE
//
// Board: Arduino Nano. Library: AccelStepper.
// Serial Monitor at 115200 baud, commands:
//   s = startEvent (both actors)
//   h = heartGesture (both actors)
//   p = print status
//
// Each actor is made of 3 pieces that always travel together:
//   xxxSetup   -> fixed values (name, rail limits, speed, home pin)
//   xxxState   -> values that change while running (state, count, flags)
//   xxxStepper -> the motor object
//
// Values marked TODO are placeholders to be replaced with the real ones.

#include <AccelStepper.h>

// ---------------------------------------------------------------- Timings (ms) TODO
const unsigned long T_IDLE_WAIT = 1000;  // wait after startEvent before showing
const unsigned long HOLD_MS     = 2000;  // max wait in HOLD (tHold)

// ---------------------------------------------------------------- Motion TODO
const long  DANCE_STEPS   = 200;   // dance wiggle amplitude
const int   DANCE_REPEATS = 3;     // number of wiggles
const float HOMING_SPEED  = 200;   // steps/s while homing
const long  HOMING_MARGIN = 200;   // extra steps beyond the rail before homing gives up

// ---------------------------------------------------------------- State machine states
enum State : uint8_t { IDLE, HOMING, MOVE_12, MOVE_21, HOLD, DANCE, EXIT };
const char* const STATE_NAMES[] = {"IDLE", "HOMING", "MOVE_12", "MOVE_21", "HOLD", "DANCE", "EXIT"};

// ---------------------------------------------------------------- Actor setup (fixed values)
struct ActorSetup {
  const char* name;
  long minSteps;     // pos 1 (virtual encoder, steps from the home switch)
  long maxSteps;     // pos 2 (steps from the home switch)
  int  direction;    // +1: scene is in the positive direction from home, -1: negative
  float speed;       // steps/s
  float accel;       // steps/s^2
  uint8_t homePin;   // home switch to GND, active LOW (INPUT_PULLUP)
};

const ActorSetup CATRINA_SETUP = { // dir +1 starts on the lefit, dir -1 starts from the right
  // name,     min, max,  dir, speed, accel, homePin   TODO
  "catrina",   0,   2048, +1,  500,   200,   2
};

const ActorSetup MARIACHI_SETUP = {
  // name,     min, max,  dir, speed, accel, homePin   TODO
  "mariachi",    0,   2048, -1,  500,   200,   3
};

// ---------------------------------------------------------------- Actor state (changes while running)
struct ActorState {
  State state = IDLE;
  bool enabled = true;
  bool firstTime = true;
  bool startEvent = false;
  bool heartGesture = false;
  bool heartCast = false;
  bool idleWaiting = false;
  int  count = 0;
  int  danceIdx = 0;
  unsigned long stateStartMs = 0;
};

ActorState catrinaState;
ActorState mariachiState;

// ---------------------------------------------------------------- Steppers
// Pin order is IN1, IN3, IN2, IN4 (required for the 28BYJ-48)
//                                      mode,                 IN1, IN3, IN2, IN4
AccelStepper catrinaStepper (AccelStepper::FULL4WIRE,  8,  10,  9,   11);   // driver pins 8, 9, 10, 11
AccelStepper mariachiStepper(AccelStepper::FULL4WIRE,  4,  6,   5,   7);    // driver pins 4, 5, 6, 7

// ---------------------------------------------------------------- Helpers
long pos1(const ActorSetup &setup) { return setup.direction * setup.minSteps; } // setup refers to the struct ActorStup
long pos2(const ActorSetup &setup) { return setup.direction * setup.maxSteps; }
bool homeSwitchPressed(const ActorSetup &setup) { return digitalRead(setup.homePin) == LOW; }

bool anyHoming() {
  return (catrinaState.enabled && catrinaState.state == HOMING) ||
         (mariachiState.enabled && mariachiState.state == HOMING);
}


// Function to update the state of an actor
void setState(const ActorSetup &setup, ActorState &actor, State newState) {
  actor.state = newState;
  actor.stateStartMs = millis();
  Serial.print(setup.name);
  Serial.print(" -> ");
  Serial.println(STATE_NAMES[newState]);
}



// *********************************************************
// ******************** State machine **********************
// *********************************************************
// Starts the homing: slow speed, move away from the scene until the home switch is pressed. Goes to HOMING.
void startHoming(const ActorSetup &setup, ActorState &actor, AccelStepper &stepper){

  stepper.setMaxSpeed(HOMING_SPEED);// use a slow speed while homing
  stepper.moveTo(-setup.direction * (setup.maxSteps + HOMING_MARGIN)); // Check directions when fully build
  setState(setup, actor, HOMING);
}

// Starts a show: reset count, heartCast, heartGesture and startEvent, move to pos 2. Goes to MOVE_12.
void startShowing(const ActorSetup &setup, ActorState &actor, AccelStepper &stepper);

//**************************************Let it Cook***************************************
// Runs ONE step of the state machine for one actor (called every loop, never blocks, no delay()).
//   IDLE    : first time -> start homing (one actor at a time); startEvent -> wait T_IDLE_WAIT -> startShowing()
//   HOMING  : home switch pressed -> zero position, restore speed, firstTime = false -> IDLE.
//             Rail travelled without finding the switch -> disable the actor and print an error
//   MOVE_12 : arrived at pos 2 -> move back to pos 1 -> MOVE_21
//   MOVE_21 : arrived at pos 1 -> count++ -> HOLD if count <= 2, otherwise EXIT
//   HOLD    : heartGesture and count == 2 -> DANCE; HOLD_MS elapsed -> move to pos 2 -> MOVE_12
//   DANCE   : wiggle DANCE_REPEATS times around pos 1 -> MOVE_21
//   EXIT    : print "done <name>" -> IDLE
void updateActor(const ActorSetup &setup, ActorState &actor, AccelStepper &stepper){
  
  switch (actor.state) {
  case IDLE:
    if (actor.firstTime && !anyHoming()) startHoming(setup, actor, stepper);
    //checks if it is the firs power up and any other actor is homming
    break;
  case HOMING:
    if (homeSwitchPressed(setup)) {
      
      stepper.setCurrentPosition (0);// Set current position as zero home
      stepper.setMaxSpeed(setup.speed); // Set normal max speed
      stepper. moveTo(pos1(setup)); // uses the helper pos1

      actor.firstTime = false; //end homing
      setState(setup, actor, IDLE); // update state

    }

    else if (stepper.distanceToGo() == 0){
      actor.enabled = false;
      Serial.print (setup.name);
      Serial.println(" --> Error, check limit switch");
    }
    // 2. switch pressed? 3. rail finished without the switch?
    break;
  default:        // the other states are written later
    break;
}
}

// ---------------------------------------------------------------- Serial commands
// Prints name, state, stepper position, count and enabled for one actor.
void printStatus(const ActorSetup &setup, ActorState &actor, AccelStepper &stepper);

// Raises startEvent for one actor, only if it is enabled and in IDLE.
void sendStartEvent(ActorState &actor);

// Raises heartGesture for one actor, only if it is enabled and not in IDLE or HOMING.
void sendHeartGesture(ActorState &actor);

// Reads the Serial Monitor: 's' = startEvent, 'h' = heartGesture, 'p' = print status (all actors).
void handleSerial();

// ---------------------------------------------------------------- Actor setup and run
// Configures one actor: home pin as INPUT_PULLUP, stepper max speed and acceleration from its setup.
void setupActor(const ActorSetup &setup, AccelStepper &stepper){
  
  pinMode(setup.homePin, INPUT_PULLUP); // Setup carriages limit switches
  stepper.setMaxSpeed(setup.speed);     // Setup stepper max speed
  stepper.setAcceleration(setup.accel); // Setup stepper acceleration
}

// Called every loop for one actor: skip if disabled, call stepper.run(), then updateActor().
void runActor(const ActorSetup &setup, ActorState &actor, AccelStepper &stepper){
  
  if (!actor.enabled) return; // only runs if the actor is enable
  updateActor(setup, actor, stepper); // update actor states (State machine)
  stepper.run(); // calling run as often as possible
}

// ---------------------------------------------------------------- Arduino
void setup() {

  Serial.begin(115200);
  setupActor(CATRINA_SETUP, catrinaStepper);
  setupActor(MARIACHI_SETUP, mariachiStepper);
  Serial.println("TestPuppetScene ready. Commands: s = startEvent, h = heartGesture, p = status");

}

void loop() {
  //handleSerial();
  
  runActor(CATRINA_SETUP, catrinaState, catrinaStepper);
  runActor(MARIACHI_SETUP, mariachiState, mariachiStepper);
}
