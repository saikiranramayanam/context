from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.db import get_db
from backend.database import models
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api/events", tags=["events"])

class EventSchema(BaseModel):
    id: int
    timestamp: datetime
    camera_id: int
    camera_name: Optional[str] = None
    score: float
    image_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[EventSchema])
def get_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.timestamp.desc()).all()
    
    result = []
    for event in events:
        # Convert path to web URL
        filename = os.path.basename(event.image_path) if event.image_path else ""
        image_url = f"/events/{filename}" if filename else None
        
        result.append(EventSchema(
            id=event.id,
            timestamp=event.timestamp,
            camera_id=event.camera_id,
            camera_name=event.camera.name if event.camera else "Unknown",
            score=event.score,
            image_url=image_url,
            description=event.description
        ))
        
    return result

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Try deleting actual file on disk if it exists
    if event.image_path and os.path.exists(event.image_path):
        try:
            os.remove(event.image_path)
        except Exception as e:
            print(f"Error removing snapshot file: {e}")
            
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

@router.delete("")
def clear_all_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).all()
    for event in events:
        if event.image_path and os.path.exists(event.image_path):
            try:
                os.remove(event.image_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
                
    db.query(models.Event).delete()
    db.commit()
    return {"message": "All events cleared successfully"}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_events = db.query(models.Event).count()
    active_cameras = db.query(models.Camera).filter(models.Camera.is_active == True).count()
    
    avg_risk_query = db.query(func.avg(models.Event.score)).scalar()
    avg_risk = avg_risk_query if avg_risk_query is not None else 0.0
    
    # Check max score of events in the last 10 minutes to evaluate safety status
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    recent_max_query = db.query(func.max(models.Event.score)).filter(models.Event.timestamp >= ten_minutes_ago).scalar()
    recent_max = recent_max_query if recent_max_query is not None else 0.0
    
    if recent_max >= 85.0:
        safety_status = "CRITICAL"
    elif recent_max >= 70.0:
        safety_status = "WARNING"
    else:
        safety_status = "SAFE"
        
    return {
        "total_events": total_events,
        "active_cameras": active_cameras,
        "avg_risk": round(float(avg_risk), 1),
        "safety_status": safety_status
    }
