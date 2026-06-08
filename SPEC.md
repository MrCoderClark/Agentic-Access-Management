# AgentGuard — Product Specification

## 1. Product Vision

AgentGuard is an AI-native Access Governance & ITSM platform that uses autonomous agents and RAG to automate access management, enforce least-privilege policies, and provide intelligent ticketing. It is self-hosted (Supabase on your infra), transparent (full decision graphs with citations), and extensible (plugin system + SDK).

**Target users**: IT teams, Security teams, HR, and employees at companies with 50–5,000 employees who currently manage access manually or through legacy tools.

---

## 2. User Personas

| Persona | Role | Primary Goals |
|---------|------|---------------|
| **IT Admin** | Manages systems, connectors, policies | Configure access policies, review agent decisions, manage integrations |
| **Security Engineer** | Monitors access posture, compliance | Access reviews, risk dashboards, audit trail, incident response |
| **Employee** | Requests access to tools/systems | Self-service access requests via Slack/Teams/web, track request status |
| **Manager** | Approves access for direct reports | Review and approve/deny access requests, see team access overview |
| **Platform Admin** | Manages AgentGuard itself | User management, system config, agent tuning, tenant setup |

---

## 3. Functional Requirements

### 3.1 Access Request Management

**FR-AR-01**: Employees can submit access requests via web portal, Slack, or Teams.
- Input: system name (or natural language description), permission level, justification, desired duration
- The system uses NLP to parse natural language requests into structured form

**FR-AR-02**: Each request is evaluated against applicable policies using RAG-retrieved context.
- Agent retrieves relevant policies, past decisions for similar requests, and system documentation
- Risk score is computed based on: permission sensitivity, requester role, request history, policy match

**FR-AR-03**: Requests are routed based on risk score:
- **Low risk** (score < configurable threshold, default 0.3): Auto-approved if policy allows, provisioned immediately
- **Medium risk** (0.3–0.7): Routed to designated approver(s) with agent recommendation
- **High risk** (> 0.7): Blocked, security team notified, detailed reasoning logged

**FR-AR-04**: Approved access is time-bound by default.
- Every grant has a TTL (max duration from policy, or requester-specified if shorter)
- Expired grants are automatically revoked via scheduled job
- Users can request renewal before expiry

**FR-AR-05**: Full audit trail for every request.
- Decision reasoning with RAG source citations
- Agent confidence score
- Approver identity and timestamp
- Provisioning result (success/failure)

#### Acceptance Criteria — Access Requests
- [ ] Employee submits request via web form → receives decision within 30 seconds (auto-approve) or notification that it's pending approval
- [ ] Natural language request "I need access to the production AWS console for debugging" correctly identifies system=AWS, permission=console-access, context=debugging
- [ ] Request denied by policy → employee sees specific reason citing the policy that blocked it
- [ ] Approved access with 24h TTL → access is revoked automatically after 24h
- [ ] All decisions appear in audit log with RAG citations within 1 second of decision

### 3.2 Policy Management

**FR-PM-01**: Admins can create, edit, and deactivate access policies via the web dashboard.

**FR-PM-02**: Policies define:
- Which systems they apply to
- Who can request (conditions: role, department, group membership, manager chain)
- Approval chain (auto-approve, single approver, multi-level)
- Maximum access duration
- Risk threshold for auto-approval

**FR-PM-03**: Policies are embedded into the RAG knowledge base on save/update, so agents always evaluate against the latest version.

**FR-PM-04**: Policy versioning — previous versions are retained for audit purposes.

#### Acceptance Criteria — Policies
- [ ] Admin creates a new policy → it's immediately available to agents for the next request evaluation
- [ ] Policy with condition "department = Engineering AND risk < 0.3" auto-approves matching requests and escalates non-matching ones
- [ ] Deactivated policy is excluded from agent evaluation but still visible in audit history
- [ ] Editing a policy creates a new version; old version is retained

### 3.3 RAG Knowledge Base

**FR-KB-01**: Admins can upload documents (PDF, Markdown, plain text) that are chunked, embedded, and stored in pgvector.

**FR-KB-02**: Document types supported: access policies, IT runbooks/SOPs, system documentation, compliance requirements.

**FR-KB-03**: Documents are automatically re-embedded when updated.

**FR-KB-04**: Retrieval uses multi-stage pipeline: vector similarity → re-ranking → context assembly.

**FR-KB-05**: Past access decisions are automatically indexed as precedent documents.

**FR-KB-06**: Employees can query the knowledge base conversationally ("How do I get access to Datadog?") and receive answers with source citations.

#### Acceptance Criteria — Knowledge Base
- [ ] Upload a 10-page PDF runbook → it's chunked and searchable within 60 seconds
- [ ] Query "What is the policy for production database access?" returns the correct policy document with >0.8 similarity
- [ ] Past decision for "John got read-only Datadog access" appears as a precedent when similar request is made
- [ ] Employee asks "How do I request VPN access?" → receives step-by-step answer citing the relevant runbook

