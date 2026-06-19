The analyzer.py prompt is returning unexpected output. Debug it.

1. Print the exact prompt being sent with real transaction data substituted in
2. Print the raw Claude API response before any parsing
3. Identify the issue: malformed JSON / backtick fences / empty flags / missing fields
4. Suggest a prompt wording change — not a code workaround
5. Log the change in docs/prompt-iterations.md
