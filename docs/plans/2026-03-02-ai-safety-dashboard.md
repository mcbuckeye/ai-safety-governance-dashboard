# AI Safety & Governance Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a unified AI safety governance dashboard with model risk registry, incident tracking, policy compliance, audit trails, alerts, and executive reporting.

**Architecture:** FastAPI backend with SQLAlchemy + Alembic for PostgreSQL, React/Vite/TypeScript frontend with Recharts for visualization. JWT auth with bcrypt. Docker Compose with nginx reverse proxy. All services prefixed `aisafety-*` on shared `dokploy-network`.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, React 18, Vite, TypeScript, Tailwind CSS, Recharts, Docker, nginx

---

## Task 1: Project Scaffolding & Docker Setup

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`
- Create: `frontend/package.json`
- Create: `.gitignore`
- Create: `.env.example`

**What to build:**
- docker-compose.yml with 3 services: `aisafety-backend` (port 8000), `aisafety-frontend` (port 80), `aisafety-db` (PostgreSQL 16)
- All on `dokploy-network` (external: true), NO `container_name`
- Named volume: `aisafety-pgdata` with explicit `name: aisafety-pgdata`
- Traefik labels prefixed `aisafety-` on frontend service for `ai-safety-governance-dashboard.machomelab.com`
- Python healthcheck on backend (no curl): `python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"`
- Backend Dockerfile: python:3.14-slim, install requirements, copy app
- Frontend Dockerfile: multi-stage — node:20-alpine for build, nginx:alpine for serve
- nginx.conf: resolver 127.0.0.11, variable proxy_pass to aisafety-backend:8000 for /api and /health
- Minimal FastAPI app with `/health` endpoint returning `{"status": "healthy"}`
- Backend environment: DATABASE_URL=postgresql://aisafety:aisafety@aisafety-db:5432/aisafety, JWT_SECRET
- Frontend: React + Vite + TypeScript + Tailwind CSS scaffold via `npm create vite@latest`

**Commit:** `feat: project scaffolding with Docker setup`

---