### 3.4 AI Agent System

**FR-AG-01**: **Request Agent** — Parses natural language requests, identifies target system and permission, enriches with requester context (role, team, existing access).

**FR-AG-02**: **Policy Agent** — Evaluates applicable policies with RAG context, computes risk score, produces recommendation with reasoning chain and citations.

**FR-AG-03**: **Provisioning Agent** — Executes approved access grants via integration connectors. Reports success/failure back to the workflow.

**FR-AG-04**: **Review Agent** — Runs scheduled access reviews. Compares current grants against policy intent. Flags: unused access (>30 days no activity), excessive permissions, policy violations.

**FR-AG-05**: **Sentinel Agent** — Background monitor that continuously scans for: permission drift, orphaned accounts, anomalous access patterns, policy compliance gaps.

**FR-AG-06**: All agent decisions include:
- Confidence score (0.0–1.0)
- Reasoning chain (step-by-step explanation)
- RAG source citations (which documents informed the decision)
- Recommended action

**FR-AG-07**: Agent Observatory — real-time dashboard showing agent activity, decision history, reasoning chains, and RAG source drill-down.

**FR-AG-08**: Human-in-the-loop escalation when agent confidence falls below configurable threshold (default: 0.6).

#### Acceptance Criteria — Agents
- [ ] Request Agent correctly parses 90%+ of natural language access requests in test suite
- [ ] Policy Agent decision includes at least one RAG citation for every non-trivial evaluation
- [ ] Provisioning Agent creates an Okta group membership within 10 seconds of approval
- [ ] Review Agent identifies an unused access grant (no activity for 30+ days) and recommends revocation
- [ ] Sentinel Agent detects a new permission not covered by any policy and creates an alert
- [ ] Agent with confidence < 0.6 routes to human approver instead of auto-deciding
- [ ] Agent Observatory shows live agent activity with <5 second latency

### 3.5 Intelligent Ticketing

**FR-TK-01**: All access requests automatically create tickets for tracking and SLA management.

**FR-TK-02**: Non-access tickets (incidents, general IT requests) can be submitted and triaged by AI.

**FR-TK-03**: AI triage uses RAG to find similar past tickets and suggest resolution paths.

**FR-TK-04**: Common requests (password resets, group membership changes) are auto-resolved using runbook procedures.

**FR-TK-05**: SLA tracking with configurable deadlines per ticket type and priority.

#### Acceptance Criteria — Ticketing
- [ ] Access request creates a ticket visible in both the admin inbox and the employee's "My Requests" view
- [ ] "Reset my password for Jira" → auto-resolved with instructions from the runbook, no human needed
- [ ] Ticket exceeding SLA deadline triggers notification to assignee and their manager
- [ ] Similar past ticket is surfaced with resolution when a new ticket matches >0.75 similarity

### 3.6 Integrations / Connectors

**FR-IN-01**: Abstract connector interface — each integration implements: list users, list groups, grant access, revoke access, check access status.

**FR-IN-02**: Initial connectors: Okta, Google Workspace, GitHub, Entra ID (Azure AD), AWS IAM.

**FR-IN-03**: Connector configuration stored encrypted in the database (field-level encryption for secrets).

**FR-IN-04**: Connector health monitoring — periodic heartbeat, alert on failure.

**FR-IN-05**: Connector sync — periodically pull current state (users, groups, permissions) to detect drift.

#### Acceptance Criteria — Integrations
- [ ] Okta connector: list users, add user to group, remove user from group — all succeed against a test tenant
- [ ] Connector secret (API key) is never logged or returned in API responses
- [ ] Connector health check runs every 5 minutes; failure triggers admin notification
- [ ] Drift detection: permission added directly in Okta (outside AgentGuard) is flagged within one sync cycle

### 3.7 Chat Interfaces

**FR-CH-01**: Slack bot supports: access requests, approval actions (approve/deny buttons), status queries, knowledge base Q&A.

**FR-CH-02**: Microsoft Teams bot with equivalent functionality.

**FR-CH-03**: Approval notifications include request details, agent recommendation, and risk score.

**FR-CH-04**: Inline action buttons (approve, deny, request more info) — no need to open the web portal.

#### Acceptance Criteria — Chat
- [ ] Employee types "I need access to GitHub org" in Slack → bot responds with confirmation and creates request
- [ ] Approver receives Slack message with approve/deny buttons → clicking "Approve" triggers provisioning
- [ ] Employee asks "What access do I have?" → bot lists current active grants

### 3.8 Dashboard & Portal

**FR-UI-01**: **Admin Dashboard** — policy management, system connections, agent observatory, analytics.

