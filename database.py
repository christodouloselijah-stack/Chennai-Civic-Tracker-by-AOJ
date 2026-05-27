from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, 'tracker.db')}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_PATH)

# Robust check: verify if the database path is writable.
# If the directory is not writable (e.g. /var/data on Render Free Tier), fall back to local workspace.
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:////", "/").replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    
    is_writable = False
    if db_dir:
        if os.path.exists(db_dir):
            # Test writability by writing a temporary file
            try:
                test_file = os.path.join(db_dir, ".write_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                is_writable = True
            except Exception:
                is_writable = False
        else:
            # Try to create the directory
            try:
                os.makedirs(db_dir, exist_ok=True)
                is_writable = True
            except Exception:
                is_writable = False
                
    if not is_writable:
        SQLALCHEMY_DATABASE_URL = DEFAULT_DB_PATH

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
