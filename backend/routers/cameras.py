from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database import models
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

class CameraBase(BaseModel):
    name: str
    source: str
    is_active: bool = True
    threshold: float = 70.0
    zone_min_x: float = 0.0
    zone_min_y: float = 0.0
    zone_max_x: float = 1.0
    zone_max_y: float = 1.0

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: int
    class Config:
        from_attributes = True

@router.get("", response_model=List[CameraResponse])
def get_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()

@router.post("", response_model=CameraResponse)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = models.Camera(
        name=camera.name,
        source=camera.source,
        is_active=camera.is_active,
        threshold=camera.threshold,
        zone_min_x=camera.zone_min_x,
        zone_min_y=camera.zone_min_y,
        zone_max_x=camera.zone_max_x,
        zone_max_y=camera.zone_max_y
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db_camera.name = camera.name
    db_camera.source = camera.source
    db_camera.is_active = camera.is_active
    db_camera.threshold = camera.threshold
    db_camera.zone_min_x = camera.zone_min_x
    db_camera.zone_min_y = camera.zone_min_y
    db_camera.zone_max_x = camera.zone_max_x
    db_camera.zone_max_y = camera.zone_max_y
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted successfully"}
