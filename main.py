import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="Pastorate Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Models =====
class Leader(BaseModel):
    name: str
    role: str
    photo: Optional[HttpUrl] = None


class NewsItem(BaseModel):
    id: int
    title: str
    excerpt: str
    date: str
    url: HttpUrl


class GalleryImage(BaseModel):
    src: HttpUrl
    alt: str


class Location(BaseModel):
    slug: str
    name: str
    address: str
    service_times: List[str]
    phone: Optional[str] = None
    email: Optional[str] = None
    hero_tagline: Optional[str] = None


class LocationDetail(BaseModel):
    location: Location
    leadership: List[Leader]
    news: List[NewsItem]
    gallery: List[GalleryImage]


# ===== Demo Data (placeholder for WordPress) =====
LOCATIONS: List[Location] = [
    Location(
        slug="central-campus",
        name="Central Congregation",
        address="100 Main St, Cityville",
        service_times=["Sundays 9:00 AM", "Sundays 11:00 AM"],
        phone="(555) 123-0001",
        email="central@example.org",
        hero_tagline="A welcoming community in the heart of the city.",
    ),
    Location(slug="north-campus", name="North Congregation", address="200 North Rd", service_times=["Sundays 10:00 AM"], phone="(555) 123-0002", email="north@example.org", hero_tagline="Growing together in faith."),
    Location(slug="south-campus", name="South Congregation", address="300 South Ave", service_times=["Sundays 10:30 AM"], phone="(555) 123-0003", email="south@example.org", hero_tagline="Serving with joy."),
    Location(slug="east-campus", name="East Congregation", address="400 East Blvd", service_times=["Sundays 9:30 AM"], phone="(555) 123-0004", email="east@example.org", hero_tagline="Hope for every home."),
    Location(slug="west-campus", name="West Congregation", address="500 West Way", service_times=["Sundays 11:15 AM"], phone="(555) 123-0005", email="west@example.org", hero_tagline="Rooted and reaching."),
    Location(slug="riverside-campus", name="Riverside Congregation", address="600 River Rd", service_times=["Sundays 9:00 AM"], phone="(555) 123-0006", email="riverside@example.org", hero_tagline="Life by the water."),
    Location(slug="hillside-campus", name="Hillside Congregation", address="700 Hill St", service_times=["Sundays 10:00 AM"], phone="(555) 123-0007", email="hillside@example.org", hero_tagline="Lifted by grace."),
]


DEMO_LEADERS = [
    Leader(name="Alex Morgan", role="Lead Pastor", photo="https://images.unsplash.com/photo-1544006659-f0b21884ce1d?q=80&w=800&auto=format&fit=crop"),
    Leader(name="Jordan Lee", role="Associate Pastor", photo="https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=800&auto=format&fit=crop"),
    Leader(name="Taylor Kim", role="Worship Director", photo="https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=800&auto=format&fit=crop"),
    Leader(name="Riley Chen", role="Next Gen Lead", photo="https://images.unsplash.com/photo-1544006658-85f8d80b2983?q=80&w=800&auto=format&fit=crop"),
]

DEMO_NEWS = [
    NewsItem(id=1, title="Pastorate Vision Night", excerpt="Join us as we share the vision for the coming year.", date="2025-01-15", url="https://example.org/news/vision-night"),
    NewsItem(id=2, title="Community Serve Day", excerpt="City-wide outreach across all locations.", date="2025-02-01", url="https://example.org/news/serve-day"),
]

DEMO_GALLERY = [
    GalleryImage(src="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200&auto=format&fit=crop", alt="Gathering"),
    GalleryImage(src="https://images.unsplash.com/photo-1520975682031-a3ee3e3c7b80?q=80&w=1200&auto=format&fit=crop", alt="Worship"),
    GalleryImage(src="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=1200&auto=format&fit=crop", alt="Community"),
]


# ===== Routes =====
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/locations", response_model=List[Location])
def list_locations():
    return LOCATIONS


@app.get("/api/location/{slug}", response_model=LocationDetail)
def get_location(slug: str):
    loc = next((l for l in LOCATIONS if l.slug == slug), None)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    # In production, fetch leadership/news/gallery from the respective WordPress site
    return LocationDetail(location=loc, leadership=DEMO_LEADERS, news=DEMO_NEWS, gallery=DEMO_GALLERY)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