## Task 2: Database Models & Migrations

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial_schema.py`

**What to build:**
- SQLAlchemy models for all 8 tables: users, models, model_risk_categories, incidents, policies, policy_model_mappings, audit_log, alerts
- Use enum types for status fields (mapped to PostgreSQL enums or string columns)
- risk_level computed property on Model based on risk_score
- Alembic setup with initial migration creating all tables
- Database session dependency for FastAPI

**Key details:**
- `audit_log` must be append-only (no update/delete endpoints)
- `models.deleted_at` for soft delete
- `policy_model_mappings` has unique constraint on (policy_id, model_id)
- All timestamps use `func.now()` defaults
- User roles: admin, safety_officer, engineer, viewer

**Commit:** `feat: database models and initial migration`

---

## Task 3: Authentication System

**Files:**
- Create: `backend/app/auth.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/tests/test_auth.py`

**What to build:**
- bcrypt password hashing (import bcrypt directly, NOT passlib)
- JWT token creation with ~10 year expiry
- Login endpoint: `POST /api/auth/login` — returns JWT
- Register endpoint: `POST /api/auth/register` — admin-only in production
- Me endpoint: `GET /api/auth/me` — returns current user
- `get_current_user` dependency extracting user from JWT
- Role-based authorization decorator/dependency

**Tests:**
- Test password hashing/verification
- Test login with valid/invalid credentials
- Test JWT token creation and decoding
- Test /me endpoint with valid token
- Test protected endpoint without token returns 401

**Commit:** `feat: JWT authentication with bcrypt`

---

## Task 4: Model Risk Registry API

**Files:**
- Create: `backend/app/routers/models.py`
- Create: `backend/app/schemas/models.py`
- Create: `backend/tests/test_models.py`

**What to build:**
- Full CRUD for model entries
- Risk score validation (1-10), auto-compute risk_level
- Model risk categories sub-resource (bias, safety, privacy, robustness, fairness scores)
- `POST /api/models/{id}/approve` — transitions status to approved, logs audit
- `GET /api/models/{id}/history` — returns audit entries for this model
- Filter by risk_level, status, team
- Soft delete (set deleted_at, exclude from list queries)
- All mutations create audit_log entries

**Tests:**
- Test CRUD operations
- Test risk level auto-classification
- Test approval workflow
- Test soft delete excludes from list
- Test filters work

**Commit:** `feat: model risk registry API`

---

## Task 5: Incidents API

**Files:**
- Create: `backend/app/routers/incidents.py`
- Create: `backend/app/schemas/incidents.py`
- Create: `backend/tests/test_incidents.py`

**What to build:**
- CRUD for incidents with model linking
- Status workflow: open → investigating → resolved → closed
- `GET /api/incidents/stats` — counts by severity, type, status; trend data
- Filter by type, severity, status, model_id, date range
- Resolution tracking: resolution_notes, resolved_at auto-set on status change
- Audit log entries for all mutations

**Tests:**
- Test CRUD
- Test status transitions
- Test stats aggregation
- Test model linking

**Commit:** `feat: incident tracking API`

---

## Task 6: Policies & Compliance API

**Files:**
- Create: `backend/app/routers/policies.py`
- Create: `backend/app/schemas/policies.py`
- Create: `backend/tests/test_policies.py`

**What to build:**
- CRUD for policies
- `POST /api/policies/{id}/map` — create/update policy-model mapping with compliance status
- `GET /api/compliance/matrix` — returns full matrix of models × policies with status
- Compliance score calculation (% compliant out of total mappings)
- Audit log entries

**Tests:**
- Test CRUD
- Test mapping creation and status updates
- Test compliance matrix structure
- Test compliance score calculation

**Commit:** `feat: policy compliance API`

---

## Task 7: Audit Log & Alerts API

**Files:**
- Create: `backend/app/routers/audit.py`
- Create: `backend/app/routers/alerts.py`
- Create: `backend/app/schemas/audit.py`
- Create: `backend/app/schemas/alerts.py`
- Create: `backend/tests/test_audit.py`
- Create: `backend/tests/test_alerts.py`

**What to build:**
- `GET /api/audit` — filterable by user, action, resource_type, date range. Read-only, no create/update/delete endpoints.
- Audit helper function used by all other routers to log actions
- Alerts CRUD with status workflow: open → acknowledged → resolved
- `POST /api/alerts/trigger-check` — simulates a safety check, creates alerts for models with risk_score > 7
- Alert assignment to users

**Tests:**
- Test audit log filtering
- Test audit entries created by other operations
- Test alert CRUD and status transitions
- Test trigger-check creates appropriate alerts

**Commit:** `feat: audit log and alerts API`

---

## Task 8: Dashboard Summary API & Seed Data

**Files:**
- Create: `backend/app/routers/dashboard.py`
- Create: `backend/app/seed.py`
- Create: `backend/tests/test_dashboard.py`

**What to build:**
- `GET /api/dashboard/summary` — returns:
  - total_models, models_by_risk_level, models_by_status
  - total_incidents, open_incidents, incidents_by_severity, incident_trend (last 30 days)
  - compliance_score, policies_count, non_compliant_count
  - open_alerts, alerts_by_severity
- Seed script: creates admin user, 5 sample models, 3 policies, 10 incidents, mappings, alerts, audit entries
- Run seed on startup if no users exist

**Tests:**
- Test summary returns correct aggregates
- Test with empty DB returns zeros
- Test seed creates expected data

**Commit:** `feat: dashboard summary API and seed data`

---

## Task 9: Frontend — Auth & Layout

**Files:**
- Create: `frontend/src/api/client.ts` — axios instance with JWT interceptor, 401 redirect
- Create: `frontend/src/context/AuthContext.tsx` — synchronous token loading
- Create: `frontend/src/pages/Login.tsx`
- Create: `frontend/src/components/Layout.tsx` — sidebar nav, hamburger on mobile
- Create: `frontend/src/components/PrivateRoute.tsx`
- Create: `frontend/src/App.tsx` — routes
- Modify: `frontend/src/main.tsx`
- Create: `frontend/tailwind.config.js`

**What to build:**
- Axios instance with baseURL `/api`, auth header injection, 401 interceptor (clear token, redirect to /login)
- Auth context loading token synchronously from localStorage (NOT useEffect)
- Login page with email/password form
- Responsive sidebar layout: full sidebar on md+, hamburger menu on mobile
- Nav items: Dashboard, Models, Incidents, Policies, Audit Log, Alerts, Settings
- Private route wrapper checking auth synchronously

**Commit:** `feat: frontend auth and responsive layout`

---

## Task 10: Frontend — Dashboard & Models Pages

**Files:**
- Create: `frontend/src/pages/Dashboard.tsx` — stat cards + charts
- Create: `frontend/src/pages/Models.tsx` — list with filters
- Create: `frontend/src/pages/ModelDetail.tsx` — detail view with risk categories
- Create: `frontend/src/components/RiskBadge.tsx`
- Create: `frontend/src/components/StatCard.tsx`

**What to build:**
- Dashboard: stat cards (total models, open incidents, compliance %, open alerts), risk distribution bar chart (Recharts), incident trend line chart, compliance donut chart
- Models list: table with columns (name, version, team, risk score, risk level badge, status), filter dropdowns, create button
- Model detail: info card, risk category breakdown (radar or bar chart), linked incidents, compliance status, approval button, lifecycle history
- Risk badge component with color coding (green/yellow/orange/red)

**Commit:** `feat: frontend dashboard and models pages`

---

## Task 11: Frontend — Incidents, Policies, Audit, Alerts Pages

**Files:**
- Create: `frontend/src/pages/Incidents.tsx`
- Create: `frontend/src/pages/IncidentDetail.tsx`
- Create: `frontend/src/pages/Policies.tsx`
- Create: `frontend/src/pages/PolicyDetail.tsx` — with compliance matrix
- Create: `frontend/src/pages/AuditLog.tsx`
- Create: `frontend/src/pages/Alerts.tsx`
- Create: `frontend/src/pages/Guide.tsx` — user guide at /guide

**What to build:**
- Incidents: list with filters (severity, type, status), create form, detail with resolution tracking
- Policies: list, create form, detail with model mapping matrix, compliance status toggles
- Audit log: filterable table (user, action, resource, date range), read-only
- Alerts: list with status badges, acknowledge/resolve buttons, trigger check button
- Guide page: usage instructions for each feature

**Commit:** `feat: frontend incidents, policies, audit, alerts pages`

---

## Task 12: Integration Testing & Final Polish

**Files:**
- Create: `backend/tests/conftest.py` — test fixtures with real PostgreSQL
- Modify: `docker-compose.yml` — add test service if needed
- Verify all tests pass in Docker

**What to build:**
- Ensure all backend tests run in Docker against real PostgreSQL (BUILD_RULES #39)
- Verify frontend TypeScript builds cleanly (`npm run build`)
- Test full Docker compose up and health check
- Verify seed data loads and dashboard populates
- Fix any CORS issues
- Final commit with all fixes

**Commit:** `fix: integration testing and polish`

---

## Execution Notes

- Sub-agents use model `sonnet46`
- Tasks 1-2 are sequential (scaffolding first)
- Tasks 3-7 can be partially parallelized (all backend APIs)
- Tasks 9-11 depend on backend being complete
- Task 12 is final integration
- All services prefixed `aisafety-` per BUILD_RULES #37
- No container_name in docker-compose.yml (BUILD_RULES #1)
- Python healthcheck, not curl (BUILD_RULES #17)
- dokploy-network external (BUILD_RULES #36)
