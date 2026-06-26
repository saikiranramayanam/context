import cv2
import base64
import os
from datetime import datetime
from backend.services.detector import detect_people
from backend.services.tracker import track_people
from backend.services.pose import detect_pose, draw_pose
from backend.services.risk_analyzer import calculate_risk

camera = cv2.VideoCapture(0)

def get_frame_data():
    success, frame = camera.read()

    if not success:
        return None

    # YOLO Detection
    results = detect_people(frame)

    # Tracking
    tracks = track_people(results, frame)

    # Risk Analysis
    risk_score, alerts = calculate_risk(tracks)

    # Pose Estimation
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    pose_results = detect_pose(rgb_frame)

    frame = draw_pose(frame, pose_results)

    # Draw Tracking
    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id

        ltrb = track.to_ltrb()

        x1, y1, x2, y2 = map(int, ltrb)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"ID: {track_id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
    # Save suspicious events
        if risk_score >= 50:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            filename = f"data/events/event_{timestamp}.jpg"

            cv2.imwrite(filename, frame)
    # Risk Score
    cv2.putText(
        frame,
        f"Risk Score: {risk_score}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )

    _, buffer = cv2.imencode(".jpg", frame)

    frame_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "frame": frame_base64,
        "risk_score": risk_score,
        "alerts": alerts
    }