# Production Security Implementation Document for Resume Enhancer

**Role:** Security Architect
**Target Audience:** Claude Code (Implementation Agent)
**Version:** 1.0

This document defines the mandatory security implementation for the Resume Enhancer application. Implementation must follow these specifications strictly using the defined technology stack (FastAPI, React/Vite, PostgreSQL/SQLAlchemy).

## 1. Security Architecture Overview

### Threat Model
*   **Primary Assets:** User resumes (PII), Auth Tokens, API Keys (Anthropic), User Accounts.
*   **Primary Threats:** Unauthorized access to resumes, Prompt Injection, API Abuse (Cost Denial of Service), Data Leakage via AI logs.

### Trust Boundaries
1.  **Frontend (Untrusted):** Mobile/Web clients.
2.  **API Gateway/Load Balancer:** TLS Termination.
3.  **Backend API (Trusted):** FastAPI application executing business logic.
4.  **Database (Trusted):** PostgreSQL storage.
5.  **External AI (Semi-Trusted):** Anthropic API (Data leaves our boundary).

### Key Security Goals
1.  **Confidentiality:** Users must only access their own resumes.
2.  **Integrity:** AI enhancements must not be tampered with by third parties.
3.  **Availability:** Prevent API abuse and cost spikes via rate limiting.

---

## 2. Authentication & Session Security

**Technology:** `python-jose` (JWT), `passlib` (Bcrypt)

### Implementation Requirements
1.  **Password Storage:**
    *   Use `passlib` with `bcrypt` scheme.
    *   Enforce minimum password length of 12 characters.
    *   **Do not** implement complexity requirements (allow passphrases).
2.  **Session Management (JWT):**
    *   Implement **Stateless JWT** for API authentication.
    *   **Access Token:** Short-lived (15-30 minutes). Include `sub` (user_id), `exp`, `iat`, `scope`.
    *   **Refresh Token:** Long-lived (7 days), stored in **HttpOnly, Secure, SameSite=Strict** cookie.
    *   **Token Rotation:** Issue new Access Token upon Refresh Token usage.
    *   **Revocation:** Implement a "UserVersion" column in DB. Encode this version in JWT. On password change/logout, increment DB version to invalidate all active JWTs.
3.  **MFA:**
    *   Prepare database schema for TOTP (Time-based One-Time Password) secret storage (encrypted).

---

## 3. Authorization & Access Control

**Pattern:** Role-Based Access Control (RBAC) + Resource Ownership

### Implementation Requirements
1.  **Resource Ownership Middleware:**
    *   Create a FastAPI Dependency `get_current_user`.
    *   For **ALL** `/api/resumes/{id}` endpoints, strictly enforce `resume.owner_id == current_user.id`.
    *   Return `404 Not Found` (not 403) for unauthorized access to prevent ID enumeration.
2.  **User Isolation:**
    *   Ensure file storage paths include user UUIDs: `uploads/{user_id}/{file_uuid}.pdf`.
    *   Verify `user_id` matches the token `sub` for every file access.
3.  **Admin Privileges:**
    *   Add `role` column to `users` table default `user`.
    *   Protect admin routes with `RequiresRole("admin")` dependency.

---

## 4. Data Protection

### Implementation Requirements
1.  **Encryption at Rest:**
    *   **Database:** Use volume-level encryption (e.g., AWS EBS encryption or PG data encryption) if cloud-managed.
    *   **Sensitive Columns:** If storing API Keys or OAuth tokens, use `fernet` (cryptography lib) to encrypt specific columns.
2.  **Encryption in Transit:**
    *   Enforce TLS 1.2+ for all connections.
    *   Set `Strict-Transport-Security` (HSTS) header in Nginx/FastAPI middleware (max-age=31536000).
3.  **Resume File Handling:**
    *   Process resumes in memory where possible.
    *   If using disk buffers, clean up immediately after processing via `tempfile` module patterns.
    *   For permanent storage (S3/Blob), ensure buckets are **private**. Generate **Presigned URLs** for frontend access (never proxy file content through API if possible).
4.  **Data Retention:**
    *   Implement a "Hard Delete" endpoint that cascades deletions to all resumes, extracted text, and generated files.

