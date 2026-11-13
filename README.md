# CPS Interactive Shadow Theatre — Group 20
<img width="1448" height="1086" alt="4792ac60-78bc-4818-94a6-db6d05263a0f" src="https://github.com/user-attachments/assets/707979b0-0ed6-41af-85f7-a26eaf36b602" />

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

Inspired by the Mexican celebration of Día de los Muertos (Day of the Dead), the shadow theatre tells the story of Catrina and Mariachi, two characters brought together through music, movement and the possibility of love. As the theatre comes to life, the audience can influence how their story unfolds through simple hand gestures. By performing the **HEART** gesture, the audience brings the two characters together, allowing them to share a romantic dance. Without this interaction, they continue on their separate paths, leaving their story unresolved. The performance celebrates love, remembrance and the idea that connections can transcend the boundaries between life and death.

## 1.2 User interaction

The audience uses two hand gestures in front of the webcam:

<img width="320" height="256" alt="WhatsApp Image 2026-11-13 at 8 16 30 PM" src="https://github.com/user-attachments/assets/33b96f10-e098-4826-9b85-4378be245b28" /><img width="280" height="280" alt="WhatsApp Image 2026-11-13 at 8 18 18 PM" src="https://github.com/user-attachments/assets/e040ce84-2adc-4459-9252-ef7b75f41c85" />




| Gesture (class) | What it does |
|---|---|
| **ACTION** | Starts the show. Both characters travel along their rails. |
| **HEART** | While the characters are waiting (HOLD), triggers the dance. |
| None | Nothing is sent; the show continues on its own timing. |

| Step | Audience action | System response | 
|---|---|---|
| 1 | Shows the **ACTION** gesture | Reflector turns on, both characters move from position 1 to position 2 and back | 
| 2 | Shows the **HEART** gesture while the characters wait | Characters meet at the centre of the stage and dance (servo rotations and wiggles) |
| 3 | No gesture during the wait | After the hold time the characters repeat the walk once, then exit | 
| 4 | — | Reflector turns off; after 5 s the theatre is ready for the next visitor |

The **ACTION** gesture is often used in films and photos as a frame, a way to focus on an object. Which creates a fun interaction with the audience because it is as if they are directing the play.

The **HEART** gesture was chosen as a way to show and spread the love, then if you don't hold it long enough, their love doesn't grow for each other.

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

### Why a new mechanism instead of the robot arm

[TODO: written justification required by the brief: why the provided robot arm was replaced, and which parts were reused.]

### Motion System & Character Mechanism
<img width="1448" height="1086" alt="508e7483-6251-4179-a854-c6a237d877be" src="https://github.com/user-attachments/assets/e1df55ab-b620-4b25-94da-ed316fd29dcf" />

*Figure 2. The overall mechanical structure of theatre.*

The movement system combines **a shared linear guide, independently driven carriages, and modular servo mechanisms** to create coordinated movements between Catrina and Mariachi.

The mechanism separates horizontal translation from character rotation, allowing both characters to move independently and perform expressive dance movements.

**Mechanical Motion Flow:**

`Stepper Motor → GT2 Timing Belt → Linear Carriage → SG90 Servo Module → Laser-Cut Silhouette`

### Theatre Frame

The theatre frame is constructed using **12 × 15 mm wooden strips and custom 3D-printed connectors**, secured with M3 and M4 hex bolts and nuts.

The structure is designed to fit within a maximum envelope of **575 × 345 × 275 mm (L × W × H)**, providing sufficient space for the dual-track motion system, lighting, and shadow projection.

The modular construction offers several advantages:

- **Easy Assembly:** 3D-printed connectors simplify the connection of wooden members.
- **Modularity:** Individual structural parts can be adjusted or replaced without rebuilding the entire frame.
- **Accessibility:** The open framework allows access to motors, servo modules, and wiring for inspection and troubleshooting.
- **Maintenance:** Removable connections support mechanical adjustments and component replacement during prototyping.

The structure also provides mounting positions for the linear rails, lighting system, projection screen, and exterior enclosure.

