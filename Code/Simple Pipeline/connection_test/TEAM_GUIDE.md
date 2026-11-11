# Team guide: using the pipeline (image test, webcam, training, music)

Read `README.md` first for the details of each script. This guide is the short version for the team.

## Status
| Part | State |
|---|---|
| Image -> landmarks -> OSC -> Wekinator -> bridge -> Arduino LED (connection test) | **Built and tested** |
| Live webcam capture (`landmarks_sender.py --webcam`) | **Built**, tested by the team |
| Training Wekinator from a photo dataset (`dataset_sender.py --class ...`) | **Built**. Classes: 1 = none, 2 = action, 3 = heart |
| Testing the trained model with random photos (`dataset_sender.py --test`) | **Built** (not yet run with new, unseen photos) |
| Bridge sends `s` (action) / `h` (heart) to the Arduino | **Built** |
| Music from the Arduino states (`bridge.py`) | **Built**, tested in `--dry-run`. **Not yet tested with the real Arduino** |
| Final Arduino sketch | In progress by the team (`Code/Quick Tests/TestPuppetScene`) |

## 1. First-time set-up (each team member, once)

### 1.1 Install the tools
1. **Anaconda** (Windows installer from anaconda.com). Choose "Just Me". You do **not** need to
   tick "Add Anaconda to PATH": PyCharm finds it by itself.
2. **PyCharm** (Community or Professional, from jetbrains.com). Both can use conda environments.
3. **Arduino IDE**, then *Tools > Board > Boards Manager* and install **Arduino megaAVR Boards**
   (we use the **Arduino Nano Every**).
4. **Wekinator** (desktop app, from wekinator.org). It needs Java, which is bundled with the
   current download. If Windows Firewall asks about Java, allow it on private networks.
5. **Git**, and the branch `Simple_pipeline` of the project.

### 1.2 Open the project in PyCharm
1. *File > Open* and choose the `connection_test` folder (`Code/Simple Pipeline/connection_test`).
   This folder is the project. Do not create a new project or sub-folder.
2. PyCharm creates a `.idea/` folder. It must not be committed.

### 1.3 Create the Python environment (inside PyCharm)
1. *File > Settings > Project: connection_test > Python Interpreter*.
2. Click **Add Interpreter > Add Local Interpreter > Conda Environment**.
3. **Conda executable:** if empty, browse to `...\anaconda3\Scripts\conda.exe`
   (usually `C:\Users\<you>\anaconda3\Scripts\conda.exe`).
4. Choose **Create new environment**, **Python version 3.11**, name it `cps`, then **OK**.
   (To reuse an environment you already have, choose **Use existing environment** instead.)
5. The bottom-right corner of PyCharm must now show the new interpreter (`cps`, Python 3.11).
   If it shows something else, click it and select the right one.

### 1.4 Install the packages (inside PyCharm)
Open the PyCharm terminal (`Alt+F12`). It should open in the `connection_test` folder with the
environment active. Check which Python it uses:

    python -c "import sys; print(sys.executable)"

The path must be inside your `cps` environment. If not, open a **new** terminal tab after
setting the interpreter. Then install, always with `python -m pip` so the packages go into
that same Python:

    python -m pip install mediapipe==1.1.1 python-osc==1.9.3 pyserial==3.5 pygame==2.6.1

**`pyserial`, never `serial`.** Both import as `serial`, but the package called `serial` is a
different project, and `serial.Serial` then fails. (`pygame` plays the music in the bridge.)

Check everything imports (should print `True`):

    python -c "import mediapipe, pythonosc, serial, pygame; print(hasattr(serial, 'Serial'))"

The pinned versions are also listed in `environment.yml`. Do not use it unless the team agrees
(it would be run from the Anaconda Prompt: `conda env create -f environment.yml`).

### 1.5 PyCharm run configurations
A run configuration is PyCharm's saved version of the command you would type in a terminal:
interpreter + script + parameters. Create one per script:
*Run > Edit Configurations > + > Python*, then fill in:
- **Name:** e.g. `bridge`
- **Script:** the `.py` file
- **Parameters:** whatever you would type after the script name (see the table in `README.md`)
- **Working directory:** the `connection_test` folder
- **Interpreter:** your `cps` environment

Different configurations (sender and bridge) run at the same time in separate tabs of the Run
window. Each tab has its own red Stop square. (Tick **Allow multiple instances** under
*Modify options* only if you need to start the *same* configuration twice.)

### 1.6 Find your COM port
Arduino IDE > *Tools > Port*, or Device Manager > Ports (COM & LPT). It is different on every
computer and can change when you use another USB socket. It goes in the bridge's
`--serial-port` parameter, not in the code. (`bridge.py` has `COM7` as its default.)

## 2. Run order for the show (every time)
1. Upload the Arduino sketch with the Serial Monitor **closed**.
2. Start `bridge` (`--serial-port <your COM port>`). Wait for the `[music] ready` line.
3. Start Wekinator (the trained project) and press **Run**.
4. Start `sender webcam` (`--webcam`).

Stop anything with the red Stop square in its PyCharm tab (or `q` / `Esc` in a preview window).
Only one program can use port 12000 and the COM port at a time: do not run `dataset_sender.py --test`
together with the bridge.

## 3. Ports and addresses (do not change without telling the team)
| Link | Protocol | Address |
|---|---|---|
| Sender -> Wekinator | OSC over UDP | `127.0.0.1:6448`, `/wek/inputs`, 63 floats |
| Wekinator -> bridge | OSC over UDP | `127.0.0.1:12000`, `/wek/outputs`, class as a float |
| Bridge -> Arduino | USB serial | your COM port, 115200 baud, one character: `s` (class 2) or `h` (class 3) |
| Arduino -> bridge | USB serial | text lines, e.g. `catrina -> DANCE`, used for the music |

