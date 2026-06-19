# Kuzana AI Financial Controller

> Bounty 1 — Kuzana x MiniHack Builder Programme | Stage 1 deadline: **June 27, 2026**

AI-powered financial flag detection for Kenyan SMEs.
Connects to Zoho Books, flags problems with Claude AI, writes a report to Google Sheets,
sends an email, and anchors the report permanently on Avalanche.

```
Zoho Books → Claude AI → Google Sheets → Email (Resend) → Avalanche Fuji
```

---

## 👋 New here? Start with this section.

Welcome to the team. Before you write a single line of code, read this entire README.
It will save you hours of confusion.

**The golden rule: you own one file. Touch only that file and your test.**

| Branch               | File             | Your job                                          |
| -------------------- | ---------------- | ------------------------------------------------- |
| `feat/zoho`          | `zoho_client.py` | Pull transactions from Zoho Books via OAuth2      |
| `feat/analyzer`      | `analyzer.py`    | Send transactions to Claude, parse the JSON flags |
| `feat/report`        | `report.py`      | Write the flagged items to Google Sheets          |
| `feat/notifier`      | `notifier.py`    | Send the flag report by email via Resend          |
| `feat/chain`         | `chain.py`       | Hash the report and anchor it on Avalanche Fuji   |
| `feat/main-pipeline` | `main.py`        | Wire all 5 modules together (Person 6 goes last)  |

---

## 🖥 Step 1 — Clone the repo and get it running

```bash
# Clone
git clone https://github.com/YOUR_ORG/financial-controller.git
cd financial-controller

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Mac / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up your environment file
cp .env.example .env
```

Now open `.env` in your editor. You only need to fill in the keys for your module
(see the "What you need" section for your module below).
Leave everything else blank — the pipeline won't break during development.

---

## 🚀 Step 2 — Start the server and confirm it works

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser. You should see:

```json
{ "status": "ok", "mock_mode": true }
```

`mock_mode: true` means the pipeline is using demo transactions from `demo_data.py`
instead of calling live Zoho. This is correct — keep it this way during development.

---

## 🌿 Step 3 — Check out your branch

```bash
git checkout feat/zoho        # replace with your branch name
```

Open your assigned file. You'll see a `raise NotImplementedError(...)` where your
code needs to go. Read the comments above it carefully — they explain exactly what
the function must return.

---

## 🧪 Step 4 — Test your module in isolation

Do not wait for Person 6 to integrate everything before you test.
Run your function directly from the terminal.

**Person 1 — zoho_client.py**

```bash
python -c "
import asyncio
from zoho_client import fetch_transactions
txs, company, month = asyncio.run(fetch_transactions())
print(f'{company} | {month} | {len(txs)} transactions')
print(txs[0])
"
```

**Person 2 — analyzer.py**

```bash
python -c "
import asyncio, json
from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH
from analyzer import analyze
result = asyncio.run(analyze(DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH))
print(json.dumps(result, indent=2))
"
```

Expected: 4 flags (2x MIXED_FUNDS, 1x DUPLICATE, 1x ROUND_NUMBER).

**Person 3 — report.py**

```bash
python -c "
import json
with open('tests/fixtures/sample_claude_response.json') as f:
    report = json.load(f)
from report import write_report
write_report(report)
print('Done — check your Google Sheet')
"
```

**Person 4 — notifier.py**

```bash
python -c "
import json
with open('tests/fixtures/sample_claude_response.json') as f:
    report = json.load(f)
from notifier import send_notification
send_notification(report)
print('Done — check your inbox')
"
```

**Person 5 — chain.py**

```bash
python -c "
from chain import anchor_report
tx = anchor_report({'company': 'Mama Fua', 'test': True})
print('Tx hash:', tx)
print('View on explorer: https://testnet.snowtrace.io/tx/' + tx)
"
```

**Person 6 — main.py**

```bash
# Only after at least Person 2's analyzer is merged
curl -X POST http://localhost:8000/run-analysis | python -m json.tool
```

---

## 🏃 Step 5 — Run the tests

```bash
pytest tests/ -v
```

All 10 baseline tests should pass before you write any code.
Add your own tests to `tests/test_{your_module}.py` as you build.

---

## 📬 Step 6 — Submit your work

When your function is working:

```bash
git add zoho_client.py           # only your file
git add tests/test_zoho.py       # and your test if you wrote one
git commit -m "feat(zoho): implement OAuth2 and fetch_transactions"
git push origin feat/zoho
```

Then open a Pull Request on GitHub from your branch into `main`.
Tag Person 6 as the reviewer — they need to merge your work to integrate.

**Commit message format:** `feat(module): what you did`
Examples:

