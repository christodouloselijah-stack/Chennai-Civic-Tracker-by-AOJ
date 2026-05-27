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
from googlenewsdecoder import gnewsdecoder

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
    "Chennai+street+lights+dark+spots",
    "Chennai+metro+water+sewerage+leakage",
    "Chennai+GCC+development+infrastructure",
    "Chennai+encroachments+eviction+removal",
    "Chennai+traffic+diversion+flyover"
]

CIVIC_KEYWORDS = [
    "road", "repair", "pothole", "pave", "paving", "lay", "laying", "drain", "stormwater", 
    "sewage", "sewer", "water", "leak", "leakage", "garbage", "waste", "dump", "bin", "trash", 
    "light", "illumination", "park", "playground", "encroachment", "eviction", "demolish", "demolition",
    "widening", "canal", "bridge", "flyover", "subway", "sanitation", "cleaning", "beautification",
    "infrastructure", "renovation", "construction"
]

POLITICAL_CRIME_KEYWORDS = [
    "election", "political", "politics", "minister", "mla", "mp", "arrest", "arrested", "police", "court", 
    "protest", "clash", "murder", "theft", "robbery", "accused", "assault", "dmk", "admk", "tvk", 
    "bjp", "congress", "chief minister", "stalin", "scam", "corruption", "council meeting", "councillor",
    "delay", "postponed", "petition"
]

def is_relevant_civic_update(title, description):
    text = (title + " " + description).lower()
    
    # Must not contain political or crime news
    if any(word in text for word in POLITICAL_CRIME_KEYWORDS):
        return False
        
    # Must contain at least one local civic keyword
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
    
    # Ensure constituencies exist
    for c_name in CONSTITUENCIES:
        if not db.query(Constituency).filter(Constituency.name == c_name).first():
            db.add(Constituency(name=c_name))
    db.commit()

    constituencies = db.query(Constituency).all()
    today = datetime.date.today()
    
    # Aggregate entries from multiple queries
    all_entries = {}
    for q in QUERIES:
        url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]: # Grab top 12 from each query to filter later
                if entry.link not in all_entries:
                    all_entries[entry.link] = entry
        except Exception as e:
            print(f"Failed parsing feed for query {q}: {e}")
            
    entries = list(all_entries.values())
    print(f"Aggregated {len(entries)} unique news updates before filtering. Filtering for civic updates...")
    
    for entry in entries:
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
        if not is_relevant_civic_update(title, summary_text):
            continue
        
        # Decode Google News redirect URL (only for relevant items!)
        real_url = link
        try:
            decoded = gnewsdecoder(link)
            if decoded.get("status"):
                real_url = decoded["decoded_url"]
        except Exception as e:
            print(f"Decoder failed for {link}: {e}")
            
        # Try to find a matching constituency in title, else random
        matched_c = next((c for c in constituencies if c.name.lower() in title.lower()), None)
        constituency = matched_c if matched_c else random.choice(constituencies)
        
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