## 4. Webcam capture
`landmarks_sender.py` has two modes. Image mode (`test_hand.jpg`) is the reference test and
is unchanged. Webcam mode: Parameters `--webcam`.

- Options: `--camera 1` (another camera), `--mirror` (flip left-right), `--rate 10` (default 15).
- One detection and one OSC message every 1/15 s. No hand found: 63 zeros are sent.
- A window shows the camera with the landmarks drawn. `q` / `Esc` quits.
- If the camera does not open, another program (Zoom, Teams) is probably using it.

### Keep these identical between training and live use
Wekinator learns from whatever it receives while recording. If anything below differs when
the model is used, recognition gets worse:
- same camera, position and lighting as much as possible
- same mirroring (`--mirror` or not). The photo dataset is **not** mirrored, so use no `--mirror`
  unless the dataset was recorded mirrored
- same `normalise()` (wrist origin, wrist to middle-finger-base scale)
- one hand only (`num_hands=1`), handedness is **not** sent
- same 63-input order

## 5. Training Wekinator from the photo dataset (by hand)
The script only plays the photos into Wekinator. You press Record and Train yourself.

**Dataset layout** (inside `connection_test`): one folder per class, with the photos inside:
`dataset/none/`, `dataset/action/`, `dataset/heart/` (`.jpg`, `.jpeg`, `.png`).

**Wekinator classes:** 63 inputs (port 6448, `/wek/inputs`), 1 output, classifier, **3 classes**, k-NN,
sends to `localhost:12000`, `/wek/outputs`.

| Class number | Name | Folder | Letter sent to the Arduino |
|---|---|---|---|
| 1 | none (no gesture) | `dataset/none` | nothing |
| 2 | action | `dataset/action` | `s` |
| 3 | heart | `dataset/heart` | `h` |

**For each class:**
1. Run `dataset_sender.py --class <name>` (e.g. `--class heart`). It shows each photo in a window and
   sends it for `--burst` seconds (default 5), photo after photo, in a loop.
2. In Wekinator set the output class to the class number, press **Start recording** while it runs,
   record at least one full pass of the photos, stop. Then stop the script.
3. After all three classes: **Train**, then **Run**. Save the project in `wekinator/`.

**Class `none`:** photos where no hand is found are **not skipped** for this class: they are sent as
63 zeros, exactly what the live sender sends when it sees no hand. Include some photos with no hand at all.

**Balance:** try to record similar numbers of photos per class, or k-NN leans toward the biggest class.

**Testing the model:** `dataset_sender.py --test --classes none,action,heart`
- Wekinator in Run mode, bridge **stopped** (both use port 12000).
- Random photos are sent. The window draws the landmarks, shows the true class, and Wekinator's
  answer (green = right, red = wrong or no answer). The console prints a score line per photo.
- Testing with the **training photos** looks almost perfect and proves little. Use **new photos** in a
  separate folder (`dataset_test/none`, `dataset_test/action`, `dataset_test/heart`) with
  `--dataset dataset_test`.

## 6. Bridge, Arduino and music
**Class to letter** (`CLASS_COMMANDS` at the top of `bridge.py`): 2 -> `s`, 3 -> `h`. Class 1 (none)
sends nothing. `COMMAND_ENDING` is `""` (only the character); set it to `"\n"` if the sketch reads lines.

**Keep-alive:** while the same class stays, the bridge re-sends its letter about every 250 ms
(`KEEPALIVE_S`). If a letter starts a movement, check this does not retrigger it.

**Music** (`bridge.py`, reads the Arduino's state lines `<actor> -> <STATE>`):

| Arduino state | Music |
|---|---|
| `IDLE`, `MOVE_12`, `MOVE_21`, `HOLD` | Track 1 (`music/Track_1.mp3`), looping |
| `DANCE` (any actor) | Track 2 (`music/Track_2.mp3`), looping |
| `EXIT` (all actors) | Stops (fade-out). The next `IDLE` starts track 1 again |
| `HOMING` | Keeps what is playing |

- `--no-music` turns the music off. If `pygame` or a track file is missing, the bridge says so and
  carries on without music.
- **Test without the Arduino:** run `bridge` with `--dry-run`, click in the console and type a state
  (`IDLE`, `DANCE`, `HOLD`, `EXIT`, or a full line like `catrina -> DANCE`).
- If the final sketch prints the states differently, change `STATE_LINE` in `bridge.py`.

## 7. Team rules
- Only one program can hold the Arduino COM port: close the Serial Monitor before the bridge,
  and only one team member's bridge can use the board at a time.
- Do not commit `.idea/`. Add `.idea/` to `.gitignore` (ask before changing files outside this folder).
- Do not change ports, addresses, the 63-value order or `normalise()` without telling the team,
  as every other script depends on them.
- Each person keeps their own run configurations. The COM port is a run parameter, not a code change.
- If something fails, follow the chain in order: sender status line, Wekinator input indicator,
  bridge `[osc]` lines, bridge `[serial] sent` lines, Arduino output. The first link that is silent
  is the one to fix. See Troubleshooting in `README.md`.

## 8. Open decisions
- Mirror the webcam image or not (it must match the training data).
- Does a repeated letter every 250 ms cause problems for the Arduino movements?
- Should the music be silent in `IDLE` after a show (today it restarts track 1)?
- Who owns which part (Wekinator training, Arduino sketch, music)?
