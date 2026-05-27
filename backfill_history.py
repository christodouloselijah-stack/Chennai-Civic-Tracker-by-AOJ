import datetime
import random
import time
import feedparser
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Constituency, CivicUpdate
from googlenewsdecoder import gnewsdecoder
from ingestion_real_news import is_relevant_civic_update, get_og_image

CONSTITUENCIES = [
    "Dr. Radhakrishnan Nagar", "Perambur", "Kolathur", "Villivakkam",
    "Thiru-Vi-Ka-Nagar", "Egmore", "Royapuram", "Harbour",
    "Chepauk-Thiruvallikeni", "Thousand Lights", "Anna Nagar",
    "Virugampakkam", "Saidapet", "Thiyagarayanagar", "Mylapore", "Velachery"
]

QUERIES = [
    "Chennai+corporation+civic+issues",
    "Chennai+road+repair+pavement+potholes",
    "Chennai+stormwater+drain+construction+flooding",
    "Chennai+garbage+clearance+waste+management",
    "Chennai+street+lights+dark+spots"
]

# Date ranges to backfill
MONTH_RANGES = [
    ("January", "2026-01-01", "2026-02-01"),
    ("February", "2026-02-01", "2026-03-01"),
    ("March", "2026-03-01", "2026-04-01"),
    ("April", "2026-04-01", "2026-05-01"),
    ("May", "2026-05-01", "2026-06-01")
]

def backfill():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Ensure constituencies exist
    for c_name in CONSTITUENCIES:
        if not db.query(Constituency).filter(Constituency.name == c_name).first():
            db.add(Constituency(name=c_name))
    db.commit()

    constituencies = db.query(Constituency).all()
    
    print("Starting historical backfill from January to May 2026...")
    total_added = 0

    for month_name, start_date, end_date in MONTH_RANGES:
        print(f"\nFetching data for {month_name} 2026 ({start_date} to {end_date})...")
        month_entries = {}
        
        for q in QUERIES:
            # Construct Google News RSS query with date parameters
            url = f"https://news.google.com/rss/search?q={q}+after:{start_date}+before:{end_date}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                feed = feedparser.parse(url)
                # Take top 8 entries from each query per month to build a good database size
                for entry in feed.entries[:8]:
                    if entry.link not in month_entries:
                        month_entries[entry.link] = entry
            except Exception as e:
                print(f"Failed parsing feed for {month_name} query '{q}': {e}")
        
        entries = list(month_entries.values())
        print(f"Collected {len(entries)} unique potential articles for {month_name}. Filtering and decoding...")
        
        added_in_month = 0
        for entry in entries:
            raw_title = entry.title
            link = entry.link
            
            # Extract source
            source = "Google News"
            title = raw_title
            if " - " in raw_title:
                parts = raw_title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1]

            summary_soup = BeautifulSoup(entry.summary, 'html.parser')
            summary_text = summary_soup.get_text()

            # Filter relevance
            if not is_relevant_civic_update(title, summary_text):
                continue
            
            # Decode Google News link
            real_url = link
            try:
                decoded = gnewsdecoder(link)
                if decoded.get("status"):
                    real_url = decoded["decoded_url"]
            except Exception:
                pass
            
            # Check if this article already exists in DB
            exists = db.query(CivicUpdate).filter(CivicUpdate.article_url == real_url).first()
            if exists:
                continue

            # Parse the published date
            article_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    tp = entry.published_parsed
                    article_date = datetime.date(tp.tm_year, tp.tm_mon, tp.tm_mday)
                except Exception:
                    pass
            
            if not article_date:
                # Fallback: parser fails, assign random date in that month
                year = 2026
                month_num = 1
                if month_name == "February": month_num = 2
                elif month_name == "March": month_num = 3
                elif month_name == "April": month_num = 4
                elif month_name == "May": month_num = 5
                
                day = random.randint(1, 28)
                article_date = datetime.date(year, month_num, day)

            # Match constituency
            matched_c = next((c for c in constituencies if c.name.lower() in title.lower()), None)
            constituency = matched_c if matched_c else random.choice(constituencies)
            
            status = random.choice(["Reported", "In Progress", "Resolved"])
            image_url = get_og_image(real_url)
            
            # Scrape description
            description = ""
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(real_url, headers=headers, timeout=4, allow_redirects=True)
                page_soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = [p.get_text().strip() for p in page_soup.find_all('p') if len(p.get_text().strip()) > 50]
                if paragraphs:
                    description = "\n\n".join(paragraphs[:2])
            except Exception:
                pass
                
            if not description:
                description = summary_text
                if len(description) > 300:
                    description = description[:300] + "..."
            
            update = CivicUpdate(
                constituency_id=constituency.id,
                title=title,
                description=description,
                status=status,
                image_url=image_url,
                date=article_date,
                source=source,
                article_url=real_url
            )
            db.add(update)
            added_in_month += 1
            total_added += 1

        db.commit()
        print(f"Added {added_in_month} civic updates for {month_name} 2026.")
        
    db.close()
    print(f"\nBackfill complete! Added a total of {total_added} historical updates.")

if __name__ == "__main__":
    backfill()
