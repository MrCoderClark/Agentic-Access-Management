# Agentic Access Management Platform — Plan & Specification

## Executive Summary

Build an **AI-native Access Governance & ITSM platform** that competes with and surpasses Console.com. The platform uses autonomous AI agents powered by **RAG (Retrieval-Augmented Generation)** to handle access requests, enforce least-privilege policies, automate onboarding/offboarding, and provide intelligent ticketing — all orchestrated through a conversational interface (Slack, Teams, Web).

**Stack**: Next.js (frontend) + Python/FastAPI (AI backend) + Supabase (local Docker — PostgreSQL, pgvector, Auth, Realtime)

---

## What Console.com Provides (Competitive Analysis)

### Core Product Modules
1. **AI Assistant** — Conversational interface for employees (Slack/Teams)
2. **Intelligent Ticketing** — AI-powered service desk inbox
3. **Workflow Automation (Playbooks)** — Natural-language automation workflows
4. **Access Management** — Identity & access governance with auto-provisioning
5. **Asset Management** — Real-time asset tracking

### Architecture
- **Context Graph** — Foundation connecting users, systems, policies, tickets
- **AI Layer** — Assistant + Background Agents scanning for gaps
- **Integrations Layer** — 600+ connectors (Okta, Entra, Google, AWS, etc.)
- **Surface Modules** — Ticketing, Playbooks, Access, Assets

### Key Differentiators
- 75%+ auto-resolution of service requests
- 4:750 IT-to-employee ratio (Cursor case study)
- No-code integration builder via AI
- Multi-team support (IT, HR, Legal, Security, Finance, RevOps)
- Enterprise security: SOC 2 Type II, HIPAA, GDPR, RBAC, SSO/SCIM

---

## Our Platform: "AgentGuard" — How We Beat Console

### Competitive Advantages Over Console

| Area | Console | AgentGuard (Ours) |
|------|---------|-------------------|
| Agent Architecture | Monolithic AI layer | Multi-agent mesh with specialized agents |
| AI Knowledge | Unknown | RAG pipeline with org-specific context (policies, runbooks, past decisions) |
| Policy Engine | Static rule-based | Dynamic risk-scoring + contextual policies via RAG |
| Access Reviews | Manual trigger | Continuous autonomous reviews |
| Agent-to-Agent Governance | Not mentioned | First-class support for governing AI agents accessing systems |
| Developer Experience | No-code only | No-code + Python SDK + REST API |
| Transparency | Basic audit logs | Full decision graph with RAG source citations |
| Real-time Posture | Periodic scans | Continuous posture monitoring |
| Open Architecture | Proprietary | Plugin system + OPA/Rego compatible policies |
| Data Sovereignty | SaaS only | Self-hosted Supabase — your data stays on your infra |

---

## Technical Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SURFACE LAYER (Next.js)                      │
│  [Web Portal] [Admin Dashboard] [Employee Portal] [API Routes] │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST / WebSocket
┌─────────────────────────────▼───────────────────────────────────┐
│                 AI BACKEND (Python / FastAPI)                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              AGENT ORCHESTRATOR (LangGraph)              │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │
│  │  │ Request  │ │ Policy   │ │ Review   │ │ Sentinel │   │    │
│  │  │ Agent    │ │ Agent    │ │ Agent    │ │ Agent    │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐      │
│  │ RAG Pipeline │ │ Risk Scorer  │ │ Connector Engine   │      │
│  │ (LangChain)  │ │              │ │ (Okta/Entra/etc.)  │      │
│  └──────────────┘ └──────────────┘ └────────────────────┘      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ SQL / pgvector / Realtime
┌─────────────────────────────▼───────────────────────────────────┐
│               DATA LAYER (Supabase — Local Docker)               │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │PostgreSQL│ │ pgvector │ │Supabase  │ │ Supabase         │  │
│  │  (data)  │ │(embeddings│ │  Auth    │ │ Realtime         │  │
│  │          │ │ for RAG) │ │(SSO/SAML)│ │ (WebSocket push) │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
│                                                                   │
│  ┌──────────────────┐ ┌──────────────────┐                      │
│  │ Supabase Storage │ │ Edge Functions   │                      │
│  │ (docs, exports)  │ │ (webhooks)       │                      │
│  └──────────────────┘ └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 15 (App Router), TailwindCSS, shadcn/ui, Lucide icons | Modern React, SSR, great DX |
| **AI Backend** | Python 3.12, FastAPI, Uvicorn | Python-first AI ecosystem, async, fast |
| **Agent Framework** | LangGraph + LangChain | Multi-agent orchestration, tool calling, state machines |
| **RAG Pipeline** | LangChain + pgvector + sentence-transformers | Retrieval over policies, runbooks, past decisions |
| **Embeddings** | OpenAI `text-embedding-3-small` (1536d) or local `all-MiniLM-L6-v2` (384d) | Vector search for semantic policy matching |
| **LLM** | Claude Sonnet 4.6 (primary) / OpenAI GPT-4o (fallback), configurable | Agent reasoning, NLP, decision-making |
| **Database** | Supabase (PostgreSQL 15 + pgvector) — local Docker | Relational data + vector store in one DB |
| **Auth** | Supabase Auth (SSO/SAML/SCIM, MFA, RLS) | Built-in, self-hosted, enterprise-grade |
| **Realtime** | Supabase Realtime (WebSocket) | Live ticket updates, agent status, notifications |
| **Policy Engine** | Custom Python + OPA (Open Policy Agent) | Declarative, auditable, Rego-compatible |
| **Task Queue** | Celery + Redis (or Supabase pg_cron) | Background agent tasks, scheduled reviews |
| **Chat Bots** | Slack Bolt (Python), MS Bot Framework | Native Python SDKs |
| **Monitoring** | OpenTelemetry, Prometheus, custom agent traces | Full observability |

