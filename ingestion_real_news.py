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

# Keywords for Civic Infrastructure categories
CIVIC_CATEGORIES = {
    "Water & Drainage": ["drain", "water", "flood", "sew", "canal", "rainwater", "swd"],
    "Roads & Traffic": ["road", "pothole", "pavement", "bridge", "street", "flyover", "highway", "traffic"],
    "Garbage & Sanitation": ["garbage", "waste", "trash", "clean", "dump", "litter", "sanitation", "dustbin"],
    "Electricity & Power": ["light", "power", "electr", "dark", "wire", "cable", "transformer"]
}

# Keywords for Government Social Impact categories
SOCIAL_IMPACT_CATEGORIES = {
    "Public Health & Addiction": ["addiction", "drug", "alcohol", "rehab", "liquor", "tasmac", "substance abuse", "tobacco", "public health"],
    "Road Safety": ["road safety", "helmet", "traffic signal", "speed limit", "accident reduction", "zebra crossing", "pedestrian"],
    "Education Quality": ["school", "education", "smart class", "teacher", "admission", "student", "college", "literacy", "library"],
    "Healthcare Access": ["hospital", "clinic", "healthcare", "medicine", "doctor", "nurse", "treatment", "phc", "medical camp"],
    "Women's Safety & Empowerment": ["women", "girl", "safety", "empowerment", "shg", "self help group", "helpline", "pudhumai penn"],
    "Environment & Water": ["lake", "pollution", "water conservation", "tree", "forest", "greenery", "climate", "wetland", "eco"],
    "Employment & Livelihoods": ["employment", "job", "livelihood", "skill training", "unemployed", "fair", "placement", "startup"],
    "Social Justice & Equality": ["caste", "discrimination", "equality", "social justice", "tribal", "scheduled caste", "dalit", "welfare board"],
    "Urban Planning": ["smart city", "urban planning", "housing board", "metro", "park", "beautification", "town", "corporation layout"],
    "Governance & Transparency": ["corruption", "governance", "transparency", "e-governance", "complaint", "cm helpline", "grievance", "rti"]
}

# Positive action keywords showing betterment
ACTION_KEYWORDS = [
    "scheme", "welfare", "fund", "sanction", "inaugurate", "appoint", "action", "improve", 
    "betterment", "launch", "benefit", "renovate", "construct", "policy", "project", 
    "commission", "distribute", "assist", "free", "announce", "setup", "allocation", "subsid"
]

POLITICAL_CRIME_KEYWORDS = [
    "election", "political campaign", "nomination", "arrest", "arrested", 
    "clash", "murder", "theft", "robbery", "accused", "assault", "dmk", "admk", "tvk", 
    "bjp", "congress", "scam", "corruption case", "corruption charges", "bribe arrest"
]

def classify_update(title, description, url=""):
    text = (title + " " + description + " " + (url or "")).lower()
    
    # Exclude other states/cities to prevent Google News overlaps
    EXCLUDE_KEYWORDS = ["ranchi", "bengaluru", "bangalore", "karnataka", "gurugram", "gurgaon", "haryana", 
                        "noida", "vijayawada", "andhra", "kerala", "delhi", "mumbai", "maharashtra", 
                        "kolkata", "hyderabad", "telangana", "patna", "bihar", "jharkhand", "ranchi"]
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return None, None
        
    if any(word in text for word in POLITICAL_CRIME_KEYWORDS) and "e-governance" not in text and "grievance" not in text:
        return None, None
        
    # 1. Check Civic Infrastructure First
    is_civic = any(word in text for word in [
        "road", "repair", "pothole", "pave", "paving", "lay", "laying", "drain", "stormwater", 
        "sewage", "sewer", "water", "leak", "leakage", "garbage", "waste", "dump", "bin", "trash", 
        "light", "illumination", "park", "playground", "encroachment", "eviction", "demolish", "demolition",
        "widening", "canal", "bridge", "flyover", "subway", "sanitation", "cleaning", "beautification",
        "infrastructure", "renovation", "construction"
    ])
    
    if is_civic:
        for cat_name, keywords in CIVIC_CATEGORIES.items():
            if any(word in text for word in keywords):
                return "civic", cat_name
        return "civic", "General Civic Issues"

    # 2. Check Government Social Impact (Needs positive action keyword)
    has_action = any(word in text for word in ACTION_KEYWORDS)
    if has_action:
        for cat_name, keywords in SOCIAL_IMPACT_CATEGORIES.items():
            if any(word in text for word in keywords):
                return "social_impact", cat_name
                
    return None, None

