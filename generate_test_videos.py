import cv2
import numpy as np
import os

data_dir = os.path.abspath("data")
os.makedirs(data_dir, exist_ok=True)

def generate_video(filename, threat_type):
    filepath = os.path.join(data_dir, filename)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, 15.0, (640, 480))
    
    num_frames = 120 # 8 seconds of video
    for frame_idx in range(num_frames):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Grid lines
        for x in range(0, 640, 40):
            cv2.line(img, (x, 0), (x, 480), (25, 25, 25), 1)
        for y in range(0, 480, 40):
            cv2.line(img, (0, y), (640, y), (25, 25, 25), 1)
            
        t = frame_idx / num_frames
        
        if threat_type == "fall":
            # Person standing, then falling over to horizontal position
            head_y = int(120 + t * 200)
            body_angle = t * 1.57 # 0 to 90 degrees
            
            # Head
            hx = int(320 + np.sin(body_angle) * 150)
            hy = int(120 + (1 - np.cos(body_angle)) * 200)
            cv2.circle(img, (hx, hy), 22, (255, 220, 180), -1)
            
            # Torso
            bx = int(hx - np.sin(body_angle) * 120)
            by = int(hy + np.cos(body_angle) * 120)
            cv2.line(img, (hx, hy), (bx, by), (0, 255, 255), 4)
            cv2.putText(img, "TEST CASE 1: SLIP & FALL SIMULATION", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
        elif threat_type == "violence":
            # Two figures moving rapidly toward each other with striking motions
            p1_x = int(200 + np.sin(t * 12) * 40)
            p2_x = int(440 - np.sin(t * 12) * 40)
            
            cv2.circle(img, (p1_x, 180), 22, (255, 220, 180), -1)
            cv2.line(img, (p1_x, 200), (p1_x, 320), (255, 0, 0), 4)
            
            cv2.circle(img, (p2_x, 180), 22, (255, 220, 180), -1)
            cv2.line(img, (p2_x, 200), (p2_x, 320), (0, 0, 255), 4)
            
            # Fast strike arm
            cv2.line(img, (p1_x, 240), (p2_x - 10, 230), (0, 0, 255), 4)
            cv2.putText(img, "TEST CASE 2: VIOLENCE / AGGRESSION SIMULATION", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
        elif threat_type == "proximity":
            # Two figures moving until they collide
            dist = max(10, int(300 - t * 280))
            p1_x = 320 - dist // 2
            p2_x = 320 + dist // 2
            
            cv2.circle(img, (p1_x, 200), 22, (255, 220, 180), -1)
            cv2.line(img, (p1_x, 220), (p1_x, 360), (0, 255, 255), 4)
            
            cv2.circle(img, (p2_x, 200), 22, (255, 220, 180), -1)
            cv2.line(img, (p2_x, 220), (p2_x, 360), (0, 255, 255), 4)
            
            # Line connecting them showing proximity
            cv2.line(img, (p1_x, 280), (p2_x, 280), (0, 0, 255), 2)
            cv2.putText(img, f"DISTANCE: {dist}px", (270, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(img, "TEST CASE 3: DANGEROUS PROXIMITY SIMULATION", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
        else: # zone intrusion
            # Draw Hot Zone Box
            cv2.rectangle(img, (220, 120), (580, 440), (255, 229, 0), 2)
            cv2.putText(img, "RESTRICTED ZONE", (230, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 229, 0), 2)
            
            # Figure walks into the box
            px = int(100 + t * 300)
            py = int(240)
            in_zone = px >= 220
            color = (0, 0, 255) if in_zone else (128, 128, 128)
            
            cv2.circle(img, (px, py - 40), 22, (255, 220, 180), -1)
            cv2.line(img, (px, py - 18), (px, py + 80), color, 4)
            cv2.putText(img, "TEST CASE 4: HOT ZONE INTRUSION SIMULATION", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 229, 0), 2)
            
        cv2.putText(img, f"Frame {frame_idx + 1}/{num_frames}", (500, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
        out.write(img)
        
    out.release()
    print(f"Generated test video: {filepath}")

generate_video("threat_1_slip_fall.mp4", "fall")
generate_video("threat_2_violence_aggression.mp4", "violence")
generate_video("threat_3_dangerous_proximity.mp4", "proximity")
generate_video("threat_4_zone_intrusion.mp4", "zone")
