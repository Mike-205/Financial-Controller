# Kuzana AI Financial Controller

AI-powered financial flag detection for Kenyan SMEs.
Bounty 1 — Kuzana x MiniHack Builder Programme.

## Pipeline
```
Zoho Books → Claude AI → Google Sheets → Email (Resend) → Avalanche Fuji
```

## Quick start

```bash
git clone <repo-url>
cd financial-controller
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn main:app --reload
# POST http://localhost:8000/run-analysis
```

With `ZOHO_MOCK=true` (default) the pipeline runs entirely on demo data — no external accounts needed.

## Team branches
| Branch | File | Owner |
|---|---|---|
| feat/zoho | zoho_client.py | Person 1 |
| feat/analyzer | analyzer.py | Person 2 |
| feat/report | report.py | Person 3 |
| feat/notifier | notifier.py | Person 4 |
| feat/chain | chain.py | Person 5 |
| feat/main-pipeline | main.py | Person 6 |

## Running tests
```bash
pytest tests/ -v
```

## Stage 1 deadline: June 27, 2026
