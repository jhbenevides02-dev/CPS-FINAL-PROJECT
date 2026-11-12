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

```
Webcam
     |
     v
landmarks_sender.py   MediaPipe -> 21 landmarks x (x, y, z) = 63 floats (normalised)
     |  OSC /wek/inputs, UDP, 127.0.0.1:6448
     v
Wekinator             classifier, k-NN, 3 classes
     |  OSC /wek/outputs, UDP, 127.0.0.1:12000
     v
bridge.py             class -> one character ('s' or 'h'), plus music
     |  USB serial, 115200 baud
     v
Arduino               stage state machine -> steppers, servos, reflector
     |  state lines, e.g. "catrina -> DANCE", back over the same serial port
     v
bridge.py             changes the music track
```

The bridge also plays the music, following the state the Arduino reports.

![System Architecture](Media/Wekinator+PythonPipeline.png)

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

*Figure 2. Theatre frame CAD model and physical assembly.* [TODO: add image to `Media/`.]

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

*Figure 3. Dual-rail layout and belt transmission mechanism.* [TODO: add image to `Media/`.]

#### B. Linear bearing carriage and servo module

Each carriage moves along a linear guide supported by bearings. A custom belt clamp connects the carriage to the timing belt, while the sliding platform provides a stable mounting base for the character mechanism. The bearing-supported structure is designed to reduce friction, limit unwanted rotation and maintain stable movement.

*Figure 4. Linear bearing, belt clamp and sliding carriage assembly.* [TODO: add image to `Media/`.]

#### C. Laser-cut silhouettes

Catrina and Mariachi are designed as two-dimensional profiles and fabricated by **laser cutting**, so their outlines project clearly. Each silhouette is attached to a removable servo module mounted on the sliding carriage.

*Figure 5. Laser-cut character designs and fabricated silhouettes.* [TODO: add image to `Media/`.]

*Figure 6. Modular servo mechanism and silhouette attachment.* [TODO: add image to `Media/`.]

### Exterior enclosure and finishing

The exterior enclosure surrounds the structural frame and conceals the internal mechanical and electronic components, creating a cohesive theatrical appearance. It keeps access to the internal mechanisms while providing a defined viewing area. Surface finishing and painting establish the visual identity of the theatre and separate the performance space from its supporting structure.

*Figure 7. Exterior enclosure design and final surface finishing.* [TODO: add image to `Media/`.]

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
| Arduino [TODO: Nano or Nano Every — `PuppetScene` says Nano, the set-up steps say Nano Every] | 1 | Runs the stage state machine |
| 28BYJ-48 stepper motor + driver board [TODO: driver model] | 2 | Drives each carriage along its rail |
| Servo motor [TODO: model] | 2 | Rotates each silhouette during the dance |
| Home (limit) switch | 2 | Zeroes each carriage at power-up |
| Reflector light assembly [TODO: LED type] | 1 | Light source for the shadows |
| Laptop webcam | 1 | Gesture input |
| Power bank + power board (module kit) | 1 | 5 V DC supply |
| [TODO: other parts] | | |

[TODO: reason for each part and confirmation that it is on the approved list.]

### Wiring and circuit diagram

Pin assignments, from the current stage sketch (`Code/Arduino/PuppetScene`):

| Function | Catrina | Mariachi |
|---|---|---|
| Stepper driver IN1, IN2, IN3, IN4 | 8, 9, 10, 11 | 4, 5, 6, 7 |
| Servo signal | 15 | 16 |
| Home switch (to GND, `INPUT_PULLUP`, active LOW) | 3 | 2 |
| Reflector (shared, active LOW) | 14 | 14 |

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

Do not change the ports, addresses, the 63-value order or `normalise()` without telling the team: every other script depends on them.

### Sender (`landmarks_sender.py`)

- Run with `--webcam` for the show.
- Webcam mode: one detection and one OSC message every 1/15 s. A preview window shows the camera with the landmarks drawn; `q` / `Esc` quits.
- The landmarks are normalised: the wrist is the origin and the wrist-to-middle-finger-base distance is the scale. If no hand is found, 63 zeros are sent, so Wekinator always receives the same number of inputs.
- One hand only (`num_hands=1`); handedness is not sent.
- Options: `--host`, `--port`, `--rate` (default 30, webcam 15), `--print-values`, and for the webcam `--camera N` (another camera) and `--mirror` (flip left-right).

### Bridge (`bridge.py`)

