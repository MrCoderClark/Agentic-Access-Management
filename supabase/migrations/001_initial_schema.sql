-- =============================================================================
-- 001_initial_schema.sql — Core tables for AgentGuard
-- =============================================================================
-- Schema: agentguard (isolated from existing public.* tables)
-- Tables: users, systems, policies, tickets, access_grants, audit_events
-- =============================================================================

-- Create dedicated schema
CREATE SCHEMA IF NOT EXISTS agentguard;

-- Set search path for this migration
SET search_path TO agentguard, public;

-- Users (synced from IdP / HRIS)
CREATE TABLE agentguard.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    department TEXT,
    title TEXT,
    manager_id UUID REFERENCES agentguard.users(id),
    status TEXT DEFAULT 'active',  -- active, suspended, offboarded
    identity_provider TEXT,         -- okta, entra, google
    groups TEXT[] DEFAULT '{}',
    risk_score FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Systems / Applications
CREATE TABLE agentguard.systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    system_type TEXT,              -- saas, infrastructure, internal
    connector_type TEXT,           -- okta, scim, api, manual
    risk_level TEXT DEFAULT 'low', -- low, medium, high, critical
    owner_id UUID REFERENCES agentguard.users(id),
    config JSONB DEFAULT '{}',    -- connector config (encrypted at app layer)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Access Policies
CREATE TABLE agentguard.policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_id UUID REFERENCES agentguard.systems(id),
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
CREATE TABLE agentguard.tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID NOT NULL REFERENCES agentguard.users(id),
    assignee_id UUID REFERENCES agentguard.users(id),
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

CREATE INDEX idx_tickets_requester_status ON agentguard.tickets(requester_id, status);
CREATE INDEX idx_tickets_assignee_status ON agentguard.tickets(assignee_id, status);
CREATE INDEX idx_tickets_type_status ON agentguard.tickets(ticket_type, status);

-- Access Grants (active permissions)
CREATE TABLE agentguard.access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES agentguard.users(id),
    system_id UUID NOT NULL REFERENCES agentguard.systems(id),
    permission TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, active, expired, revoked
    granted_by TEXT,                -- agent or human approver
    justification TEXT,
    risk_score FLOAT,
    granted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    request_id UUID REFERENCES agentguard.tickets(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_grants_user_status ON agentguard.access_grants(user_id, status);
CREATE INDEX idx_grants_system_status ON agentguard.access_grants(system_id, status);
CREATE INDEX idx_grants_expires ON agentguard.access_grants(expires_at) WHERE status = 'active';

-- Audit Events (immutable log)
CREATE TABLE agentguard.audit_events (
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

CREATE INDEX idx_audit_target ON agentguard.audit_events(target_type, target_id);
CREATE INDEX idx_audit_actor ON agentguard.audit_events(actor_type, actor);
CREATE INDEX idx_audit_action ON agentguard.audit_events(action, created_at);

-- Enable RLS on all tables
ALTER TABLE agentguard.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentguard.systems ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentguard.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentguard.access_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentguard.tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentguard.audit_events ENABLE ROW LEVEL SECURITY;

-- updated_at trigger function (in agentguard schema)
CREATE OR REPLACE FUNCTION agentguard.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER set_updated_at_users
    BEFORE UPDATE ON agentguard.users
    FOR EACH ROW EXECUTE FUNCTION agentguard.update_updated_at_column();

CREATE TRIGGER set_updated_at_policies
    BEFORE UPDATE ON agentguard.policies
    FOR EACH ROW EXECUTE FUNCTION agentguard.update_updated_at_column();

CREATE TRIGGER set_updated_at_tickets
    BEFORE UPDATE ON agentguard.tickets
    FOR EACH ROW EXECUTE FUNCTION agentguard.update_updated_at_column();
