"""
dataset_sender.py: play the images of ONE class into Wekinator, so it can be trained by hand.

dataset/<class>/*.jpg -> MediaPipe -> 63 normalised floats -> OSC /wek/inputs -> Wekinator

Each image is sent for a while (--burst seconds), then the next image, looping until you stop.
A window shows the image that is being sent. Press q or Esc in the window (or Stop) to quit.
In Wekinator you set the class value and press Start/Stop recording yourself.

TEST MODE (--test): random photos from ALL the class folders are sent, the window shows the true
class and what Wekinator answered (Wekinator must be in Run mode, and the bridge must be stopped,
because both listen on port 12000).

Usage (PyCharm: Run > Edit Configurations > Parameters):
    dataset_sender.py --class heart [--dataset dataset] [--burst 10] [--rate 30]     (training)
    dataset_sender.py --test [--classes heart,action] [--dataset dataset]            (testing)
"""
import argparse
import itertools
import random
import sys
import threading
import time
from pathlib import Path

import cv2   # OpenCV: only used to show the image window (installed with mediapipe)
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

# Reuse the exact same detection and normalisation as the single-image sender.
from landmarks_sender import (
    DEFAULT_HOST, DEFAULT_PORT, DEFAULT_RATE, OSC_ADDRESS, NUM_VALUES,
    create_detector, detect_landmarks, normalise, draw_landmarks,
)

# ---- Settings (change here, not in the code below) ----
DEFAULT_DATASET = Path(__file__).parent / "dataset"   # holds one sub-folder per class
DEFAULT_BURST_S = 5.0                                # seconds each image is sent for
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
NONE_CLASS = "none"                                   # "no gesture": photos without a hand are kept as 63 zeros
WINDOW_NAME = "Image sent to Wekinator"
WINDOW_MAX_HEIGHT = 600                               # big photos are shrunk to fit the screen
QUIT_KEYS = (ord("q"), 27)                            # q or Esc
# Test mode
DEFAULT_CLASSES = "heart,action"      # class number in Wekinator = position in this list (1, 2, ...)
DEFAULT_LISTEN_PORT = 12000           # Wekinator's output port
REPLY_ADDRESS = "/wek/outputs"        # Wekinator's output message
GREEN = (0, 200, 0)                   # colours are (blue, green, red)
RED = (0, 0, 255)


def parse_args():
    """Read the command-line arguments (set in the PyCharm run configuration)."""
    parser = argparse.ArgumentParser(description="Play one class of the dataset into Wekinator.")
    # "class" is a Python keyword, so store it as class_name.
    parser.add_argument("--class", dest="class_name",
                        help="training: name of the class folder inside the dataset folder, e.g. heart")
    parser.add_argument("--test", action="store_true",
                        help="test mode: random photos from all the classes, shows Wekinator's answer")
    parser.add_argument("--classes", default=DEFAULT_CLASSES,
                        help="test mode: class folder names in Wekinator's class order (1, 2, ...)")
    parser.add_argument("--listen-port", type=int, default=DEFAULT_LISTEN_PORT,
                        help="test mode: port where Wekinator's answer arrives")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="dataset folder")
    parser.add_argument("--burst", type=float, default=DEFAULT_BURST_S, help="seconds per image")
    parser.add_argument("--host", default=DEFAULT_HOST, help="OSC destination IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OSC destination port")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE, help="messages per second")
    args = parser.parse_args()
    if not args.test and not args.class_name:
        parser.error("use --class <name> to train, or --test to test")
    return args


def find_images(class_folder):
    """Return a sorted list of the image files (Paths) in class_folder."""
    images = []                                   # empty list, we fill it below
    for path in class_folder.iterdir():           # look at every item in the folder
        if not path.is_file():                    # skip sub-folders
            continue
        extension = path.suffix.lower()           # e.g. ".JPG" -> ".jpg"
        if extension in IMAGE_EXTENSIONS:         # keep only .jpg, .jpeg, .png
            images.append(path)
    return sorted(images)                         # sorted: same order every run


