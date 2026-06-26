# Context-Aware Safety Monitoring

This is an AI-based system that uses live video input to monitor human interactions and detect unusual or unsafe activities in real-time.

## Features
- Real-time person detection (YOLOv8)
- Multi-person tracking (DeepSORT)
- Pose estimation (MediaPipe)
- Feature extraction (Distance, Speed, Posture)
- Behavioral analysis and risk scoring (Heuristics & Proxy LSTM)
- Web dashboard (Flask)
- Automatic event capture

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt deepsort-realtime
```

2. Run the application:
```bash
python main.py
```

3. Open the web dashboard:
Navigate to `http://localhost:5000` in your web browser.

## Directory Structure
- `src/camera/`: Video capture
- `src/detection/`: YOLO and DeepSORT
- `src/pose/`: MediaPipe Pose Estimation
- `src/features/`: Movement and posture analysis
- `src/model/`: Risk score analysis
- `src/api/`: Flask dashboard
- `src/core/`: Application pipeline logic
- `data/events/`: Saved image captures of high-risk events
