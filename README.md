# ⚽ Football Intelligence API – Backend System (Phase 2)

This is the backend system for the **Football Intelligence Project**, a smart assistant built for football club managers, scouts, and analysts. It enables users to:

- Discover trending players based on biometric performance.
- Ask tactical questions like “Who is a good midfielder?”
- Log feedback for insight cards.
- Simulate market value and contract renewals.
- Compare two players head-to-head.

---

## 📦 Project Contents

The project includes:

- A PostgreSQL-backed database with players, biometric data, match stats, contracts, and feedback logs.
- A FastAPI server that provides multiple endpoints for tactical search, chat logging, and comparisons.
- A complete data validation pipeline using Great Expectations.
- Timezone-aware timestamp formatting for global users.

---

## 🚀 Getting Started (Setup from Scratch)

> **No coding knowledge required – just follow the steps below.**

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd FootballProject
```

### 2. Create and activate your virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create the database

```bash
psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS football_db;"
psql -U postgres -d postgres -c "CREATE DATABASE football_db;"
```

### 4. Initialize the database tables

```bash
alembic upgrade head
```

### 5. Populate the database with test data

```bash
python scripts/mock_players.py             # Creates base players
python scripts/mock_biometric_status.py    # Adds injury/suspension and biometric logs
python scripts/seed_match_stats.py         # Adds match stats for Jude Bellingham and Pedri
```

### 6. Start the backend server

```bash
uvicorn main:app --reload
```

Now the API is live at:  
🌐 http://127.0.0.1:8000

---

## 📘 API Overview

| Endpoint | Description |
|----------|-------------|
| `/docs/schema` | View your full ERD schema |
| `/insights` | Returns dummy tactical suggestions for top players |
| `/feedback` | Records user thumbs-up/down feedback |
| `/metrics` | Returns basic usage stats (feedback count, player total, etc.) |
| `/contracts/{player_id}` | Simulates contract value, renewal risk, and confidence |
| `/players/trending` | Finds trending players using sprint and HRV delta |
| `/chat/search` | Smart keyword matcher for football queries (e.g., "good defender") |
| `/chat/prompt` | Logs a user prompt and returns canned AI response |
| `/chat/insight` | Uses prompt+context to return player insights |
| `/chat/ask` | Classifies prompt intent and routes to `/insight`, `/compare`, etc. |
| `/chat/compare` | Compares two players' metrics and picks a winner |

---

## 🧪 Sample Commands

Here are some examples you can run in your terminal using `curl`:

### Search for a Player Type

```bash
curl -X POST http://127.0.0.1:8000/chat/search \
  -H "Content-Type: application/json" \
  -d '{"question": "show me a good midfielder", "user_id": "demo"}'
```

### Generate AI Insight

```bash
curl -X POST http://127.0.0.1:8000/chat/insight \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How did Lena Goeßling perform?", "context": "She played midfield and had 3 key passes."}'
```

### Trending Players

```bash
curl -X POST http://127.0.0.1:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me trending players"}'
```

### Contract Simulation

```bash
curl -X POST http://127.0.0.1:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the contract of Jude Bellingham?"}'
```

### Compare Two Players

```bash
curl -X POST http://127.0.0.1:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Compare Pedri and Bellingham"}'
```

---

## 🌍 Timezone Awareness

All responses include timestamps that respect the user's timezone using this header:

```bash
-H "X-Timezone: Asia/Riyadh"
```

If you skip it, times default to UTC.

---

## ✅ Data Quality Validation

We use [Great Expectations](https://greatexpectations.io/) to validate our data integrity.

### Run validation manually:

```bash
python scripts/validate_table.py players
```

This checks that:
- All player IDs are unique
- Names are not null
- Ages are between 15–45
- Ratings are between 0.0–10.0

Results are stored in the `gx/` folder and can be viewed with:

```bash
great_expectations docs build
open gx/uncommitted/data_docs/local_site/index.html
```

---

## ✅ Phase 2 Wrap-Up

We have successfully implemented the following deliverables:

- ✔️ Database schema finalized (players, contracts, feedback, match stats, logs)
- ✔️ Seed scripts for players, biometrics, match stats
- ✔️ Chat endpoints: search, ask, prompt, insight, comparison
- ✔️ Timestamp formatting with timezone awareness
- ✔️ Feedback logging and `/metrics` reporting
- ✔️ Data validation using Great Expectations
- ✔️ Contract simulation model
- ✔️ Trending player detection using biometric deltas