def load_picture(path):
    """Load an image for the window, shrunk so it fits on the screen."""
    picture = cv2.imread(str(path))
    height = picture.shape[0]
    if height > WINDOW_MAX_HEIGHT:
        scale = WINDOW_MAX_HEIGHT / height
        picture = cv2.resize(picture, None, fx=scale, fy=scale)
    return picture


def load_messages(detector, images, draw=False, keep_empty=False):
    """Detect every image once. Return [(path, 63 floats, picture)] for the images with a hand.
    With draw=True the landmarks are drawn on the picture.
    With keep_empty=True an image without a hand is kept and sent as 63 zeros (as the live sender
    does), instead of being skipped. Used for the 'none' class."""
    messages = []
    for path in images:
        landmarks = detect_landmarks(detector, path)
        picture = load_picture(path)
        if landmarks is None:
            if not keep_empty:
                print(f"  skipped (no hand found): {path.name}")
                continue
            print(f"  no hand found, sent as 63 zeros: {path.name}")
            messages.append((path, [0.0] * NUM_VALUES, picture))
            continue
        if draw:
            draw_landmarks(picture, landmarks)
        messages.append((path, normalise(landmarks), picture))
    return messages


def start_listener(port, prediction):
    """Listen for Wekinator's answer in a background thread. Keeps the last class in prediction."""
    def on_output(address, *values):
        if values:
            prediction["value"] = int(round(values[0]))   # Wekinator sends 1.0, 2.0, ...

    dispatcher = Dispatcher()
    dispatcher.map(REPLY_ADDRESS, on_output)
    try:
        server = ThreadingOSCUDPServer(("127.0.0.1", port), dispatcher)
    except OSError as error:
        print(f"Could not listen on port {port}: {error}\n"
              "  The window will NOT show Wekinator's answer. Is the bridge running? Stop it.")
        return
    threading.Thread(target=server.serve_forever, daemon=True).start()


