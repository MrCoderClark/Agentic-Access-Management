-- =============================================================================
-- 004_functions.sql — Utility functions for AgentGuard
-- =============================================================================
-- Schema: agentguard
-- Helper functions for common operations used by the backend.
-- =============================================================================

SET search_path TO agentguard, public;

-- =============================================================================
-- Get user by email (used for auth mapping)
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.get_user_by_email(user_email TEXT)
RETURNS agentguard.users
AS $$
    SELECT * FROM agentguard.users WHERE email = user_email LIMIT 1;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- =============================================================================
-- Get active grants for a user
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.get_user_active_grants(target_user_id UUID)
RETURNS SETOF agentguard.access_grants
AS $$
    SELECT * FROM agentguard.access_grants
    WHERE user_id = target_user_id
      AND status = 'active'
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY granted_at DESC;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- =============================================================================
-- Expire stale grants (called by scheduled job / pg_cron)
-- Returns count of expired grants
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.expire_stale_grants()
RETURNS INT
AS $$
DECLARE
    expired_count INT;
BEGIN
    UPDATE agentguard.access_grants
    SET status = 'expired',
        revoked_at = NOW()
    WHERE status = 'active'
      AND expires_at IS NOT NULL
      AND expires_at <= NOW();

    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- Append audit event (convenience wrapper, ensures immutability)
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.append_audit_event(
    p_actor TEXT,
    p_actor_type TEXT,
    p_action TEXT,
    p_target_type TEXT DEFAULT NULL,
    p_target_id UUID DEFAULT NULL,
    p_decision TEXT DEFAULT NULL,
    p_reasoning TEXT DEFAULT NULL,
    p_confidence FLOAT DEFAULT NULL,
    p_rag_sources JSONB DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS UUID
AS $$
DECLARE
    new_id UUID;
BEGIN
    INSERT INTO agentguard.audit_events (
        actor, actor_type, action, target_type, target_id,
        decision, reasoning, confidence, rag_sources, metadata
    ) VALUES (
        p_actor, p_actor_type, p_action, p_target_type, p_target_id,
        p_decision, p_reasoning, p_confidence, p_rag_sources, p_metadata
    )
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- Get pending tickets for a user (approver view)
-- Returns tickets waiting for approval where the user is a potential approver
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.get_pending_approvals(approver_email TEXT)
RETURNS SETOF agentguard.tickets
AS $$
    SELECT t.* FROM agentguard.tickets t
    WHERE t.status = 'waiting_approval'
      AND t.assignee_id IN (
          SELECT id FROM agentguard.users WHERE email = approver_email
      )
    ORDER BY t.created_at ASC;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- =============================================================================
-- Get system risk summary (for security dashboard)
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.get_risk_summary()
RETURNS TABLE (
    system_id UUID,
    system_name TEXT,
    risk_level TEXT,
    active_grants_count BIGINT,
    avg_risk_score FLOAT,
    expired_unrevoked BIGINT
)
AS $$
    SELECT
        s.id AS system_id,
        s.name AS system_name,
        s.risk_level,
        COUNT(ag.id) FILTER (WHERE ag.status = 'active') AS active_grants_count,
        AVG(ag.risk_score) FILTER (WHERE ag.status = 'active') AS avg_risk_score,
        COUNT(ag.id) FILTER (
            WHERE ag.status = 'active'
              AND ag.expires_at IS NOT NULL
              AND ag.expires_at <= NOW()
        ) AS expired_unrevoked
    FROM agentguard.systems s
    LEFT JOIN agentguard.access_grants ag ON ag.system_id = s.id
    GROUP BY s.id, s.name, s.risk_level
    ORDER BY active_grants_count DESC;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- =============================================================================
-- Grant Supabase roles access to the agentguard schema
-- =============================================================================
GRANT USAGE ON SCHEMA agentguard TO authenticated;
GRANT USAGE ON SCHEMA agentguard TO service_role;
GRANT USAGE ON SCHEMA agentguard TO anon;

-- authenticated: SELECT on all tables (RLS controls row visibility)
GRANT SELECT ON ALL TABLES IN SCHEMA agentguard TO authenticated;
GRANT INSERT ON agentguard.tickets TO authenticated;

-- service_role: full access (backend uses this role)
GRANT ALL ON ALL TABLES IN SCHEMA agentguard TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA agentguard TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA agentguard TO service_role;

-- Ensure future tables inherit these grants
ALTER DEFAULT PRIVILEGES IN SCHEMA agentguard
    GRANT SELECT ON TABLES TO authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA agentguard
    GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA agentguard
    GRANT ALL ON SEQUENCES TO service_role;
