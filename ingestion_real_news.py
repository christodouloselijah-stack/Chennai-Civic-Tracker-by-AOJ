import datetime
import random
import feedparser
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Constituency, CivicUpdate
import base64

def decode_google_news_url(url):
    try:
        if "/articles/" in url:
            parts = url.split("/articles/")[1]
            parts = parts.split("?")[0].split("&")[0]
            clean_parts = re.sub(r'[^A-Za-z0-9\-_]', '', parts)
            rem = len(clean_parts) % 4
            if rem == 1:
                clean_parts = clean_parts[:-1]
            elif rem == 2:
                clean_parts += "=="
            elif rem == 3:
                clean_parts += "="
            decoded_bytes = base64.urlsafe_b64decode(clean_parts)
            decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
            match = re.search(r'(https?://[^\s\x00-\x1f\x7f-\xff]+)', decoded_str)
            if match:
                clean_url = match.group(1)
                clean_url = re.sub(r'[^\w\d\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\%].*$', '', clean_url)
                return clean_url
    except Exception as e:
        print(f"Decode failed: {e}")
    return url

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'tn_constituencies.json'), 'r', encoding='utf-8') as f:
    TN_MAPPING = json.load(f)

CIVIC_KEYWORDS = [
    "road", "repair", "pothole", "pave", "paving", "lay", "laying", "drain", "stormwater", 
    "sewage", "sewer", "water", "leak", "leakage", "garbage", "waste", "dump", "bin", "trash", 
    "light", "illumination", "park", "playground", "encroachment", "eviction", "demolish", "demolition",
    "widening", "canal", "bridge", "flyover", "subway", "sanitation", "cleaning", "beautification",
    "infrastructure", "renovation", "construction"
]

POLITICAL_CRIME_KEYWORDS = [
    "election", "political campaign", "nomination", "arrest", "arrested", 
    "clash", "murder", "theft", "robbery", "accused", "assault", "dmk", "admk", "tvk", 
    "bjp", "congress", "scam", "corruption"
]

def is_relevant_civic_update(title, description, url=""):
    text = (title + " " + description + " " + (url or "")).lower()
    
    # Exclude other states/cities to prevent Google News autocorrect overlaps
    EXCLUDE_KEYWORDS = ["ranchi", "bengaluru", "bangalore", "karnataka", "gurugram", "gurgaon", "haryana", 
                        "noida", "vijayawada", "andhra", "kerala", "delhi", "mumbai", "maharashtra", 
                        "kolkata", "hyderabad", "telangana", "patna", "bihar", "jharkhand", "ranchi"]
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False
        
    if any(word in text for word in POLITICAL_CRIME_KEYWORDS):
        return False
    if any(word in text for word in CIVIC_KEYWORDS):
        return True
    return False

def get_og_image(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content'].strip()
            return urllib.parse.urljoin(url, img_url)
    except Exception as e:
        print(f"Failed to fetch image for {url}: {e}")
    
    return f"https://picsum.photos/400/300?random={random.randint(1,1000)}"

def ingest_real_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Ensure all constituencies and their districts exist in database
    for district, constituencies_list in TN_MAPPING.items():
        for c_name in constituencies_list:
            if not db.query(Constituency).filter(Constituency.name == c_name, Constituency.district == district).first():
                db.add(Constituency(name=c_name, district=district))
    db.commit()
 
    constituencies = db.query(Constituency).all()
    today = datetime.date.today()
    
    # Target major municipal corporations and populated districts where civic news is active
    MAJOR_CIVIC_DISTRICTS = [
        "Chennai North", "Chennai Central", "Chennai South", "Coimbatore", "Madurai", 
        "Tiruchirappalli", "Salem", "Tirunelveli", "Vellore", "Thanjavur", "Thiruvallur", "Chengalpattu"
    ]
    
    all_entries = [] # List of tuples: (entry, district)
    processed_search_keys = set()
    
    for district_name in MAJOR_CIVIC_DISTRICTS:
        if district_name not in TN_MAPPING:
            continue
        search_key = "Chennai" if "Chennai" in district_name else district_name
        if search_key in processed_search_keys:
            continue
        processed_search_keys.add(search_key)
        
        # Two highly-focused queries to retrieve road, water, drainage and garbage updates
        queries = [
            f"{search_key}+Tamil+Nadu+road+pothole+traffic",
            f"{search_key}+Tamil+Nadu+garbage+waste+water+drainage"
        ]
        
        for q in queries:
            url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                feed = feedparser.parse(url)
                # Parse top 8 articles to get high-density real updates quickly
                for entry in feed.entries[:8]:
                    all_entries.append((entry, district_name))
            except Exception as e:
                print(f"Failed parsing feed for query {q}: {e}")
            
    print(f"Aggregated {len(all_entries)} potential news updates before filtering. Filtering for civic updates...")
    
    for entry, district_name in all_entries:
        raw_title = entry.title
        link = entry.link
        
        # Extract source from title
        source = "Google News"
        title = raw_title
        if " - " in raw_title:
            parts = raw_title.rsplit(" - ", 1)
            title = parts[0]
            source = parts[1]
 
        # Extract entry summary to test relevance
        summary_soup = BeautifulSoup(entry.summary, 'html.parser')
        summary_text = summary_soup.get_text()
 
        # Relevance filtering
        if not is_relevant_civic_update(title, summary_text, link):
            continue
        
        # Decode Google News redirect URL (only for relevant items!)
        real_url = decode_google_news_url(link)
            
        # Check if this article already exists in DB
        exists = db.query(CivicUpdate).filter(CivicUpdate.article_url == real_url).first()
        if exists:
            continue
            
        # Try to find a matching constituency in title, else random from the same district
        district_constituencies = [c for c in constituencies if c.district == district_name]
        if not district_constituencies:
            district_constituencies = constituencies # Fallback
            
        matched_c = next((c for c in district_constituencies if c.name.lower() in title.lower()), None)
        constituency = matched_c if matched_c else random.choice(district_constituencies)
        
        status = random.choice(["Reported", "In Progress", "Resolved"])
        image_url = get_og_image(real_url)
        
        # Scrape full description (paragraphs) from real URL
        description = ""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            response = requests.get(real_url, headers=headers, timeout=6, allow_redirects=True)
            page_soup = BeautifulSoup(response.text, 'html.parser')
            # Extract paragraphs that look like article content
            paragraphs = [p.get_text().strip() for p in page_soup.find_all('p') if len(p.get_text().strip()) > 50]
            if paragraphs:
                # Take first 3 paragraphs and join them
                description = "\n\n".join(paragraphs[:3])
        except Exception as e:
            print(f"Failed to scrape body for {real_url}: {e}")
            
        if not description:
            description = summary_text
            if len(description) > 300:
                description = description[:300] + "..."
        
        # Parse the published date
        article_date = today
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                tp = entry.published_parsed
                article_date = datetime.date(tp.tm_year, tp.tm_mon, tp.tm_mday)
            except Exception:
                pass

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
    
    db.commit()
    db.close()
    print("Real news ingested successfully.")

if __name__ == "__main__":
    ingest_real_data()
