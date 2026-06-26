from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_people(frame):
    results = model(frame)

    return results