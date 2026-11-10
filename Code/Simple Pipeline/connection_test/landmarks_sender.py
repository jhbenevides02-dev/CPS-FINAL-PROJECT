"""
landmarks_sender.py: Part 1 of the CPS connection test.

Image or webcam -> MediaPipe hand landmarks -> 63 normalised floats -> OSC /wek/inputs -> Wekinator

Usage (PyCharm: Run > Edit Configurations > Parameters):
    landmarks_sender.py path/to/image.jpg [--host 127.0.0.1] [--port 6448] [--rate 30]
    landmarks_sender.py --webcam [--camera 0] [--mirror] [--rate 15]
In webcam mode a window shows the camera with the landmarks drawn. Press q or Esc (or Stop) to quit.
"""
import argparse
import math
import sys
import time
from pathlib import Path

import cv2   # OpenCV: camera and preview window (installed with mediapipe)
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pythonosc.udp_client import SimpleUDPClient

# ---- Settings (change here, not in the code below) ----
DEFAULT_HOST = "127.0.0.1"   # this computer; Wekinator runs here too
DEFAULT_PORT = 6448          # Wekinator's default input port
DEFAULT_RATE = 30            # messages per second (image mode)
DEFAULT_WEBCAM_RATE = 15     # messages per second (webcam mode): one detection + message per 1/15 s
OSC_ADDRESS = "/wek/inputs"  # Wekinator's default input message
WEBCAM_WINDOW_NAME = "Webcam: landmarks sent to Wekinator"
QUIT_KEYS = (ord("q"), 27)   # q or Esc
BONE_COLOUR = (255, 255, 0)  # lines between landmarks (cyan), colours are (blue, green, red)
JOINT_COLOUR = (0, 0, 255)   # landmark dots (red)
# The hand skeleton: pairs of landmark numbers joined by a line (0 = wrist, 4/8/12/16/20 = fingertips)
HAND_BONES = [
    (0, 1), (1, 2), (2, 3), (3, 4),            # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),            # index finger
    (5, 9), (9, 10), (10, 11), (11, 12),       # middle finger
    (9, 13), (13, 14), (14, 15), (15, 16),     # ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),    # little finger
    (0, 17),                                   # edge of the palm
]
NUM_LANDMARKS = 21           # MediaPipe hand model
NUM_VALUES = NUM_LANDMARKS * 3   # x, y, z each -> 63
WRIST = 0                    # landmark used as the origin
MIDDLE_MPB = 9               # landmark used as the "hand size" ruler, base of middle finger to wrist
# The model file sits next to this script, whatever the working directory is.
MODEL_PATH = Path(__file__).parent / "hand_landmarker.task"


def parse_args():
    """Read the command-line arguments (set in the PyCharm run configuration)."""
    parser = argparse.ArgumentParser(description="Send hand landmarks from an image or webcam to Wekinator.")
    parser.add_argument("image", nargs="?", help="path to the image file (not needed with --webcam)")
    parser.add_argument("--webcam", action="store_true", help="use the webcam instead of an image")
    parser.add_argument("--camera", type=int, default=0, help="webcam number (0 = first camera)")
    parser.add_argument("--mirror", action="store_true", help="webcam: flip the picture left-right")
    parser.add_argument("--host", default=DEFAULT_HOST, help="OSC destination IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OSC destination port")
    parser.add_argument("--rate", type=float, default=None,
                        help=f"messages per second (default {DEFAULT_RATE}, webcam {DEFAULT_WEBCAM_RATE})")
    parser.add_argument("--print-values", action="store_true", help="print the 63 values once, then keep sending")
    args = parser.parse_args()
    if args.webcam == (args.image is not None):   # need exactly one of: an image, --webcam
        parser.error("give an image path, or use --webcam (not both)")
    if args.rate is None:
        args.rate = DEFAULT_WEBCAM_RATE if args.webcam else DEFAULT_RATE
    return args


