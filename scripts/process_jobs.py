import json
import sqlite3
import hashlib
from datetime import datetime

def main():
    n8n_data = yepcode.context.parameters.n8n
    items = n8n_data.get('items', [])
    jobs = items[0].get('json', {}).get('data', []) if items else []

    conn = sqlite3.connect('/tmp/jobs.db')
    cursor = conn.cursor() 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            tags TEXT,
            url TEXT,
            posted_date TEXT,
            fetched_at TEXT
        )
    """)

    new_jobs = []

    for job in jobs:
        job_id = hashlib.md5(
            (str(job.get('title', '')) +
             str(job.get('company_name', ''))).encode()
        ).hexdigest()

        cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))

        if cursor.fetchone():
            continue

        cursor.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?)", (
            job_id,
            job.get('title', 'N/A'),
            job.get('company_name', 'N/A'),
            job.get('location', 'N/A'),
            json.dumps(job.get('tags', [])),
            job.get('url', ''),
            job.get('created_at', ''),
            datetime.utcnow().isoformat()
        ))

        new_jobs.append(job)

    conn.commit()
    conn.close()

    return {"new_jobs": new_jobs, "count": len(new_jobs)}


