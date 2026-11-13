# Shearline Voice Receptionist

A demonstration website for a fictional hair salon, with a browser-based AI voice receptionist that books real appointments in a real database. A conventional booking form covers visitors who can't or won't use voice.

Shearline Hair Studio is fictional. It offers no real services.

This project is a sibling of PawCare Voice Receptionist (dog grooming) and shares its booking engine and voice design. Prices and durations depend on the customer's **current hair length** (short, medium, long). Extensions and very thick hair need a stylist consultation, so they are routed to a callback instead of being booked.

## What it does

- Shows services, prices, hours, and FAQs from the database.
- Calculates real availability from business hours, stylist hours, breaks, blocked time, and existing bookings.
- Books in two steps (prepare, then confirm), with a PostgreSQL exclusion constraint so two bookings can never overlap.
- Holds voice conversations in the browser through the OpenAI Realtime API over WebRTC. The assistant checks availability, prepares a booking, and takes callback requests. A booking is made only when the visitor presses **Confirm booking**.
- Gives staff a protected dashboard for bookings, cancellations, blocked time, callbacks, and voice metrics.

Not included yet (they exist in PawCare and can be ported later): phone calls (OpenAI SIP or Vapi), Google Calendar sync, n8n automation webhooks, subscriber sign-up, and the evaluation harness.

## Stack

React, TypeScript, and Vite on the frontend. FastAPI, SQLAlchemy, Alembic, and PostgreSQL on the backend. The OpenAI Realtime API over WebRTC provides voice. See [docs/architecture.md](docs/architecture.md).

## Run it locally

You need Docker Desktop running.

```bash
docker compose up --build
```

| What | URL |
|---|---|
| Website | http://localhost:5174 |
| API documentation | http://localhost:8001/docs |
| Readiness check | http://localhost:8001/health/ready |

Host ports are bound to localhost only, and chosen so this project can run beside PawCare: PostgreSQL 5441, API 8001, website 5174.

### Check that it works

```bash
curl -s http://localhost:8001/health/ready
```

Expected: `{"status":"ready","database":"ok","schema_revision":"0001"}`

Check real availability for a future open date. The seeded salon opens Tuesday to Saturday:

```bash
curl -s "http://localhost:8001/api/v1/availability?service=haircut&hair_length=medium&date=YYYY-MM-DD"
```

## Run the checks

Backend tests need PostgreSQL, because the guarantees they verify live in the database. They create and use a separate `salon_test` database.

```bash
docker compose up -d db
```

```bash
cd backend && uv sync && uv run ruff check . && uv run ruff format --check . && uv run pytest
```

Frontend checks need Node 22 (see `frontend/.nvmrc`):

```bash
cd frontend && npm ci && npm run typecheck && npm test && npm run build
```

GitHub Actions runs the same checks, plus a backend image build, on every pull request.

## Configuration

Examples, without secrets: [backend/.env.example](backend/.env.example) and [frontend/.env.example](frontend/.env.example). Anything prefixed `VITE_` ships in the browser bundle, so it must never hold a secret. Voice runs in a labelled test mode until `VOICE_MODE=live` and `OPENAI_API_KEY` are set on the backend.

## Deployment

The frontend deploys to Netlify, and the backend and PostgreSQL deploy to Railway. Follow [docs/deployment.md](docs/deployment.md).

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Deployment](docs/deployment.md)
- [Manual voice testing](docs/voice-testing.md)
- Decisions: [voice](docs/decisions/0001-voice-architecture.md), [booking consistency](docs/decisions/0002-booking-consistency.md), [scope](docs/decisions/0003-scope.md), [staff authentication](docs/decisions/0004-staff-authentication.md)

## Current limitations

- Voice booking has passed automated tests only. No live voice call has been made against this salon yet.
- One stylist calendar. Choosing a stylist is not supported yet.
- Prices are indicative demo values for a fictional business.
