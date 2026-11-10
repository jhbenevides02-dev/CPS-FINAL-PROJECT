"""
landmarks_sender.py: Part 1 of the CPS connection test.

Image -> MediaPipe hand landmarks -> 63 normalised floats -> OSC /wek/inputs -> Wekinator

Usage (PyCharm: Run > Edit Configurations > Parameters):
    landmarks_sender.py path/to/image.jpg [--host 127.0.0.1] [--port 6448] [--rate 30]
"""
import argparse
import math
import time
from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pythonosc.udp_client import SimpleUDPClient

# ---- Settings (change here, not in the code below) ----
DEFAULT_HOST = "127.0.0.1"   # this computer; Wekinator runs here too
DEFAULT_PORT = 6448          # Wekinator's default input port
DEFAULT_RATE = 30            # messages per second
OSC_ADDRESS = "/wek/inputs"  # Wekinator's default input message
NUM_LANDMARKS = 21           # MediaPipe hand model
NUM_VALUES = NUM_LANDMARKS * 3   # x, y, z each -> 63
WRIST = 0                    # landmark used as the origin
MIDDLE_MPB = 9               # landmark used as the "hand size" ruler, base of middle finger to wrist
# The model file sits next to this script, whatever the working directory is.
MODEL_PATH = Path(__file__).parent / "hand_landmarker.task"


def parse_args():
    """Read the command-line arguments (set in the PyCharm run configuration)."""
    parser = argparse.ArgumentParser(description="Send hand landmarks from an image to Wekinator.")
    parser.add_argument("image", help="path to the image file")
    parser.add_argument("--host", default=DEFAULT_HOST, help="OSC destination IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OSC destination port")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE, help="messages per second")
    parser.add_argument("--print-values", action="store_true", help="print the 63 values once, then keep sending")
    return parser.parse_args()


def create_detector():
    """Build the MediaPipe HandLandmarker (IMAGE mode = one still picture, one hand)."""
    base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        running_mode=vision.RunningMode.IMAGE,
    )
    return vision.HandLandmarker.create_from_options(options)


def detect_landmarks(detector, image_path):
    """Return a list of 21 (x, y, z) tuples for the first hand, or None if no hand is found."""
    image = mp.Image.create_from_file(str(image_path))
    result = detector.detect(image)
    if not result.hand_landmarks:       # empty list = no hand detected
        return None
    hand = result.hand_landmarks[0]     # first (and only) hand
    return [(lm.x, lm.y, lm.z) for lm in hand]


def normalise(landmarks):
    """Return 63 floats,one per landmark."""
    """Wrist as the origin,and each landmark normalised to ruler"""

    landmarksWeki = []
    wrist_x, wrist_y, wrist_z = landmarks[WRIST]  # Unpack Wrist
    palmBase_x, palmBase_y, palmBase_z = landmarks[MIDDLE_MPB] # Unpack Middle finger base

    #Substracting MPB to wrist

    palmBase_x = palmBase_x-wrist_x
    palmBase_y = palmBase_y-wrist_y
    palmBase_z = palmBase_z-wrist_z

    ruler_MPB = math.sqrt(palmBase_x**2 + palmBase_y**2 + palmBase_z**2) # rule calculation

    if ruler_MPB == 0:
        ruler_MPB = 1.0

    for i in range(len(landmarks)):
        lm_x, lm_y, lm_z = landmarks[i]  # extracting coordinates for each landmark
        lm_x = (lm_x-wrist_x)/ruler_MPB
        lm_y = (lm_y-wrist_y)/ruler_MPB
        lm_z = (lm_z-wrist_z)/ruler_MPB
        landmarksWeki.append(lm_x)
        landmarksWeki.append(lm_y)
        landmarksWeki.append(lm_z)

    return landmarksWeki

def build_message(landmarks):
    """Return exactly 63 floats: the normalised hand, or 63 zeros if no hand was found."""
    if landmarks is None:
        return [0.0] * NUM_VALUES
    return normalise(landmarks)


def main():
    args = parse_args()
    detector = create_detector()

    # The image never changes, so detect once and re-send the same message.
    landmarks = detect_landmarks(detector, args.image)
    hand_found = landmarks is not None
    values = build_message(landmarks)
    if args.print_values:
        print(f"{len(values)} values:")
        print(values)

    client = SimpleUDPClient(args.host, args.port)   # UDP: no connection, no reply
    interval = 1.0 / args.rate                       # seconds between messages
    print(f"Sending {OSC_ADDRESS} to {args.host}:{args.port} at {args.rate} Hz. Stop with Ctrl+C.")

    sent = 0
    last_status = 0.0
    try:
        while True:
            client.send_message(OSC_ADDRESS, values)
            sent += 1
            # Status line about once a second (not every message, to keep the console readable).
            if time.time() - last_status >= 1.0:
                print(f"hand found: {'yes' if hand_found else 'no'} | messages sent: {sent}")
                last_status = time.time()
            time.sleep(interval)
    except KeyboardInterrupt:   # Ctrl+C or PyCharm's Stop button
        print(f"\nStopped after {sent} messages.")


if __name__ == "__main__":
    main()
