Run the full analysis pipeline end to end using mock data.

1. Confirm ZOHO_MOCK=true is set in .env
2. Load transactions from demo_data.py
3. Call analyzer.py — print the raw Claude JSON response
4. Call report.py — confirm rows written to the dev Google Sheet
5. Call notifier.py — confirm email sent
6. Call chain.py — print the Fuji transaction hash

Report what each step returned. Show the exact exception if any step fails.
