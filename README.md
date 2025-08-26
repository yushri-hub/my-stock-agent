# Stock Agent (Fixed)
This repository is a patched version of the stock watcher agent that includes a few robustness fixes to make it suitable for running in GitHub Actions.

## Quick setup
1. Create a new GitHub repo and upload the files from this project (or push via git).
2. Add these repository secrets (Settings → Secrets and variables → Actions):
   - `GROQ_API_KEY` (optional but recommended)
   - `EMAIL_USER` (your Gmail address)
   - `EMAIL_PASS` (16-character Gmail App Password; requires 2FA)
   - `RECIPIENT_EMAIL` (where reports should be sent)
3. Optionally change `TICKERS` in `src/main.py` or set `TICKERS` env var in Actions.
4. Run the workflow manually (Actions → Daily StockWatcher Run → Run workflow) to test.

## Notes & troubleshooting
- If the job fails during `pip install`, check the action logs for the failing package and try installing locally to reproduce.
- If email fails, make sure 2FA is enabled on Gmail and the `EMAIL_PASS` is an App Password. Consider using a transactional email provider if Gmail blocks the connection.
- The Groq integration is guarded: if `GROQ_API_KEY` is not present, the agent will use short fallback summaries.
