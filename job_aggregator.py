"""Job aggregation utilities.

Scrapes job listings from known career sites and stores them in a
SQLite database using SQLAlchemy. Jobs are refreshed daily via
APScheduler.
"""

from datetime import datetime
import json
import os
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = os.environ.get("JOB_DB_URL", "sqlite:///jobs.db")
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
JOBS_JSON = os.path.join(STATIC_DIR, "jobs.json")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    link = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('link', name='uix_link'),)

def init_db():
    Base.metadata.create_all(engine)


def _fetch_exampleco():
    """Example scraper for a fictional careers page."""
    url = "https://example.com/careers"
    jobs = []
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select('a[href*="/job/"]'):
            title = a.get_text(strip=True)
            link = a['href']
            if not link.startswith('http'):
                link = url.rstrip('/') + '/' + link.lstrip('/')
            location = ""
            loc = a.find_next(class_='location')
            if loc:
                location = loc.get_text(strip=True)
            jobs.append({
                'company': 'ExampleCo',
                'title': title,
                'location': location,
                'link': link,
            })
    except Exception as exc:
        print(f"Failed to fetch {url}: {exc}")
    return jobs


SCRAPERS = [_fetch_exampleco]


def export_jobs():
    """Write all jobs to a JSON file for static hosting."""
    session = SessionLocal()
    jobs = session.query(Job).order_by(Job.timestamp.desc()).all()
    data = [
        {
            'company': j.company,
            'title': j.title,
            'location': j.location,
            'link': j.link,
        }
        for j in jobs
    ]
    os.makedirs(STATIC_DIR, exist_ok=True)
    with open(JOBS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    session.close()


def fetch_jobs():
    """Run all scrapers and store results."""
    session = SessionLocal()
    for scraper in SCRAPERS:
        for job in scraper():
            exists = session.query(Job).filter_by(link=job['link']).first()
            if exists:
                continue
            session.add(Job(**job))
    session.commit()
    export_jobs()
    session.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_jobs, 'interval', days=1)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--once",
        action="store_true",
        help="Fetch jobs once and exit without running the scheduler",
    )
    args = parser.parse_args()

    init_db()
    fetch_jobs()
    if not args.once:
        start_scheduler()
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            pass
