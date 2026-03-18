# 🔐 Zero Trust Network Simulation Lab

A production-style **Zero Trust Architecture (ZTA) simulation platform** built for security portfolios, labs, and interview demos. It shows how modern access decisions are made using **identity**, **device trust**, **micro-segmentation**, **continuous verification**, and a **policy engine**.

## What this project demonstrates

- Identity-based authentication with JWT
- Policy-based authorization per user, device, location, and resource
- Micro-segmented protected resources (`admin`, `engineering`, `finance`, `db`)
- Continuous verification with risk scoring on every request
- Simulated threat and access events for demos
- Security events API + Streamlit dashboard
- Recruiter-friendly architecture with clean separation of concerns

## Architecture

```text
┌──────────────┐      login/access      ┌─────────────────┐
│   User/App   │ ────────────────────▶ │   FastAPI API    │
└──────────────┘                        │  Access Gateway │
                                        └────────┬────────┘
                                                 │
                             ┌───────────────────┼────────────────────┐
                             │                   │                    │
                             ▼                   ▼                    ▼
                    ┌────────────────┐   ┌───────────────┐   ┌────────────────┐
                    │ Identity Check │   │ Policy Engine │   │ Risk Evaluator │
                    └────────────────┘   └───────────────┘   └────────────────┘
                             │                   │                    │
                             └───────────────────┴────────────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │ Decision Logger │
                                        └────────┬────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    ▼                            ▼                            ▼
           ┌────────────────┐         ┌────────────────┐           ┌─────────────────┐
           │ SQLite Storage │         │ Streamlit SOC  │           │ Protected Zones │
           │ users/events   │         │ Dashboard      │           │ /admin /db ...  │
           └────────────────┘         └────────────────┘           └─────────────────┘
```

## Project structure

```text
ztn-lab/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── scripts/
│   └── seed_and_demo.py
├── tests/
│   └── test_policy_engine.py
├── docker-compose.yml
├── .env.example
└── README.md
```

## Roles and trust model

### Users
- `admin_user` / `Admin@123`
- `dev_user` / `Dev@123`
- `analyst_user` / `Analyst@123`
- `guest_user` / `Guest@123`

### Device trust
- `trusted` → low risk
- `managed` → medium-low risk
- `unknown` → high risk
- `compromised` → critical risk

### Sample resources
- `/zones/admin`
- `/zones/engineering`
- `/zones/finance`
- `/zones/db`

## Access decision logic

Every access request is evaluated against:

1. **Identity** — authenticated user and role
2. **Device trust** — trusted vs unknown vs compromised
3. **Location** — corporate vs remote vs foreign
4. **Risk score** — calculated per request
5. **Policy rules** — allow / deny / conditional allow
6. **Continuous verification** — each request re-evaluated

## Quick start

### Option 1: Local run

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

#### Dashboard
```bash
cd dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### Option 2: Docker Compose
```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

## Demo flow

1. Open API docs.
2. Log in with one of the demo accounts.
3. Call `POST /access/evaluate` with different devices/locations/resources.
4. Watch decisions appear on the Streamlit dashboard.
5. Run `scripts/seed_and_demo.py` to generate activity quickly.

## Example access request

```json
{
  "resource": "/zones/admin",
  "action": "read",
  "device_trust": "unknown",
  "location": "remote",
  "ip_address": "203.0.113.20"
}
```

## Example access decision

```json
{
  "decision": "deny",
  "risk_score": 77,
  "resource_segment": "admin",
  "reason": "Role not allowed for segment admin; risk score exceeded threshold",
  "policy": "deny_non_admin_admin_zone"
}
```

## Future upgrades

- Open Policy Agent (OPA) integration
- PostgreSQL + Alembic migrations
- Redis for session and rate tracking
- GeoIP enrichment
- SIEM forwarding to Elasticsearch
- Device posture collection agent
- mTLS between services