**FR-UI-02**: **Employee Portal** — self-service request form, "My Requests" tracker, "My Access" overview, knowledge base search.

**FR-UI-03**: **Security Dashboard** — access review queue, risk heatmap, posture score, compliance status.

**FR-UI-04**: Real-time updates via Supabase Realtime (request status changes, agent decisions, ticket updates).

**FR-UI-05**: Responsive design — functional on tablet and desktop (mobile is not a priority for v1).

#### Acceptance Criteria — UI
- [ ] Admin can create a policy, connect a system, and view agent activity without leaving the dashboard
- [ ] Employee submits request → sees real-time status updates (pending → approved → provisioned) without page refresh
- [ ] Security dashboard shows access review items sorted by risk score
- [ ] Page load time < 2 seconds on standard connection

### 3.9 Playbooks / Workflow Automation

**FR-PB-01**: Template-based workflows for common procedures: onboarding, offboarding, role change, access review.

**FR-PB-02**: Natural language workflow definition — admin describes the workflow, LLM generates the steps.

**FR-PB-03**: Visual workflow builder (drag-and-drop, React Flow) for custom workflows.

**FR-PB-04**: Trigger types: manual, scheduled (cron), event-driven (HRIS webhook, access expiry).

**FR-PB-05**: Workflow steps can invoke agents, send notifications, create tickets, grant/revoke access, or wait for human input.

#### Acceptance Criteria — Playbooks
- [ ] "Onboarding" template: given a new employee record, provisions default access for their role across configured systems
- [ ] Admin describes "When someone leaves, revoke all access and notify their manager" → system generates an offboarding workflow
- [ ] Scheduled access review workflow runs weekly, creates review tickets for flagged grants

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Access request decision (auto-approve path) | < 5 seconds end-to-end | From request submission to decision logged |
| Access request decision (agent evaluation) | < 30 seconds | Including RAG retrieval + LLM reasoning |
| RAG retrieval | < 500ms | pgvector query + re-ranking |
| Dashboard page load | < 2 seconds | Time to interactive (LCP) |
| API response (CRUD operations) | < 200ms (p95) | Excluding LLM calls |
| Concurrent users | 100+ simultaneous | Without degradation |

### 4.2 Scalability

- Database: PostgreSQL handles up to ~1M access grants, ~100K users, ~50K documents without architectural changes
- Agent workers: Horizontally scalable via Celery worker pool
- Embedding pipeline: Batch processing for initial ingest, incremental for updates
- If load exceeds single-node capacity, add read replicas for queries and additional Celery workers for agent processing

### 4.3 Availability

- Target: 99.5% uptime for web portal and API (during business hours)
- Agent processing is asynchronous — brief backend outages don't lose requests (queued in database)
- Supabase Realtime reconnects automatically; client polls as fallback
- No single-point-of-failure for critical path (access revocation must work even if LLM is down)

### 4.4 Security

- All API endpoints require authentication (Supabase Auth JWT)
- Row Level Security enforced at database level — even raw SQL access respects tenant boundaries
- Agent actions are constrained by policy — no autonomous high-risk actions without human approval
- Connector secrets encrypted at rest with field-level encryption (not just disk encryption)
- Audit log is append-only — no UPDATE or DELETE on audit_events table
- RAG documents respect access control — embeddings are filtered by tenant/role
- Rate limiting on all public endpoints (auth, chat bots, API)
- CORS restricted to known frontend origins

### 4.5 Data Retention

| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Audit events | 7 years minimum | SOC 2 / compliance requirement |
| Access grants (revoked/expired) | 3 years | Compliance + precedent for RAG |
| Tickets (closed) | 2 years | Precedent + analytics |
| RAG documents | Until manually deleted | Active knowledge base |
| Agent decision logs | 3 years | Explainability + compliance |
| User data (offboarded) | 90 days after offboarding, then anonymized | GDPR compliance |

### 4.6 Observability

- **Structured logging**: JSON format, correlation IDs across request lifecycle
- **Metrics**: OpenTelemetry → Prometheus (request latency, agent decision times, RAG retrieval quality, error rates)
- **Tracing**: Distributed traces for agent workflows (request → RAG → policy eval → provision)
- **Agent-specific**: Decision confidence distribution, escalation rate, auto-approval rate, RAG hit rate
- **Alerts**: Connector failures, agent error rate spikes, SLA breach rates, security anomalies

---

## 5. API Design

### 5.1 API Conventions

- RESTful JSON API over HTTPS
- Base path: `/api/v1/`
- Authentication: Bearer token (Supabase Auth JWT) in `Authorization` header
- Pagination: cursor-based (`?cursor=<id>&limit=20`)
- Error format: `{ "error": { "code": "POLICY_NOT_FOUND", "message": "...", "details": {...} } }`
- Rate limiting: 100 req/min per user (configurable)

### 5.2 Core Endpoints