---

## 5. AI-Specific Security

**Threat:** Prompt Injection & Leakage

### Implementation Requirements
1.  **Prompt Separation:**
    *   Use Anthropic's `system` parameter for all structural instructions.
    *   **Never** concatenate user input directly into the `system` prompt.
    *   Wrap user content in XML tags (e.g., `<user_resume>`, `<job_description>`) to strictly demarcate input.
2.  **Sanitization:**
    *   Strip "System instruction" like keywords from user resumes before processing (e.g., "Ignore previous instructions").
3.  **Output Validation:**
    *   Validate AI response structure against Pydantic models (Structural adherence).
    *   Check for potential PII leakage (e.g., ensuring the AI didn't hallucinate someone else's data, though unlikely with direct context).

---

## 6. API & Backend Security

**Technology:** FastAPI, `slowapi`

### Implementation Requirements
1.  **Rate Limiting (`slowapi`):**
    *   **Auth Routes:** Strict limit (e.g., 5/minute) on login/register to prevent brute force.
    *   **AI Routes:** Cost-based limit (e.g., 10 enhancements/hour/user).
    *   **Global:** Fallback limit (e.g., 60/minute) for general API.
2.  **Input Validation:**
    *   Use Pydantic models for **ALL** POST/PUT bodies.
    *   Enforce strict type checking and string length constraints (e.g., `resume_text: str = Field(..., max_length=50000)`).
3.  **Error Handling:**
    *   Override default 500 handler. Return generic messages ("Internal Server Error").
    *   **Never** leak stack traces or SQL exceptions to the client.
    *   Log full details internally with correlation IDs.

---

## 7. Secrets & Configuration Management

**Technology:** `pydantic-settings`

### Implementation Requirements
1.  **Environment Variables:**
    *   Load all config via `pydantic-settings`.
    *   Required secrets: `DATABASE_URL`, `SECRET_KEY`, `ANTHROPIC_API_KEY`.
    *   Fail startup if any secret is missing.
2.  **Storage:**
    *   Local: `.env` file (gitignored).
    *   Production: Inject via container orchestration (Docker Secrets/K8s Secrets).
3.  **Key Rotation:**
    *   Design `SECRET_KEY` usage to allow rotation (e.g., support validating against list of keys, though single key is acceptable for MVP if rotation procedure is documented).

---

## 8. Logging, Monitoring & Auditing

### Implementation Requirements
1.  **Structured Logging:**
    *   Use Python `logging` with JSON formatter (production) or readable (dev).
    *   Log format: `{"timestamp": "...", "level": "...", "correlation_id": "...", "msg": "..."}`.
2.  **Privacy in Logs:**
    *   **REDACT** the following before logging:
        *   `password`, `token`, `access_token` fields.
        *   Resume text content (too large and contains PII).
        *   Raw AI prompt inputs/outputs.
3.  **Audit Trail:**
    *   Log security events: Login success/fail, Password change, Admin actions.

---

## 9. Compliance & Privacy Considerations

### Implementation Requirements
1.  **Data Minimization:**
    *   Only store extracted text required for current enhancement context.
2.  **Constraint of Processing:**
    *   Do not use user data for model training (Anthropic default is generally safe, but ensure API settings confirm this).
3.  **Consent:**
    *   Add terms of service acceptance checkbox on Registration.
    *   Clearly state "Data is processed by Anthropic AI".

---

## 10. Production Hardening Checklist

### Actionable Setup for Deployment
1.  [ ] **Disable Debug Mode:** Ensure `FASTAPI_DEBUG=False` in environment.
2.  [ ] **CORS Policy:** Restrict `Allow-Origins` to exact frontend domain (no `*`).
3.  [ ] **Database User:** App should connect as a non-superuser.
4.  [ ] **Filesystem:** Run Docker container as non-root user.
5.  [ ] **Security Headers:** Add Middleware for:
    *   `X-Content-Type-Options: nosniff`
    *   `X-Frame-Options: DENY`
    *   `Content-Security-Policy` (Restrict scripts to self).
6.  [ ] **Dependency Scan:** Run `safety check` or `pip-audit` on `requirements.txt`.