- Class to letter (`CLASS_COMMANDS` at the top of `bridge.py`): class 2 → `s`, class 3 → `h`. Class 1 (none) sends nothing.
- `COMMAND_ENDING` is `""`, so only the character is sent. Set it to `"\n"` if the sketch reads lines.
- Keep-alive: while the same class stays, the letter is re-sent about every 250 ms (`KEEPALIVE_S`).
- Waits 2 s after opening the port, because the Arduino resets when the port opens. Arduino replies are read on a background thread.
- Options: `--serial-port` (default `COM7`), `--osc-port`, `--baud`, `--no-music`, `--dry-run` (no Arduino).

### Music

The bridge reads the Arduino's state lines (`<actor> -> <STATE>`):

| Arduino state | Music |
|---|---|
| `IDLE`, `MOVE_12`, `MOVE_21`, `HOLD` | Track 1 (`music/Track_1.mp3`), looping |
| `DANCE` (any actor) | Track 2 (`music/Track_2.mp3`), looping |
| `EXIT` (all actors) | Stops with a fade-out. The next `IDLE` starts track 1 again |
| `HOMING` | Keeps what is playing |

- `--no-music` turns the music off. If `pygame` or a track file is missing, the bridge says so and carries on without music.
- If the sketch prints the states differently, change `STATE_LINE` in `bridge.py`.

![Software Pipeline](Media/Wekinator+PythonPipeline.png)

### State machine (Arduino)

Each character (actor) runs its own copy of the state machine, without blocking (`millis()`, no `delay()`):

| State | Movement |
|---|---|
| `HOMING` | First power-up only: moves slowly until the home switch is pressed, then zeroes the position |
| `IDLE` | Waits for `s` (start) |
| `MOVE_12` | Moves from position 1 to position 2. Reflector on |
| `MOVE_21` | Returns to position 1 |
| `HOLD` | Waits up to 2 s for `h` (heart) |
| `DANCE` | Both actors go to the centre; servo rotations and wiggles, stepper off while each servo moves |
| `EXIT` | Steppers off, reflector off; after 5 s back to `IDLE` |

The music for each state is in the Music table above.

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
- **Classes:**

| Class number | Name | Dataset folder | Letter sent to the Arduino |
|---|---|---|---|
| 1 | none (no gesture) | `dataset/none` | nothing |
| 2 | action | `dataset/action` | `s` |
| 3 | heart | `dataset/heart` | `h` |

**Wekinator settings:** 63 inputs, listening on port `6448`, message `/wek/inputs`. 1 output, classifier, 3 classes, k-NN, sending to `localhost` port `12000`, message `/wek/outputs`.

**Keep these identical between training and live use.** Wekinator learns from whatever it receives while recording, so any difference makes recognition worse:

- same camera, position and lighting, as far as possible
- same mirroring: the photo dataset is **not** mirrored, so do not use `--mirror` unless the dataset was recorded mirrored
- same `normalise()` (wrist origin, wrist to middle-finger-base scale)
- one hand only; handedness is not sent
- same 63-input order

### Training data

Photo dataset in `Code/Python/dataset/` (`.jpg`, `.jpeg`, `.png`, one folder per class):

| Class | Photos |
|---|---|
| none | 34 |
| action | 31 |
| heart | 27 |

Saved trained project: `Code/Wekinator/` (`TRAINCLASSIFIER10-11-2026.wekproj`).

**How the model is trained (by hand).** `dataset_sender.py` only plays the photos into Wekinator; recording and training are done in Wekinator:

1. Run `dataset_sender.py --class <name>` (e.g. `--class heart`). It shows each photo in a window and sends it for `--burst` seconds (default 5), photo after photo, in a loop.
2. In Wekinator, set the output class to the class number, press **Start recording** while the script runs, record at least one full pass of the photos, then stop. Stop the script.
3. Repeat for the other classes. Then **Train**, **Run**, and save the project in `Code/Wekinator/`.

- **Class `none`:** photos where no hand is found are **not skipped**. They are sent as 63 zeros, exactly what the live sender sends when it sees no hand, so some photos with no hand at all are included.
- **Balance:** similar numbers of photos per class, otherwise k-NN leans toward the biggest class.
- Options: `--dataset <folder>`, `--burst <seconds>`, `--rate`.

[TODO: who is in the photos, lighting and background, mirroring.]

### Why this model

[TODO: justify k-NN and hand landmarks (e.g. compared with the Processing video features). Link to the evaluation in 3.4.]

---

# 3. Debugging

## 3.1 Unit and integration tests

**Status of each part** (before the demo):

