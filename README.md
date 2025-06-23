# Job Aggregator

This project provides a small but extensible job aggregator that scrapes job
listings from known career pages and exposes them through a REST API. Jobs are
persisted using SQLAlchemy so any database supported by the library can be used.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the job fetcher and web app:

```bash
python job_aggregator.py &
python app.py
```

The aggregator will fetch jobs on startup and then once per day. Set the
`JOB_DB_URL` environment variable to change the database location from the
default `jobs.db` SQLite file.

Open your browser to `http://localhost:5000` to view the React front-end.

### Searching

Use the search box on the page to filter jobs by company name or job title.
