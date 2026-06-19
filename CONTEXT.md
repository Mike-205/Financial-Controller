# 🧠 Project Context — Kuzana AI Financial Controller
> Read this entire file before writing any code. This is the source of truth for the project.

---

## 🎯 What We're Building
An AI Financial Controller for Kenyan SMEs that:
1. Connects to Zoho Books and pulls monthly financial data
2. Uses Claude AI to analyze transactions and flag problems
3. Outputs a plain-language risk report to Google Sheets
4. Notifies the founder and accountant via email
5. Anchors each report immutably on Avalanche C-Chain (audit trail)

---

## 🏆 Why We're Building It
This is a submission for the **Kuzana x MiniHack Builder Bounty Programme — Bounty 1: AI Financial Controller**.

- **Stage 1 deadline:** June 27, 2026
- **Stage 1 deliverable:** 1-minute screen recording of working MVP
- **Stage 2 deadline:** August 28, 2026
- **Prize:** Ksh 20,000 + plaque

Kuzana is Kenya's fastest-growing SME accelerator. They back businesses doing Ksh 400k+/month revenue. The problem they face: founders and investors discover financial issues too late, after the damage is done.

---

## 👤 Target Users
- Kenyan SME founder (messy books, mixing personal + business expenses)
- Their accountant
- Their Kuzana investor

---

## 🚩 MVP Scope (Stage 1 Only — Do NOT expand this)
Focus on ONE specific problem to prove it works:

**Flag when personal and business transactions are mixed.**

Secondary flags (add only if the above is done):
- Duplicate transactions (same amount, same vendor, close dates)
- Round number payments (e.g. exactly Ksh 50,000 to an individual — fraud signal)

Everything else is August (Stage 2) scope. Do not build it now.

---

## 🛠 Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Language | Python 3.11+ | Use throughout |
| Web framework | FastAPI | Lightweight, fast |
| Zoho integration | Zoho Books API v3 | OAuth2 auth |
| AI analysis | Anthropic Claude API | Model: `claude-sonnet-4-6` |
| Report output | Google Sheets API | Via `gspread` library |
| Email notifications | Resend.com API | Free tier |
| Blockchain audit trail | Web3.py + Avalanche Fuji Testnet | EVM-compatible, free testnet |
| Environment variables | python-dotenv | All secrets in `.env` |
| Hosting | Railway.app | Free tier, one-click deploy |

---

## 📁 Project File Structure

```
financial-controller/
├── main.py              # FastAPI app entry point + scheduler
├── zoho_client.py       # Zoho Books OAuth2 + data fetching
├── analyzer.py          # Claude API prompt + analysis logic
├── report.py            # Google Sheets report builder
├── notifier.py          # Email via Resend
├── chain.py             # Avalanche Fuji hash anchoring
├── .env                 # All API keys (never commit this)
├── .env.example         # Template with key names, no values
├── requirements.txt     # All dependencies
└── README.md            # Setup instructions
```

---

## 🔑 Environment Variables Required

```env
# Zoho Books
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REDIRECT_URI=http://localhost:8000/zoho/callback
ZOHO_ORGANIZATION_ID=

# Claude AI
ANTHROPIC_API_KEY=

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_JSON=  # path to service account JSON file
GOOGLE_SHEET_ID=

# Resend (email)
RESEND_API_KEY=
FOUNDER_EMAIL=
ACCOUNTANT_EMAIL=

# Avalanche Fuji Testnet
AVAX_PRIVATE_KEY=          # wallet private key (testnet only, no real money)
AVAX_FUJI_RPC=https://api.avax-test.network/ext/bc/C/rpc
```

---

## 🔄 System Flow (Build in this order)

```
Step 1: Zoho Books API
  → OAuth2 authentication
  → Pull last 30 days of transactions
  → Pull trial balance

Step 2: Claude Analysis
  → Send transactions to Claude
  → Claude flags: mixed personal/business, duplicates, round numbers
  → Returns structured JSON with flagged items + explanation

Step 3: Google Sheets Report
  → Write flagged items to a Google Sheet
  → One row per flag: date, amount, description, flag type, explanation

Step 4: Email Notification
  → Send email to founder + accountant
  → Subject: "⚠️ Financial flags found for [Company] — [Month]"
  → Body: plain language summary of what was found

Step 5: Avalanche Audit Trail (ADD LAST)
  → SHA-256 hash the full report JSON
  → Write hash to Avalanche Fuji C-Chain as a transaction
  → Store the tx hash alongside the report in Google Sheets
```

