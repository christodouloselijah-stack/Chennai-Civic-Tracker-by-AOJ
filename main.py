from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from database import engine, Base, SessionLocal
from models import Constituency, CivicUpdate
from scheduler import start_scheduler
from pdf_generator import generate_pdf_report

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chennai Civic Tracker")

# Mount static files and templates
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Start background scheduler
@app.on_event("startup")
def startup_event():
    start_scheduler()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/constituencies")
def get_constituencies(db: Session = Depends(get_db)):
    return db.query(Constituency).all()

from sqlalchemy import func, extract
from typing import Optional

@app.get("/api/updates/all")
def get_all_updates(month: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CivicUpdate)
    if month:
        try:
            y, m = map(int, month.split('-'))
            query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
        except ValueError:
            pass
    return query.order_by(CivicUpdate.date.desc()).all()

@app.get("/api/stats/all_aggregate")
def get_all_aggregate_stats(month: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CivicUpdate)
    if month:
        try:
            y, m = map(int, month.split('-'))
            query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
        except ValueError:
            pass
    updates = query.all()
    total = len(updates)
    resolved = sum(1 for u in updates if u.status == "Resolved")
    in_progress = sum(1 for u in updates if u.status == "In Progress")
    reported = sum(1 for u in updates if u.status == "Reported")
    return {
        "total": total,
        "resolved": resolved,
        "in_progress": in_progress,
        "reported": reported
    }

@app.get("/api/reports/all_aggregate/download")
def download_all_aggregate_report(month: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CivicUpdate)
    if month:
        try:
            y, m = map(int, month.split('-'))
            query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
        except ValueError:
            pass
    updates = query.all()
    pdf_buffer = generate_pdf_report("Chennai (Overall)", updates, month)
    headers = {
        'Content-Disposition': 'attachment; filename="overall_chennai_report.pdf"'
    }
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)

@app.get("/api/updates/{constituency_id}")
def get_updates(constituency_id: int, month: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CivicUpdate).filter(CivicUpdate.constituency_id == constituency_id)
    if month:
        try:
            y, m = map(int, month.split('-'))
            query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
        except ValueError:
            pass
    return query.order_by(CivicUpdate.date.desc()).all()

@app.get("/api/all_stats")
def get_all_stats(month: Optional[str] = None, db: Session = Depends(get_db)):
    constituencies = db.query(Constituency).all()
    result = []
    for c in constituencies:
        query = db.query(CivicUpdate).filter(CivicUpdate.constituency_id == c.id)
        if month:
            try:
                y, m = map(int, month.split('-'))
                query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
            except ValueError:
                pass
        updates = query.all()
        total = len(updates)
        resolved = sum(1 for u in updates if u.status == "Resolved")
        in_progress = sum(1 for u in updates if u.status == "In Progress")
        reported = sum(1 for u in updates if u.status == "Reported")
        result.append({
            "id": c.id,
            "name": c.name,
            "total": total,
            "resolved": resolved,
            "in_progress": in_progress,
            "reported": reported
        })
    return result

@app.get("/api/stats/{constituency_id}")
def get_stats(constituency_id: int, month: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CivicUpdate).filter(CivicUpdate.constituency_id == constituency_id)
    if month:
        try:
            y, m = map(int, month.split('-'))
            query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
        except ValueError:
            pass
    updates = query.all()
    total = len(updates)
    resolved = sum(1 for u in updates if u.status == "Resolved")
    in_progress = sum(1 for u in updates if u.status == "In Progress")
    reported = sum(1 for u in updates if u.status == "Reported")
    return {
        "total": total,
        "resolved": resolved,
        "in_progress": in_progress,
        "reported": reported
    }

@app.get("/api/reports/{constituency_id}/download")
def download_report(constituency_id: int, month: Optional[str] = None, db: Session = Depends(get_db)):
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    if not constituency:
        return {"error": "Constituency not found"}
        
    query = db.query(CivicUpdate).filter(CivicUpdate.constituency_id == constituency_id)
    if month:
        try:
            y, m = map(int, month.split('-'))
            query = query.filter(extract('year', CivicUpdate.date) == y, extract('month', CivicUpdate.date) == m)
        except ValueError:
            pass
    
    updates = query.all()
    pdf_buffer = generate_pdf_report(constituency.name, updates, month)
    
    headers = {
        'Content-Disposition': f'attachment; filename="report_{constituency.name.replace(" ", "_")}.pdf"'
    }
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
