# Team guide: using the connection test and moving to live capture

Read `README.md` first for the details of each script. This guide is the short version
for the team, plus the plan for replacing the static image with the webcam.

## Status
| Part | State |
|---|---|
| Image -> landmarks -> OSC -> Wekinator -> bridge -> Arduino LED | **Built and tested** (this folder) |
| Live webcam capture | **Not built yet.** Plan below |
| Several gesture classes in Wekinator | **Not done yet.** Plan below |
| Final Arduino sketch with servos | **Not done yet** (`Code/Arduino/stageControl` is an empty skeleton) |

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

    python -m pip install mediapipe==1.1.1 python-osc==1.9.3 pyserial==3.5

**`pyserial`, never `serial`.** Both import as `serial`, but the package called `serial` is a
different project, and `serial.Serial` then fails.

Check everything imports (should print `True`):

    python -c "import mediapipe, pythonosc, serial; print(hasattr(serial, 'Serial'))"

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
`--serial-port` parameter, not in the code.

## 2. Run order (every time)
1. Upload the sketch with the Serial Monitor **closed**.
2. Start `bridge` (`--serial-port <your COM port>`).
3. Start Wekinator and press **Run**.
4. Start the sender.

Stop anything with the red Stop square in its PyCharm tab. The LED should go off within about 1 s.

## 3. Ports and addresses (do not change without telling the team)
| Link | Protocol | Address |
|---|---|---|
| Sender -> Wekinator | OSC over UDP | `127.0.0.1:6448`, `/wek/inputs`, 63 floats |
| Wekinator -> bridge | OSC over UDP | `127.0.0.1:12000`, `/wek/outputs`, class as a float |
| Bridge -> Arduino | USB serial | your COM port, 115200 baud, text line `"<class>\n"` |
| Arduino -> bridge | USB serial | `"ACK <class>\n"` |

## 4. Plan: live webcam capture (to build)
Make a new script, e.g. `landmarks_live.py`, **a copy of `landmarks_sender.py`**. Keep the
working image sender untouched as the reference test. Reuse `normalise()`, `build_message()`
and the OSC code as they are, because Wekinator must receive exactly the same kind of 63 numbers.

### What changes
| | Image sender (today) | Live sender (to build) |
|---|---|---|
| Input | one image file | webcam frames, one after another |
| MediaPipe mode | `RunningMode.IMAGE` | `RunningMode.VIDEO` (simplest), frame timestamps must increase |
| Detection | once, before the loop | **every frame**, inside the loop |
| Sending | same message repeated at `--rate` | one message per frame (cap about 30 per second) |
| No hand | 63 zeros | 63 zeros (unchanged) |
| Stopping | Ctrl+C / Stop | Ctrl+C / Stop, plus a key such as `q` in the preview window |

### Suggested build steps (one at a time, test each)
1. **Camera only:** open the webcam with OpenCV (`cv2.VideoCapture(0)`, on Windows
   `cv2.CAP_DSHOW` is often more reliable), show the frames in a window, quit with `q`.
   OpenCV is already installed as a MediaPipe dependency.
2. **Detection per frame:** convert each frame from BGR to RGB, wrap it with
   `mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)`, call
   `detector.detect_for_video(image, timestamp_ms)`. Draw the landmarks on the preview so
   you can see what the detector sees.
3. **Send:** reuse `build_message()` + `SimpleUDPClient`. Print the same status line
   (hand found yes/no, messages sent).
4. **Test with Wekinator** in Run mode using the existing 1-class project: output 1,
   LED on while a hand is in view or not (one class gives 1 for everything).
5. Only then train real classes (next section).

### Keep these identical between training and live use
Wekinator learns from whatever it receives while recording. If anything below differs when
the model is used, recognition gets worse:
- same camera, same position and lighting as much as possible
- same mirroring (`cv2.flip`) setting. Decide once and write it down
- same `normalise()` (wrist origin, wrist to middle-finger-base scale)
- same hand (one hand only, `num_hands=1`), handedness is **not** sent
- same 63-input order

## 5. Plan: real gestures in Wekinator
1. Decide the gesture list and give each a class number (for example 1 = open hand,
   2 = fist, 3 = pointing). Write it in the README.
2. New Wekinator project: 63 inputs, 1 output, classifier, **number of classes = number of
   gestures**, k-NN, same ports and addresses as in section 3.
3. Run the live sender. For each class: set the class value, hold the gesture, record
   3 to 5 seconds while moving the hand a little (distance, angle), stop.
4. Train, Run, test every gesture. Add examples where it mistakes one for another.
5. Save the project in the repository (`wekinator/`) and commit it so everyone has the same model.
6. Check the **no hand** case: it will output one of the classes. Decide whether that is
   acceptable or whether to train an explicit "no hand" class (63 zeros are sent in that case).

## 6. Plan: Arduino side
- The connection-test sketch only understands `1` and the LED. The final sketch must map each
  class to a servo movement and keep the 1000 ms timeout idea (stop or rest position if the
  stream stops).
- The bridge already sends any integer class as text, so it should need no change.
- If the sketch also drives servos, prefer reading serial one character at a time into a
  buffer (non-blocking) instead of `readStringUntil`, so the servo timing is never delayed.

## 7. Team rules
- Only one program can hold the Arduino COM port: close the Serial Monitor before the bridge,
  and only one team member's bridge can use the board at a time.
- Do not commit `.idea/`. Add `.idea/` to `.gitignore` (ask before changing files outside this folder).
- Do not change ports, addresses, the 63-value order or `normalise()` without telling the team,
  as every other script depends on them.
- Each person keeps their own run configurations. The COM port is a run parameter, not a code change.
- If something fails, follow the chain in order: sender status line, Wekinator input indicator,
  bridge `[osc]` lines, bridge `[serial] sent` lines, Arduino `ACK`. The first link that is silent
  is the one to fix. See Troubleshooting in `README.md`.

## 8. Open decisions
- Mirror the webcam image or not?
- Gesture list and class numbers.
- Explicit "no hand" class or not.
- Who owns which part (live sender, Wekinator training, Arduino sketch)?
