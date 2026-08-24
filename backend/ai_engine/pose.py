import cv2
import numpy as np

try:
    import mediapipe as mp
    if hasattr(mp, 'solutions'):
        mp_pose_module = mp.solutions.pose
        mp_drawing_module = mp.solutions.drawing_utils
    else:
        mp_pose_module = None
        mp_drawing_module = None
except Exception:
    mp_pose_module = None
    mp_drawing_module = None

class PoseEstimator:
    def __init__(self):
        if mp_pose_module is not None:
            try:
                self.pose = mp_pose_module.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                )
            except Exception as e:
                print(f"[WARNING] Failed to initialize MediaPipe Pose: {e}")
                self.pose = None
        else:
            self.pose = None
        
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
            landmarks_abs = []
            if self.pose:
                try:
                    pose_result = self.pose.process(crop_rgb)
                    if pose_result and pose_result.pose_landmarks:
                        for lm in pose_result.pose_landmarks.landmark:
                            # Absolute coordinate in full frame
                            abs_x = int(lm.x * (x2 - x1)) + x1
                            abs_y = int(lm.y * (y2 - y1)) + y1
                            landmarks_abs.append((abs_x, abs_y, lm.visibility))
                except Exception as e:
                    print(f"Error processing pose: {e}")
                    
            obj['landmarks'] = landmarks_abs if landmarks_abs else None
            results.append(obj)
            
        return results