---

## RAG Architecture (Key Differentiator)

### What Gets Embedded & Retrieved

| Document Type | Purpose | Update Frequency |
|---------------|---------|-----------------|
| Access policies | Agent uses to decide approvals | On policy change |
| IT runbooks / SOPs | Auto-resolve tickets using org knowledge | On upload |
| Past access decisions | Learn from precedent (similar requests) | On each decision |
| System documentation | Understand what each app does, who owns it | On sync |
| Employee directory | Context about requester (role, team, manager) | Real-time from HRIS |
| Compliance requirements | SOC2/HIPAA constraints for sensitive systems | On upload |

### RAG Flow

```
User Request → Embed query → pgvector similarity search (top-k candidates)
                                    │
                                    ▼
                          Re-ranker (cross-encoder or LLM-based)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Relevant         Past similar      System
              policies         decisions        docs/runbooks
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                        LLM (with retrieved context)
                                    │
                                    ▼
                        Agent Decision + Citations
```

### Retrieval Strategy
- **Stage 1 — Candidate retrieval**: pgvector cosine similarity, fetch top-k (k=10-20) candidates
- **Stage 2 — Re-ranking**: Cross-encoder model or LLM-based re-ranking to reorder by relevance
- **Stage 3 — Context assembly**: Top-n (n=3-5) documents assembled into agent prompt with source metadata
- **Hybrid search** (future): Combine vector similarity with PostgreSQL full-text search (`tsvector`) for keyword-heavy policy documents

### Supabase pgvector Schema

```sql
-- Vector store for RAG documents
-- Dimension depends on embedding model: OpenAI text-embedding-3-small = 1536, all-MiniLM-L6-v2 = 384
-- Set via env var EMBEDDING_DIMENSION at migration time; default 1536
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    doc_type TEXT NOT NULL,  -- 'policy', 'runbook', 'decision', 'system_doc'
    source_id UUID,          -- FK to the source record
    embedding VECTOR(1536),  -- adjust dimension to match your embedding model
    org_id UUID,             -- tenant isolation for multi-org
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_documents_type ON documents(doc_type);

-- RPC function for similarity search with re-ranking support
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 10,
    filter_type TEXT DEFAULT NULL
)
RETURNS TABLE (id UUID, content TEXT, metadata JSONB, similarity FLOAT)
AS $$
    SELECT id, content, metadata, 1 - (embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE (filter_type IS NULL OR doc_type = filter_type)
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$ LANGUAGE sql STABLE;
-- Note: Application-level re-ranking (cross-encoder or LLM-based) is applied
-- after this initial retrieval to improve precision for policy documents.
```

---

## Module Specifications

### Module 1: Context Graph (Supabase PostgreSQL)

The foundation that connects all entities in the org.

**Core Tables:**

