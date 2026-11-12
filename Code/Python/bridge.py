"""
bridge.py: Part 3 of the CPS connection test.

Wekinator -> OSC /wek/outputs (port 12000) -> this script -> USB serial -> Arduino

Usage (PyCharm: Run > Edit Configurations > Parameters):
    bridge.py --serial-port COM5 [--osc-port 12000] [--baud 115200]
    bridge.py --dry-run          (no Arduino: just print what would be sent)
"""
import argparse
import os
import re
import sys
import threading
import time
from pathlib import Path

import serial   # this is the "pyserial" package (never install the package called "serial")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")   # no welcome banner in the console
try:
    import pygame   # plays the music (pip install pygame). The bridge still works without it.
except ImportError:
    pygame = None
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher


# ---- Settings (change here, not in the code below) ----
OSC_HOST = "127.0.0.1"        # listen on this computer only
DEFAULT_OSC_PORT = 12000      # Wekinator's default output port
OSC_ADDRESS = "/wek/outputs"  # Wekinator's default output message
DEFAULT_BAUD = 115200         # must match Serial.begin() in the Arduino sketch
ARDUINO_DEFAULT_PORT = "COM7" # Default COM port used in Arduino Nano Every test board.
RESET_WAIT_S = 2.0            # the Arduino resets when the port opens; give it time to boot
KEEPALIVE_S = 0.25            # (not used any more: letters are now sent once per hold, see HOLD_S)
HOLD_S = 3.0                  # a class must be held this long before its letter is sent (45 frames at 15 Hz)
MAX_GAP_S = 0.5               # no OSC message for longer than this restarts the count
# Wekinator class number -> character sent to the Arduino. Other classes send nothing.
CLASS_COMMANDS = {
    2: "s",   # action
    3: "h",   # heart
}
COMMAND_ENDING = ""           # added after the character. "" = just the character, "\n" = a full line
# Music: which track plays in which Arduino state. HOMING keeps the current track; EXIT stops the music.
MUSIC_FOLDER = Path(__file__).parent / "music"
TRACK_FILES = {1: MUSIC_FOLDER / "Track_1.mp3", 2: MUSIC_FOLDER / "Track_2.mp3"}
TRACK_1_STATES = {"IDLE", "MOVE_12", "MOVE_21", "HOLD"}
TRACK_2_STATES = {"DANCE"}
STOP_STATE = "EXIT"           # an actor reaching this state has finished its show
SHOW_START_STATE = "MOVE_12"  # an actor entering this state starts a new show (music may start again)
KNOWN_STATES = TRACK_1_STATES | TRACK_2_STATES | {STOP_STATE, "HOMING"}   # other words are ignored
MUSIC_FADE_MS = 500           # fade-in when a track starts, fade-out when it stops
STATE_LINE = re.compile(r"^(\w+)\s*->\s*(\w+)$")   # the Arduino prints e.g. "catrina -> MOVE_12"


def parse_args():
    """Read the command-line arguments (set in the PyCharm run configuration)."""
    parser = argparse.ArgumentParser(description="Bridge Wekinator OSC output to an Arduino over serial.")
    parser.add_argument("--osc-port", type=int, default=DEFAULT_OSC_PORT, help="port to listen on for Wekinator")
    parser.add_argument("--serial-port", default=ARDUINO_DEFAULT_PORT, help="Arduino COM port, e.g. COM5 (required unless --dry-run)")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD, help="serial baud rate")
    parser.add_argument("--dry-run", action="store_true", help="no serial port: only print")
    parser.add_argument("--no-music", action="store_true", help="do not play the music tracks")
    args = parser.parse_args()
    if not args.dry_run and not args.serial_port:
        parser.error("--serial-port is required (or use --dry-run)")
    return args


def open_serial(port, baud):
    """Open the Arduino's serial port, wait for its reset to finish, and return it."""
    try:
        # timeout=1: readline() gives up after 1 s, so the reader thread can check if it should stop.
        ser = serial.Serial(port, baud, timeout=1)
    except serial.SerialException as error:
        sys.exit(
            f"Could not open {port}: {error}\n"
            "  - Is the Arduino IDE Serial Monitor (or another program) using the port? Close it.\n"
            "  - Is the COM port right? Check Arduino IDE > Tools > Port, or Device Manager."
        )
    print(f"Opened {port} at {baud} baud. Waiting {RESET_WAIT_S} s for the Arduino to reset...")
    time.sleep(RESET_WAIT_S)
    ser.reset_input_buffer()    # throw away anything the Arduino printed while booting
    return ser