- `feat(analyzer): implement Claude prompt and JSON parsing`
- `fix(chain): add 20% gas buffer to prevent silent failures`
- `docs(zoho): add token refresh gotcha to zoho-api-notes.md`

---

## 🔑 What you need — by module

### Person 1 — Zoho Books (`zoho_client.py`)

**Accounts to create:**

1. Free Zoho Books account → `books.zoho.com` (use the dummy company "Mama Fua Enterprises")
2. Zoho API app → `api-console.zoho.com` → Self Client → get Client ID and Secret

**Keys to add to your `.env`:**

```
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_ORGANIZATION_ID=    # found in Zoho Books → Settings → Organisation Profile
ZOHO_REDIRECT_URI=http://localhost:8000/zoho/callback
ZOHO_MOCK=true           # keep this true until your OAuth flow works
```

**What your function must return:**

```python
# fetch_transactions() must return this tuple:
(
  [
    {
      "date": "2026-05-03",
      "amount": 3500.0,
      "description": "Naivas Supermarket",
      "vendor": "Naivas",
      "reference": ""        # empty string, never None
    },
    # ... more transactions
  ],
  "Mama Fua Enterprises",   # company name string
  "May 2026"                # month label string
)
```

**Add your findings to:** `docs/zoho-api-notes.md`

---

### Person 2 — Claude Analyzer (`analyzer.py`)

**Accounts to create:**

1. Anthropic account → `console.anthropic.com` → API Keys → create one

**Keys to add to your `.env`:**

```
ANTHROPIC_API_KEY=
```

**What your function must return:**

```python
# analyze() must return this dict (matches tests/fixtures/sample_claude_response.json)
{
  "company": "Mama Fua Enterprises",
  "month": "May 2026",
  "total_transactions_reviewed": 15,
  "flags": [
    {
      "type": "MIXED_FUNDS",          # or DUPLICATE or ROUND_NUMBER
      "date": "2026-05-03",
      "amount": 3500,
      "description": "Naivas Supermarket",
      "explanation": "...",
      "action_required": "..."
    }
  ],
  "summary": "Plain English paragraph..."
}
```

**Known gotcha:** Claude sometimes wraps JSON in backticks even when told not to.
The `_strip_json_fences()` function in your file already handles this — don't remove it.

**Log every prompt change in:** `docs/prompt-iterations.md`

---

### Person 3 — Google Sheets (`report.py`)

**Accounts to create:**

1. Google account (you probably have one)
2. Google Cloud Console → New Project → Enable Google Sheets API
3. Create a Service Account → download `credentials.json` → place in project root
4. Create a Google Sheet with two tabs: **"Flags"** and **"Summary"**
5. Share the sheet with the service account email (found inside `credentials.json` as `client_email`)

**Keys to add to your `.env`:**

```
GOOGLE_SHEETS_CREDENTIALS_JSON=credentials.json
GOOGLE_SHEET_ID=                 # the long ID from the sheet URL
SHEET_ENV=dev
```

**Flags tab columns (in this order):**

```
Date | Amount (Ksh) | Vendor | Flag Type | Explanation | Action Required | Tx Hash
```

**Summary tab columns:**

```
Company | Month | Total Transactions | Flags Found | Run Timestamp | Tx Hash
```

**Important:** use `batch_update` not `append_row` in a loop — it's faster and
looks cleaner during the demo screen recording.

---

### Person 4 — Email Notifier (`notifier.py`)

**Accounts to create:**

1. Resend account → `resend.com` → API Keys → create one
2. Free tier lets you send from `onboarding@resend.dev` — no domain needed for the demo

**Keys to add to your `.env`:**

```
RESEND_API_KEY=
FOUNDER_EMAIL=           # where the alert goes (can be your own email for testing)
ACCOUNTANT_EMAIL=        # second recipient (can also be your email for testing)
```

**Email format to produce:**

```
Subject: ⚠️ 4 financial flags found — Mama Fua Enterprises — May 2026

Hi,

We reviewed 15 transactions for May 2026 and found 4 issues.

🔴 MIXED FUNDS (2 flags)
- Ksh 3,500 at Naivas Supermarket on May 3rd
  → Move this to your personal account or reimburse the business.
- Ksh 850 parking fee on May 12th
  → Confirm business purpose. If personal, recode to owner drawings.

🟡 DUPLICATE PAYMENT (1 flag)
- Ksh 45,000 to Supplier XYZ — paid twice (May 1 and May 3)
  → Confirm with supplier whether both payments are valid.

🔴 ROUND NUMBER (1 flag)
- Ksh 100,000 to John Kamau — no invoice reference
  → Obtain a signed invoice before month end.

Summary:
15 transactions reviewed. 4 issues found that need your attention before your
next investor update.

Full report: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID
```

