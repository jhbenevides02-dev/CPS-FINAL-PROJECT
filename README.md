# CPS-FINAL-PROJECT
## Group 20
interactive-shadow-theatre/
│
├── README.md
├── LICENSE
├── CHANGELOG.md
│
├── firmware/
│   ├── src/
│   │   ├── main.cpp
│   │   ├── sensors.cpp
│   │   ├── state_machine.cpp
│   │   ├── lighting.cpp
│   │   └── actuators.cpp
│   ├── include/
│   └── platformio.ini
│
├── hardware/
│   ├── wiring/
│   │   ├── wiring-diagram.svg
│   │   └── pin-map.csv
│   ├── mechanical/
│   │   ├── theatre-frame.svg
│   │   ├── puppet-mechanism.svg
│   │   └── weight-platform.svg
│   └── bom.csv
│
├── story/
│   ├── story.json
│   ├── cues.csv
│   └── copy/
│       ├── en.json
│       └── zh-CN.json
│
├── assets/
│   ├── puppets/
│   ├── silhouettes/
│   ├── images/
│   ├── icons/
│   ├── audio/
│   └── references/
│
├── tests/
│   ├── sensor-test/
│   ├── actuator-test/
│   └── interaction-test/
│
├── presentation/
│   ├── source/
│   ├── export_pptx.py
│   └── interactive-shadow-theatre.pptx
│stateDiagram-v2
    [*] --> Idle

    Idle --> Attract: Motion detected
    Attract --> AwaitObject: Audience approaches

    AwaitObject --> ObjectDetected: Valid weight range
    ObjectDetected --> SceneOne: Object classified

    SceneOne --> LightExploration: Character movement complete

    LightExploration --> PerspectiveReveal: Light target reached
    LightExploration --> LightExploration: Light angle changes

    PerspectiveReveal --> Choice: Reveal alternative shadow

    Choice --> SceneA: Left button
    Choice --> SceneB: Right button

    SceneA --> Reflection
    SceneB --> Reflection

    Reflection --> Reset: End / timeout
    Reset --> Idle
└── docs/
    ├── assembly.md
    ├── calibration.md
    ├── troubleshooting.md
    └── credits.md
