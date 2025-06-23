# Job Aggregator

This project provides a simple job aggregator that collects job postings from
specified company career pages, stores them in a local SQLite database and
serves them via a small Flask web application.

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

The aggregator will fetch jobs on startup and then once per day.

Open your browser to `http://localhost:5000` to view the React front-end.

### Searching

Use the search box on the page to filter jobs by company name or job title.
