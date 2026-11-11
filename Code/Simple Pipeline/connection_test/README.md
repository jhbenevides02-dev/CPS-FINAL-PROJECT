# Connection test: Python -> Wekinator -> Python -> Arduino

## Purpose
Prove that a message can travel through the whole CPS pipeline, using one static image
and the built-in LED of the Arduino. This is **not** gesture recognition (see the note
at the end).

The same folder has since grown into the working pipeline: webcam capture, training from a photo
dataset, the class-to-letter mapping for the stage Arduino, and music. See "Beyond the connection
test" below, and `TEAM_GUIDE.md` for the short team version.

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
| `environment.yml` | Pinned package versions (Python 3.11, mediapipe, python-osc, pyserial, pygame) |
| `landmarks_sender.py` | Part 1: image **or webcam** -> 63 floats -> OSC `/wek/inputs` |
| `dataset_sender.py` | Plays a photo dataset into Wekinator (training) or tests the trained model (`--test`) |
| `bridge.py` | Part 3: OSC `/wek/outputs` -> serial (class 2 -> `s`, class 3 -> `h`), plus music |
| `dataset/<class>/`, `music/` | Training photos per class (`none`, `action`, `heart`), and `Track_1.mp3`, `Track_2.mp3` |
| `TEAM_GUIDE.md` | Short guide for the team |
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
   `python -m pip install mediapipe==1.1.1 python-osc==1.9.3 pyserial==3.5 pygame==2.6.1`
   Install **`pyserial`, never `serial`** (both import as `serial`). `pygame` is only for the music.
4. Check: `python -c "import mediapipe, pythonosc, serial, pygame; print(hasattr(serial, 'Serial'))"` prints `True`.

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
| `sender webcam` | `landmarks_sender.py` | `--webcam` |
| `dataset heart` / `dataset action` / `dataset none` | `dataset_sender.py` | `--class heart` / `--class action` / `--class none` |
| `dataset test` | `dataset_sender.py` | `--test --classes none,action,heart` |

Optional sender arguments: `--host`, `--port`, `--rate` (default 30, webcam 15), `--print-values`,
and for the webcam `--camera N`, `--mirror`. Give **either** an image path **or** `--webcam`.
Optional dataset arguments: `--dataset <folder>`, `--burst <seconds>` (default 5), `--rate`;
test mode also `--listen-port`.
Optional bridge arguments: `--osc-port`, `--baud`, `--no-music`.

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

## Beyond the connection test
### Webcam
`landmarks_sender.py --webcam` replaces the image: one detection and one OSC message every 1/15 s,
63 zeros when no hand is found, a preview window with the landmarks drawn (`q` / `Esc` quits).
Use the same mirroring (`--mirror` or not) for training and use.

### Training Wekinator from the photo dataset (manual)
Wekinator project for the stage: 63 inputs, 1 classifier output, **3 classes**, k-NN. Class numbers:
**1 = none (no gesture), 2 = action, 3 = heart.**
1. Photos in `dataset/none`, `dataset/action`, `dataset/heart`.
2. For each class run `dataset_sender.py --class <name>`. It shows each photo and sends it for `--burst`
   seconds, in a loop. In Wekinator set the class number and press **Start recording**, then stop.
   For `none`, photos without a hand are sent as 63 zeros (like the live sender).
3. **Train**, **Run**, save the project in `wekinator/`.
4. Test: `dataset_sender.py --test --classes none,action,heart` (Wekinator in Run mode, bridge stopped).
   Use **unseen** photos (`--dataset dataset_test`) for a real accuracy figure.

### Bridge to the stage Arduino
Class 2 -> `s`, class 3 -> `h` (`CLASS_COMMANDS` in `bridge.py`), class 1 sends nothing. The character is
sent alone (`COMMAND_ENDING = ""`). While a class is held, its letter is repeated about every 250 ms.

### Music
The bridge reads the Arduino's `<actor> -> <STATE>` lines (e.g. `catrina -> DANCE`): track 1
(`music/Track_1.mp3`) in `IDLE`, `MOVE_12`, `MOVE_21`, `HOLD`; track 2 (`Track_2.mp3`) while any actor is in
`DANCE`; stops when all actors are in `EXIT`; `HOMING` keeps the current track. Test without the Arduino:
`bridge.py --dry-run`, then type states (`IDLE`, `DANCE`, `HOLD`, `EXIT`) in the console. `--no-music` disables it.

## Troubleshooting
<!-- TODO (written by the team): one entry per problem: symptom, cause, fix. Also cover: camera does not
open (another program uses it), `[music]` messages (pygame missing, track file missing), port 12000 busy
(bridge and `dataset_sender.py --test` both listen on it). -->

## What this test does and does not prove
With only one class, Wekinator's k-NN classifier outputs 1 for any input, even 63 zeros
(no hand). So this test proves the **connection** (messages arrive at every stage, the
Arduino reacts, and the timeout notices when the stream stops). It does **not** test
gesture **recognition**.
