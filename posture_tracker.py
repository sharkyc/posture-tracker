import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
from PyQt5.QtCore import QThread, pyqtSignal
import os
import time

class PostureTracker(QThread):
    # Signals to communicate with the UI
    posture_status_signal = pyqtSignal(float, float)  # current_score, baseline_score
    error_signal = pyqtSignal(str)
    frame_signal = pyqtSignal(object)  # Add signal to emit the video frame
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = True
        self.baseline = None
        
        # Initialize MediaPipe Pose using Tasks API
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pose_landmarker_lite.task'))
        print(f"Loading model from: {model_path}")
        
        # Load model data into memory first to avoid Windows path issues in MediaPipe C++ backend
        with open(model_path, 'rb') as f:
            model_data = f.read()
            
        base_options = python.BaseOptions(model_asset_buffer=model_data)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        
    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.error_signal.emit("无法打开摄像头")
            return
            
        start_time = time.time()
        
        while self.running:
            success, image = cap.read()
            if not success:
                continue
                
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            
            # Timestamp in milliseconds
            frame_timestamp_ms = int((time.time() - start_time) * 1000)
            if frame_timestamp_ms < 0:
                frame_timestamp_ms = 0
                
            try:
                detection_result = self.detector.detect_for_video(mp_image, frame_timestamp_ms)
                
                # Copy image for drawing
                annotated_image = np.copy(image_rgb)
                
                if detection_result.pose_landmarks and len(detection_result.pose_landmarks) > 0:
                    landmarks = detection_result.pose_landmarks[0]
                    
                    # Draw landmarks manually since protobuf might be missing
                    # Draw points
                    for landmark in landmarks:
                        x = int(landmark.x * annotated_image.shape[1])
                        y = int(landmark.y * annotated_image.shape[0])
                        cv2.circle(annotated_image, (x, y), 5, (0, 255, 0), -1)
                        
                    # MediaPipe Pose landmarks: 0=nose, 11=left_shoulder, 12=right_shoulder
                    nose = landmarks[0]
                    left_shoulder = landmarks[11]
                    right_shoulder = landmarks[12]
                    
                    # Calculate metric
                    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2.0
                    
                    vertical_dist = shoulder_mid_y - nose.y
                    shoulder_width = math.sqrt(
                        (left_shoulder.x - right_shoulder.x)**2 + 
                        (left_shoulder.y - right_shoulder.y)**2
                    )
                    
                    if shoulder_width > 0.01:  # Avoid division by zero
                        current_score = vertical_dist / shoulder_width
                        
                        if self.baseline is not None:
                            self.posture_status_signal.emit(current_score, self.baseline)
                        else:
                            # If not calibrated, send 0 for baseline
                            self.posture_status_signal.emit(current_score, 0.0)
                
                # Emit the annotated frame
                self.frame_signal.emit(annotated_image)
            except Exception as e:
                print(f"Detection error: {e}")
                        
            # Small delay
            self.msleep(50)
            
        cap.release()
        self.detector.close()
        
    def calibrate(self, current_score):
        """Set the current score as the baseline (good posture)"""
        self.baseline = current_score
        
    def reset_baseline(self):
        """Reset baseline to None"""
        self.baseline = None
        
    def set_baseline(self, score):
        """Manually set baseline score"""
        self.baseline = score
        
    def stop(self):
        self.running = False
        self.wait()
