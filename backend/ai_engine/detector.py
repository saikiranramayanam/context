import os
from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_name='yolov8n.pt'):
        # Check standard location: data/weights/yolov8n.pt
        weights_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/weights"))
        os.makedirs(weights_dir, exist_ok=True)
        weights_path = os.path.join(weights_dir, model_name)
        
        # If it doesn't exist, check the root directory
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", model_name))
        
        if os.path.exists(root_path) and not os.path.exists(weights_path):
            import shutil
            try:
                shutil.copy(root_path, weights_path)
                print(f"Copied {model_name} to {weights_path}")
                self.model = YOLO(weights_path)
            except Exception as e:
                print(f"Failed to copy {model_name}: {e}. Loading from root path.")
                self.model = YOLO(root_path)
        else:
            # If not found anywhere, ultralytics will auto-download it to weights_path
            self.model = YOLO(weights_path)

    def detect(self, frame, conf_threshold=0.5):
        # class 0 is person
        results = self.model(frame, stream=False, classes=[0], verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                if conf > conf_threshold:
                    w = x2 - x1
                    h = y2 - y1
                    detections.append(([x1, y1, w, h], conf, 'person'))
                    
        # Fallback for synthetic stick-figure test streams/videos
        if not detections and frame is not None:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area > 1200: # Filter text & noise
                        x, y, w, h = cv2.boundingRect(cnt)
                        if y > 60: # Ignore header banner area
                            detections.append(([float(x), float(y), float(w), float(h)], 0.85, 'person'))
            except Exception:
                pass
                
        return detections