```sql
-- Users (synced from IdP / HRIS)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    department TEXT,
    title TEXT,
    manager_id UUID REFERENCES users(id),
    status TEXT DEFAULT 'active',  -- active, suspended, offboarded
    identity_provider TEXT,         -- okta, entra, google
    groups TEXT[] DEFAULT '{}',
    risk_score FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Systems / Applications
CREATE TABLE systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    system_type TEXT,              -- saas, infrastructure, internal
    connector_type TEXT,           -- okta, scim, api, manual
    risk_level TEXT DEFAULT 'low', -- low, medium, high, critical
    owner_id UUID REFERENCES users(id),
    config JSONB DEFAULT '{}',    -- connector config (encrypted)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Access Policies
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_id UUID REFERENCES systems(id),
    name TEXT NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL,     -- who can request, under what conditions
    approvers JSONB,               -- approval chain config
    max_duration_hours INT,        -- max TTL for access grants
    risk_threshold FLOAT,          -- auto-approve below this score
    auto_approve BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tickets (service requests) — defined before access_grants due to FK dependency
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID NOT NULL REFERENCES users(id),
    assignee_id UUID REFERENCES users(id),
    ticket_type TEXT NOT NULL,      -- access_request, incident, change, general
    subject TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',     -- open, in_progress, waiting_approval, resolved, closed
    priority TEXT DEFAULT 'medium', -- low, medium, high, critical
    resolution TEXT,
    resolved_by TEXT,               -- agent name or user id
    sla_deadline TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tickets_requester_status ON tickets(requester_id, status);
CREATE INDEX idx_tickets_assignee_status ON tickets(assignee_id, status);
CREATE INDEX idx_tickets_type_status ON tickets(ticket_type, status);

-- Access Grants (active permissions)
CREATE TABLE access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    system_id UUID NOT NULL REFERENCES systems(id),
    permission TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, active, expired, revoked
    granted_by TEXT,                -- agent or human approver
    justification TEXT,
    risk_score FLOAT,
    granted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    request_id UUID REFERENCES tickets(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_grants_user_status ON access_grants(user_id, status);
CREATE INDEX idx_grants_system_status ON access_grants(system_id, status);
CREATE INDEX idx_grants_expires ON access_grants(expires_at) WHERE status = 'active';

-- Audit Events (immutable log)
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor TEXT NOT NULL,            -- user id, agent name, or 'system'
    actor_type TEXT NOT NULL,       -- user, agent, system
    action TEXT NOT NULL,           -- access_granted, access_revoked, policy_evaluated, etc.
    target_type TEXT,               -- user, system, policy, ticket
    target_id UUID,
    decision TEXT,                  -- approved, denied, escalated
    reasoning TEXT,                 -- agent's explanation (RAG citations included)
    confidence FLOAT,              -- agent confidence score
    rag_sources JSONB,             -- which documents were retrieved for this decision
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_target ON audit_events(target_type, target_id);
CREATE INDEX idx_audit_actor ON audit_events(actor_type, actor);
CREATE INDEX idx_audit_action ON audit_events(action, created_at);

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE systems ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
```

### Module 2: AI Agent Orchestrator (Python / LangGraph)

Multi-agent system where each agent has a specialized role:

1. **Request Agent** — Parses incoming requests (NLP), identifies system + permission, retrieves relevant policies via RAG
2. **Policy Agent** — Evaluates policies against request context, computes risk score using RAG-retrieved precedents
3. **Provisioning Agent** — Executes access grants/revocations via integration connectors
4. **Review Agent** — Runs continuous access reviews, uses RAG to compare current state vs. policy intent
5. **Sentinel Agent** — Background monitor: scans for unused permissions, drift, anomalies

**LangGraph State Machine:**

```python
from langgraph.graph import StateGraph, END

class AccessRequestState(TypedDict):
    request: dict
    requester_context: dict
    retrieved_policies: list[dict]
    similar_past_decisions: list[dict]
    risk_score: float
    decision: str  # "auto_approve", "needs_approval", "deny"
    reasoning: str
    rag_citations: list[dict]
    provisioning_result: dict | None

workflow = StateGraph(AccessRequestState)
workflow.add_node("parse_request", request_agent)
workflow.add_node("retrieve_context", rag_retrieval)
workflow.add_node("evaluate_policy", policy_agent)
workflow.add_node("route_decision", decision_router)
workflow.add_node("provision_access", provisioning_agent)
workflow.add_node("request_approval", human_approval)
workflow.add_node("log_audit", audit_logger)

workflow.set_entry_point("parse_request")
workflow.add_edge("parse_request", "retrieve_context")
workflow.add_edge("retrieve_context", "evaluate_policy")
workflow.add_conditional_edges("evaluate_policy", route_decision, {
    "auto_approve": "provision_access",
    "needs_approval": "request_approval",
    "deny": "log_audit",
})
workflow.add_edge("provision_access", "log_audit")
workflow.add_edge("request_approval", "log_audit")
workflow.add_edge("log_audit", END)
```

