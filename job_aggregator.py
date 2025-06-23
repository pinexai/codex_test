# Job aggregator script
# Fetch job postings from company career pages and store them in SQLite

import requests
from bs4 import BeautifulSoup
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Configuration: list of company job page URLs
COMPANY_PAGES = {
    'ExampleCo': 'https://example.com/careers',
    # Add more company career page URLs here
}

def init_db(db_path='jobs.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        title TEXT,
        location TEXT,
        link TEXT UNIQUE,
        timestamp DATETIME
    )''')
    conn.commit()
    conn.close()


def fetch_jobs(db_path='jobs.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for company, url in COMPANY_PAGES.items():
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            # This parsing is highly dependent on page structure
            for job_link in soup.select('a[href*="/job/"]'):
                title = job_link.get_text(strip=True)
                link = job_link['href']
                if not link.startswith('http'):
                    link = url.rstrip('/') + '/' + link.lstrip('/')
                location = job_link.find_next(class_='location')
                if location:
                    location = location.get_text(strip=True)
                else:
                    location = ''
                c.execute('INSERT OR IGNORE INTO jobs (company, title, location, link, timestamp) VALUES (?,?,?,?,?)',
                          (company, title, location, link, datetime.utcnow()))
        except Exception as e:
            print(f'Failed to fetch {url}: {e}')
    conn.commit()
    conn.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_jobs, 'interval', days=1)
    scheduler.start()

if __name__ == '__main__':
    init_db()
    fetch_jobs()
    start_scheduler()
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        pass
