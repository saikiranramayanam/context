# Aegis Sentinel: Context-Aware Safety Monitoring System

Aegis Sentinel is an enterprise-grade, AI-powered CCTV surveillance and safety monitoring system. By leveraging advanced deep learning pipelines, it processes video streams (RTSP feeds, local webcams, or MP4 files), tracks active subjects, estimates skeletal poses, recognizes unsafe behaviors (falls or violent actions), calculates proximity threats, and streams real-time feeds and telemetry directly to a React-based operator dashboard.

---

## 🚀 Key Dashboard Features

The operator interface is divided into four highly responsive, modular views:

### 1. Operations Overview
* **KPI Metrics**: Displays live indicators for Operational Nodes, Active Threats Flagged, Average Threat Index, and the overall Safety Severity Status.
* **Safety Threat Level Trend (Recharts)**: An interactive area graph showing real-time threat index scores for recent events.
* **Incident Frequency by Node (Recharts)**: A bar graph summarizing and comparing event counts across all registered cameras.
* **Camera Status Grid**: Quick-glance directory of online/offline cameras, listing their stream sources, detection zones, and alarm thresholds.

### 2. Live Monitor Feed
* **Live WebSocket Stream**: Renders active camera feeds annotated with real-time YOLOv8 bounding boxes, tracker IDs, and MediaPipe pose overlays.
* **Real-time Alert Ticker**: A side-panel feed updating instantly with chronological warning descriptions and time logs.
* **Synthetic Sound Alerts**: Leverages the browser's Web Audio API to trigger audio warnings when a critical threshold (≥70% threat) is breached.
* **Channel Selector**: Strip of clickable node buttons at the bottom to easily switch the active monitor feed.

### 3. Incident History Logs
* **Search Field**: Instantly filters log entries by incident description or camera name.
* **Severity Filters**: Filter records by All, Critical Threats (≥70%), or Warnings (<70%).
* **Snapshot Inspector**: Clickable thumbnails that open an overlay modal to inspect the high-resolution event image saved on disk.
* **CSV Audit Exporter**: Downloads a structured CSV report of the current filtered logs.
* **Log Purger**: An option to clear the entire local database incident history.

### 4. Node Settings & Zone Calibrator
* **Stream Registration Form**: Add or edit camera feeds by entering a name, video source, and threat threshold.
* **Active Zone Calibrator**: Sliders to define coordinates (Min/Max X and Y) of the active detection region.
* **Dynamic Boundary Preview**: An interactive visualization box showing the exact shape of the active monitoring zone.
* **Nodes Directory**: Manage registered cameras with quick toggles to enable/disable streams, edit calibrations, or delete feeds.

---

## 🛠️ Tech Stack & Directory Structure

```
safety-monitor/
├── backend/               # Python API & Computer Vision Engine
│   ├── ai_engine/         # YOLOv8, DeepSORT, MediaPipe, LSTM Models
│   ├── camera/            # Multithreaded Video Capture Stream
│   ├── database/          # SQLite DB Configuration & SQLAlchemy ORM
│   ├── routers/           # FastAPI Camera, Event, and WebSocket Stream Routers
│   └── main.py            # FastAPI Application Entrypoint
├── frontend/              # React & Vite Dashboard
│   ├── src/
│   │   ├── components/    # Reusable UI Blocks (Overview, Live, Logs, Settings)
│   │   ├── pages/         # Dashboard Page Router Shell
│   │   ├── styles/        # CSS Stylesheets (Modern Slate Dark Theme)
│   │   └── main.jsx       # Client Entrypoint
├── data/                  # Local Storage (Excluded from Git)
│   ├── events/            # Saved high-risk event JPEG frames
│   ├── weights/           # Pre-trained deep learning model weights
│   └── safety_monitor.db  # SQLite database file
├── main.py                # Root Startup Script
└── requirements.txt       # Backend Dependencies
```

---

## ⚙️ Installation & Running the System

Ensure you have **Python 3.8+** and **Node.js 18+** installed.

### 1. Backend Setup & Run
1. Open a terminal in the root directory and install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI backend server:
   ```bash
   python main.py
   ```
   *The backend will run on `http://127.0.0.1:8000`. On startup, it checks database migrations, seeds a default webcam camera, and trains/loads the PyTorch LSTM model weights.*

### 2. Frontend Setup & Run
1. Open a second terminal window, navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to the displayed URL (typically `http://localhost:5173`).
