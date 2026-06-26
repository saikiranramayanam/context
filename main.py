import sys
import os
import uvicorn

if __name__ == "__main__":
    print("Starting CCTV Safety Monitoring System Backend...")
    print("Initializing AI components (YOLOv8, MediaPipe Pose, Action LSTM)...")
    
    # Run the FastAPI app
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