<img width="1448" height="1086" alt="e172a33b-e2b4-4ea0-a627-67861c5e2382" src="https://github.com/user-attachments/assets/b087db9a-79a6-434c-b086-c52282bf8207" />

*Figure 3. Theatre frame constructed from wooden strips and custom 3D-printed connectors.*

#### A. Linear Guide & Belt Transmission

The linear motion system uses **two parallel 6 mm metal guide rods shared by both character carriages**, supported by custom 3D-printed mounting components.

Each carriage is driven independently by a **28BYJ-48 geared stepper motor**, controlled through a ULN2003 driver board. Each motor drives its own GT2 timing belt and pulley system, converting rotational motion into horizontal translation.

This arrangement allows the characters to approach each other and return to their starting positions independently while sharing the same guiding structure. Mechanical limit switches establish reference positions during the homing process.

**Linear Bearing Carriage**

Each carriage contains two **LM6 linear ball bearings (6 × 12 × 19 mm)**, housed within an upper and lower 3D-printed structure secured using bolts and nuts.

An **extended 3D-printed belt clamp** connects each carriage to its corresponding GT2 timing belt. The extension keeps the belt connection as horizontal and aligned as possible, reducing unwanted pulling angles and lateral forces.

The belt is secured using bolts and nuts, allowing adjustments during assembly and tensioning.

**Key Design Considerations:**

- **Shared Linear Guide:** Reduces structural complexity and space requirements.
- **Independent Belt Drives:** Allow individual control of character movement.

  
  <img width="1372" height="1147" alt="34a5d12d-de15-4d36-bcd9-c454c3210d28" src="https://github.com/user-attachments/assets/836c9f0f-deb1-44c8-9b6b-fa07e54e1bca" />

*Figure 4. Shared dual-rod linear guide and independently driven GT2 belt transmissions.*

<img width="1105" height="1423" alt="96b60c0a-9957-450c-beda-7acc471c73c6" src="https://github.com/user-attachments/assets/ad868186-7925-4137-8f76-75e4d326c080" />
*Figure 5. Exploded view of the two-part linear carriage, LM6 bearings, and extended belt clamp.*

---

#### B. Modular SG90 Servo & Laser-Cut Silhouettes

The character mechanism combines **modular SG90 servo units with laser-cut silhouettes**, enabling changes in projected poses through controlled rotation.

**Modular SG90 Servo Unit**

Each sliding carriage supports an **SG90 micro servo**, housed inside a custom 3D-printed module and secured using bolts and nuts.

The servo rotates the character around a vertical axis, changing its orientation relative to the light source.

- **Quick Testing:** Individual servos can be accessed and tested to identify movement issues.
- **Easy Replacement:** Servo modules can be removed or replaced without disassembling the linear carriage.
- **Independent Maintenance:** Servo adjustments can be performed without disturbing the belt transmission or guide rods.

<img width="1024" height="1536" alt="c2db957d-c997-4e89-b0b4-5f477fd6cf1b" src="https://github.com/user-attachments/assets/32aaaef1-ccee-48ab-94f1-460486f1c09c" />

*Figure 6. Exploded and generated view of the modular SG90 servo housing and character mounting structure.*

**Character Design & Laser-Cut Silhouettes**

Catrina and Mariachi are designed as two contrasting dance characters inspired by traditional Mexican cultural imagery.

- **Catrina:** Her flowing dress emphasises elegant movement and changes in the projected skirt shape.
- **Mariachi:** His distinctive hat and costume create a recognisable silhouette and contrasting dance poses.

Both characters are constructed using **two intersecting laser-cut profiles**, combining perpendicular outlines into a lightweight three-dimensional assembly.



## Character Inspiration


<img width="620" height="500" alt="catrina_illustrationchronicles_1500" src="https://github.com/user-attachments/assets/e59fee42-a361-4b10-abdc-3cc9199c7f3c" /><img width="300" height="500" alt="mariachidrawing" src="https://github.com/user-attachments/assets/4835d55e-9a9e-4397-846c-8f3e182d12d2" />