**Agent Communication:**
- Agents communicate via FastAPI internal calls + Supabase Realtime events
- Each agent decision is logged with full reasoning chain + RAG source citations
- Human-in-the-loop escalation when confidence < configurable threshold

### Module 3: Access Request Flow

```
Employee Request (Slack/Teams/Web)
        │
        ▼
  Request Agent (NLP parse → identify system & permission)
        │
        ▼
  RAG Retrieval (fetch relevant policies, past decisions, system docs)
        │
        ▼
  Policy Agent (evaluate policies with RAG context, compute risk score)
        │
        ├── Low Risk + Auto-approve → Provisioning Agent → Grant Access
        │
        ├── Medium Risk → Route to approver(s) → Approval → Provision
        │
        └── High Risk → Block + Notify Security + Log with reasoning
        │
        ▼
  Access Grant (with TTL) → pg_cron scheduled revocation
        │
        ▼
  Audit Event Logged (with RAG citations + confidence score)
```

### Module 4: Intelligent Ticketing

- AI-powered triage and routing (RAG over past tickets for similar resolution)
- Auto-resolution for common requests (password resets, group adds, etc.)
- SLA tracking with intelligent prioritization
- Knowledge base integration for self-service (RAG over runbooks)

### Module 5: Playbooks (Workflow Automation)

- Natural language workflow definition (LLM-generated from description)
- Visual workflow builder (React Flow drag-and-drop)
- Template library (onboarding, offboarding, access reviews, etc.)
- Trigger types: manual, scheduled (pg_cron), event-driven, HRIS webhook

### Module 6: Web Dashboard (Next.js)

- **Admin Portal** — Policy management, system connections, analytics
- **Employee Portal** — Self-service access requests, ticket status
- **Security Portal** — Access reviews, posture dashboard, risk heatmap
- **Agent Observatory** — Real-time view of agent decisions, RAG sources, reasoning chains

---

## Implementation Phases

### Phase 1: Project Scaffold & Data Layer (Weeks 1-2)
- [ ] Monorepo setup: `frontend/` (Next.js) + `backend/` (Python/FastAPI)
- [ ] Docker Compose config (backend + Supabase services)
- [ ] Supabase local Docker verification + initial schema migration
- [ ] PostgreSQL schema: users, systems, policies (core tables only)
- [ ] pgvector extension + documents table for RAG
- [ ] FastAPI project scaffold with Supabase client, health check, CORS
- [ ] Next.js project with shadcn/ui, TailwindCSS, Supabase JS client
- [ ] Supabase Auth setup (email/password + SSO placeholder)
- [ ] `.env.example` with all required config vars documented

### Phase 2: Dashboard Shell & CRUD APIs (Weeks 3-4)
- [ ] Basic dashboard layout (sidebar nav, admin + employee views)
- [ ] API routes: CRUD for users, systems, policies
- [ ] Tickets + access_grants tables + API routes
- [ ] Audit events table + append-only write API
- [ ] RLS policies for all tables
- [ ] Frontend: systems list, policy editor, user management pages
- [ ] API error handling middleware + structured error responses

### Phase 3: RAG Pipeline + Policy Engine (Weeks 5-7)
- [ ] Embedding pipeline: ingest policies, runbooks → chunk → embed → pgvector
- [ ] RAG retrieval function: similarity search + metadata filtering
- [ ] Re-ranking layer (cross-encoder for policy relevance)
- [ ] Document upload/management UI for knowledge base
- [ ] Policy engine (Python): evaluate conditions, compute risk score
- [ ] Access request flow (web form → FastAPI → policy eval → response)
- [ ] Approval routing logic (Supabase Realtime for live updates)
- [ ] Time-bound access with auto-revocation (pg_cron or Celery)
- [ ] Audit trail with RAG citations

### Phase 4: AI Agents (Weeks 8-11)
- [ ] LangGraph agent orchestrator with error handling + retries
- [ ] Request Agent (NLP intent parsing + RAG context retrieval)
- [ ] Policy Agent (risk scoring with RAG-retrieved precedents)
- [ ] Provisioning Agent (execute via connector adapters)
- [ ] Sentinel Agent (background: unused permissions, policy drift)
- [ ] Agent decision explainability UI (show RAG sources, reasoning chain)
- [ ] First integrations: Okta, Google Workspace, GitHub
- [ ] Agent confidence thresholds + human-in-the-loop escalation

