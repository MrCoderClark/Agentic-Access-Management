# AgentGuard

AI-native Access Governance & ITSM platform. Uses autonomous AI agents with RAG to automate access management, enforce least-privilege policies, and provide intelligent ticketing.

<img width="1408" height="768" alt="Agentic-Access-Management" src="https://github.com/user-attachments/assets/784526c6-fa15-4fb3-9049-c917227d1dab" />

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TailwindCSS, shadcn/ui |
| Backend | Python 3.12+, FastAPI, LangGraph |
| Database | Supabase (PostgreSQL + pgvector) |
| Auth | Supabase Auth (SSO/SAML/MFA) |
| LLM | Claude Sonnet (primary), GPT-4o (fallback) |

## Prerequisites

- Docker (Supabase services)
- Node.js 20+ / pnpm
- Python 3.12+ / uv
- OpenAI or Anthropic API key

## Quick Start

```bash
# 1. Copy environment config
cp .env.example .env
# Fill in your Supabase keys and API keys

# 2. Frontend
cd frontend
pnpm install
pnpm dev                    # http://localhost:3000

# 3. Backend
cd backend
uv venv
uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload --port 8001

# 4. Supabase (already running via Docker)
# Studio:  http://localhost:54323
# API:     http://localhost:8000
```

## Project Structure

```
├── frontend/       # Next.js 15 application
├── backend/        # Python FastAPI + AI agents
├── supabase/       # Migrations and seed data
├── docs/           # Documentation
├── PLAN.md         # Technical architecture & roadmap
├── SPEC.md         # Product specification
├── UI-SPEC.md      # UI design specification
└── CLAUDE.md       # AI coding assistant instructions
```

## Documentation

- **[PLAN.md](./PLAN.md)** — Architecture, database schema, agent design, implementation phases
- **[SPEC.md](./SPEC.md)** — Functional requirements, acceptance criteria, API design
- **[UI-SPEC.md](./UI-SPEC.md)** — Design system, wireframes, component specifications
