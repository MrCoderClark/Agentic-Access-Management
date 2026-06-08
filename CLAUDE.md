# CLAUDE.md — AgentGuard Project Instructions

## Project Overview

AgentGuard is an AI-native Access Governance & ITSM platform. Multi-agent system (LangGraph) with RAG over policies/runbooks, intelligent ticketing, and conversational access requests.

## Tech Stack

- **Frontend**: Next.js 15 (App Router), TailwindCSS, shadcn/ui, Lucide icons, Geist font, Recharts
- **Backend**: Python 3.12+, FastAPI, Uvicorn, LangGraph, LangChain
- **Database**: Supabase (local Docker) — PostgreSQL 15 + pgvector + Auth + Realtime
- **Embeddings**: OpenAI text-embedding-3-small (1536d) or local all-MiniLM-L6-v2 (384d)
- **LLM**: Claude Sonnet (primary), OpenAI GPT-4o (fallback)
- **Task Queue**: Celery + Redis (or pg_cron)

## Directory Structure

```
agentic-access-management/
├── frontend/          # Next.js 15 application
├── backend/           # Python FastAPI application
├── supabase/          # Migrations, seed data, config
├── docs/              # Documentation
├── docker-compose.yml # Local dev (backend + Supabase services)
├── PLAN.md            # Implementation roadmap
├── SPEC.md            # Product specification
├── UI-SPEC.md         # UI design specification
└── CLAUDE.md          # This file
```

## Python Rules

- **Always use `uv` for all Python operations** — virtual environments, package installs, running scripts
- Create venvs: `uv venv`
- Install packages: `uv pip install -r requirements.txt` or `uv pip install <package>`
- Run scripts: `uv run python <script.py>` or `uv run uvicorn app.main:app --reload`
- Use `pyproject.toml` as the primary dependency file with a `requirements.txt` for Docker builds
- Target Python 3.12+

## Frontend Rules

- Use `pnpm` as the package manager
- App Router (not Pages Router)
- All components in `src/components/`
- shadcn/ui components in `src/components/ui/`
- Follow the design system in UI-SPEC.md (amber accent, Geist font, 64px icon sidebar)

## Design System Summary

- **Dark theme**: Deep ink (#0C0E14) + amber (#D4930D) accent
- **Light theme**: Employee portal only — warm off-white (#F6F5F2)
- **Font**: Geist (headings/body) + Geist Mono (data/code/agent logs)
- **Cards**: 8px border-radius, 1px borders, no shadows on dark backgrounds
- **Sidebar**: 64px collapsed, 220px on hover, icon-only by default
- **Status colors**: Active=#34D399, Warning=#FBBF24, Danger=#EF4444, Info=#60A5FA

## Code Style

- Python: Follow PEP 8, use type hints, Pydantic for schemas
- TypeScript: Strict mode, prefer named exports, use interfaces over types for objects
- SQL: Uppercase keywords, snake_case for identifiers
- Never hardcode secrets — use environment variables
- Always include proper error handling

## Key Conventions

- All agent decisions must include: confidence score, reasoning chain, RAG citations
- Audit events are append-only (no UPDATE/DELETE)
- Access grants are time-bound by default (TTL)
- Row Level Security (RLS) on all Supabase tables
- API base path: `/api/v1/`
- Cursor-based pagination
- Structured error responses: `{ "error": { "code": "...", "message": "...", "details": {...} } }`

## Testing

- Backend: `uv run pytest`
- Frontend: `pnpm test` (Vitest)
- E2E: Playwright

## Local Dev

```bash
# Frontend
cd frontend && pnpm install && pnpm dev

# Backend
cd backend && uv venv && uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload --port 8000

# Supabase (Docker)
# Dashboard: http://localhost:54323
# API: http://localhost:54321
```

## Reference Documents

- **PLAN.md** — Architecture, DB schema, agent design, implementation phases
- **SPEC.md** — Functional requirements, acceptance criteria, API endpoints
- **UI-SPEC.md** — Design system, wireframes, component specs, accessibility
