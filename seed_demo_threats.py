import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from backend.database.db import SessionLocal, engine, Base
from backend.database.models import Camera, Event, Alert

# Ensure data folders exist
events_dir = os.path.abspath("data/events")
os.makedirs(events_dir, exist_ok=True)
os.makedirs(os.path.abspath("data/weights"), exist_ok=True)

# Build database tables if not created
Base.metadata.create_all(bind=engine)

def create_synthetic_snapshot(filename, title, threat_score, desc, color_rgb):
    """Generate a realistic HUD-annotated snapshot frame for incident inspection."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Draw background grid
    for x in range(0, 640, 40):
        cv2.line(img, (x, 0), (x, 480), (30, 30, 30), 1)
    for y in range(0, 480, 40):
        cv2.line(img, (0, y), (640, y), (30, 30, 30), 1)
        
    # Draw camera header
    cv2.rectangle(img, (0, 0), (640, 45), (15, 15, 20), -1)
    cv2.putText(img, f"FEED: {title.upper()}", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, "REC [AI GUARD ACTIVE]", (430, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Draw Threat Index Badge
    cv2.rectangle(img, (460, 60), (620, 110), (10, 10, 15), -1)
    cv2.rectangle(img, (460, 60), (620, 110), color_rgb, 2)
    cv2.putText(img, "THREAT INDEX", (470, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
    cv2.putText(img, f"{threat_score:.1f}%", (470, 104), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_rgb, 2)
    
    # Draw stick figure / bounding box based on threat type
    if "FALL" in title.upper():
        # Horizontal fallen posture
        cv2.rectangle(img, (140, 280), (480, 400), color_rgb, 2)
        cv2.putText(img, "ID: 1 [FALLEN POSTURE]", (140, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_rgb, 2)
        cv2.circle(img, (170, 340), 20, (255, 220, 180), -1) # Head
        cv2.line(img, (190, 340), (380, 340), (255, 255, 0), 4) # Body
        cv2.line(img, (380, 340), (460, 370), (255, 255, 0), 4) # Legs
    elif "VIOLENCE" in title.upper():
        # Aggressive interaction between two figures
        cv2.rectangle(img, (180, 150), (320, 420), color_rgb, 2)
        cv2.putText(img, "ID: 1 [AGGRESSOR]", (180, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_rgb, 2)
        cv2.rectangle(img, (330, 150), (470, 420), color_rgb, 2)
        cv2.putText(img, "ID: 2 [TARGET]", (330, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_rgb, 2)
        # High velocity striking pose
        cv2.line(img, (250, 200), (360, 210), (0, 0, 255), 4)
    elif "PROXIMITY" in title.upper():
        # Two people standing too close
        cv2.rectangle(img, (220, 120), (340, 420), (0, 255, 255), 2)
        cv2.putText(img, "ID: 1 & ID: 2 [PROXIMITY RISK]", (180, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.line(img, (250, 250), (310, 250), (0, 0, 255), 2)
        cv2.putText(img, "45px THREAT DISTANCE", (210, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
    else: # Hot zone intrusion
        # Zone box
        cv2.rectangle(img, (200, 100), (600, 440), (255, 229, 0), 2)
        cv2.putText(img, "RESTRICTED ACTIVE MONITOR ZONE", (210, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 229, 0), 2)
        # Intruder inside zone
        cv2.rectangle(img, (280, 140), (420, 410), color_rgb, 2)
        cv2.putText(img, "ID: 3 [ZONE INTRUDER]", (280, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_rgb, 2)
        cv2.circle(img, (350, 180), 22, (255, 220, 180), -1)

    # Footer banner
    cv2.rectangle(img, (10, 435), (630, 470), (10, 10, 15), -1)
    cv2.putText(img, f"ALERT: {desc}", (20, 458), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    filepath = os.path.join(events_dir, filename)
    cv2.imwrite(filepath, img)
    return filepath

def seed_threats():
    db = SessionLocal()
    try:
        # Get or create camera
        cam = db.query(Camera).first()
        if not cam:
            cam = Camera(
                name="Factory Floor Cam 01",
                source="0",
                is_active=True,
                threshold=70.0
            )
            db.add(cam)
            db.commit()
            db.refresh(cam)

        # 4 distinct threat scenarios
        threat_configs = [
            {
                "title": "Slip & Fall Incident",
                "score": 88.5,
                "desc": "Fall detected for Person 1 (Conf: 0.88), Horizontal posture breach",
                "color": (0, 0, 255), # Red
                "filename": "event_fall_threat.jpg",
                "minutes_ago": 2
            },
            {
                "title": "Violent Aggression",
                "score": 94.0,
                "desc": "Violence/aggression detected for Person 2 (Conf: 0.94), High velocity motion",
                "color": (0, 0, 255), # Red
                "filename": "event_violence_threat.jpg",
                "minutes_ago": 5
            },
            {
                "title": "Dangerously Close Proximity",
                "score": 72.5,
                "desc": "Person 1 and Person 2 are dangerously close (45.0px hazard distance)",
                "color": (0, 255, 255), # Yellow/Cyan
                "filename": "event_proximity_threat.jpg",
                "minutes_ago": 8
            },
            {
                "title": "Restricted Zone Intrusion",
                "score": 81.0,
                "desc": "Person 3 entered restricted Active Monitor Zone (Boundary Breach)",
                "color": (0, 165, 255), # Orange
                "filename": "event_zone_intrusion.jpg",
                "minutes_ago": 12
            }
        ]

        now = datetime.utcnow()
        added_count = 0

        for config in threat_configs:
            filepath = create_synthetic_snapshot(
                config["filename"],
                config["title"],
                config["score"],
                config["desc"],
                config["color"]
            )

            event_time = now - timedelta(minutes=config["minutes_ago"])

            db_event = Event(
                camera_id=cam.id,
                timestamp=event_time,
                score=config["score"],
                image_path=filepath,
                description=f"{config['title']}: {config['desc']}"
            )
            db.add(db_event)
            db.commit()
            db.refresh(db_event)

            db_alert = Alert(
                event_id=db_event.id,
                timestamp=event_time,
                message=config["desc"]
            )
            db.add(db_alert)
            db.commit()
            added_count += 1

        print(f"Successfully seeded {added_count} distinct safety threats into SQLite DB & data/events folder!")

    except Exception as e:
        print(f"Error seeding demo threats: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_threats()
