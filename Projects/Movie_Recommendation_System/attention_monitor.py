import cv2
import mediapipe as mp
import numpy as np
import time
import os
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def download_model(model_path='face_landmarker.task'):
    """Download the face landmarker model if not present."""
    if not os.path.exists(model_path):
        print(f"Downloading face landmarker model to {model_path}...")
        url = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
        try:
            urllib.request.urlretrieve(url, model_path)
            print("Model downloaded successfully.")
        except Exception as e:
            print(f"Failed to download model: {e}")
            raise

class AttentionMonitor:
    """
    Monitors user attention via webcam using MediaPipe FaceMesh.
    Detects SLEEPING (eyes closed), DISTRACTED (head turned away), ABSENT (no face).
    """

    # --- Tunable parameters ---
    EAR_THRESHOLD = 0.2          # Eye Aspect Ratio threshold for closed eyes
    EAR_CONSECUTIVE_FRAMES = 15  # Number of consecutive frames below threshold to trigger SLEEPING

    HEAD_POSE_THRESHOLD = 0.3    # Normalized head turn threshold (0-1) for distraction
    HEAD_POSE_CONSECUTIVE_FRAMES = 15  # Consecutive frames turned away to trigger DISTRACTED

    ABSENT_TIMEOUT = 5.0         # Seconds of no face to trigger ABSENT

    FRAME_SKIP = 3               # Process every Nth frame for performance

    # MediaPipe FaceMesh landmark indices (same as before)
    LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]
    NOSE_IDX = 1
    LEFT_FACE_IDX = 234   # approximate left cheek
    RIGHT_FACE_IDX = 454  # approximate right cheek

    def __init__(self):
        # Ensure model is downloaded
        download_model()

        # Set up MediaPipe FaceLandmarker
        base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1)
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options)

        # State tracking
        self.ear_below_counter = 0
        self.head_away_counter = 0
        self.last_face_seen_time = time.time()
        self.frame_count = 0
        self.last_status = "OK"
        self.last_ear = 0.0
        self.last_head_pose = 0.0

    def _eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio for given eye landmarks."""
        # Get coordinates
        points = np.array([
            [landmarks[i].x, landmarks[i].y] for i in eye_indices
        ])
        # Compute vertical distances
        vertical1 = np.linalg.norm(points[1] - points[5])
        vertical2 = np.linalg.norm(points[2] - points[4])
        # Compute horizontal distance
        horizontal = np.linalg.norm(points[0] - points[3])
        # Avoid division by zero
        if horizontal == 0:
            return 0.0
        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return ear

    def _head_pose_direction(self, landmarks):
        """
        Estimate head turn direction.
        Returns normalized value: 0 = centered, >0 = turned right, <0 = turned left.
        Uses nose x position relative to face width.
        """
        nose = landmarks[self.NOSE_IDX]
        left = landmarks[self.LEFT_FACE_IDX]
        right = landmarks[self.RIGHT_FACE_IDX]

        face_width = right.x - left.x
        if face_width == 0:
            return 0.0
        # Normalized nose position: 0 at left edge, 1 at right edge
        nose_pos = (nose.x - left.x) / face_width
        # Centered at 0.5, so deviation from center
        deviation = nose_pos - 0.5
        # Return absolute deviation for distraction detection (both sides)
        return abs(deviation)

    def update(self, frame):
        """
        Process a single frame and return attention status.
        Returns one of: "OK", "SLEEPING", "DISTRACTED", "ABSENT"
        """
        self.frame_count += 1

        # Skip frames for performance
        if self.frame_count % self.FRAME_SKIP != 0:
            # Return last known status for skipped frames
            return self.last_status

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect face landmarks
        detection_result = self.face_landmarker.detect(mp_image)

        if not detection_result.face_landmarks:
            # No face detected
            # Reset counters because if face is not visible, we cannot be sleeping or distracted
            self.ear_below_counter = 0
            self.head_away_counter = 0
            # Check if we have been absent for too long
            if time.time() - self.last_face_seen_time > self.ABSENT_TIMEOUT:
                self.last_status = "ABSENT"
            # else: keep last status (which could be OK, but we just reset counters so it's not SLEEPING/DISTRACTED)
            return self.last_status

        # Face detected
        self.last_face_seen_time = time.time()
        landmarks = detection_result.face_landmarks[0]

        # Calculate EAR for both eyes
        left_ear = self._eye_aspect_ratio(landmarks, self.LEFT_EYE_IDX)
        right_ear = self._eye_aspect_ratio(landmarks, self.RIGHT_EYE_IDX)
        ear = (left_ear + right_ear) / 2.0
        self.last_ear = ear

        # Calculate head pose deviation
        head_pose = self._head_pose_direction(landmarks)
        self.last_head_pose = head_pose

        # Check for SLEEPING
        if ear < self.EAR_THRESHOLD:
            self.ear_below_counter += 1
        else:
            self.ear_below_counter = 0

        # Check for DISTRACTED
        if head_pose > self.HEAD_POSE_THRESHOLD:
            self.head_away_counter += 1
        else:
            self.head_away_counter = 0

        # Determine status
        if self.ear_below_counter >= self.EAR_CONSECUTIVE_FRAMES:
            self.last_status = "SLEEPING"
        elif self.head_away_counter >= self.HEAD_POSE_CONSECUTIVE_FRAMES:
            self.last_status = "DISTRACTED"
        else:
            self.last_status = "OK"

        return self.last_status