def run_test(args):
    """Test mode: send random photos from all classes and compare Wekinator's answer."""
    class_names = [name.strip() for name in args.classes.split(",")]

    # 1. Load the photos of every class (detect once, keep in memory)
    detector = create_detector()
    samples = []                                    # (true class, path, 63 values, picture)
    for class_name in class_names:
        folder = args.dataset / class_name
        if not folder.is_dir():   # e.g. class 'none' may have no photos: its name is still used for the answer
            print(f"No folder for class '{class_name}' ({folder}): no photos of it will be sent.")
            continue
        print(f"Detecting hands in class '{class_name}'...")
        keep_empty = class_name == NONE_CLASS
        for path, values, picture in load_messages(detector, find_images(folder), draw=True,
                                                   keep_empty=keep_empty):
            samples.append((class_name, path, values, picture))
    if not samples:
        sys.exit("Nothing to send.")
    print(f"{len(samples)} photos loaded.")

    # 2. Listen to Wekinator's answer and prepare the sender
    prediction = {"value": None}                    # filled by the background thread
    start_listener(args.listen_port, prediction)
    client = SimpleUDPClient(args.host, args.port)
    interval = 1.0 / args.rate
    print(f"Test mode: random photos, {args.burst} s each. Wekinator must be in Run mode. "
          "Press q or Esc in the window (or Stop) to quit.")

    # 3. Pick a random photo, send it for --burst seconds, show truth vs Wekinator's answer
    correct = 0
    total = 0
    try:
        while True:
            true_class, path, values, picture = random.choice(samples)
            prediction["value"] = None              # forget the answer to the previous photo
            quit_requested = False
            burst_end = time.monotonic() + args.burst
            while time.monotonic() < burst_end:
                client.send_message(OSC_ADDRESS, values)

                # Turn Wekinator's number into a class name (1 -> first name in --classes)
                answer = prediction["value"]
                if answer is None:
                    answer_text, colour = "waiting for Wekinator...", RED
                elif 1 <= answer <= len(class_names):
                    answer_text = class_names[answer - 1]
                    colour = GREEN if answer_text == true_class else RED
                else:
                    answer_text, colour = f"class {answer} (unknown)", RED

                shown = picture.copy()
                cv2.putText(shown, f"true: {true_class}  ({path.name})", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(shown, f"Wekinator: {answer_text}", (10, 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
                cv2.imshow(WINDOW_NAME, shown)
                key = cv2.waitKey(max(1, int(interval * 1000)))   # also the pause between messages
                if key in QUIT_KEYS:
                    quit_requested = True
                    break
            if quit_requested:
                break

            # End of this photo: count it and print a result line
            final = prediction["value"]
            final_name = class_names[final - 1] if final and 1 <= final <= len(class_names) else None
            total += 1
            correct += final_name == true_class
            print(f"{path.name}: true {true_class}, Wekinator {final_name}  "
                  f"{'OK' if final_name == true_class else 'WRONG'}   ({correct}/{total} correct)")
    except KeyboardInterrupt:   # Ctrl+C or PyCharm's Stop button
        pass
    finally:
        cv2.destroyAllWindows()
        print(f"\nResult: {correct} of {total} photos correct.")


def main():
    args = parse_args()
    if args.test:
        run_test(args)
        return

    # 1. Find the folder of the chosen class, e.g. dataset/heart
    class_folder = args.dataset / args.class_name
    if not class_folder.is_dir():
        found = [p.name for p in args.dataset.iterdir() if p.is_dir()] if args.dataset.is_dir() else []
        sys.exit(f"Class folder not found: {class_folder}\n  Folders in the dataset: {found}")

    images = find_images(class_folder)
    if not images:
        sys.exit(f"No images ({', '.join(sorted(IMAGE_EXTENSIONS))}) in {class_folder}")

    # 2. Detect the hand in every image ONCE (slow), keep the 63 values in memory
    print(f"Detecting hands in {len(images)} images of class '{args.class_name}'...")
    messages = load_messages(create_detector(), images, keep_empty=args.class_name == NONE_CLASS)
    print(f"{len(messages)} of {len(images)} images have a hand and will be sent.")
    if not messages:
        sys.exit("Nothing to send.")

    # 3. Send the images to Wekinator: one image at a time, in a loop, until Stop
    client = SimpleUDPClient(args.host, args.port)   # OSC sender
    interval = 1.0 / args.rate                       # seconds between two messages
    print(f"Sending {OSC_ADDRESS} to {args.host}:{args.port}. Set the class in Wekinator and "
          f"record while this runs. Stop with Ctrl+C.")

    sent = 0
    quit_requested = False
    try:
        for number, (path, values, picture) in itertools.cycle(enumerate(messages, start=1)):
            print(f"image {number}/{len(messages)}: {path.name}")

            # Write the class and image name on a copy of the picture, so you see what is sent
            shown = picture.copy()
            label = f"{args.class_name}  {number}/{len(messages)}  {path.name}"
            cv2.putText(shown, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            burst_end = time.monotonic() + args.burst
            while time.monotonic() < burst_end:     # same image for the whole burst
                client.send_message(OSC_ADDRESS, values)      # send the 63 values
                sent += 1
                cv2.imshow(WINDOW_NAME, shown)                # show the image in the window
                # waitKey keeps the window alive AND is our pause between messages (in ms)
                key = cv2.waitKey(max(1, int(interval * 1000)))
                if key in QUIT_KEYS:
                    quit_requested = True
                    break
            if quit_requested:
                break
        print(f"\nStopped after {sent} messages.")
    except KeyboardInterrupt:   # Ctrl+C or PyCharm's Stop button
        print(f"\nStopped after {sent} messages.")
    finally:
        cv2.destroyAllWindows()   # close the image window


if __name__ == "__main__":
    main()