### Phase 5: Chat Interfaces & Conversational UX (Weeks 12-13)
- [ ] Slack bot (Python Bolt SDK: access requests, approvals, notifications)
- [ ] Microsoft Teams bot
- [ ] Conversational RAG: employees ask questions, agent answers from knowledge base
- [ ] Inline approval buttons in chat
- [ ] Rate limiting on chat endpoints

### Phase 6: Advanced Features (Weeks 14-17)
- [ ] Continuous access reviews (Review Agent + scheduled scans)
- [ ] Playbook/workflow engine
- [ ] Visual workflow builder (React Flow)
- [ ] Analytics and reporting dashboard
- [ ] Agent-to-agent governance (unique differentiator)
- [ ] Risk heatmap and security posture dashboard

### Phase 7: Enterprise & Scale (Weeks 18-22)
- [ ] SCIM provisioning endpoint
- [ ] RBAC for the platform itself (Supabase RLS policies)
- [ ] Multi-tenant architecture
- [ ] SOC 2 compliance logging (OCSF format)
- [ ] Custom integration builder (LLM generates connector code)
- [ ] Python SDK + API documentation
- [ ] Production deployment guide (Docker, managed Supabase, or self-hosted)
- [ ] CI/CD pipeline (GitHub Actions: lint, test, build, deploy)

---

## Key Files & Directory Structure

```
agentic-access-management/
├── frontend/                        # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Landing/login
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx        # Main admin dashboard
│   │   │   │   ├── requests/       # Access request management
│   │   │   │   ├── policies/       # Policy editor
│   │   │   │   ├── systems/        # Connected systems
│   │   │   │   ├── agents/         # Agent observatory
│   │   │   │   ├── reviews/        # Access reviews
│   │   │   │   ├── knowledge/      # RAG document management
│   │   │   │   └── analytics/      # Reports & analytics
│   │   │   ├── portal/             # Employee self-service
│   │   │   └── api/                # Next.js API routes (proxy to FastAPI)
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   ├── dashboard/
│   │   │   ├── agents/
│   │   │   └── shared/
│   │   └── lib/
│   │       ├── supabase.ts         # Supabase client
│   │       ├── api.ts              # FastAPI client
│   │       └── utils.ts
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── backend/                         # Python FastAPI application
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Settings (Supabase URL, API keys)
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── access.py       # Access request endpoints
│   │   │   │   ├── policies.py     # Policy CRUD
│   │   │   │   ├── tickets.py      # Ticket endpoints
│   │   │   │   ├── agents.py       # Agent status/control
│   │   │   │   ├── knowledge.py    # RAG document management
│   │   │   │   └── integrations.py # Connector management
│   │   │   └── deps.py             # Dependency injection
│   │   ├── agents/
│   │   │   ├── orchestrator.py     # LangGraph workflow
│   │   │   ├── request_agent.py
│   │   │   ├── policy_agent.py
│   │   │   ├── provisioning_agent.py
│   │   │   ├── review_agent.py
│   │   │   ├── sentinel_agent.py
│   │   │   └── tools.py            # Agent tools (DB queries, API calls)
│   │   ├── rag/
│   │   │   ├── pipeline.py         # Ingest → chunk → embed → store
│   │   │   ├── retriever.py        # pgvector similarity search
│   │   │   ├── embeddings.py       # Embedding model wrapper
│   │   │   └── chunker.py          # Document chunking strategies
│   │   ├── integrations/
│   │   │   ├── base.py             # Abstract connector interface
│   │   │   ├── okta.py
│   │   │   ├── google_workspace.py
│   │   │   ├── github.py
│   │   │   ├── entra_id.py
│   │   │   └── aws.py
│   │   ├── core/
│   │   │   ├── policy_engine.py    # Policy evaluation logic
│   │   │   ├── risk_scorer.py      # Risk computation
│   │   │   ├── audit.py            # Audit event logger
│   │   │   └── security.py         # Auth middleware, RLS helpers
│   │   └── models/
│   │       ├── schemas.py          # Pydantic models
│   │       └── enums.py            # Status/type enums
│   │   ├── bots/                    # Chat bot handlers (part of backend)
│   │   │   ├── slack_handler.py     # Slack Bolt event handlers
│   │   │   └── teams_handler.py     # MS Teams bot handlers
│   ├── tests/
│   │   ├── test_agents.py
│   │   ├── test_rag.py
│   │   ├── test_policy_engine.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
│
├── supabase/                        # Supabase config & migrations
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_pgvector_setup.sql
│   │   ├── 003_rls_policies.sql
│   │   └── 004_functions.sql       # match_documents, etc.
│   ├── seed.sql                    # Demo data
│   └── config.toml
│
├── docs/                            # Documentation
│   ├── api.md
│   ├── architecture.md
│   └── deployment.md
│
├── .env.example                     # Environment template (never commit .env)
├── docker-compose.yml               # Local dev (backend alongside Supabase)
├── PLAN.md                          # Implementation roadmap (how)
├── SPEC.md                          # Product specification (what)
├── CLAUDE.md                        # Claude Code project config
└── README.md
```