def create_detector(video=False):
    """Build the MediaPipe HandLandmarker (one hand). IMAGE mode = one still picture,
    VIDEO mode = a stream of camera frames."""
    base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        running_mode=vision.RunningMode.VIDEO if video else vision.RunningMode.IMAGE,
    )
    return vision.HandLandmarker.create_from_options(options)


def landmarks_from_result(result):
    """Return a list of 21 (x, y, z) tuples for the first hand, or None if no hand is found."""
    if not result.hand_landmarks:       # empty list = no hand detected
        return None
    hand = result.hand_landmarks[0]     # first (and only) hand
    return [(lm.x, lm.y, lm.z) for lm in hand]


def detect_landmarks(detector, image_path):
    """Image mode: detect the hand in an image file."""
    image = mp.Image.create_from_file(str(image_path))
    return landmarks_from_result(detector.detect(image))


def detect_frame(detector, frame, timestamp_ms):
    """Webcam mode: detect the hand in one camera frame (timestamp_ms must keep increasing)."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)     # OpenCV frames are BGR, MediaPipe wants RGB
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    return landmarks_from_result(detector.detect_for_video(image, timestamp_ms))


def draw_landmarks(picture, landmarks):
    """Draw the 21 landmarks and the bones between them on the picture (in place)."""
    height, width = picture.shape[:2]
    # Landmark x, y are 0..1 fractions of the image: multiply by the size to get pixels
    points = [(int(x * width), int(y * height)) for x, y, z in landmarks]
    for start, end in HAND_BONES:
        cv2.line(picture, points[start], points[end], BONE_COLOUR, 2)   # bones
    for point in points:
        cv2.circle(picture, point, 5, JOINT_COLOUR, -1)                 # joints (filled circles)


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


def run_webcam(args, detector):
    """Webcam mode: detect the hand in the live camera and send 63 values --rate times a second."""
    capture = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)   # CAP_DSHOW is more reliable on Windows
    if not capture.isOpened():
        sys.exit(f"Could not open camera {args.camera}. Is another program (Zoom, Teams...) using it? "
                 "Try --camera 1.")

    client = SimpleUDPClient(args.host, args.port)
    interval = 1.0 / args.rate                       # 15 Hz -> one detection + message every 66 ms
    print(f"Webcam {args.camera}: sending {OSC_ADDRESS} to {args.host}:{args.port} at {args.rate} Hz. "
          "Press q or Esc in the window (or Stop) to quit.")

    sent = 0
    last_send = 0.0
    last_status = 0.0
    landmarks = None                                 # result of the last detection
    try:
        while True:
            ok, frame = capture.read()               # always read, so the camera never lags behind
            if not ok:
                print("The camera stopped giving pictures.")
                break
            if args.mirror:
                frame = cv2.flip(frame, 1)

            now = time.monotonic()
            if now - last_send >= interval:          # time for the next detection + message
                last_send = now
                landmarks = detect_frame(detector, frame, int(now * 1000))
                client.send_message(OSC_ADDRESS, build_message(landmarks))   # 63 zeros if no hand
                sent += 1
                if time.time() - last_status >= 1.0:  # status line about once a second
                    print(f"hand found: {'yes' if landmarks is not None else 'no'} | messages sent: {sent}")
                    last_status = time.time()

            if landmarks is not None:
                draw_landmarks(frame, landmarks)
            cv2.imshow(WEBCAM_WINDOW_NAME, frame)
            if cv2.waitKey(1) in QUIT_KEYS:          # also keeps the window alive
                break
    except KeyboardInterrupt:   # Ctrl+C or PyCharm's Stop button
        pass
    finally:
        capture.release()
        cv2.destroyAllWindows()
        print(f"\nStopped after {sent} messages.")


def main():
    args = parse_args()
    detector = create_detector(video=args.webcam)
    if args.webcam:
        run_webcam(args, detector)
        return

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
