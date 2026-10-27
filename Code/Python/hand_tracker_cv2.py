import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load MediaPipe drawing utilities and connection definitions
mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles
MARGIN = 10 # pixels offset for text placement

FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # Green color
def draw_landmarks_on_image(rgb_image, detection_result):
    """Draws 21 hand landmarks, connection lines, and handedness labels on the image."""
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through each detected hand
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]

        #Access the first Category object from the list
        category = handedness_list[idx][0]

        # STEP A: Draw hand landmarks and skeletal connection lines
        mp_drawing.draw_landmarks(
            annotated_image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style() )

        # STEP B: Calculate text label placement above the detected hand
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # STEP C: Render handedness label (Left/Right) onto the image
        cv2.putText(
            annotated_image,
            f"{category.category_name}",
            (text_x, text_y),
            cv2.FONT_HERSHEY_DUPLEX,
            FONT_SIZE,
            HANDEDNESS_TEXT_COLOR,
            FONT_THICKNESS,
            cv2.LINE_AA )
    return annotated_image

# =============================================================
# Pipeline Execution
# =============================================================
# STEP 1 & 2: Configure & Create HandLandmarker Instance

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options, num_hands=2,
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)

# STEP 3: Load the input image using MediaPipe
image = mp.Image.create_from_file("test_hand.jpg")
# STEP 4: Perform landmark detection
detection_result = detector.detect(image)

# STEP 5: Render and display annotated results
# Extract raw NumPy RGB pixel data from the MediaPipe Image object
rgb_image = image.numpy_view()
# Annotate image with skeletal connections and handedness labels
annotated_rgb_image = draw_landmarks_on_image(rgb_image, detection_result)

# OpenCV expects BGR pixel ordering for window display and disk writes
annotated_bgr_image = cv2.cvtColor(annotated_rgb_image, cv2.COLOR_RGB2BGR)

# Save the annotated BGR image directly to disk
output_path = "annotated_hand_output.jpg"
cv2.imwrite(output_path, annotated_bgr_image)
print(f"Annotated image saved successfully to {output_path}")

# Optional display window call
cv2.imshow("MediaPipe Hand Landmarks", annotated_bgr_image)
cv2.waitKey(0)
cv2.destroyAllWindows()