---

## 🤖 Claude Prompt Template (for analyzer.py)

```python
SYSTEM_PROMPT = """
You are an AI financial controller reviewing books for a Kenyan SME.
Your job is to flag problems in plain language that a non-accountant founder can understand.
You are NOT building a full audit. You are flagging specific, actionable issues.
Always respond in valid JSON only. No explanations outside the JSON.
"""

USER_PROMPT = """
Review these transactions from {company_name} for {month}:

{transactions_json}

Flag any of the following:
1. MIXED_FUNDS: Transactions that look personal (groceries, fuel, personal services, school fees, household items) paid from the business account
2. DUPLICATE: Same amount to same vendor within 7 days
3. ROUND_NUMBER: Exact round amounts (e.g. 50000, 100000) paid to individuals with no invoice reference

Respond ONLY with this JSON structure:
{
  "company": "{company_name}",
  "month": "{month}",
  "total_transactions_reviewed": 0,
  "flags": [
    {
      "type": "MIXED_FUNDS | DUPLICATE | ROUND_NUMBER",
      "date": "YYYY-MM-DD",
      "amount": 0,
      "description": "original transaction description",
      "explanation": "plain English explanation of why this is flagged",
      "action_required": "specific thing the founder should do"
    }
  ],
  "summary": "2-3 sentence plain English summary of overall financial health"
}
"""
```

---

## ⛓ Avalanche Integration (chain.py)

```python
# What this does:
# 1. Takes the full report as a dict
# 2. SHA-256 hashes it
# 3. Sends a 0 AVAX transaction to Fuji testnet with hash in the data field
# 4. Returns the transaction hash (proof of timestamp)

# Libraries needed:
# pip install web3

# Network: Avalanche Fuji C-Chain
# RPC: https://api.avax-test.network/ext/bc/C/rpc
# Chain ID: 43113
# Get free test AVAX from: https://faucet.avax.network/

# The pitch: "Every report is permanently timestamped on Avalanche.
# No one can claim they didn't know — the blockchain proves when the flag was raised."
```

---

## 🧪 Demo Data Setup

Create a free Zoho Books account with a dummy company called **"Mama Fua Enterprises"**.

Add these transactions manually to make the demo interesting:
1. Ksh 3,500 — "Naivas Supermarket" (personal groceries — MIXED_FUNDS flag)
2. Ksh 45,000 — "Supplier XYZ" on March 1st
3. Ksh 45,000 — "Supplier XYZ" on March 3rd (DUPLICATE flag)
4. Ksh 100,000 — "John Kamau" with no description (ROUND_NUMBER flag)
5. Ksh 850 — "Parking fee CBD" (personal — MIXED_FUNDS flag)
6. ~15 normal business transactions (invoices, rent, salaries, utilities)

---

## 📹 Screen Recording Script (1 minute)

```
0:00 — "This is the Kuzana AI Financial Controller"
0:08 — Show Zoho Books dashboard with Mama Fua Enterprises transactions
0:18 — Run the analysis: "Watch as it pulls the data and sends it to Claude"
0:28 — Show Claude returning flagged items
0:38 — Show Google Sheets report populating with flags in real time
0:48 — Show email notification arriving in inbox
0:54 — Show Avalanche Fuji transaction: "This report is now permanently on-chain"
1:00 — Done
```

---

## ✅ Definition of Done (Stage 1)

- [ ] Zoho Books OAuth2 working
- [ ] Transactions pulled successfully from dummy account
- [ ] Claude correctly flags at least 3 different issues
- [ ] Google Sheets report populates automatically
- [ ] Email sent to founder + accountant
- [ ] Avalanche tx hash stored alongside report
- [ ] 1-minute screen recording recorded and ready to submit

---

## ⚠️ What NOT to Build Right Now

- Cash flow scoring → August
- Fraud detection beyond round numbers → August
- Unreconciled accounts checker → August
- Dashboard UI → August
- Multi-company support → August
- Real-time monitoring → August

**One pipeline. One demo. Ship it.**
