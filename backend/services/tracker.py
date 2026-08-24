from backend.ai_engine.tracker import PersonTracker

_tracker = PersonTracker()

def track_people(results, frame):
    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            if class_id == 0:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], confidence, "person"))
    return _tracker.track(detections, frame)