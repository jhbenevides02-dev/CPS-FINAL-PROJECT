"""
dataset_sender.py: play the images of ONE class into Wekinator, so it can be trained by hand.

dataset/<class>/*.jpg -> MediaPipe -> 63 normalised floats -> OSC /wek/inputs -> Wekinator

Each image is sent as a short burst, then the next image, looping until you stop.
In Wekinator you set the class value and press Start/Stop recording yourself.

Usage (PyCharm: Run > Edit Configurations > Parameters):
    dataset_sender.py --class heart [--dataset dataset] [--burst 0.5] [--rate 30]
"""
import argparse
import itertools
import sys
import time
from pathlib import Path

from pythonosc.udp_client import SimpleUDPClient

# Reuse the exact same detection and normalisation as the single-image sender.
from landmarks_sender import (
    DEFAULT_HOST, DEFAULT_PORT, DEFAULT_RATE, OSC_ADDRESS,
    create_detector, detect_landmarks, normalise,
)

# ---- Settings (change here, not in the code below) ----
DEFAULT_DATASET = Path(__file__).parent / "dataset"   # holds one sub-folder per class
DEFAULT_BURST_S = 0.5                                 # seconds each image is sent for
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def parse_args():
    """Read the command-line arguments (set in the PyCharm run configuration)."""
    parser = argparse.ArgumentParser(description="Play one class of the dataset into Wekinator.")
    # "class" is a Python keyword, so store it as class_name.
    parser.add_argument("--class", dest="class_name", required=True,
                        help="name of the class folder inside the dataset folder, e.g. heart")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="dataset folder")
    parser.add_argument("--burst", type=float, default=DEFAULT_BURST_S, help="seconds per image")
    parser.add_argument("--host", default=DEFAULT_HOST, help="OSC destination IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OSC destination port")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE, help="messages per second")
    return parser.parse_args()


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


def load_messages(detector, images):
    """Detect every image once. Return [(image path, 63 floats)] for the images with a hand."""
    messages = []
    for path in images:
        landmarks = detect_landmarks(detector, path)
        if landmarks is None:
            print(f"  skipped (no hand found): {path.name}")
            continue
        messages.append((path, normalise(landmarks)))
    return messages


def main():
    args = parse_args()

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
    messages = load_messages(create_detector(), images)
    print(f"{len(messages)} of {len(images)} images have a hand and will be sent.")
    if not messages:
        sys.exit("Nothing to send.")

    # 3. Send the images to Wekinator: one image at a time, in a loop, until Stop
    client = SimpleUDPClient(args.host, args.port)   # OSC sender
    interval = 1.0 / args.rate                       # seconds between two messages
    print(f"Sending {OSC_ADDRESS} to {args.host}:{args.port}. Set the class in Wekinator and "
          f"record while this runs. Stop with Ctrl+C.")

    sent = 0
    try:
        for number, (path, values) in itertools.cycle(enumerate(messages, start=1)):
            print(f"image {number}/{len(messages)}: {path.name}")
            burst_end = time.monotonic() + args.burst
            while time.monotonic() < burst_end:     # same image for the whole burst
                client.send_message(OSC_ADDRESS, values)
                sent += 1
                time.sleep(interval)
    except KeyboardInterrupt:   # Ctrl+C or PyCharm's Stop button
        print(f"\nStopped after {sent} messages.")


if __name__ == "__main__":
    main()