---

### Person 5 — Avalanche Chain (`chain.py`)

**Accounts to create:**

1. Create a **new** EVM wallet — use MetaMask or any wallet. **NEVER use a wallet with real money.**
2. Switch to Avalanche Fuji Testnet (Chain ID: 43113)
3. Get free test AVAX → `faucet.avax.network` (request 2 AVAX — enough for 1,000+ transactions)

**Keys to add to your `.env`:**

```
AVAX_PRIVATE_KEY=        # export from MetaMask — testnet wallet only
AVAX_FUJI_RPC=https://api.avax-test.network/ext/bc/C/rpc
```

**What your function must do:**

1. Take the report dict
2. `json.dumps(report, sort_keys=True)` → deterministic string
3. `hashlib.sha256(...).hexdigest()` → 64-char hex hash
4. Build a Web3 tx: 0 AVAX value, hash in the `data` field, Chain ID 43113
5. Sign with private key, broadcast to Fuji RPC
6. Return the transaction hash string

**Verify your tx:** paste the returned hash at `testnet.snowtrace.io`

**Gas formula (the 20% buffer is not optional):**

```python
gas_limit = int((21000 + len(data_bytes) * 68) * 1.2)
```

---

### Person 6 — Pipeline (`main.py`)

**You go last.** Wait until at least Person 2's `analyzer.py` is merged.

**Your job:**

1. Pull each branch as it's ready: `git fetch --all`
2. Merge into `feat/main-pipeline` one at a time
3. Test after each merge: `curl -X POST http://localhost:8000/run-analysis`
4. Once all 5 are merged, flip `ZOHO_MOCK=false` and test with live Zoho data
5. Record the 1-minute demo

**Merge order (safest):**

```bash
git checkout feat/main-pipeline
git merge origin/feat/analyzer     # core of the demo — merge first
git merge origin/feat/report
git merge origin/feat/notifier
git merge origin/feat/chain
git merge origin/feat/zoho         # last — needs live Zoho account
```

**Your combined `.env`** will have all keys from all 5 modules. Collect them from your
teammates over WhatsApp/Slack DM — never share `.env` files through GitHub.

---

## 🗂 Project structure

```
financial-controller/
├── CLAUDE.md                          ← AI assistant context (read-only)
├── main.py                            ← Person 6
├── zoho_client.py                     ← Person 1
├── analyzer.py                        ← Person 2
├── report.py                          ← Person 3
├── notifier.py                        ← Person 4
├── chain.py                           ← Person 5
├── demo_data.py                       ← Shared — never modify the transaction shape
├── requirements.txt
├── .env.example                       ← Copy to .env, fill in your keys
├── .gitignore                         ← .env is gitignored — never commit it
├── docs/
│   ├── zoho-api-notes.md             ← Person 1 fills in
│   └── prompt-iterations.md          ← Person 2 fills in
├── tests/
│   ├── fixtures/
│   │   └── sample_claude_response.json  ← Real Claude output shape for tests
│   ├── test_analyzer.py
│   └── test_demo_data.py
└── .claude/
    ├── settings.json
    └── commands/
        ├── run-pipeline.md
        ├── fix-analyzer.md
        └── check-zoho-auth.md
```

---

## ⚠️ Rules everyone must follow

1. **Never commit `.env`** — it's gitignored. Share keys over DM only.
2. **Never commit `credentials.json`** — same rule.
3. **Only touch your file** — if you need something from another module, ask that person.
4. **Always keep `ZOHO_MOCK=true`** during development — flip it only for the final demo run.
5. **Test your function in isolation** before asking Person 6 to integrate.
6. **Log your gotchas** in `docs/` — if something took you 2 hours to figure out, write it down.

---

## 📅 Timeline

| Date        | Milestone                                                                             |
| ----------- | ------------------------------------------------------------------------------------- |
| Today       | Everyone clones, checks out their branch, confirms `GET /` returns `{"status": "ok"}` |
| Day 2–3     | Person 2 (analyzer) has working Claude flags on demo data                             |
| Day 3–4     | Persons 1, 3, 4, 5 have their functions working in isolation                          |
| Day 5–6     | Person 6 integrates all modules, runs full pipeline end to end                        |
| Day 7       | Full pipeline runs on live Zoho data. Screen recording done.                          |
| **June 27** | **Stage 1 submission deadline**                                                       |

---

## ❓ Questions

Post in the group chat. Tag the person who owns the relevant file.
If something is broken and you've been stuck for more than 30 minutes, ask — don't disappear.

The goal is one working demo by June 27. Ship it.