class MusicPlayer:
    """Plays track 1 or track 2 (looping), depending on the states the Arduino prints."""

    def __init__(self, enabled=True):
        self.states = {}          # latest state of each actor, e.g. {"catrina": "IDLE", "mariachi": "IDLE"}
        self.done = set()         # actors that reached EXIT and have not started a new show yet
        self.current = None       # track playing now: 1, 2 or None
        self.enabled = False      # becomes True only if pygame and the files are available
        if not enabled:
            return
        if pygame is None:
            print("[music] pygame is not installed (python -m pip install pygame): no music.")
            return
        missing = [str(path) for path in TRACK_FILES.values() if not path.is_file()]
        if missing:
            print(f"[music] track file(s) not found: {missing}. No music.")
            return
        try:
            pygame.mixer.init()   # opens the computer's audio output
        except pygame.error as error:
            print(f"[music] could not open the audio output: {error}. No music.")
            return
        self.enabled = True
        print("[music] ready: track 1 in IDLE/MOVE_12/MOVE_21/HOLD, track 2 in DANCE, stops in EXIT.")

    def on_arduino_line(self, line):
        """Called for every line from the Arduino. Only state lines ('catrina -> DANCE') matter."""
        if not self.enabled:
            return
        match = STATE_LINE.match(line)
        if not match:
            return
        actor, state = match.groups()
        if state not in KNOWN_STATES:      # e.g. the sketch also prints "Servos -> A": not a puppet state
            return
        self.states[actor] = state

        # The Arduino goes EXIT -> IDLE almost at once. So an actor that has reached EXIT is "done":
        # its IDLE is ignored (otherwise track 1 would restart straight away) until it starts a new
        # show (MOVE_12).
        if state == STOP_STATE:
            self.done.add(actor)
        elif state == SHOW_START_STATE:
            self.done.discard(actor)

        # Decide from the actors that are not done (a state line only changes one actor):
        #   any actor in DANCE                          -> track 2
        #   else any actor in IDLE/MOVE_12/MOVE_21/HOLD -> track 1
        #   else (everyone done, or in HOMING)          -> no music
        current_states = {s for a, s in self.states.items() if a not in self.done}
        if TRACK_2_STATES & current_states:
            self.play(2)
        elif TRACK_1_STATES & current_states:
            self.play(1)
        else:
            self.stop_music()

    def play(self, track):
        """Start a track (looping). Does nothing if it is already playing."""
        if track == self.current:
            return
        pygame.mixer.music.load(str(TRACK_FILES[track]))
        pygame.mixer.music.play(loops=-1, fade_ms=MUSIC_FADE_MS)   # loops=-1: repeat until changed
        self.current = track
        print(f"[music] playing track {track}")

    def stop_music(self):
        """Fade the music out. The next IDLE starts track 1 again."""
        if self.current is None:
            return
        pygame.mixer.music.fadeout(MUSIC_FADE_MS)   # waits until the fade is finished
        self.current = None
        print("[music] stopped")

    def stop(self):
        if self.enabled:
            pygame.mixer.music.stop()
            pygame.mixer.quit()


def read_replies(ser, stop_event, music):
    """Background thread: print every line the Arduino sends back and let the music react to it."""
    while not stop_event.is_set():
        try:
            line = ser.readline().decode(errors="ignore").strip()
        except serial.SerialException:   # port closed or unplugged
            break
        if line:
            print(f"[arduino] {line}")
            try:
                music.on_arduino_line(line)
            except Exception as error:   # a music problem must never stop the bridge
                print(f"[music] error: {error}")


