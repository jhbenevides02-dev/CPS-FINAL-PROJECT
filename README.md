# CPS-FINAL-PROJECT
## Group 20

# CPS Interactive Shadow Theatre — Group XX

## Introduction

This repository contains the design, hardware documentation, software, and testing materials for our interactive shadow theatre, developed for the Cyber-Physical Systems (CPS) module.

Inspired by Plato's *Allegory of the Cave*, the project explores how light angles, mechanical movement, and audience interaction can transform shadows and challenge our perception of reality.

## Team Members

- [Name]
- [Name]
- [Name]

## The Shadow Theatre

[Introduce the final installation, its physical structure, mechanical movement, lighting, and interactive features.]

![Shadow Theatre](media/shadow-theatre.jpg)

## How It Works

The theatre combines physical mechanisms, lighting, and interactive inputs to create a dynamic shadow storytelling experience.

**Audience Input → Processing → Physical Output → Shadow & Story Experience**

![System Overview](media/system-overview.png)

| Input | Processing | Output | Audience Experience |
|---|---|---|---|
| [Input 1] | [Recognition / Control] | [Movement / Lighting] | [Effect] |
| [Input 2] | [Recognition / Control] | [Movement / Lighting] | [Effect] |

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [What You Need](#2-what-you-need)
3. [Mechanical & Electrical Setup](#3-mechanical--electrical-setup)
4. [Software Setup](#4-software-setup)
5. [How to Run](#5-how-to-run)
6. [Interaction Guide](#6-interaction-guide)
7. [Expected Results & Testing](#7-expected-results--testing)
8. [Debugging](#8-debugging)
9. [Project Files](#9-project-files)
10. [Demonstration & Limitations](#10-demonstration--limitations)
11. [References](#11-references)

---


# 1. System Architecture

## 1.1 System Overview

The **Interactive Shadow Theatre** is a cyber-physical installation that combines gesture recognition, mechanical movement, and light projection to create an interactive shadow performance.

Inspired by Plato's *Allegory of the Cave*, the project explores how physical objects, light, and movement can transform projected shadows into a dynamic storytelling experience.

The performance features two characters, **Catrina and Mariachi**, which move along independent tracks and perform a coordinated dance in response to audience interaction.

The system integrates three main elements:

- **Input:** A camera captures audience gestures.
- **Processing:** Processing, Wekinator, and Arduino interpret gestures and coordinate the performance.
- **Output:** Motors, servos, lighting, and synchronised music produce the shadow performance.

**System Workflow:**

`Audience Gesture → Camera → Processing → Wekinator → Interaction Logic → Arduino → Motors & Servos → Shadow Performance`

![System Architecture](media/system-architecture.png)

*Figure 1. Overall system architecture.*

---

## 1.2 Software Design & Gesture Recognition

The software system connects audience gestures to the physical theatre through **camera-based input, machine learning, and Arduino control**.

Processing handles gesture input and communicates with Wekinator, which uses a trained model to recognise the audience's **Heart Gesture**. The recognition result is translated into commands that trigger character movements and the dance sequence.

### A. Gesture Recognition & Machine Learning

The camera captures audience gestures, while Processing extracts and sends input features to Wekinator for classification.

Wekinator is trained to distinguish the Heart Gesture from other inputs, allowing the system to respond to a recognised interaction.

![Gesture Recognition](media/software/gesture-recognition.jpg)

*Figure 2. Camera input and Wekinator training.*

### B. Interaction Logic & Arduino Control

Once a valid gesture is recognised, Processing uses the current interaction state to determine when to send commands to Arduino.

Arduino controls the motors and servos, coordinating the characters' horizontal movement and rotation. Music transitions are synchronised with the performance sequence.

The state-based approach prevents repeated gesture inputs from interrupting an active performance.

![Software Control Flow](media/software/control-flow.png)

*Figure 3. Software processing and Arduino control.*

**Software Workflow:**

`Camera → Processing → Wekinator → Interaction Logic → Arduino → Motors & Servos`

**Detailed Documentation:**

- [Software Implementation & Source Code](code/README.md)
- [Gesture Recognition & Wekinator](code/gesture-recognition/README.md)

---

## 1.3 Mechanical & Lighting Design

The physical system consists of a modular theatre frame, a motor-driven character movement mechanism, and a lighting system that transforms moving silhouettes into projected shadows.

### 1.3.1 Theatre Frame & Structural Assembly

The theatre is constructed using **cut wooden strips and custom 3D-printed connectors**. The frame supports the projection screen, internal tracks, motors, and lighting system while allowing convenient assembly and adjustments.

The modular structure was designed for stability, ease of fabrication, and accessibility during maintenance.

![Theatre Frame](media/mechanical/theatre-frame.jpg)

*Figure 4. Theatre frame CAD model and physical assembly.*

[Theatre Frame Design & Assembly](hardware/mechanical/theatre-frame/README.md)

### 1.3.2 Motion Transmission & Character Mechanism

The movement system integrates **two independent linear tracks, belt-driven carriages, and modular servo mechanisms** to create coordinated movements between the two shadow characters.

The system combines horizontal translation with individual character rotation.

#### A. Belt-Driven Linear Motion

Motor-driven GT2 timing belts convert rotational motion into horizontal movement, allowing both characters to approach the centre and return to their starting positions.

The two independent tracks enable separate movement control, while pulley alignment and belt tension help maintain consistent transmission.

![Belt Transmission](media/mechanical/belt-drive.jpg)

*Figure 5. Dual-track layout and belt transmission mechanism.*

#### B. Linear Bearing & Sliding Carriage

Each carriage moves along a linear guide supported by bearings. A custom belt clamp connects the carriage to the timing belt, while the sliding platform provides a stable mounting base for the character mechanism.

The bearing-supported structure is designed to reduce friction, limit unwanted rotation, and maintain stable movement.

![Linear Carriage](media/mechanical/carriage.jpg)

*Figure 6. Linear bearing, belt clamp, and sliding carriage assembly.*

#### C. Modular Servo & Laser-Cut Silhouettes

Catrina and Mariachi are designed as two-dimensional profiles and fabricated through **laser cutting**, allowing their distinctive outlines to be projected clearly.

Each silhouette is attached to a removable servo module mounted on the sliding carriage. While the belt-driven system controls horizontal movement, the servo enables independent character rotation.

The modular design allows different silhouettes to be replaced without modifying the underlying motion mechanism.

![Laser-Cut Silhouettes](media/mechanical/laser-cut-silhouettes.jpg)

*Figure 7. Laser-cut character designs and fabricated silhouettes.*

![Servo Module](media/mechanical/servo-module.jpg)

*Figure 8. Modular servo mechanism and silhouette attachment.*

**Mechanical Motion Flow:**

`Motor → Timing Belt → Linear Carriage → Servo Module → Laser-Cut Silhouette`

**Detailed Documentation:**

[Motion System Design & CAD Files](hardware/mechanical/motion-system/README.md)

### 1.3.3 Lighting & Shadow Projection

The lighting system projects the moving silhouettes onto a translucent screen, transforming mechanical movements into visual storytelling.

Light positioning, projection angles, and distances are adjusted to control shadow scale, sharpness, and visibility throughout the performance.

Lighting tests focus on reducing **double shadows**, maintaining consistent projection quality, and ensuring that the characters appear to interact naturally.

![Lighting System](media/lighting/lighting-system.jpg)

*Figure 9. Lighting installation and shadow projection arrangement.*

![Lighting Tests](media/lighting/lighting-tests.jpg)

*Figure 10. Comparison of shadow projection under different lighting conditions.*

[Lighting Installation & Projection Testing](hardware/lighting/README.md)

---

## 1.4 Control & Communication

Processing and Wekinator handle gesture recognition, while Arduino controls the motors and servos. The control system coordinates movement commands and music transitions throughout the performance.

### Communication Pipeline

| Connection | Protocol / Interface | Purpose |
|---|---|---|
| Camera → Processing | USB / Video Input | Capture audience gestures |
| Processing → Wekinator | OSC | Send gesture input features |
| Wekinator → Processing | OSC | Return recognition results |
| Processing → Arduino | Serial Communication | Send movement commands |
| Arduino → Motors / Servos | Motor Driver / Servo Signals | Execute character movements |

### Performance State Management

| State | Movement | Audio |
|---|---|---|
| `OPENING` | Characters remain stationary | Music 1 — Mysterious Intro |
| `APPROACH` | Characters move towards the centre | Music 2 — Building Anticipation |
| `WAIT_GESTURE` | Characters wait at the centre | Background Music |
| `DANCE` | Coordinated character rotation and dance movements | Music 3 — Dance Theme |
| `RETURN` | Characters return to their starting positions | Music 2 |
| `RESET` | System prepares for the next interaction | Fade Out |

The state-based sequence prevents conflicting commands and supports coordinated character movement and audio playback.

![Control Flowchart](media/control-flowchart.png)

*Figure 11. Performance state machine and communication sequence.*

**Detailed Documentation:**

- [Arduino Motor & Servo Control](code/arduino/README.md)
- [Processing & Interaction Logic](code/processing/README.md)


## 2. What You Need

### 2.1 Hardware

| Component | Quantity | Purpose |
|---|---|---|
| [Microcontroller] | [Quantity] | [Purpose] |
| [Sensor] | [Quantity] | [Purpose] |
| [Motor / Servo] | [Quantity] | [Purpose] |
| [Light Source] | [Quantity] | [Purpose] |
| [Mechanical Components] | [Quantity] | [Purpose] |

### 2.2 Software & Libraries

| Software / Library | Version | Purpose |
|---|---|---|
| [Software 1] | [Version] | [Purpose] |
| [Software 2] | [Version] | [Purpose] |

### 2.3 Required Files

| File | Description |
|---|---|
| `[File path]` | [Description] |
| `[File path]` | [Description] |

---

## 3. Mechanical & Electrical Setup

### 3.1 Safety and Power-Off Check

1. Disconnect the system from all power sources.
2. Check for loose wires or exposed electrical connections.
3. Confirm that moving mechanisms are unobstructed.
4. [Add project-specific safety checks.]

### 3.2 Mechanical Assembly

[Describe the assembly process of the theatre structure, shadow puppets, and moving mechanisms.]

1. [Assembly step 1]
2. [Assembly step 2]
3. [Assembly step 3]

![Mechanical Assembly](media/mechanical-assembly.png)

### 3.3 Electrical Connections

[Describe how sensors, motors, lights, and the microcontroller are connected.]

| Component | Pin / Connection | Function |
|---|---|---|
| [Component 1] | [Pin] | [Function] |
| [Component 2] | [Pin] | [Function] |

![Circuit Diagram](media/circuit-diagram.png)

### 3.4 Lighting & Shadow Alignment

1. [Position the projection screen.]
2. [Adjust the light source angle.]
3. [Position the shadow objects.]
4. [Check the projected shadows and movement range.]

### 3.5 Power-On Check

[Describe the checks required before switching on the complete system.]

---

## 4. Software Setup

### 4.1 Installation

[List the required software, libraries, and installation steps.]

### 4.2 Uploading the Code

1. [Open the relevant project file.]
2. [Select the correct board and port.]
3. [Upload the firmware.]
4. [Confirm successful upload.]

### 4.3 Communication Configuration

| Setting | Value | Description |
|---|---|---|
| Board | [Board] | Microcontroller |
| Serial Port | [Port] | Communication port |
| Baud Rate | [Value] | Serial communication |
| [Other Setting] | [Value] | [Description] |

### 4.4 Calibration

[Describe sensor thresholds, motor limits, light positions, and any calibration required.]

---

## 5. How to Run

### 5.1 Starting the System

1. [Connect the required hardware.]
2. [Power on the system.]
3. [Launch the required software.]
4. [Check the communication status.]
5. [Start the interactive theatre.]

### 5.2 Running the Shadow Theatre

[Explain the normal operating sequence from startup to audience interaction.]

### 5.3 Shutting Down

1. [Stop the running program.]
2. [Return moving mechanisms to a safe position, if applicable.]
3. [Disconnect the power supply.]

---

## 6. Interaction Guide

### 6.1 Audience Instructions

[Explain how visitors should interact with the theatre.]

### 6.2 Interaction Sequence

| Step | Audience Action | System Response | Shadow / Story Effect |
|---|---|---|---|
| 1 | [Action] | [Response] | [Effect] |
| 2 | [Action] | [Response] | [Effect] |
| 3 | [Action] | [Response] | [Effect] |

### 6.3 Story Progression

[Briefly describe how the audience's interactions influence the narrative and reveal different perspectives.]

---

## 7. Expected Results & Testing

### 7.1 Expected Behaviour

| Check | Pass When… |
|---|---|
| Code compilation and upload | [Expected result] |
| System startup | [Expected result] |
| Input detection | [Expected result] |
| Mechanical movement | [Expected result] |
| Lighting control | [Expected result] |
| Complete interaction sequence | [Expected result] |

### 7.2 Component Testing

[Document the tests performed on individual components.]

| Test | What It Checks | Result |
|---|---|---|
| [Mechanical Test] | [Description] | [Pass / Fail] |
| [Input Test] | [Description] | [Pass / Fail] |
| [Lighting Test] | [Description] | [Pass / Fail] |

### 7.3 Integration Testing

[Describe how the complete input-processing-output chain is tested.]

### 7.4 Known Behaviours

[Record expected system behaviours that should not be mistaken for faults.]

---

## 8. Debugging (Physical and Firmware)

### 8.1 Find the Failing Stage

Check each stage in order:

1. Power and hardware connections
2. Software startup
3. Input detection
4. Data processing and communication
5. Mechanical and lighting outputs
6. Complete interaction sequence

Stop at the first failing stage and investigate the corresponding subsystem.

### 8.2 Mechanical Issues

| Symptom | Likely Cause | Action |
|---|---|---|
| [Problem] | [Cause] | [Solution] |

### 8.3 Electrical Issues

| Symptom | Likely Cause | Action |
|---|---|---|
| [Problem] | [Cause] | [Solution] |

### 8.4 Software & Communication Issues

| Symptom | Likely Cause | Action |
|---|---|---|
| [Problem] | [Cause] | [Solution] |

### 8.5 Configuration Reference

| Setting | Default Value | What It Does |
|---|---|---|
| [Motor Pin] | [Value] | [Description] |
| [Sensor Threshold] | [Value] | [Description] |
| [Communication Port] | [Value] | [Description] |
| [Other Setting] | [Value] | [Description] |

---

## 9. Project Files

Example repository structure (update to match the actual files):

    Interactive-Shadow-Theatre/
    ├── README.md
    ├── code/
    │   ├── arduino/
    │   └── processing/
    ├── hardware/
    │   ├── mechanical/
    │   └── circuits/
    ├── media/
    └── docs/

| Folder | Contents |
|---|---|
| `code/` | Firmware and software |
| `hardware/` | Mechanical designs and circuit diagrams |
| `media/` | Photos, diagrams, and videos |
| `docs/` | Supporting documentation and test records |

---

## 10. Demonstration & Limitations

### 10.1 Final Demonstration

[Insert a photo or GIF of the completed installation.]

[Add a link to the demonstration video.]

### 10.2 Known Limitations

[Describe any limitations observed during testing.]

### 10.3 Future Improvements

[Describe potential improvements to the mechanics, interaction, lighting, or storytelling.]

---

## 11. References

- [Conceptual inspiration]
- [Technical documentation]
- [Software libraries]
- [Image and media credits]
