Test whether the Zoho OAuth2 flow is working.

1. Check ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_ORGANIZATION_ID are in .env
2. Check if zoho_tokens.json exists and has a refresh_token
3. If yes: attempt token refresh and print success or exact error
4. If no: print the full authorization URL to open in a browser
5. Diagnose only — do not write any code
