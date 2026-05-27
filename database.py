from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, 'tracker.db')}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_PATH)

# Robust check: if the database folder doesn't exist, try to create it.
# If it fails (due to write restrictions on custom paths), fall back to the local workspace folder.
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    # Clean up the path
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:////", "/").replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            # Fallback to local project directory
            SQLALCHEMY_DATABASE_URL = DEFAULT_DB_PATH

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
