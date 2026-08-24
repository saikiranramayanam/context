from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.database.db import SessionLocal
from backend.database import models
from backend.ai_engine.pipeline import SafetyPipeline
import asyncio
import cv2
import base64
import json

router = APIRouter(prefix="/ws", tags=["stream"])

# Active camera streams manager
# { camera_id: { "pipeline": SafetyPipeline, "clients": set(WebSocket), "task": asyncio.Task } }
active_streams = {}
stream_lock = asyncio.Lock()

def stop_stream(camera_id: int):
    """Stop active stream and clean up pipeline for given camera_id."""
    stream = active_streams.get(camera_id)
    if stream:
        task = stream.get("task")
        if task and not task.done():
            task.cancel()
        pipeline = stream.get("pipeline")
        if pipeline:
            try:
                pipeline.cleanup()
            except Exception as e:
                print(f"Error cleaning up pipeline for camera {camera_id}: {e}")
        active_streams.pop(camera_id, None)

async def broadcast_camera_feed(camera_id: int):
    """
    Background loop that runs the pipeline and broadcasts frames to all connected WebSockets.
    """
    stream = active_streams.get(camera_id)
    if not stream:
        return
        
    pipeline = stream["pipeline"]
    try:
        while True:
            # Check if there are active clients
            if not stream["clients"]:
                await asyncio.sleep(0.1)
                continue
                
            # Run one step of pipeline in the default thread pool executor to keep event loop responsive
            loop = asyncio.get_running_loop()
            display_frame, risk_score, alerts = await loop.run_in_executor(None, pipeline.run_step)
            
            if display_frame is not None:
                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', display_frame)
                if ret:
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    frame_data = f"data:image/jpeg;base64,{jpg_as_text}"
                    
                    # Construct payload
                    payload = {
                        "frame": frame_data,
                        "risk_score": float(risk_score),
                        "alerts": list(alerts)
                    }
                    payload_str = json.dumps(payload)
                    
                    # Broadcast to all clients
                    disconnected_clients = []
                    for client in list(stream["clients"]):
                        try:
                            await client.send_text(payload_str)
                        except Exception:
                            disconnected_clients.append(client)
                            
                    for client in disconnected_clients:
                        stream["clients"].discard(client)
                        
            # Roughly 30 FPS cap
            await asyncio.sleep(0.03)
            
            # If no clients are connected anymore, exit loop
            if not stream["clients"]:
                break
                
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in stream broadcast loop for camera {camera_id}: {e}")
    finally:
        # Clean up and close pipeline
        print(f"Cleaning up pipeline and releasing camera source {camera_id}")
        pipeline.cleanup()
        active_streams.pop(camera_id, None)

@router.websocket("/stream/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    await websocket.accept()
    
    # Check if camera exists and is active
    db = SessionLocal()
    camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    db.close()
    
    if not camera:
        await websocket.close(code=4004, reason="Camera not found")
        return
        
    if not camera.is_active:
        await websocket.close(code=4003, reason="Camera is inactive")
        return

    async with stream_lock:
        # If camera_id has an abandoned stream with no clients, stop it first
        if camera_id in active_streams and not active_streams[camera_id]["clients"]:
            stop_stream(camera_id)
            await asyncio.sleep(0.2)

        # Check if stream already exists
        if camera_id not in active_streams:
            try:
                pipeline = SafetyPipeline(
                    camera_id=camera.id,
                    name=camera.name,
                    source=camera.source,
                    threshold=camera.threshold if camera.threshold is not None else 70.0,
                    zone_min_x=camera.zone_min_x if camera.zone_min_x is not None else 0.0,
                    zone_min_y=camera.zone_min_y if camera.zone_min_y is not None else 0.0,
                    zone_max_x=camera.zone_max_x if camera.zone_max_x is not None else 1.0,
                    zone_max_y=camera.zone_max_y if camera.zone_max_y is not None else 1.0
                )
                active_streams[camera_id] = {
                    "pipeline": pipeline,
                    "clients": {websocket},
                    "task": None
                }
                # Start background task
                task = asyncio.create_task(broadcast_camera_feed(camera_id))
                active_streams[camera_id]["task"] = task
            except Exception as e:
                print(f"Failed to start pipeline for camera {camera_id}: {e}")
                await websocket.close(code=4005, reason="Failed to start video source")
                return
        else:
            active_streams[camera_id]["clients"].add(websocket)
        
    # Listen to WebSocket client disconnect
    try:
        while True:
            # Just keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"WebSocket disconnected from camera {camera_id}")
    finally:
        # Client disconnect cleanup
        if camera_id in active_streams:
            active_streams[camera_id]["clients"].discard(websocket)
            # If no clients left, cancel task to clean up pipeline
            if not active_streams[camera_id]["clients"]:
                stop_stream(camera_id)