# PRD: AI Safety & Governance Dashboard

## Overview
A unified dashboard for research institutions and enterprises to monitor, govern, and audit their AI deployments. Provides centralized safety oversight including model risk scoring, incident tracking, policy compliance mapping, audit trails, and executive reporting.

## Problem
Organizations deploying AI lack centralized safety/governance oversight. Safety teams exist but use fragmented, ad-hoc tools. No unified SaaS solution exists for AI safety governance.

## Target Users
- AI Safety Officers / Governance leads
- ML Engineers registering and monitoring models
- Compliance teams mapping models to regulatory policies
- Executives needing compliance posture summaries

## Tech Stack
- **Backend:** FastAPI (Python 3.14)
- **Frontend:** React + Vite + TypeScript
- **Database:** PostgreSQL 16
- **Auth:** JWT + bcrypt (steve@ipwatcher.com / 5678*Stud)
- **Container:** Docker Compose on Dokploy
- **DNS:** ai-safety-governance-dashboard.machomelab.com

## Features (MVP)

### 1. Authentication & User Management
- JWT login with bcrypt password hashing
- Token expiry ~10 years (per BUILD_RULES 13b)
- Synchronous auth token loading in route guards (per BUILD_RULES 13c)
- 401 auto-redirect to /login (per BUILD_RULES 40)
- User roles: admin, safety_officer, engineer, viewer

### 2. Model Risk Registry
- CRUD for AI model entries (name, version, description, team, deployment status)
- Risk score (1-10) with category breakdown: bias, safety, privacy, robustness, fairness
- Risk level auto-classification: Low (1-3), Medium (4-6), High (7-8), Critical (9-10)
- Filter/sort by risk level, team, deployment status
- Model lifecycle tracking: draft → review → approved → deployed → retired

### 3. Incident Tracking
- Log safety events: type (bias detection, safety violation, near-miss, drift alert, privacy breach)
- Severity levels: info, low, medium, high, critical
- Link incidents to specific models
- Timeline view of incidents
- Resolution tracking with notes and assignee

### 4. Policy Compliance Dashboard
- Define governance policies (name, description, requirements, applicable model types)
- Map models to policies (many-to-many)
- Compliance status per model-policy pair: compliant, non-compliant, pending_review, exempt
- Overall compliance score (percentage of compliant mappings)
- Visual compliance matrix: models × policies

### 5. Audit Trail
- Automatic logging of all actions: model registration, approval, policy changes, incident creation
- Who did what, when, to which resource
- Filterable by user, action type, resource, date range
- Immutable (append-only, no deletion)

### 6. Safety Checks & Alerts
- Define safety check rules (threshold-based)
- Simulated drift detection alerts (MVP: manual trigger + scheduled demo data)
- Alert dashboard with status: open, acknowledged, resolved
- Alert assignment to team members

### 7. Executive Reporting
- Dashboard overview: total models, risk distribution, compliance posture, open incidents
- Charts: risk score distribution, incident trends over time, compliance by policy
- Export summary as PDF (stretch goal — MVP: on-screen only)

### 8. UI/UX
- Mobile-first responsive design (sidebar collapses to hamburger on mobile, per BUILD_RULES 41)
- Clean dashboard layout with card-based widgets
- Navigation: Dashboard, Models, Incidents, Policies, Audit Log, Alerts, Settings
- User guide at /guide

## API Endpoints

### Auth
- `POST /api/auth/login` — JWT login
- `POST /api/auth/register` — create user (admin only in production, open for seeding)
- `GET /api/auth/me` — current user

### Models
- `GET /api/models` — list with filters (risk_level, status, team)
- `POST /api/models` — create model entry
- `GET /api/models/{id}` — detail
- `PUT /api/models/{id}` — update
- `DELETE /api/models/{id}` — soft delete
- `POST /api/models/{id}/approve` — approve model for deployment
- `GET /api/models/{id}/history` — lifecycle history

### Incidents
- `GET /api/incidents` — list with filters
- `POST /api/incidents` — create
- `GET /api/incidents/{id}` — detail
- `PUT /api/incidents/{id}` — update/resolve
- `GET /api/incidents/stats` — aggregate stats

### Policies
- `GET /api/policies` — list
- `POST /api/policies` — create
- `GET /api/policies/{id}` — detail with mapped models
- `PUT /api/policies/{id}` — update
- `POST /api/policies/{id}/map` — map model to policy
- `GET /api/compliance/matrix` — full compliance matrix

### Audit
- `GET /api/audit` — filterable audit log (read-only)

### Alerts
- `GET /api/alerts` — list with filters
- `POST /api/alerts` — create (or auto-generated)
- `PUT /api/alerts/{id}` — acknowledge/resolve
- `POST /api/alerts/trigger-check` — manual safety check trigger

### Dashboard
- `GET /api/dashboard/summary` — aggregate stats for executive view

### Health
- `GET /health` — `{"status": "healthy"}`

## Database Schema

### users
id, email, password_hash, name, role (admin/safety_officer/engineer/viewer), created_at, updated_at

### models
id, name, version, description, team, risk_score, risk_level (auto), status (draft/review/approved/deployed/retired), created_by, created_at, updated_at, deleted_at

### model_risk_categories
id, model_id (FK), category (bias/safety/privacy/robustness/fairness), score (1-10)

### incidents
id, title, description, type, severity, model_id (FK nullable), status (open/investigating/resolved/closed), assigned_to (FK nullable), reported_by (FK), resolution_notes, created_at, updated_at, resolved_at

### policies
id, name, description, requirements (text), applicable_model_types (json), created_at, updated_at

### policy_model_mappings
id, policy_id (FK), model_id (FK), compliance_status (compliant/non_compliant/pending_review/exempt), reviewed_by (FK nullable), reviewed_at, notes

### audit_log
id, user_id (FK), action, resource_type, resource_id, details (json), created_at

### alerts
id, title, description, type, severity, model_id (FK nullable), status (open/acknowledged/resolved), assigned_to (FK nullable), created_at, updated_at, resolved_at

## Docker Services
- `aisafety-backend` — FastAPI on port 8000
- `aisafety-frontend` — nginx serving React build on port 80
- `aisafety-db` — PostgreSQL 16

All on `dokploy-network` (external). Nginx uses `resolver 127.0.0.11` with variable proxy_pass. Python healthcheck (no curl). Named volumes: `aisafety-pgdata`.

## Traefik Labels
Prefix: `aisafety-*`

## Seed Data
On first run, seed:
- Admin user: steve@ipwatcher.com / 5678*Stud
- 5 sample models with varying risk scores
- 3 sample policies
- 10 sample incidents across models
- Sample compliance mappings
- Demo audit entries
