"""MediaPipe Tasks adapter. A locally supplied hand_landmarker.task is required."""
from pathlib import Path
import time

class HandTracker:
    def __init__(self, model):
        if not Path(model).is_file(): raise FileNotFoundError('Supply a local hand_landmarker.task with --model')
        import mediapipe as mp
        self.mp=mp; self.last=-1
        options=mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,num_hands=1,
            min_hand_detection_confidence=0.7,min_tracking_confidence=0.7)
        self.detector=mp.tasks.vision.HandLandmarker.create_from_options(options)
    def detect(self, bgr):
        import cv2
        timestamp=max(self.last+1,time.monotonic_ns()//1_000_000); self.last=timestamp
        image=self.mp.Image(image_format=self.mp.ImageFormat.SRGB,data=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
        result=self.detector.detect_for_video(image,timestamp)
        if not result.hand_landmarks: return []
        h,w=bgr.shape[:2]
        return [(min(w-1,max(0,int(p.x*w))),min(h-1,max(0,int(p.y*h)))) for p in result.hand_landmarks[0]]
    def close(self): self.detector.close()