*Figures 7.1-7.2 Character Design Inspiration*

## Laser-cut Profiles

<img width="510" height="452" alt="catrina" src="https://github.com/user-attachments/assets/b9b321bf-6d6f-41fb-964f-4e88afcce8a5" /><img width="438" height="452" alt="mariachi" src="https://github.com/user-attachments/assets/5ebddde0-e961-47bf-8372-574cced9950e" />

*Figures 7.3-7.4 Laser-Cut Profiles*

## Assembled Figures

<img width="300" height="500" alt="catrina_two_view_1_second" src="https://github.com/user-attachments/assets/1c66ce31-3911-4962-b20a-9145eb4eaace" /><img width="300" height="500" alt="mariachi_two_poses" src="https://github.com/user-attachments/assets/e70a916f-705b-4a7e-a1a8-a4b337c3e279" />

*Figures 7.5-7.6 Assembled Silhouttes*


*Figures 7.1-7.6 Character designs, laser-cut profiles, and assembled Catrina and Mariachi silhouettes.*

### Exterior enclosure and finishing

The exterior enclosure surrounds the structural frame and conceals the internal mechanical and electronic components, creating a cohesive theatrical appearance. Wooden panels were cut to fit the frame, forming the outer casing while maintaining access to the internal mechanisms and providing a defined viewing area.

Surface finishing and painting, combined with laser-cut decorative details and red curtains, establish the theatre's visual identity and separate the performance space from its supporting structure.

<img width="4096" height="3072" alt="a9be0985d4db4d5169e1ef3d4d55eb80" src="https://github.com/user-attachments/assets/d06776bd-2b3d-4ebc-9424-76ea33a116fe" />
<img width="1448" height="1086" alt="d640d71f-6dcc-4e76-81dd-3cd03d9627ac" src="https://github.com/user-attachments/assets/d4120eb5-a6c1-4e39-8537-cc37a44a73f9" />
<img width="3072" height="4096" alt="984efee3b1fa96b544d054b6b9cd4bfa" src="https://github.com/user-attachments/assets/9b6f073d-eb3e-4300-8b5a-775b28a041bc" />

*Figure 8. Exterior enclosure design and final surface finishing.*

### Design Decisions & Prototype Testing

Several design decisions were informed by early prototyping and shadow projection experiments, focusing on simplifying mechanical movement and improving visual performance.

| Design Aspect | Initial Approach / Challenge | Final Design | Reason & Impact |
|---|---|---|---|
| **Character Movement** | Traditional puppetry requires individual limb control and complex mechanisms. | Interlocking silhouettes driven by translation and rotation. | Creates changing shadow poses with fewer mechanical movements, inspired by rotational dance. |
| **Shadow Scale** | Character dimensions and projection proportions needed to be determined. | Laser-cut silhouettes of different sizes were tested. | Helped establish suitable character proportions and light-to-screen distances. |
| **Screen Material** | Different translucent materials produced varying projection effects. | Frosted translucent paper. | Selected for its balance of light transmission and shadow visibility. |
| **Lighting System** | Diffused and focused light sources were explored. | Simple direct-light arrangement without additional focusing lenses. | Reduces optical complexity while maintaining a clear shadow projection. |

*Figure 9. Prototype comparisons of character movement, silhouette scale, screen materials, and lighting conditions.* [TODO: add image to `Media/`.]

### Assembly

The mechanical assembly follows four main stages, from structural construction and motion system integration to projection setup and final enclosure. The internal mechanisms remain accessible for testing and adjustment before the theatre is fully enclosed.

#### 1. Main Frame Assembly

1. Cut the 12 × 15 mm wooden strips to the required lengths.
2. Assemble the supporting frame using custom PLA 3D-printed connectors.
3. Secure the joints using M3/M4 bolts and nuts.
4. Check the frame alignment and stability, ensuring sufficient space for the internal mechanisms.

*Figure 10. Assembly of the wooden frame using 3D-printed connectors and bolted joints.* [TODO: add image to `Media/`.]

