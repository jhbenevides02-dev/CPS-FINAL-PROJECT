import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#STEP 1 & 2: Set configuration options and create the task instance

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)

#STEP3 Load Input
image = mp.Image.create_from_file("test_hand.jpg")

#STEP4 Perform hand landmarks detection
detection_result = detector.detect(image)

 #STEP5 Process and display the output

for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
    print(f"Hand #{idx+1} Detected:")
    for lm_id, landmark in enumerate(hand_landmarks):
        print(f" Landmark {lm_id}: x={landmark.x:.4f}, y={landmark.y:.4f}, z={landmark.z:.4f}")
for idx, (hand_landmarks, handedness) in enumerate(zip(detection_result.hand_landmarks, detection_result.handedness)):
    category = handedness
    print(f"Hand #{idx + 1}: {category.category_name} (Confidence: {category.score:.2f})")

    for lm_id, landmark in enumerate(hand_landmarks):
        print(f" Landmark {lm_id}: x={landmark.x:.4f}, y={landmark.y:.4f}, z={landmark.z:.4f}")