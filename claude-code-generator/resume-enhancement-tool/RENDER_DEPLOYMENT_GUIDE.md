# Render.com Deployment Guide

This guide details how to deploy the **Resume Enhancement Tool** to Render.com using the Infrastructure-as-Code Blueprint (`render.yaml`).

## 1. Prerequisites

1.  **GitHub Repository:** Ensure your code is pushed to a GitHub repository.
2.  **Render Account:** Sign up at [dashboard.render.com](https://dashboard.render.com).
3.  **API Keys:** have your `ANTHROPIC_API_KEY` ready.

## 2. Setup "Blueprints"

1.  Go to the [Render Dashboard](https://dashboard.render.com).
2.  Click **New +** -> **Blueprint**.
3.  Connect your GitHub repository.
4.  Render will automatically detect `render.yaml` in the root.
5.  **Service Name:** Enter a name (e.g., `resume-enhancer-prod`).
6.  **Branch:** Select `main` (or your production branch).

## 3. Configure Environment Variables

During the Blueprint setup, Render may prompt for sensitive variables that are NOT in `render.yaml`. If not, or for future updates:

1.  Finish the Blueprint creation. It might fail initially if keys are missing.
2.  Go to **Dashboard** -> **resume-enhancer-backend** -> **Environment**.
3.  Add the following Variable:
    *   `ANTHROPIC_API_KEY`: starts with `sk-ant...`
    *   `AUTH_SECRET_KEY`: (If you chose to manually set it, otherwise `render.yaml` generates a `SECRET_KEY` automatically).
    *   **CHECK:** Ensure `DEBUG` is set to `False` (It is not explicitly set in yaml, so backend defaults to whatever is in code. Recommendation: Add `DEBUG=False`).

## 4. Verify Services

You should see 4 resources created:
1.  **resume-enhancer-db:** PostgreSQL Database.
2.  **resume-enhancer-redis:** Redis instance (For Rate Limiting).
3.  **resume-enhancer-backend:** Python Web Service.
4.  **resume-enhancer-frontend:** Static Site.

## 5. First Run & Database Migration

The backend `startCommand` is configured to run `./start.sh`.
*   This script automatically runs `alembic upgrade head` on every deploy.
*   **Action:** Check the Logs of the `resume-enhancer-backend` service.
*   **Look for:** `INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.` -> `Running upgrade -> ...`

## 6. Access the Application

1.  Go to **resume-enhancer-frontend** service.
2.  Click the URL (e.g., `https://resume-enhancer-frontend-xxxx.onrender.com`).
3.  **Verify:**
    *   Sign Up / Login works.
    *   Upload a Resume actions work.
    *   "Enhance" triggers the AI (Check backend logs for activity).

## Troubleshooting

### "Missing dependencies"
If the build fails, check logs. Ensure `requirements.txt` is in the `backend/` directory.

### "Internal Server Error" (500)
*   Check Backend Logs.
*   Common cause: `DATABASE_URL` not linked correctly (Blueprint handles this).
*   Common cause: `ANTHROPIC_API_KEY` missing.

### "Rate Limit Exceeded"
*   If redis fails to connect, the application might fallback or fail depending on `slowapi` config. Check `REDIS_URL` env var is present in backend.