---

## Security Requirements

- **Authentication**: Supabase Auth with SSO (SAML 2.0, OIDC), MFA enforcement
- **Authorization**: Row Level Security (RLS) at database level + RBAC in application
- **Data**: Encryption at rest (Supabase/PostgreSQL) and in transit (TLS), field-level encryption for connector secrets
- **Audit**: Immutable append-only audit_events table, OCSF format export for SIEM
- **Compliance**: SOC 2 Type II ready, GDPR data handling, HIPAA compatible
- **Agent Security**: All AI agent actions require policy validation, no autonomous high-risk actions without human approval
- **RAG Security**: Document-level access control on embeddings (RLS on documents table)

---

## Verification & Testing Strategy

1. **Python Tests**: pytest for FastAPI routes, agent logic, RAG pipeline, policy engine
2. **Frontend Tests**: Vitest for React components
3. **Integration Tests**: Test connector adapters against mock APIs
4. **E2E Tests**: Playwright for critical flows (request → approve → provision)
5. **Agent Tests**: Scenario-based testing with recorded RAG contexts
6. **RAG Tests**: Relevance scoring — verify correct documents are retrieved for known queries
7. **Security Tests**: RLS policy validation, auth boundary tests
8. **Load Tests**: Locust for API performance under concurrent requests

---

## Environment & Local Development

### Prerequisites
- Docker + Docker Compose (Supabase already running)
- Node.js 20+ / pnpm
- Python 3.12+ / uv or pip
- OpenAI API key (or local LLM via Ollama)

### Local Dev Commands
```bash
# Frontend
cd frontend && pnpm install && pnpm dev        # http://localhost:3000

# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000       # http://localhost:8000

# Supabase (already running via Docker)
# Dashboard at http://localhost:54323
# API at http://localhost:54321
```

---

## Error Handling & Resilience

| Failure Mode | Handling Strategy |
|-------------|-------------------|
| LLM API timeout/rate limit | Exponential backoff with configurable retry (max 3), fallback to cached policy rules |
| Connector timeout (Okta, etc.) | Circuit breaker pattern, queue for retry, notify admin |
| RAG retrieval returns no results | Fall back to rule-based policy evaluation, flag for human review |
| Agent confidence below threshold | Escalate to human approver, never auto-approve uncertain decisions |
| Supabase Realtime disconnect | Client-side reconnect with exponential backoff, poll fallback |
| Embedding model unavailable | Queue documents for later embedding, serve from cached embeddings |

---

## Production Deployment

### Target Architecture
- **Frontend**: Vercel or self-hosted Docker (Next.js standalone)
- **Backend**: Docker container on cloud VM, Kubernetes, or serverless (Cloud Run / ECS)
- **Supabase**: Supabase Cloud (managed) or self-hosted via Docker Compose
- **Task Queue**: Redis (managed) + Celery workers in separate containers
- **Secrets**: Cloud-native secrets manager (AWS Secrets Manager, GCP Secret Manager, or Vault)

### CI/CD
- GitHub Actions: lint → type-check → test → build → deploy
- Database migrations run as a pre-deploy step (Supabase CLI)
- Separate staging and production environments

---

## Getting Started (Next Steps)

Once this plan is approved:
1. Scaffold Next.js frontend with shadcn/ui
2. Scaffold Python FastAPI backend
3. Create Supabase migrations (schema + pgvector + RLS)
4. Build the dashboard UI shell
5. Implement RAG pipeline (embed policies → pgvector)
6. Implement the policy engine + first AI agent (Request Agent)
7. Wire up end-to-end: web form → agent → decision → audit log
