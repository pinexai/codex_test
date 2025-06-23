from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine, text
import os

app = Flask(__name__, static_folder='static', static_url_path='/')
DB_URL = os.environ.get('JOB_DB_URL', 'sqlite:///jobs.db')
engine = create_engine(DB_URL, echo=False)


def get_jobs(search=None):
    query = text('SELECT company, title, location, link FROM jobs')
    params = {}
    if search:
        query = text('''SELECT company, title, location, link FROM jobs
                        WHERE company LIKE :q OR title LIKE :q
                        ORDER BY timestamp DESC''')
        params['q'] = f'%{search}%'
    else:
        query = text('SELECT company, title, location, link FROM jobs ORDER BY timestamp DESC')
    with engine.connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(company=r[0], title=r[1], location=r[2], link=r[3]) for r in rows]


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/jobs')
def api_jobs():
    q = request.args.get('q', '')
    jobs = get_jobs(q if q else None)
    return jsonify(jobs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
