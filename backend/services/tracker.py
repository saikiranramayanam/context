from deep_sort_realtime.deepsort_tracker import DeepSort

tracker = DeepSort(max_age=30)

def track_people(results, frame):
    detections = []

    for result in results:
        boxes = result.boxes

        for box in boxes:
            class_id = int(box.cls[0])

            # YOLO class 0 = person
            if class_id == 0:
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                confidence = float(box.conf[0])

                detections.append(
                    ([x1, y1, x2 - x1, y2 - y1], confidence, "person")
                )

    tracks = tracker.update_tracks(detections, frame=frame)

    return tracks