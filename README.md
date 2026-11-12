# UniFi OS Server – user flow tests

Automated tests for a self-hosted **UniFi OS Server** covering one scenario in two ways:

1. Log in as the admin (UI account with MFA)
2. Create a new local user
3. Log out
4. Log in as the new local user

| Test | Technology | File |
|---|---|---|
| REST API | pytest + requests | `tests/api/test_user_flow_api.py` |
| End-to-end | pytest + Playwright (Chromium) | `tests/e2e/test_user_flow_e2e.py` |

## Prerequisites

- Python 3.11+
- UniFi OS Server 5.x running locally (default console: `https://localhost:11443`) and set up with a UI account.
- The UI account must use an **authenticator app (TOTP)** for MFA. Email codes and passkeys cannot be automated.
  Keep the Base32 secret shown next to the QR code when enabling it.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
Copy-Item .env.example .env
```

Edit `.env` (never commit it):

| Variable | Meaning |
|---|---|
| `UNIFI_BASE_URL` | Console URL, default `https://localhost:11443` |
| `UNIFI_ADMIN_USERNAME` | UI account email or local admin username |
| `UNIFI_ADMIN_PASSWORD` | Its password |
| `UNIFI_ADMIN_TOTP_SECRET` | Base32 TOTP secret (empty if MFA is off) |
| `UNIFI_LOCAL_USER_PASSWORD` | Password for the throwaway local users the tests create |

## Running

```powershell
python -m pytest                 # everything
python -m pytest -m api          # REST API test only
python -m pytest -m e2e          # browser test only
python -m pytest -m e2e --headed # watch the browser
```

## Reports and failures

- HTML report: `reports/report.html` (self-contained)
- On failure Playwright keeps a screenshot and a trace in `test-results/`.
  Open a trace with `python -m playwright show-trace test-results/<test>/trace.zip`.
- Assertion messages include the HTTP status and response body.
- Reports and traces may contain account data. Review them before sharing.

## CI: self-hosted runner in Docker (manual trigger)

The workflow `.github/workflows/unifi-tests.yml` runs only on demand (Actions → *UniFi tests* → *Run workflow*).
Job `api` (pytest + requests) runs first, then job `e2e` (Playwright). Each uploads its reports
(`api.html`/`api.xml`, `e2e.html`/`e2e.xml`, plus screenshots/traces on failure) as artifacts.

1. Install Docker Engine inside WSL2 Ubuntu and start it. Start the UniFi server too.
2. Add these repository secrets: `UNIFI_ADMIN_USERNAME`, `UNIFI_ADMIN_PASSWORD`,
   `UNIFI_ADMIN_TOTP_SECRET`, `UNIFI_LOCAL_USER_PASSWORD`.
3. `cd runner`, copy `.env.example` to `.env`, fill in `REPO_URL` and a fresh `RUNNER_TOKEN`
   (Settings → Actions → Runners → New self-hosted runner), then `docker compose up -d --build`.
4. The container reaches UniFi at `https://host.docker.internal:11443` (`host-gateway` mapping in the compose file).

Security: the workflow has no `pull_request` trigger. For a public repository also set
Settings → Actions → General → *Require approval for all outside collaborators*.

## Design notes

- `unifi_tests/api_client.py` – thin REST client (login, roles, create/list/delete user, logout).
- `unifi_tests/pages.py` – Playwright page objects (`LoginPage`, `AdminsPage`, `Navigation`).
- `unifi_tests/config.py` – settings from `.env`; secrets are hidden from `repr`, so they don't show up in tracebacks.
- `tests/conftest.py` – shared fixtures: `settings`, `new_user` (unique credentials per run) and `user_cleanup`, which deletes created users even when a test fails.
- A TOTP code can only be used once. `Settings.admin_otp()` waits for the next 30-second window when needed, so the login in a test and the login in cleanup never reuse a code. A full run can therefore take up to ~30 s longer.
- The server uses a self-signed certificate, so certificate verification is disabled for localhost.
- Local users are created as administrators with the **Super Admin** role. The console only offers local credentials for admins.
- Deleting an active admin is refused by the server, so the client deactivates the user first.
