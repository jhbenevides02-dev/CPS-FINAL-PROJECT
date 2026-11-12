# CPS Interactive Shadow Theatre — Group 20

_First draft (v0.1 of the new structure). Items marked **[TODO]** still need the team's input or evidence._

## Team members

- Ari Wang
- Christian Gutierrez
- Julia Benevides

## Table of contents

1. [How it works](#1-how-it-works)
2. [System design](#2-system-design)
   - [2.1 Mechanical design](#21-mechanical-design)
   - [2.2 Electrical and electronics](#22-electrical-and-electronics)
   - [2.3 Software](#23-software)
   - [2.4 Machine learning](#24-machine-learning)
3. [Debugging](#3-debugging)
4. [Project files](#4-project-files)
5. [References](#5-references)

---

# 1. How it works

## 1.1 Concept

This repository contains the design, hardware documentation, software and testing materials for our interactive shadow theatre, developed for the Cyber-Physical Systems (CPS) module.

Inspired by Plato's *Allegory of the Cave*, the project explores how light angles, mechanical movement and audience interaction can transform shadows and challenge our perception of reality.

The performance features two characters, **Catrina and Mariachi**, which move along independent rails and perform a coordinated dance in response to audience interaction.

[TODO: introduce the final installation: physical structure, mechanical movement, lighting and interactive features. Explain the "hidden layer" of the story.]

![Shadow Theatre](media/shadow-theatre.jpg)

## 1.2 User interaction

The audience uses two hand gestures in front of the webcam:

| Gesture (class) | What it does |
|---|---|
| **Action** | Starts the show. Both characters travel along their rails. |
| **Heart** | While the characters are waiting (HOLD), triggers the dance. |
| None | Nothing is sent; the show continues on its own timing. |

| Step | Audience action | System response | Shadow / story effect |
|---|---|---|---|
| 1 | Shows the **action** gesture | Reflector turns on, both characters move from position 1 to position 2 and back | [TODO] |
| 2 | Shows the **heart** gesture while the characters wait | Characters meet at the centre of the stage and dance (servo rotations and wiggles) | [TODO] |
| 3 | No gesture during the wait | After the hold time the characters repeat the walk once, then exit | [TODO] |
| 4 | — | Reflector turns off; after 5 s the theatre is ready for the next visitor | [TODO] |

[TODO: why these gestures fit the story; how visitors are told what to do.]

## 1.3 Demonstration

[TODO: insert a photo or GIF of the completed installation.]

[TODO: add a link to the demonstration video.]

## 1.4 System overview

`Hand gesture → Webcam → Python (MediaPipe hand landmarks) → Wekinator (classifier) → Python bridge → Arduino → Steppers, servos, reflector → Shadow performance`

The bridge also plays the music, following the state the Arduino reports.

![System Architecture](Code/Wekinator+PythonPipeline.png)

*Figure 1. Overall system pipeline.* [TODO: check this is the final diagram.]

---

# 2. System design

## 2.1 Mechanical design

The physical system consists of a modular theatre frame, a motor-driven character movement mechanism, and a lighting system that transforms moving silhouettes into projected shadows.

### Why a new mechanism instead of the robot arm

[TODO: written justification required by the brief: why the provided robot arm was replaced, and which parts were reused.]

### Theatre frame

The theatre is constructed using **cut wooden strips and custom 3D-printed connectors**. The frame supports the projection screen, internal rails, motors and lighting system while allowing convenient assembly and adjustments.

The modular structure was designed for stability, ease of fabrication and accessibility. A cut wooden frame holds translucent paper as the screen, with a custom 3D-printed light holder.

![Theatre Frame](media/mechanical/theatre-frame.jpg)

*Figure 2. Theatre frame CAD model and physical assembly.*

[TODO: dimensions, fit in the 605 × 370 × 280 mm box, materials, connector clearances.]

### Motion system and character mechanism

The movement system uses **two independent linear rails, belt-driven carriages and modular servo mechanisms** to create coordinated movements between the two shadow characters. It combines horizontal translation with individual character rotation.

**Mechanical motion flow:** `Stepper motor → GT2 timing belt → Linear carriage → Servo module → Laser-cut silhouette`

#### A. Belt-driven linear motion

Each rail is driven by a stepper motor through a GT2 timing belt, which converts rotation into horizontal movement so that both characters can approach the centre and return to their starting positions. The two independent rails allow separate movement control, while pulley alignment and belt tension help maintain consistent transmission.

| Rail | Travel (estimated) | Steps (estimated) |
|---|---|---|
| Catrina | 143 mm | 7293 |
| Mariachi | 137 mm | 6987 |

Each rail has a home switch, used to zero the carriage position at power-up.

![Belt Transmission](media/mechanical/belt-drive.jpg)

*Figure 3. Dual-rail layout and belt transmission mechanism.*

#### B. Linear bearing carriage and servo module

Each carriage moves along a linear guide supported by bearings. A custom belt clamp connects the carriage to the timing belt, while the sliding platform provides a stable mounting base for the character mechanism. The bearing-supported structure is designed to reduce friction, limit unwanted rotation and maintain stable movement.

![Linear Carriage](media/mechanical/carriage.jpg)

*Figure 4. Linear bearing, belt clamp and sliding carriage assembly.*

#### C. Laser-cut silhouettes

Catrina and Mariachi are designed as two-dimensional profiles and fabricated by **laser cutting**, so their outlines project clearly. Each silhouette is attached to a removable servo module mounted on the sliding carriage.

![Laser-Cut Silhouettes](media/mechanical/laser-cut-silhouettes.jpg)

*Figure 5. Laser-cut character designs and fabricated silhouettes.*

![Servo Module](media/mechanical/servo-module.jpg)

*Figure 6. Modular servo mechanism and silhouette attachment.*

### Exterior enclosure and finishing

The exterior enclosure surrounds the structural frame and conceals the internal mechanical and electronic components, creating a cohesive theatrical appearance. It keeps access to the internal mechanisms while providing a defined viewing area. Surface finishing and painting establish the visual identity of the theatre and separate the performance space from its supporting structure.

![Exterior Enclosure](media/mechanical/exterior-enclosure.jpg)

*Figure 7. Exterior enclosure design and final surface finishing.*

### Design decisions and options rejected

[TODO: e.g. belt vs. other linear drives, rail layout, light source options. Add evidence from tests.]

### Assembly

**Theatre frame**

1. Prepare the wooden strips and printed connectors.
2. Assemble the main supporting frame.
3. Secure the joints and check structural alignment.
4. Prepare mounting positions for the internal mechanisms.

**Internal motion system**

1. Install and align the linear guide rods.
2. Mount the motors and timing pulleys.
3. Install the GT2 timing belts and adjust their tension.
4. Attach the linear bearings and sliding carriages.
5. Connect each carriage to its timing belt.
6. Manually check the full movement range of both rails.

**Servo modules and silhouettes**

1. Prepare and laser-cut the Catrina and Mariachi silhouettes.
2. Assemble the 3D-printed servo holders.
3. Install the servo modules onto the carriages.
4. Attach the silhouettes to their holders.
5. Check attachment stability and rotation clearance.

**Exterior enclosure**

1. Prepare the exterior enclosure panels.
2. Check their fit against the assembled frame.
3. Complete surface preparation and painting, and let the finish cure.
4. Install the panels while keeping access to the internal mechanisms.

**Lighting and shadow alignment**

1. Install the translucent projection screen.
2. Mount the light source inside the theatre.
3. Adjust the light angle and projection distance.
4. Test shadow sharpness and scale.
5. Minimise overlapping or double shadows.
6. Secure the final lighting position.

[TODO: build photos for each stage.]

---

## 2.2 Electrical and electronics

_This section covers the **hardware** assessment criterion._

### Bill of materials

| Component | Quantity | Purpose |
|---|---|---|
| Arduino [TODO: Nano or Nano Every — the sketches state both] | 1 | Runs the stage state machine |
| 28BYJ-48 stepper motor + driver board [TODO: driver model] | 2 | Drives each carriage along its rail |
| Servo motor [TODO: model] | 2 | Rotates each silhouette during the dance |
| Home (limit) switch | 2 | Zeroes each carriage at power-up |
| Reflector light assembly [TODO: LED type] | 1 | Light source for the shadows |
| Laptop webcam | 1 | Gesture input |
| Power bank + power board (module kit) | 1 | 5 V DC supply |
| [TODO: other parts] | | |

[TODO: reason for each part and confirmation that it is on the approved list.]

### Wiring and circuit diagram

Pin assignments, from the current stage sketch (`Code/Quick Tests/TestPuppetScene`):

| Function | Catrina | Mariachi |
|---|---|---|
| Stepper driver IN1, IN2, IN3, IN4 | 8, 9, 10, 11 | 4, 5, 6, 7 |
| Servo signal | 15 | 16 |
| Home switch (to GND, `INPUT_PULLUP`, active LOW) | 3 | 2 |
| Reflector (shared, active LOW) | 14 | 14 |

![Circuit Diagram](media/electrical/circuit-diagram.png)

*Figure 8. Electrical circuit and hardware connections.* [TODO: circuit diagram.]

### Power estimate

[TODO: current of each stepper, servo and the reflector at idle and at peak, compared with the power bank rating. Measured values preferred.]

### Safe powering

- [TODO: confirm 5 V DC from the module power bank and power board only.]
- [TODO: confirm servos and steppers are not powered from the Arduino pins, and all grounds are common.]
- The sketch switches each stepper off (`disableOutputs`) while its servo rotates, and after the show (EXIT). [TODO: state whether this was done to limit current.]

### Electrical safety and power-on check

Before connecting or adjusting electrical components:

1. Disconnect all power sources.
2. Check for damaged cables and exposed connections.
3. Confirm that electrical components are securely mounted.
4. Verify the voltage and current requirements of motors, servos and lighting.
5. Ensure that cables will not interfere with moving mechanisms.

Before running the software:

1. Verify all electrical connections and power supply ratings.
2. Check that both carriages move freely by hand with power disconnected.
3. Ensure all moving parts are clear of cables and obstacles.
4. Power on the control system.
5. Test each motor and servo individually at low speed.
6. Verify lighting operation.

---

## 2.3 Software

### Pipeline and message formats

| Link | Protocol | Address / format |
|---|---|---|
| Webcam → `landmarks_sender.py` | USB video, MediaPipe | 21 hand landmarks × (x, y, z) |
| `landmarks_sender.py` → Wekinator | OSC over UDP | `127.0.0.1:6448`, `/wek/inputs`, 63 floats, 15 messages/s |
| Wekinator → `bridge.py` | OSC over UDP | `127.0.0.1:12000`, `/wek/outputs`, class as a float |
| `bridge.py` → Arduino | USB serial, 115200 baud | One character: `s` (class 2, action) or `h` (class 3, heart) |
| Arduino → `bridge.py` | USB serial | Text lines such as `catrina -> DANCE`, used for the music |

- The sender normalises the landmarks: the wrist is the origin and the wrist-to-middle-finger-base distance is the scale. If no hand is found, it sends 63 zeros.
- While the same class is held, the bridge re-sends its letter about every 250 ms. Class 1 (none) sends nothing.

![Software Pipeline](Code/Wekinator+PythonPipeline.png)

### State machine (Arduino)

Each character (actor) runs its own copy of the state machine, without blocking (`millis()`, no `delay()`):

| State | Movement | Music (bridge) |
|---|---|---|
| `HOMING` | First power-up only: moves slowly until the home switch is pressed, then zeroes the position | Keeps current track |
| `IDLE` | Waits for `s` (start) | Track 1 |
| `MOVE_12` | Moves from position 1 to position 2. Reflector on | Track 1 |
| `MOVE_21` | Returns to position 1 | Track 1 |
| `HOLD` | Waits up to 2 s for `h` (heart) | Track 1 |
| `DANCE` | Both actors go to the centre; servo rotations and wiggles, stepper off while each servo moves | Track 2 |
| `EXIT` | Steppers off, reflector off; after 5 s back to `IDLE` | Stops (fade-out) |

![Control Flowchart](media/control-flowchart.png)

*Figure 9. Performance state machine.* [TODO: state machine diagram.]

### Gating logic

- `s` is accepted only when both actors are in `IDLE` and homed; otherwise the sketch replies "Not ready, start ignored".
- `h` is accepted only while the show is running (not in `IDLE` or `HOMING`), and the dance can happen only once per show.
- The dance starts only when both actors are at the centre.

### Changes beyond the provided examples

[TODO: list what was changed or added beyond the module's example code (e.g. MediaPipe hand landmarks instead of the Processing video input, the bridge, the state machine).]

---

## 2.4 Machine learning

### Features and classes

- **Input:** 63 values per frame (21 MediaPipe hand landmarks × x, y, z), normalised for position and scale. One hand only; handedness is not sent.
- **Model:** Wekinator, 1 classifier output, **k-nearest neighbours (k-NN)**.
- **Classes:** 1 = none (no gesture), 2 = action, 3 = heart.

### Training data

Photo dataset in `Code/Simple Pipeline/connection_test/dataset/`, played into Wekinator with `dataset_sender.py` (each photo sent for 5 s):

| Class | Photos |
|---|---|
| none | 34 |
| action | 31 |
| heart | 27 |

Photos with no hand in the `none` class are sent as 63 zeros, the same as the live sender. Saved trained project: `wekinator/WekinatorProject/TRAINCLASSIFIER10-11-2026`.

[TODO: who is in the photos, lighting and background, mirroring.]

### Why this model

[TODO: justify k-NN and hand landmarks (e.g. compared with the Processing video features). Link to the evaluation in 3.3.]

---

# 3. Debugging

## 3.1 Unit and integration tests

**Connection test** (`Code/Simple Pipeline/connection_test`): one image → landmarks → Wekinator (1 class) → bridge → Arduino LED. Pass criteria:

- The LED turns on and stays on while everything runs.
- The bridge console shows `[osc]`, `[serial] sent '1'` and `[arduino] ACK 1` lines.
- Stopping the sender or Wekinator turns the LED off within about 1 s.

This test proves the **connection**, not gesture recognition.

**Other tests in the repo:**

- `Code/Quick Tests/StepperMotorTest` and `TestAccelStepper`: stepper motor tests. [TODO: results.]
- `Code/Quick Tests/TestPuppetScene`: the stage state machine, driven from the Serial Monitor (`s`, `h`, `v` servos to A, `r` servos to rest).
- `bridge.py --dry-run`: music tested by typing states. [TODO: test with the real Arduino.]

**Finding the failing stage:** follow the chain in order — sender status line, Wekinator input indicator, bridge `[osc]` lines, bridge `[serial] sent` lines, Arduino output. The first silent link is the one to fix.

## 3.2 Mechanical and electrical issues

| Symptom | Likely cause | Action |
|---|---|---|
| Sketch prints "Error, check limit switch" and the actor stops | Home switch not reached within the rail travel | Check the switch wiring and the homing direction |
| [TODO] | | |

## 3.3 Software and communication issues

| Symptom | Likely cause | Action |
|---|---|---|
| Bridge cannot open the COM port | Arduino IDE Serial Monitor or another bridge is using it | Close the Serial Monitor; only one program can hold the port |
| Port 12000 busy | Bridge and `dataset_sender.py --test` both listen on it | Run only one of them |
| Camera does not open | Another program (Zoom, Teams) is using it | Close the other program |
| Recognition gets worse live | Camera, lighting or mirroring differs from training | Keep the same set-up and `--mirror` setting as the dataset |
| [TODO] | | |

## 3.4 ML formal evaluation

`dataset_sender.py --test --classes none,action,heart` sends random photos and compares the true class with Wekinator's answer.

[TODO: run with **unseen** photos (`--dataset dataset_test`) and add the confusion matrix and accuracy per class. Compare two models or datasets if possible.]

## 3.5 Unseen users and set-up time

[TODO: results with people not in the training data; timed set-up (≤ 15 min).]

## 3.6 Improvements and limitations

_Maximum 200 words._

[TODO]

---

# 4. Project files

## 4.1 How to run

### Software needed

| Software / library | Version | Purpose |
|---|---|---|
| Python (conda environment `cps`) | 3.11 | Sender and bridge scripts |
| mediapipe | 1.1.1 | Hand landmarks |
| python-osc | 1.9.3 | OSC send/receive |
| pyserial (never `serial`) | 3.5 | Serial port |
| pygame | 2.6.1 | Music |
| Wekinator | [TODO] | Classifier |
| Arduino IDE + AccelStepper, Servo | [TODO] | Stage sketch |

Pinned versions are in `Code/Simple Pipeline/connection_test/environment.yml`. Full set-up steps are in `Code/Simple Pipeline/connection_test/TEAM_GUIDE.md`.

### Run order

1. Upload the Arduino sketch with the Serial Monitor **closed**. [TODO: final sketch path.]
2. Start `bridge.py --serial-port <COM port>`. Wait for the `[music] ready` line.
3. Open the trained Wekinator project and press **Run**.
4. Start `landmarks_sender.py --webcam`.

Stop each script with its Stop button (or `q` / `Esc` in the preview window).

[TODO: shutdown steps and the 15-minute set-up checklist.]

## 4.2 Repository structure

| Path | Contents |
|---|---|
| `Code/Simple Pipeline/connection_test/` | Working pipeline: `landmarks_sender.py`, `dataset_sender.py`, `bridge.py`, dataset, music, Wekinator project, guides |
| `Code/Quick Tests/TestPuppetScene/` | Current stage sketch (state machine) |
| `Code/Quick Tests/StepperMotorTest/`, `TestAccelStepper/` | Stepper tests |
| `Code/Arduino/stageControl/` | [TODO: final single Arduino sketch] |
| `Code/Hand_Landmark_Test/`, `Code/Python/` | Early MediaPipe hand landmark tests |
| `Code/Processing/` | Processing video input example (100 inputs) |
| `Code/Wekinator/` | [TODO] |
| `STAGE/` | [TODO: CAD and fabrication files] |
| `media/` | [TODO: create — photos, diagrams and videos referenced in this README] |

---

# 5. References

## 5.1 Citations

- Plato, *Allegory of the Cave* (conceptual inspiration). [TODO: full reference]
- Wekinator — wekinator.org. [TODO: full reference]
- MediaPipe Hand Landmarker (Google). [TODO: full reference]
- AccelStepper library. [TODO: full reference]
- [TODO: module example code, datasheets, image and music credits]

## 5.2 AI-use notice

Generative AI (Claude, Anthropic) was used in this project. What it was used for, and what each team member wrote, is recorded in `Code/Simple Pipeline/connection_test/LEARNING_LOG.md`. Claude also helped restructure this README.

[TODO: complete for all parts of the project and all team members.]

## 5.3 Team contributions

[TODO]
