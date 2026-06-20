# analyzer.py — Claude API prompt + analysis logic
# Owner: Person 2 (feat/analyzer)
#
# Responsibilities:
#   - Build the prompt with transaction data
#   - Call Claude claude-sonnet-4-6 API
#   - Parse JSON response (strip backticks first — Claude sometimes adds them)
#   - Return structured report dict
#
# GOTCHA: Claude occasionally wraps JSON in ```json ... ```.
#         Always strip before json.loads() or you'll get a parse error.

import os, json, re
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

_client = None


def _get_client() -> "anthropic.AsyncAnthropic":
    """Lazily build the async client so importing this module never requires
    an API key (keeps unit tests import-safe; they mock this out)."""
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client

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

Respond ONLY with this JSON:
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
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


async def analyze(transactions: list, company_name: str, month: str) -> dict:
    """Send transactions to Claude and return structured flag report."""
    prompt = USER_PROMPT_TEMPLATE.format(
        company_name=company_name,
        month=month,
        transactions_json=json.dumps(transactions, indent=2),
    )

    response = await _get_client().messages.create(
        model=MODEL,
        max_tokens=2000,  # 4 flags + explanations can exceed the original 1000
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    # GOTCHA: Claude sometimes wraps JSON in ```json ... ``` despite the
    # system prompt. Strip fences before json.loads() or it raises.
    raw = _strip_json_fences(response.content[0].text)
    return json.loads(raw)
