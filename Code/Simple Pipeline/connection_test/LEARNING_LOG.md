# Learning log: connection test

Used for the contribution log and the AI-use notice.

## Part 0: Environment
- **Built:** `environment.yml` (pinned `mediapipe==1.1.1`, `python-osc==1.9.3`, `pyserial==3.5`) and a PyCharm interpreter set up with the packages installed through the PyCharm terminal.
- **Written by me:** the interpreter set-up, package installs and the import check (`check_env.py`). The `environment.yml` was drafted by Claude.
- **Learned:** why versions are pinned, how pip installs into a specific interpreter (`python -m pip`), and that `pyserial` and `serial` both import as `serial`, so only `pyserial` is installed.

## Part 1: landmarks_sender.py
- **Built:** a script that detects one hand in an image with MediaPipe (Tasks API), normalises it to 63 floats and sends them to Wekinator over OSC (`/wek/inputs`, port 6448) at a fixed rate, with 63 zeros if no hand is found. The model file was copied into the test folder.
- **Written by me:** the `normalise()` function (subtract the wrist, divide by the wrist to middle-finger-base distance) and the PyCharm run configurations. Claude wrote the argument parsing, detection, OSC send loop and status line, and reviewed my function.
- **Learned:** why landmarks are normalised for position and scale, why the ruler is the palm and not a fingertip, how UDP/OSC sends without confirming delivery, why PyCharm run configurations hold the script arguments, and why a fixed 63-value message (zeros for no hand) keeps Wekinator's input count stable.

## Part 2: Wekinator set-up
- **Built:** a Wekinator project with 63 inputs (port 6448, `/wek/inputs`) and 1 classifier output with 1 class (k-NN), sending `/wek/outputs` to port 12000. Trained on a few seconds of the sender's stream, run, and saved in `wekinator/`.
- **Written by me:** the whole set-up, done by hand in the Wekinator GUI (no code). Claude explained each screen.
- **Learned:** how k-NN stores examples and votes among the nearest ones, why one class always gives output 1, and that Wekinator only outputs while inputs arrive. This test proves the connection, not gesture recognition.

## Part 3: bridge.py
- **Built:** a script that listens for Wekinator's `/wek/outputs` on port 12000, converts the class to an int, and sends it as a text line over USB serial. It sends on change plus a keep-alive every 250 ms, waits 2 s for the Arduino reset, prints Arduino replies from a background thread, and has a `--dry-run` mode and a clear error if the port is busy. Tested in dry run with Wekinator and the sender running.
- **Written by me:** `should_send()` (send if the value changed or 250 ms passed) and the PyCharm run configuration. Claude wrote the argument parsing, serial opening, reader thread, OSC handler and server.
- **Learned:** how an OSC dispatcher calls a handler per message, why the keep-alive sits in the handler (so it stops when Wekinator stops and the Arduino timeout turns the LED off), why the Arduino resets when the port opens, what baud rate means, and why a thread is used to read replies.

## Part 4: connection_test.ino
- **Built:** a test sketch for the Arduino Nano Every. It reads one line at a time from serial (115200), turns the built-in LED on and replies `ACK 1` when it gets `1`, and turns the LED off if nothing arrives for 1000 ms. Tested on its own with the Arduino IDE Serial Monitor (Newline).
- **Written by me:** the whole sketch (serial setup, line reading, LED logic, `millis()` timeout, `Serial.setTimeout(50)` to avoid blocking). Claude gave the spec and reviewed it (initial timestamp, template comments).
- **Learned:** non-blocking timing with `millis()` instead of `delay()`, why `readStringUntil` can block (and how `setTimeout` limits it), why the 250 ms keep-alive sits well inside the 1000 ms timeout, and that the Nano Every uses the megaAVR core with no old-bootloader option.
