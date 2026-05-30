from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from ingestion_real_news import ingest_real_data
import datetime
from database import SessionLocal
from models import CivicUpdate
import threading

def run_ingestion_check():
    """Checks if updates have been ingested today. If not, runs ingestion in a background thread."""
    db = SessionLocal()
    try:
        today = datetime.date.today()
        today_updates = db.query(CivicUpdate).filter(CivicUpdate.date == today).count()
        if today_updates == 0:
            print("No updates found for today. Triggering automatic startup ingestion...")
            threading.Thread(target=ingest_real_data, daemon=True).start()
        else:
            print("Database already has updates for today.")
    except Exception as e:
        print(f"Failed to run startup ingestion check: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Schedule to run every day at 06:00 AM IST
    trigger = CronTrigger(hour=6, minute=0, timezone=ist)
    scheduler.add_job(ingest_real_data, trigger=trigger, id="daily_ingestion", replace_existing=True)
    
    scheduler.start()
    print("Scheduler started. Background job configured for 06:00 AM IST daily.")
    
    # Run the startup check to backfill if missed
    run_ingestion_check()
