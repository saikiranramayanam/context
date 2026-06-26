import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database path: data/safety_monitor.db
db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
os.makedirs(db_dir, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(db_dir, 'safety_monitor.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