def get_og_image(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }
        response = requests.get(url, headers=headers, timeout=6, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Try OpenGraph image metadata
        og_image = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'})
        if og_image and og_image.get('content'):
            img_url = og_image['content'].strip()
            return urllib.parse.urljoin(url, img_url)
            
        # 2. Try Twitter image metadata
        twitter_image = soup.find('meta', property='twitter:image') or soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            img_url = twitter_image['content'].strip()
            return urllib.parse.urljoin(url, img_url)
            
        # 3. Try legacy image_src links
        img_src = soup.find('link', rel='image_src')
        if img_src and img_src.get('href'):
            return urllib.parse.urljoin(url, img_src['href'].strip())
            
        # 4. Search inline img elements in page content, filtering out icons, logos, trackers
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src:
                src = src.strip()
                text_to_check = src.lower()
                ignore_keywords = ["logo", "icon", "avatar", "pixel", "ad-", "banner", "spinner", "loader", "sprite", "nav"]
                if any(kw in text_to_check for kw in ignore_keywords):
                    continue
                if any(ext in text_to_check for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    return urllib.parse.urljoin(url, src)
                    
    except Exception as e:
        print(f"Failed to fetch image for {url}: {e}")
        
    # High-quality realistic civic fallbacks when the page blocks access (403/Forbidden)
    fallback_images = [
        "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1590486803833-1c5dc8ddd4c8?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80"
    ]
    return random.choice(fallback_images)

def ingest_real_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Ensure all constituencies exist in DB
    for district, constituencies_list in TN_MAPPING.items():
        for c_name in constituencies_list:
            if not db.query(Constituency).filter(Constituency.name == c_name, Constituency.district == district).first():
                db.add(Constituency(name=c_name, district=district))
    db.commit()
 
    constituencies = db.query(Constituency).all()
    today = datetime.date.today()
    
    all_entries = [] # List of tuples: (entry, district)
    processed_search_keys = set()
    import time
    
    for district_name in TN_MAPPING.keys():
        search_key = "Chennai" if "Chennai" in district_name else district_name
        if search_key in processed_search_keys:
            continue
        processed_search_keys.add(search_key)
        
        # Combined queries to pull both Civic and Social Impact reports
        queries = [
            f"{search_key}+Tamil+Nadu+road+pothole+traffic",
            f"{search_key}+Tamil+Nadu+garbage+waste+water+drainage",
            f"{search_key}+Tamil+Nadu+scheme+welfare+health+education",
            f"{search_key}+Tamil+Nadu+safety+environment+employment+governance"
        ]
        
        for q in queries:
            url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                feed = feedparser.parse(url)
                # Parse top 3 articles per query
                for entry in feed.entries[:3]:
                    all_entries.append((entry, district_name))
                time.sleep(0.05) # Prevent rate-limiting
            except Exception as e:
                print(f"Failed parsing feed for query {q}: {e}")
            
    print(f"Aggregated {len(all_entries)} potential news updates before filtering. Filtering and classifying...")
    
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
 
        # Classification & Filtering
        up_type, up_cat = classify_update(title, summary_text, link)
        if not up_type:
            continue
        
        # Decode Google News redirect URL
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
        
        # Scrape description
        description = ""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            response = requests.get(real_url, headers=headers, timeout=5, allow_redirects=True)
            page_soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = [p.get_text().strip() for p in page_soup.find_all('p') if len(p.get_text().strip()) > 50]
            if paragraphs:
                description = "\n\n".join(paragraphs[:3])
        except Exception as e:
            print(f"Failed to scrape body for {real_url}: {e}")
            
        if not description:
            description = summary_text
            if len(description) > 300:
                description = description[:300] + "..."
        
        # Parse published date
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
            article_url=real_url,
            type=up_type,
            category=up_cat
        )
        db.add(update)
    
    db.commit()
    db.close()
    print("Real news ingested successfully.")

if __name__ == "__main__":
    ingest_real_data()