| Part | State |
|---|---|
| Live webcam capture (`landmarks_sender.py --webcam`) | Built, tested by the team |
| Training Wekinator from the photo dataset | Built |
| Testing the trained model with photos (`dataset_sender.py --test`) | Built, not yet run with new, unseen photos |
| Bridge sends `s` (action) / `h` (heart) to the Arduino | Built |
| Music from the Arduino states | Built, tested in `--dry-run`, not yet tested with the real Arduino |
| Final Arduino sketch | In progress (`Code/Arduino/PuppetScene`) |

[TODO: update this table after the demo.]

**Other tests:**

- `Code/Arduino/PuppetScene` on its own: the stage state machine, driven from the Serial Monitor (`s`, `h`, `v` servos to A, `r` servos to rest).
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
| `[music]` message and no sound | `pygame` not installed, or a track file is missing | Install `pygame` in the `cps` environment; check `music/Track_1.mp3` and `Track_2.mp3` |
| `serial.Serial` fails | The package called `serial` was installed instead of `pyserial` | Uninstall `serial`, install `pyserial==3.5` |
| Bridge sends nothing | Wekinator is not in Run mode, or only class 1 (none) is recognised | Check the Wekinator input indicator and the bridge `[osc]` lines |
| [TODO] | | |

## 3.4 ML formal evaluation

`dataset_sender.py --test --classes none,action,heart` sends random photos and compares the true class with Wekinator's answer.

- Wekinator in Run mode, bridge **stopped** (both use port 12000).
- The window draws the landmarks, shows the true class and Wekinator's answer (green = right, red = wrong or no answer). The console prints a score line per photo.
- Testing with the **training photos** looks almost perfect and proves little. A real accuracy figure needs **new photos** in a separate folder (`dataset_test/none`, `dataset_test/action`, `dataset_test/heart`), used with `--dataset dataset_test`.
- Option: `--listen-port`.

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

Pinned versions are in `Code/Python/environment.yml`.

### First-time set-up (once per computer)

**1. Install the tools**

1. **Anaconda** (Windows installer from anaconda.com). Choose "Just Me". "Add Anaconda to PATH" is not needed: PyCharm finds it by itself.
2. **PyCharm** (Community or Professional, from jetbrains.com). Both can use conda environments.
3. **Arduino IDE**, then *Tools > Board > Boards Manager* and install **Arduino megaAVR Boards** (for the Arduino Nano Every).
4. **Wekinator** (desktop app, from wekinator.org). Java is bundled with the current download. If Windows Firewall asks about Java, allow it on private networks.
5. **Git**, and a clone of this repository.

**2. Open the project in PyCharm**

1. *File > Open* and choose `Code/Python`. This folder is the project; do not create a new project or sub-folder.
   If you set up PyCharm before the folders were reorganised, open `Code/Python` again and update the working directory of each run configuration.
2. PyCharm creates a `.idea/` folder. It must not be committed.

**3. Create the Python environment**

1. *File > Settings > Project: Python > Python Interpreter*.
2. **Add Interpreter > Add Local Interpreter > Conda Environment**.
3. **Conda executable:** if empty, browse to `...\anaconda3\Scripts\conda.exe` (usually `C:\Users\<you>\anaconda3\Scripts\conda.exe`).
4. **Create new environment**, **Python 3.11**, name `cps`, then **OK**. (To reuse an existing environment, choose **Use existing environment**.)
5. The bottom-right corner of PyCharm must show the new interpreter (`cps`, Python 3.11).

**4. Install the packages**

Open the PyCharm terminal (`Alt+F12`). Check that it uses the `cps` environment:

    python -c "import sys; print(sys.executable)"

If the path is not inside `cps`, open a **new** terminal tab after setting the interpreter. Then install, always with `python -m pip`:

    python -m pip install mediapipe==1.1.1 python-osc==1.9.3 pyserial==3.5 pygame==2.6.1

Install **`pyserial`, never `serial`**. Both import as `serial`, but the package called `serial` is a different project and `serial.Serial` then fails.

Check that everything imports (prints `True`):

    python -c "import mediapipe, pythonosc, serial, pygame; print(hasattr(serial, 'Serial'))"

Alternative (only if the team agrees): `conda env create -f environment.yml` from the Anaconda Prompt.

**5. PyCharm run configurations**

A run configuration is PyCharm's saved version of a terminal command: interpreter + script + parameters. Create one per script with *Run > Edit Configurations > + > Python*: set the name, the script, the parameters, the working directory (`Code/Python`) and the `cps` interpreter.

| Name | Script | Parameters |
|---|---|---|
| `sender webcam` | `landmarks_sender.py` | `--webcam` |
| `bridge dry run` | `bridge.py` | `--dry-run` |
| `bridge` | `bridge.py` | `--serial-port COM7` (use your port) |
| `dataset heart` / `dataset action` / `dataset none` | `dataset_sender.py` | `--class heart` / `--class action` / `--class none` |
| `dataset test` | `dataset_sender.py` | `--test --classes none,action,heart` |

