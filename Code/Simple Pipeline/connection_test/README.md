# Connection test: Python -> Wekinator -> Python -> Arduino

## Purpose
Prove that a message can travel through the whole CPS pipeline, using one static image
and the built-in LED of the Arduino. This is **not** gesture recognition (see the note
at the end).

## Pipeline
```
test_hand.jpg
     |
     v
landmarks_sender.py   MediaPipe -> 21 landmarks x (x, y, z) = 63 floats (normalised)
     |  OSC /wek/inputs, UDP, 127.0.0.1:6448
     v
Wekinator             classifier, k-NN, 1 class
     |  OSC /wek/outputs, UDP, 127.0.0.1:12000
     v
bridge.py             class -> text line "1\n"
     |  USB serial, 115200 baud, e.g. COM7
     v
connection_test.ino   Arduino Nano Every: LED on, replies "ACK 1"
     |  "ACK 1\n" back over the same serial port
     v
bridge.py             prints the reply
```

## Files
| File | What it is |
|---|---|
| `environment.yml` | Pinned package versions (Python 3.11, mediapipe, python-osc, pyserial) |
| `landmarks_sender.py` | Part 1: image -> 63 floats -> OSC `/wek/inputs` |
| `bridge.py` | Part 3: OSC `/wek/outputs` -> serial text line |
| `connection_test/connection_test.ino` | Part 4: Arduino test sketch (folder name = file name) |
| `wekinator/` | Saved Wekinator project |
| `hand_landmarker.task`, `test_hand.jpg`, `no_hand.jpg` | MediaPipe model and test images |
| `LEARNING_LOG.md` | What we built and learned, for the contribution log and AI-use notice |

## Set-up
### Python (PyCharm + conda)
1. Open the `connection_test` folder as the PyCharm project.
2. **Settings > Project > Python Interpreter**: choose a conda environment with Python 3.11
   (see `environment.yml`).
3. Install the packages inside that environment, from the PyCharm terminal:
   `python -m pip install mediapipe==1.1.1 python-osc==1.9.3 pyserial==3.5`
   Install **`pyserial`, never `serial`** (both import as `serial`).
4. Check: `python -c "import mediapipe, pythonosc, serial; print(hasattr(serial, 'Serial'))"` prints `True`.

### PyCharm run configurations
Create one per script (Run > Edit Configurations > + > Python). Set the script, the
working directory (`connection_test` folder) and the interpreter. Different configurations
run at the same time in separate tabs.

| Name | Script | Parameters |
|---|---|---|
| `sender hand` | `landmarks_sender.py` | `test_hand.jpg` |
| `sender no hand` | `landmarks_sender.py` | `no_hand.jpg` |
| `bridge dry run` | `bridge.py` | `--dry-run` |
| `bridge` | `bridge.py` | `--serial-port COM7` (use your port) |

Optional sender arguments: `--host`, `--port`, `--rate`, `--print-values`.
Optional bridge arguments: `--osc-port`, `--baud`.

### Arduino IDE
1. *Tools > Board > Boards Manager*: install **Arduino megaAVR Boards** (once).
2. *Tools > Board*: **Arduino Nano Every**.
3. *Tools > Port*: the COM port of the board. Device Manager > Ports (COM & LPT) also lists it.
4. Open `connection_test/connection_test.ino`, **Upload**.
5. **Close the Serial Monitor** afterwards. Only one program can hold the port.

### Wekinator
- Inputs: 63, listening on port `6448`, message `/wek/inputs`.
- Outputs: 1, **all classifiers**, 1 class, algorithm k-NN, sending to `localhost` port `12000`, message `/wek/outputs`.
- Record a few seconds of class 1 while the sender runs, **Train**, then **Run**.
- The saved project is in `wekinator/`.

## Run order
1. Upload the sketch (Serial Monitor closed).
2. Start **bridge** in PyCharm. Wait for `Opened COM7 ... Waiting 2.0 s`.
3. Start Wekinator and press **Run**.
4. Start **sender hand** in PyCharm.

## Pass criteria
- The LED turns on and stays on while everything runs.
- The bridge console shows `[osc]`, `[serial] sent '1'` and `[arduino] ACK 1` lines.
- Stopping the sender, or stopping Wekinator, turns the LED off within about 1 s.
- Starting the sender again turns the LED on again.

## Troubleshooting
<!-- TODO (written by the team): one entry per problem: symptom, cause, fix. -->

## What this test does and does not prove
With only one class, Wekinator's k-NN classifier outputs 1 for any input, even 63 zeros
(no hand). So this test proves the **connection** (messages arrive at every stage, the
Arduino reacts, and the timeout notices when the stream stops). It does **not** test
gesture **recognition**.
