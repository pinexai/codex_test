from flask import Flask, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__, static_folder='static', static_url_path='/')
DB_PATH = 'jobs.db'


def get_jobs(search=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if search:
        like = f"%{search}%"
        c.execute('''SELECT company, title, location, link FROM jobs
                     WHERE company LIKE ? OR title LIKE ?
                     ORDER BY timestamp DESC''', (like, like))
    else:
        c.execute('SELECT company, title, location, link FROM jobs ORDER BY timestamp DESC')
    jobs = [dict(company=row[0], title=row[1], location=row[2], link=row[3]) for row in c.fetchall()]
    conn.close()
    return jobs


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