Different configurations run at the same time in separate tabs of the Run window, each with its own Stop button. Tick **Allow multiple instances** (under *Modify options*) only to start the *same* configuration twice.

**6. Find the COM port**

Arduino IDE > *Tools > Port*, or Device Manager > Ports (COM & LPT). It differs on every computer and can change with another USB socket. It goes in the bridge's `--serial-port` parameter, not in the code.

**7. Arduino IDE**

1. *Tools > Board*: **Arduino Nano Every**. [TODO: confirm the board — `PuppetScene` says Arduino Nano.]
2. *Tools > Port*: the board's COM port.
3. Open `Code/Arduino/PuppetScene/PuppetScene.ino` and **Upload**.
4. **Close the Serial Monitor** afterwards. Only one program can hold the port.

### Run order (every time)

1. Upload `Code/Arduino/PuppetScene` with the Serial Monitor **closed**.
2. Start `bridge` (`--serial-port <your COM port>`). Wait for the `[music] ready` line.
3. Open the trained Wekinator project (`Code/Wekinator/TRAINCLASSIFIER10-11-2026.wekproj`) and press **Run**.
4. Start `sender webcam` (`--webcam`).

Stop each script with the Stop button in its PyCharm tab (or `q` / `Esc` in the preview window).

**Rules**

- Only one program can hold the Arduino COM port: close the Serial Monitor before starting the bridge, and only one team member's bridge can use the board at a time.
- Only one program can listen on port 12000: do not run `dataset_sender.py --test` together with the bridge.
- The COM port is a run parameter, not a code change. Each person keeps their own run configurations.

[TODO: shutdown steps and the 15-minute set-up checklist.]

## 4.2 Repository structure

| Path | Contents |
|---|---|
| `Code/Python/` | Python pipeline: sender, dataset sender, bridge, dataset, music, environment |
| `Code/Wekinator/` | Trained Wekinator project used in the show (3 classes) |
| `Code/Arduino/PuppetScene/` | Stage sketch (state machine) |
| `Build/` | [TODO: CAD and fabrication files] |
| `Media/` | Images for this README: pipeline diagrams (`Wekinator+PythonPipeline.png`, `WekinatorOnlyPipeline.png`) [TODO: add photos, CAD renders, circuit and state machine diagrams] |

**Inside `Code/Python/`:**

| File | What it is |
|---|---|
| `environment.yml` | Pinned package versions (Python 3.11, mediapipe, python-osc, pyserial, pygame) |
| `check_env.py` | Import check for the environment |
| `landmarks_sender.py` | Webcam → 63 floats → OSC `/wek/inputs` |
| `dataset_sender.py` | Plays the photo dataset into Wekinator (training) or tests the trained model (`--test`) |
| `bridge.py` | OSC `/wek/outputs` → serial (class 2 → `s`, class 3 → `h`), plus music |
| `dataset/<class>/` | Training photos per class (`none`, `action`, `heart`) |
| `music/` | `Track_1.mp3`, `Track_2.mp3` |
| `hand_landmarker.task` | MediaPipe hand landmark model |

The scripts find `dataset/`, `music/` and `hand_landmarker.task` relative to their own folder, so `Code/Python` must be kept together.

`.idea/` folders (PyCharm) must not be committed. [TODO: add `.idea/` to `.gitignore`.]

---

# 5. References

## 5.1 Citations

- Plato, *Allegory of the Cave* (conceptual inspiration). [TODO: full reference]
- Wekinator — wekinator.org. [TODO: full reference]
- MediaPipe Hand Landmarker (Google). [TODO: full reference]
- AccelStepper library. [TODO: full reference]
- [TODO: module example code, datasheets, image and music credits]
- Anthropic Claude. Anthropic Claude response to Group 20. 26 October to 11 November 2026.


## 5.2 AI-use notice

Generative AI (Claude, Anthropic) was used in this project by all three team members (see the Anthropic Claude references in 5.1).

- **Debugging (main use):** the Arduino IDE has no integrated debugger (no breakpoints or step-by-step execution), so Claude was our main debugging tool. We shared code, Serial Monitor output and error messages, and used its suggestions to find and fix faults. Every fix was tested by the team on the hardware.
- **Code:** Claude reviewed code written by the team, to identify any possible issues in the pipeline.
- **Learning:** explanations of the tools and concepts used (Wekinator, k-NN, OSC, serial communication, non-blocking timing).

All AI output was checked, tested and edited by the team, and the team is responsible for the final work.