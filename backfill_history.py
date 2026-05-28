import datetime
import random
import time
import feedparser
import requests
import re
import urllib.parse
import json
import os
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Constituency, CivicUpdate
from googlenewsdecoder import gnewsdecoder
from ingestion_real_news import is_relevant_civic_update, get_og_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'tn_constituencies.json'), 'r', encoding='utf-8') as f:
    TN_MAPPING = json.load(f)

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
    
    # Ensure all constituencies and their districts exist in database
    for district, constituencies_list in TN_MAPPING.items():
        for c_name in constituencies_list:
            if not db.query(Constituency).filter(Constituency.name == c_name, Constituency.district == district).first():
                db.add(Constituency(name=c_name, district=district))
    db.commit()

    constituencies = db.query(Constituency).all()
    
    print("Starting historical backfill from January to May 2026...")
    total_added = 0

    # Get deduplicated list of search keys to run queries
    processed_search_keys = set()
    search_keys = []
    for district_name in TN_MAPPING.keys():
        search_key = "Chennai" if "Chennai" in district_name else district_name
        if search_key not in processed_search_keys:
            processed_search_keys.add(search_key)
            search_keys.append((search_key, district_name))

    for month_name, start_date, end_date in MONTH_RANGES:
        print(f"\nFetching data for {month_name} 2026 ({start_date} to {end_date})...")
        month_entries = [] # List of tuples: (entry, district_name)
        
        for search_key, district_name in search_keys:
            # Construct Google News RSS query with date parameters
            q = f"{search_key}+civic+issues+road+garbage+water"
            url = f"https://news.google.com/rss/search?q={q}+after:{start_date}+before:{end_date}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                feed = feedparser.parse(url)
                # Take top 3 entries per query to keep run time and API usage reasonable
                for entry in feed.entries[:3]:
                    month_entries.append((entry, district_name))
                time.sleep(0.2) # Small delay to be polite
            except Exception as e:
                print(f"Failed parsing feed for {month_name} query '{q}': {e}")
        
        print(f"Collected {len(month_entries)} unique potential articles for {month_name}. Filtering and decoding...")
        
        added_in_month = 0
        for entry, district_name in month_entries:
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
            district_constituencies = [c for c in constituencies if c.district == district_name]
            if not district_constituencies:
                district_constituencies = constituencies
                
            matched_c = next((c for c in district_constituencies if c.name.lower() in title.lower()), None)
            constituency = matched_c if matched_c else random.choice(district_constituencies)
            
            status = random.choice(["Reported", "In Progress", "Resolved"])
            image_url = get_og_image(real_url)
            
            # Scrape description
            description = ""
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
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