#### 2. Linear Motion & Character Assembly

**Linear Carriages & Guide Rods**

1. Insert two LM6 linear bearings (6 × 12 × 19 mm) into each custom 3D-printed carriage housing and assemble the sliding platforms.
2. Prepare the modular SG90 servo holders and check their fit with the carriages.
3. Pass the two parallel 6 mm metal guide rods through the bearings of both carriages.
4. Attach the two 3D-printed rail supports and secure the guide assembly to the wooden frame using bolts and nuts.
5. Adjust the rail supports and carriage positions to maintain rod alignment and ensure smooth sliding movement.

**Servo Modules & Silhouettes**

6. Install the SG90 micro servos into their custom 3D-printed housings.
7. Mount the servo modules onto the sliding carriages and secure them using bolts and nuts.
8. Assemble the laser-cut character silhouettes and test different orientations to achieve the desired shadow poses.
9. Once the positions and projection effects are confirmed, secure the silhouette components using hot glue and attach them to the servo modules.
10. Check attachment stability and rotation clearance.

**Belt-Driven Transmission**

11. Mount the 28BYJ-48 stepper motors and timing pulleys onto the supporting frame.
12. Measure and cut the GT2 timing belts to approximately 750 mm, based on repeated fitting and adjustment during assembly.
13. Route the two independent belts around their corresponding pulleys and connect them to the sliding carriages using 3D-printed belt clamps, secured with bolts and nuts.
14. Adjust belt tension and pulley alignment, then manually check the full movement range of both carriages with the power disconnected.

*Figure 11. Assembly of the bearing-supported carriages, shared guide rods, SG90 character modules, and independent belt transmissions.* [TODO: add image to `Media/`.]

#### 3. Screen & Lighting Installation

1. Prepare the frosted translucent paper and position it across the front projection area.
2. Secure the projection screen to the wooden frame using screws.
3. Install the light sources using custom 3D-printed mounting brackets, secured with screws.
4. Adjust the light angles and projection distances to achieve suitable shadow size and clarity.
5. Test character translation, rotation, and shadow projection before installing the exterior enclosure.

*Figure 12. Installation of the projection screen, lighting brackets, and shadow alignment.* [TODO: add image to `Media/`.]

#### 4. Final Enclosure & Finishing

1. Complete the electrical integration and verify the operation of the stepper motors, SG90 servos, and mechanical limit switches.
2. Cut and prepare the wooden enclosure panels to fit the assembled frame.
3. Install the exterior panels after successful system testing, retaining access to internal components where necessary.
4. Complete the surface finishing and add the laser-cut decorative elements and red curtains.
5. Perform a final check of mechanical movement and shadow projection.

*Figure 13. Final enclosure installation and completed shadow theatre.* [TODO: add image to `Media/`.]

#### Final Assembly Checklist

Before installing the exterior enclosure, a final check is conducted to ensure all mechanical components are securely assembled and functioning correctly. This helps identify potential issues while the internal system remains accessible for adjustment and maintenance.

- [x] **Frame Stability:** Wooden joints, 3D-printed connectors, bolts and nuts are securely fastened.
- [x] **Linear Motion:** Guide rods are aligned, and both carriages slide smoothly without interference.
- [x] **Belt Transmission:** GT2 belts are securely clamped, properly tensioned, and aligned with the pulleys.
- [x] **Servo & Silhouettes:** SG90 modules and character silhouettes are firmly attached, with sufficient rotation clearance.
- [x] **Motion & Homing:** Both characters move independently, and the mechanical limit switches function correctly.
- [x] **Projection & Enclosure:** The screen and lights are securely mounted, shadows remain clear, and the enclosure does not interfere with the mechanisms.

*Note: Manual mechanical checks should be performed with power disconnected. Complete powered system testing before final enclosure.*

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

*Figure 14. Electrical circuit and hardware connections.* [TODO: circuit diagram.]

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

*Figure 15. Performance state machine.* [TODO: state machine diagram.]

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
