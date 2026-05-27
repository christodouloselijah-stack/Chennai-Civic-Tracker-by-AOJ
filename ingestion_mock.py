import datetime
import random
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Constituency, CivicUpdate

# List of the 16 assembly constituencies
CONSTITUENCIES = [
    "Dr. Radhakrishnan Nagar",
    "Perambur",
    "Kolathur",
    "Villivakkam",
    "Thiru-Vi-Ka-Nagar",
    "Egmore",
    "Royapuram",
    "Harbour",
    "Chepauk-Thiruvallikeni",
    "Thousand Lights",
    "Anna Nagar",
    "Virugampakkam",
    "Saidapet",
    "Thiyagarayanagar",
    "Mylapore",
    "Velachery"
]

TITLES = [
    "Stormwater Drain Expansion",
    "Pothole Repair",
    "LED Street Light Installation",
    "Park Renovation",
    "Sewage Pipeline Replacement",
    "Pedestrian Walkway Upgrade"
]

STATUSES = ["Reported", "In Progress", "Resolved"]

IMAGES = [
    "https://images.unsplash.com/photo-1584463699039-444855562d98?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1541888081691-1cb118a803e4?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80"
]

def ingest_mock_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Ensure all constituencies exist
    for c_name in CONSTITUENCIES:
        constituency = db.query(Constituency).filter(Constituency.name == c_name).first()
        if not constituency:
            constituency = Constituency(name=c_name)
            db.add(constituency)
    
    db.commit()

    # Generate daily mock updates
    constituencies = db.query(Constituency).all()
    today = datetime.date.today()

    for constituency in constituencies:
        # 1 to 3 updates per constituency per day
        num_updates = random.randint(1, 3)
        for _ in range(num_updates):
            update = CivicUpdate(
                constituency_id=constituency.id,
                title=random.choice(TITLES),
                description=f"Mock progress update for {constituency.name}.",
                status=random.choice(STATUSES),
                image_url=random.choice(IMAGES),
                date=today
            )
            db.add(update)
    
    db.commit()
    db.close()
    print("Mock data ingested successfully.")

if __name__ == "__main__":
    ingest_mock_data()
