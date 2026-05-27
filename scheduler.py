from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from ingestion_real_news import ingest_real_data

def start_scheduler():
    scheduler = BackgroundScheduler()
    ist = pytz.timezone('Asia/Kolkata')
    
    # Schedule to run every day at 06:00 AM IST
    trigger = CronTrigger(hour=6, minute=0, timezone=ist)
    scheduler.add_job(ingest_real_data, trigger=trigger, id="daily_ingestion", replace_existing=True)
    
    scheduler.start()
    print("Scheduler started. Background job configured for 06:00 AM IST daily.")
