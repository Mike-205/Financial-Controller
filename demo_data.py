# demo_data.py — Mama Fua Enterprises demo transactions
# Used when ZOHO_MOCK=true. Never delete or modify transaction shapes —
# the rest of the pipeline depends on this exact structure.

COMPANY_NAME = "Mama Fua Enterprises"
REPORT_MONTH = "May 2026"

DEMO_TRANSACTIONS = [
    # ── Should trigger MIXED_FUNDS ─────────────────────────────────
    {"date": "2026-05-03", "amount": 3500,   "description": "Naivas Supermarket",     "vendor": "Naivas",        "reference": ""},
    {"date": "2026-05-12", "amount": 850,    "description": "Parking fee CBD",        "vendor": "Parking",       "reference": ""},

    # ── Should trigger DUPLICATE ───────────────────────────────────
    {"date": "2026-05-01", "amount": 45000,  "description": "Supplier XYZ Invoice",   "vendor": "Supplier XYZ",  "reference": "INV-001"},
    {"date": "2026-05-03", "amount": 45000,  "description": "Supplier XYZ Invoice",   "vendor": "Supplier XYZ",  "reference": ""},

    # ── Should trigger ROUND_NUMBER ────────────────────────────────
    {"date": "2026-05-07", "amount": 100000, "description": "John Kamau",             "vendor": "John Kamau",    "reference": ""},

    # ── Normal business transactions (no flags expected) ───────────
    {"date": "2026-05-02", "amount": 85000,  "description": "May Rent - Office",      "vendor": "Landlord Ltd",  "reference": "RENT-05"},
    {"date": "2026-05-05", "amount": 120000, "description": "Staff Salaries May",     "vendor": "Payroll",       "reference": "PAY-05"},
    {"date": "2026-05-08", "amount": 12000,  "description": "Electricity KPLC",       "vendor": "KPLC",          "reference": "KPLC-8821"},
    {"date": "2026-05-10", "amount": 5500,   "description": "Internet - Safaricom",   "vendor": "Safaricom",     "reference": "SAF-991"},
    {"date": "2026-05-15", "amount": 32000,  "description": "Raw Materials Jua Kali", "vendor": "Jua Kali Sup",  "reference": "JK-203"},
    {"date": "2026-05-18", "amount": 8000,   "description": "Printer Paper & Ink",    "vendor": "Office Mart",   "reference": "OM-441"},
    {"date": "2026-05-20", "amount": 15000,  "description": "Delivery - DHL Kenya",   "vendor": "DHL",           "reference": "DHL-7721"},
    {"date": "2026-05-22", "amount": 3200,   "description": "Water Bill NBI Water",   "vendor": "Nairobi Water", "reference": "NW-5530"},
    {"date": "2026-05-24", "amount": 45000,  "description": "Client Invoice Payment", "vendor": "ABC Client",    "reference": "INV-REC-88"},
    {"date": "2026-05-28", "amount": 6700,   "description": "Airtime - Staff Phones", "vendor": "Safaricom",     "reference": "AIR-05"},
]