```
# Access Requests
POST   /api/v1/requests              # Submit new access request
GET    /api/v1/requests              # List requests (filtered by role/permissions)
GET    /api/v1/requests/:id          # Get request details + decision trail
POST   /api/v1/requests/:id/approve  # Approve a pending request
POST   /api/v1/requests/:id/deny     # Deny a pending request

# Policies
GET    /api/v1/policies              # List policies
POST   /api/v1/policies              # Create policy
PUT    /api/v1/policies/:id          # Update policy (creates new version)
DELETE /api/v1/policies/:id          # Deactivate policy (soft delete)

# Systems / Connectors
GET    /api/v1/systems               # List connected systems
POST   /api/v1/systems               # Register new system
PUT    /api/v1/systems/:id           # Update system config
POST   /api/v1/systems/:id/sync      # Trigger connector sync
GET    /api/v1/systems/:id/health    # Connector health status

# Users
GET    /api/v1/users                 # List users (synced from IdP)
GET    /api/v1/users/:id             # User details + current access
GET    /api/v1/users/:id/access      # List user's active grants
POST   /api/v1/users/:id/sync       # Re-sync user from IdP

# Knowledge Base
POST   /api/v1/knowledge/documents   # Upload document for RAG
GET    /api/v1/knowledge/documents   # List documents
DELETE /api/v1/knowledge/documents/:id
POST   /api/v1/knowledge/query       # Semantic search / Q&A

# Tickets
GET    /api/v1/tickets               # List tickets
POST   /api/v1/tickets               # Create ticket
PUT    /api/v1/tickets/:id           # Update ticket
GET    /api/v1/tickets/:id           # Ticket details

# Agents
GET    /api/v1/agents/status         # Agent health and activity
GET    /api/v1/agents/decisions      # Decision history with filters
GET    /api/v1/agents/decisions/:id  # Decision detail with reasoning + RAG sources

# Audit
GET    /api/v1/audit                 # Query audit log (time range, actor, action filters)
GET    /api/v1/audit/export          # Export audit log (CSV/JSON, OCSF format)

# Analytics
GET    /api/v1/analytics/overview    # Dashboard stats
GET    /api/v1/analytics/risk        # Risk heatmap data
GET    /api/v1/analytics/agents      # Agent performance metrics
```

---

## 6. Data Model Summary

See PLAN.md for full SQL schemas. Key relationships:

```
users ──< access_grants >── systems
  │              │
  │              └── tickets (request_id FK)
  │
  ├──< tickets (requester_id, assignee_id)
  │
  └── users (manager_id self-ref)

policies ──── systems (system_id FK)

audit_events ── polymorphic (target_type + target_id)

documents ── RAG vector store (standalone, linked via source_id)
```

---

## 7. Out of Scope (v1)

- Mobile-native apps (responsive web only)
- On-premises Active Directory connector (cloud IdPs only for v1)
- Custom LLM fine-tuning (uses general-purpose models with RAG)
- White-label / reseller support
- Real-time bidirectional sync with IdPs (periodic pull only)
- Multi-region deployment
- Workflow marketplace / community templates

---

## 8. Open Questions

- [ ] **Embedding model choice**: Start with OpenAI `text-embedding-3-small` (better quality, API cost) or local `all-MiniLM-L6-v2` (free, self-hosted, lower quality)? Decision affects vector dimension and infra requirements.
- [ ] **Approval UX**: Should approvals require the web portal, or is Slack/Teams inline approval sufficient for all cases?
- [ ] **Multi-tenant from day one?**: Building multi-tenant early adds complexity but avoids a painful retrofit. Single-tenant MVP first, or multi-tenant from the start?
- [ ] **LLM provider strategy**: Claude as primary with OpenAI fallback, or provider-agnostic from the start? Affects prompt engineering investment.
- [ ] **Connector priority**: Which 3 integrations to build first? Proposed: Okta, Google Workspace, GitHub. Alternatives: Entra ID, AWS IAM, Jira.

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| **Access Grant** | A time-bound permission assigned to a user for a specific system |
| **Connector** | An integration adapter that communicates with an external system (Okta, GitHub, etc.) |
| **Decision Graph** | The full chain of reasoning an agent used to reach a decision, including RAG sources |
| **Drift** | When actual system permissions diverge from what AgentGuard policies intend |
| **Playbook** | A reusable workflow template (onboarding, offboarding, etc.) |
| **Posture Score** | An aggregate measure of how well the org's actual access aligns with policies |
| **RAG** | Retrieval-Augmented Generation — LLM reasoning augmented with retrieved organizational documents |
| **Risk Score** | A 0.0–1.0 score representing the risk level of an access request based on context |
| **Sentinel** | A background agent that continuously monitors for security issues |
| **TTL** | Time-To-Live — the duration an access grant remains active before auto-revocation |