def simulate_arduino(music):
    """Dry run only: lines you type in the PyCharm Run console act as the Arduino's state lines.
    Type 'DANCE' (or the full line 'catrina -> DANCE'). Background thread."""
    print("[dry-run] To test the music, click in this console and type a state, then Enter: "
          "IDLE, MOVE_12, MOVE_21, DANCE, HOLD ...")
    while True:
        try:
            text = input().strip()
        except EOFError:          # the console has no input available
            return
        if not text:
            continue
        line = text if "->" in text else f"test -> {text.upper()}"   # 'DANCE' -> 'test -> DANCE'
        print(f"[simulated arduino] {line}")
        music.on_arduino_line(line)


def should_send(value, last_value, last_sent_time, now):
    """TODO (you write this): decide whether this OSC value should go to the Arduino now."""
    send = False
    if last_value is None:
        send = True
    elif value != last_value:
        send = True
    else :
        if (now-last_sent_time) > KEEPALIVE_S:
            send= True
    return send


def make_handler(ser, dry_run):
    """Return the function python-osc calls for every /wek/outputs message.
    A letter is sent ONCE, only after the same class has been held for HOLD_S seconds."""
    # Remembered between messages:
    #   held_class: the class we are counting for, held_since: when it started,
    #   last_message: when the last OSC message arrived, sent: letter already sent for this hold,
    #   last_progress: when the progress line was last printed
    state = {"held_class": None, "held_since": 0.0, "last_message": 0.0,
             "sent": False, "last_progress": 0.0}

    def on_outputs(address, *values):
        if not values:
            return
        value = int(round(values[0]))        # Wekinator sends the class as a float, e.g. 2.0
        print(f"[osc] {address} {values}")
        now = time.monotonic()

        # A different class, or a gap in the messages, starts a new count from zero
        if value != state["held_class"] or now - state["last_message"] > MAX_GAP_S:
            if state["held_class"] is not None and value != state["held_class"]:
                print(f"[bridge] class changed {state['held_class']} -> {value}: count restarts")
            state["held_class"] = value
            state["held_since"] = now
            state["sent"] = False
            state["last_progress"] = now
        state["last_message"] = now
        held_for = now - state["held_since"]

        # Turn the class number into the character for the Arduino (2 -> 's', 3 -> 'h')
        command = CLASS_COMMANDS.get(value)
        if command is None:                  # a class with no command (e.g. 1): send nothing
            return

        if state["sent"]:                    # already sent for this hold: wait for a new gesture
            return
        if held_for < HOLD_S:                # not held long enough yet
            if now - state["last_progress"] >= 1.0:   # progress line about once a second
                print(f"[bridge] class {value} held {held_for:.1f} / {HOLD_S:.1f} s")
                state["last_progress"] = now
            return

        # Held long enough: send the letter once
        if dry_run:
            print(f"[dry-run] would send '{command}' (class {value}, held {held_for:.1f} s)")
        else:
            ser.write((command + COMMAND_ENDING).encode())   # the character, as bytes
            print(f"[serial] sent '{command}' (class {value}, held {held_for:.1f} s)")
        state["sent"] = True

    return on_outputs


def main():
    args = parse_args()

    ser = None
    stop_event = threading.Event()
    music = MusicPlayer(enabled=not args.no_music)
    if args.dry_run:
        # No Arduino: you type the state lines yourself to test the music
        threading.Thread(target=simulate_arduino, args=(music,), daemon=True).start()
    else:
        ser = open_serial(args.serial_port, args.baud)
        threading.Thread(target=read_replies, args=(ser, stop_event, music), daemon=True).start()

    dispatcher = Dispatcher()
    dispatcher.map(OSC_ADDRESS, make_handler(ser, args.dry_run))
    try:
        server = BlockingOSCUDPServer((OSC_HOST, args.osc_port), dispatcher)
    except OSError as error:
        sys.exit(f"Could not listen on UDP port {args.osc_port}: {error}\n"
                 "  - Is another copy of the bridge already running?")

    print(f"Listening for {OSC_ADDRESS} on {OSC_HOST}:{args.osc_port}"
          f"{' (dry run, no serial)' if args.dry_run else ''}. Stop with Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:   # Ctrl+C or PyCharm's Stop button
        print("\nStopped.")
    finally:
        stop_event.set()
        music.stop()
        if ser is not None:
            ser.close()


if __name__ == "__main__":
    main()
