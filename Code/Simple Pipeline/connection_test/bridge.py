"""
bridge.py: Part 3 of the CPS connection test.

Wekinator -> OSC /wek/outputs (port 12000) -> this script -> USB serial -> Arduino

Usage (PyCharm: Run > Edit Configurations > Parameters):
    bridge.py --serial-port COM5 [--osc-port 12000] [--baud 115200]
    bridge.py --dry-run          (no Arduino: just print what would be sent)
"""
import argparse
import sys
import threading
import time

import serial   # this is the "pyserial" package (never install the package called "serial")
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher


# ---- Settings (change here, not in the code below) ----
OSC_HOST = "127.0.0.1"        # listen on this computer only
DEFAULT_OSC_PORT = 12000      # Wekinator's default output port
OSC_ADDRESS = "/wek/outputs"  # Wekinator's default output message
DEFAULT_BAUD = 115200         # must match Serial.begin() in the Arduino sketch
ARDUINO_DEFAULT_PORT = "COM7" # Default COM port used in Arduino Nano Every test board.
RESET_WAIT_S = 2.0            # the Arduino resets when the port opens; give it time to boot
KEEPALIVE_S = 0.25            # re-send the same value at most this often


def parse_args():
    """Read the command-line arguments (set in the PyCharm run configuration)."""
    parser = argparse.ArgumentParser(description="Bridge Wekinator OSC output to an Arduino over serial.")
    parser.add_argument("--osc-port", type=int, default=DEFAULT_OSC_PORT, help="port to listen on for Wekinator")
    parser.add_argument("--serial-port", default=ARDUINO_DEFAULT_PORT, help="Arduino COM port, e.g. COM5 (required unless --dry-run)")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD, help="serial baud rate")
    parser.add_argument("--dry-run", action="store_true", help="no serial port: only print")
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


def read_replies(ser, stop_event):
    """Background thread: print every line the Arduino sends back (e.g. 'ACK 1')."""
    while not stop_event.is_set():
        try:
            line = ser.readline().decode(errors="ignore").strip()
        except serial.SerialException:   # port closed or unplugged
            break
        if line:
            print(f"[arduino] {line}")


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
    """Return the function python-osc calls for every /wek/outputs message."""
    state = {"last_value": None, "last_sent": 0.0}   # remembered between messages

    def on_outputs(address, *values):
        if not values:
            return
        value = int(round(values[0]))        # Wekinator sends the class as a float, e.g. 1.0
        print(f"[osc] {address} {values}")
        now = time.monotonic()
        if should_send(value, state["last_value"], state["last_sent"], now):
            if dry_run:
                print(f"[dry-run] would send '{value}'")
            else:
                ser.write(f"{value}\n".encode())   # one line of text, ended by a newline
                print(f"[serial] sent '{value}'")
            state["last_value"] = value
            state["last_sent"] = now

    return on_outputs


def main():
    args = parse_args()

    ser = None
    stop_event = threading.Event()
    if not args.dry_run:
        ser = open_serial(args.serial_port, args.baud)
        threading.Thread(target=read_replies, args=(ser, stop_event), daemon=True).start()

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
        if ser is not None:
            ser.close()


if __name__ == "__main__":
    main()
