# Automated Job Market Intelligence System

A fully automated pipeline that fetches daily job listings, processes and deduplicates them using Python, analyzes market trends with Groq LLaMA 3.3, and delivers an AI generated intelligence report to your inbox every morning without any manual effort.

## Motivation

Manually searching job boards every day is repetitive and time consuming. Instead of doing that, I built a system that does it automatically. Every morning I wake up to an email summarizing what's hiring, where, and what skills are in demand and all analyzed by AI.

## Demo

```
Subject: Job Market Report - Thu Mar 05 2026

📈 Top In Demand Roles
  1. Software Engineer
  2. Data Scientist
  3. DevOps Engineer
  4. Product Manager
  5. Frontend Developer

🛠️ Most Requested Skills
  1. Python
  2. React
  3. AWS
  4. Docker
  5. SQL

💻 Remote vs Onsite
  65% of positions are fully remote.

📍 Geographic Hotspots
  Berlin, Frankfurt, Amsterdam, London

📋 Market Summary
  Strong demand for backend and data roles across
  European tech hubs. Python remains the most
  requested skill for the third consecutive week.
```

Delivered automatically every morning. Zero manual work.

## How It Works

```
n8n Schedule Trigger (runs daily at 7AM)
        ↓
HTTP Request → Arbeitnow API (fetch job listings)
        ↓
Code Node → Filter & trim data (Frankfurt/Germany focus)
        ↓
YepCode → Python: deduplicate + save to SQLite database
        ↓
HTTP Request → Groq API (LLaMA 3.3 analyzes trends)
        ↓
Code Node → Format HTML email report
        ↓
Gmail SMTP → Deliver report to inbox
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Workflow Automation | n8n |
| Job Data Source | Arbeitnow API (free, no key required) |
| Data Processing | Python, SQLite, hashlib |
| Cloud Code Execution | YepCode |
| AI Analysis | Groq API — LLaMA 3.3 70B Versatile |
| Report Delivery | Gmail SMTP |
| Data Transformation | JavaScript (n8n Code nodes) |

## Key Features

- **Zero manual effort** — runs on a schedule, fully automated
- **Smart deduplication** — MD5 hashing ensures the same job is never stored twice
- **Location filtering** — currently targeting Frankfurt, Germany job market
- **AI trend analysis** — LLaMA 3.3 identifies patterns across roles, skills, and geography
- **Persistent storage** — SQLite database tracks all jobs over time
- **Free to run** — all APIs and tools used are on free tiers

## Cost

| Service | Cost |
|---------|------|
| Arbeitnow API | Free — no key needed |
| Groq API | Free tier — 30 runs/month easily covered |
| n8n | Free — self-hosted |
| YepCode | Free tier — 200 executions/month |
| Gmail SMTP | Free |
| **Total** | **$0/month** |

## n8n Workflow Nodes

| # | Node | Purpose |
|---|------|---------|
| 1 | Schedule Trigger | Fires daily at 7:00 AM |
| 2 | HTTP Request | Fetches jobs from Arbeitnow API |
| 3 | Code Node (JS) | Filters Frankfurt jobs, limits to 20 |
| 4 | YepCode | Python — deduplicates and saves to SQLite |
| 5 | HTTP Request | Sends data to Groq LLaMA 3.3 for analysis |
| 6 | Code Node (JS) | Formats AI response into HTML report |
| 7 | Gmail SMTP | Delivers report to inbox |

## Python — Deduplication Script

```python
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
            title TEXT, company TEXT,
            location TEXT, tags TEXT,
            url TEXT, posted_date TEXT,
            fetched_at TEXT
        )
    """)

    new_jobs = []
    for job in jobs:
        
        job_id = hashlib.md5(
            (str(job.get('title','')) +
             str(job.get('company_name',''))).encode()
        ).hexdigest()

        cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
        if cursor.fetchone():
            continue  # Already exists — skip

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
```

## Location Filtering

Currently configured for Frankfurt, Germany. To target a different city, update the filter in the JavaScript Code node:

```javascript
const filtered = jobs.filter(job => {
  const location = (job.location || '').toLowerCase();
  return location.includes('frankfurt') ||
         location.includes('germany');
});
```

Just will replace with any city or country we want to track.

## What I Learned

- How to design multi step automated workflows in n8n
- Python deduplication using MD5 hashing for efficient data management
- How to work around platform restrictions (n8n Cloud Python limitations) using YepCode
- Integrating Groq's LLaMA API as a cost free alternative to OpenAI
- Structuring prompts to get consistent JSON output from an LLM
- Combining multiple free tier tools into a production ready pipeline

## Planned Improvements

- Add more job sources — Adzuna, The Muse, RemoteOK
- Weekly summary report with trend comparison vs previous week
- Salary trend tracking and visualization
- Telegram bot delivery as alternative to email
- Streamlit dashboard connected to the SQLite database
- Skills gap analysis comparing job requirements to a resume

## Getting Started

### Requirements
- n8n account (cloud or self-hosted)
- YepCode account — [yepcode.io](https://yepcode.io)
- Groq API key — [console.groq.com](https://console.groq.com)
- Gmail account with App Password enabled

### Setup Steps

1. Import `workflow.json` into n8n instance
2. Add a Groq API key as a Header Auth credential in n8n
3. Add a Gmail App Password as an SMTP credential in n8n
4. Connect YepCode credential to the YepCode nodes
5. Toggle the workflow to **Active**

The system will run automatically on the next scheduled trigger.

## Project Structure

```
automated-job-market-intelligence/
├── workflow.json          # n8n workflow export
├── scripts/
│   └── process_jobs.py    # Python deduplication script (runs in YepCode)
├── sample_output/
│   └── sample_report.html # Example of the daily email report
└── README.md
```

## License

MIT
