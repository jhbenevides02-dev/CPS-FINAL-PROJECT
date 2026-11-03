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

## 1. System Architecture

### 1.1 System Overview

[Explain how the mechanical, electronic, and software components work together.]

![System Architecture](media/system-architecture.png)

### 1.2 Input System

[Describe the input methods and what they detect.]

| Input Device | Function | Connection |
|---|---|---|
| [Sensor 1] | [Function] | [Pin / Port] |
| [Sensor 2] | [Function] | [Pin / Port] |

### 1.3 Mechanical & Lighting System

[Explain how mechanical movement and lighting create different shadow effects.]

### 1.4 Control & Communication

[Describe the communication between the microcontroller, software, sensors, and actuators.]

| Connection | Protocol / Setting | Purpose |
|---|---|---|
| [Device A → Device B] | [Setting] | [Function] |

---

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
