import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database.db import engine, Base, SessionLocal
from backend.database.models import Camera
from backend.routers import cameras, events, stream

# Ensure folders exist
os.makedirs(os.path.abspath("data/events"), exist_ok=True)
os.makedirs(os.path.abspath("data/weights"), exist_ok=True)

# Build database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CCTV Safety Monitor API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static media directories
app.mount("/events", StaticFiles(directory="data/events"), name="events")

# Include API and WS routers
app.include_router(cameras.router)
app.include_router(events.router)
app.include_router(stream.router)

# Seed DB on startup if empty
@app.on_event("startup")
def startup_event():
    # Run migrations for the cameras table (adding threshold & zone columns if they don't exist)
    try:
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(cameras)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        
        migrations = [
            ("threshold", "ALTER TABLE cameras ADD COLUMN threshold FLOAT DEFAULT 70.0"),
            ("zone_min_x", "ALTER TABLE cameras ADD COLUMN zone_min_x FLOAT DEFAULT 0.0"),
            ("zone_min_y", "ALTER TABLE cameras ADD COLUMN zone_min_y FLOAT DEFAULT 0.0"),
            ("zone_max_x", "ALTER TABLE cameras ADD COLUMN zone_max_x FLOAT DEFAULT 1.0"),
            ("zone_max_y", "ALTER TABLE cameras ADD COLUMN zone_max_y FLOAT DEFAULT 1.0")
        ]
        for col_name, sql in migrations:
            if col_name not in existing_cols:
                try:
                    cursor.execute(sql)
                    connection.commit()
                except Exception as e:
                    print(f"Error adding column {col_name}: {e}")
        cursor.close()
        connection.close()
        print("Database schema migration checked.")
    except Exception as e:
        print(f"Migration error: {e}")

    db = SessionLocal()
    try:
        if db.query(Camera).count() == 0:
            default_cam = Camera(
                name="Local Camera 0 (Webcam)",
                source="0",
                is_active=True,
                threshold=70.0,
                zone_min_x=0.0,
                zone_min_y=0.0,
                zone_max_x=1.0,
                zone_max_y=1.0
            )
            db.add(default_cam)
            db.commit()
            print("Successfully seeded DB with local webcam camera.")
    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"status": "running", "info": "CCTV Safety Monitor API"}