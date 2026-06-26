import math

previous_positions = {}

def calculate_risk(tracks):
    risk_score = 0
    alerts = []

    current_positions = {}

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id

        ltrb = track.to_ltrb()

        x1, y1, x2, y2 = ltrb

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        current_positions[track_id] = (center_x, center_y)

        # Movement speed detection
        if track_id in previous_positions:
            prev_x, prev_y = previous_positions[track_id]

            distance = math.sqrt(
                (center_x - prev_x) ** 2 +
                (center_y - prev_y) ** 2
            )

            if distance > 50:
                risk_score += 20
                alerts.append(f"Fast movement detected: ID {track_id}")

    # Crowd proximity detection
    ids = list(current_positions.keys())

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            x1, y1 = current_positions[ids[i]]
            x2, y2 = current_positions[ids[j]]

            distance = math.sqrt(
                (x2 - x1) ** 2 +
                (y2 - y1) ** 2
            )

            if distance < 100:
                risk_score += 30
                alerts.append("People too close")

    previous_positions.clear()
    previous_positions.update(current_positions)

    return risk_score, alerts