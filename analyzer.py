 # analyzer.py — Claude API prompt + analysis logic
# Owner: Person 2 (feat/analyzer)
#
# Responsibilities:
#   - Build the prompt with transaction data
#   - Call Claude API asynchronously
#   - Parse JSON response (strip backticks first)
#   - Return structured report dict

import os
import json
import re
import anthropic
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the async client with the appropriate environment key
client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
You are an AI financial controller reviewing books for a Kenyan SME.
Flag problems in plain language a non-accountant founder can understand.
You are NOT building a full audit — flag specific, actionable issues only.
Always respond in valid JSON only. No text outside the JSON object.
"""

USER_PROMPT_TEMPLATE = """
Review these transactions from {company_name} for {month}:

{transactions_json}

Flag any of the following:
1. MIXED_FUNDS: Personal expenses (groceries, fuel, school fees, household items,
   parking, personal services) paid from the business account.
   Kenyan personal merchants to flag: Naivas, Carrefour, Quickmart, personal KPLC prepaid.
2. DUPLICATE: Same amount to the same vendor within 7 days.
3. ROUND_NUMBER: Exact round amounts (e.g. 50000, 100000) paid to individuals
   with no invoice reference number.

Respond ONLY with this JSON structure:
{{
  "company": "{company_name}",
  "month": "{month}",
  "total_transactions_reviewed": 0,
  "flags": [
    {{
      "type": "MIXED_FUNDS | DUPLICATE | ROUND_NUMBER",
      "date": "YYYY-MM-DD",
      "amount": 0,
      "description": "original transaction description",
      "explanation": "plain English explanation of why this is flagged",
      "action_required": "specific thing the founder should do"
    }}
  ],
  "summary": "2-3 sentence plain English summary of overall financial health"
}}
"""


def _strip_json_fences(text: str) -> str:
    """Remove ```json ... ``` fences Claude sometimes adds despite instructions."""
    text = text.strip()
    # Safely strip leading markdown code blocks (case-insensitive)
    text = re.sub(r"^