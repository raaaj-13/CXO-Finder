# 🎯 CXO Finder

Find CXO contacts (CEO, CFO, CTO, COO and more) for any company.

## Features
- 100+ pre-loaded real CXO executives from top companies
- SQLite3 database for fast local search
- Web search fallback for companies not in DB
- Search history tracking
- LinkedIn profile links for every contact
- Beautiful dark-mode UI

## Setup & Run

### 1. Install dependencies
```bash
pip install flask requests beautifulsoup4
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

## Project Structure
```
cxo-finder/
├── app.py                  ← Flask app entry point
├── requirements.txt
├── config/
│   └── config.py           ← Settings + 100 CXO names
├── models/
│   └── database.py         ← SQLite3 database logic
├── services/
│   └── cxo_service.py      ← Search logic (DB + Web)
├── routes/
│   └── routes.py           ← URL routes
├── templates/
│   ├── base.html
│   ├── index.html          ← Main search page
│   └── history.html        ← Search history
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/logo.svg
└── data/
    └── cxo_finder.db       ← SQLite3 DB (auto-created)
```

## Companies with CXO Data
Microsoft, Apple, Google, Amazon, Meta, Tesla, NVIDIA, AMD, Intel, IBM,
Cisco, Broadcom, JPMorgan, Bank of America, Citigroup, Wells Fargo,
Goldman Sachs, Morgan Stanley, BlackRock, Salesforce, Oracle, Adobe,
ServiceNow, Snowflake, Anthropic, OpenAI, CrowdStrike, Palo Alto,
VMware, Qualcomm, Uber, Lyft, Airbnb, Shopify, Stripe, Zoom, Box,
Dropbox, Slack, and many more...
