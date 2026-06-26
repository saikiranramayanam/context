import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def estimate(self, frame, tracked_objects):
        results = []
        for obj in tracked_objects:
            x1, y1, x2, y2 = map(int, obj['bbox'])
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 - x1 < 10 or y2 - y1 < 10:
                obj['landmarks'] = None
                results.append(obj)
                continue
                
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                obj['landmarks'] = None
                results.append(obj)
                continue
                
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            pose_result = self.pose.process(crop_rgb)
            
            landmarks_abs = []
            if pose_result.pose_landmarks:
                for lm in pose_result.pose_landmarks.landmark:
                    # Absolute coordinate in full frame
                    abs_x = int(lm.x * (x2 - x1)) + x1
                    abs_y = int(lm.y * (y2 - y1)) + y1
                    landmarks_abs.append((abs_x, abs_y, lm.visibility))
                    
            obj['landmarks'] = landmarks_abs if landmarks_abs else None
            results.append(obj)
            
        return results
