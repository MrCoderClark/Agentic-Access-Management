-- =============================================================================
-- 003_rls_policies.sql — Row Level Security policies for AgentGuard
-- =============================================================================
-- Schema: agentguard
-- Defines RLS policies for all tables.
-- Uses Supabase Auth JWT claims (auth.uid(), auth.jwt()).
-- Service role bypasses RLS for backend operations.
-- =============================================================================

SET search_path TO agentguard, public;

-- =============================================================================
-- USERS table
-- - Authenticated users can read all users (needed for directory lookups)
-- - Only service role (backend) can insert/update/delete
-- =============================================================================
CREATE POLICY users_select_authenticated ON agentguard.users
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY users_insert_service ON agentguard.users
    FOR INSERT TO service_role
    WITH CHECK (true);

CREATE POLICY users_update_service ON agentguard.users
    FOR UPDATE TO service_role
    USING (true) WITH CHECK (true);

CREATE POLICY users_delete_service ON agentguard.users
    FOR DELETE TO service_role
    USING (true);

-- =============================================================================
-- SYSTEMS table
-- - Authenticated users can read all systems
-- - Only service role can modify (admin actions go through backend)
-- =============================================================================
CREATE POLICY systems_select_authenticated ON agentguard.systems
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY systems_insert_service ON agentguard.systems
    FOR INSERT TO service_role
    WITH CHECK (true);

CREATE POLICY systems_update_service ON agentguard.systems
    FOR UPDATE TO service_role
    USING (true) WITH CHECK (true);

CREATE POLICY systems_delete_service ON agentguard.systems
    FOR DELETE TO service_role
    USING (true);

-- =============================================================================
-- POLICIES table
-- - Authenticated users can read active policies
-- - Service role can manage all policies (including inactive for admin views)
-- =============================================================================
CREATE POLICY policies_select_authenticated ON agentguard.policies
    FOR SELECT TO authenticated
    USING (is_active = true);

CREATE POLICY policies_all_service ON agentguard.policies
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

-- =============================================================================
-- TICKETS table
-- - Users can read their own tickets (requester or assignee)
-- - Service role has full access (agents create/update tickets)
-- =============================================================================
CREATE POLICY tickets_select_own ON agentguard.tickets
    FOR SELECT TO authenticated
    USING (
        requester_id IN (
            SELECT id FROM agentguard.users WHERE email = auth.jwt()->>'email'
        )
        OR assignee_id IN (
            SELECT id FROM agentguard.users WHERE email = auth.jwt()->>'email'
        )
    );

CREATE POLICY tickets_insert_authenticated ON agentguard.tickets
    FOR INSERT TO authenticated
    WITH CHECK (
        requester_id IN (
            SELECT id FROM agentguard.users WHERE email = auth.jwt()->>'email'
        )
    );

CREATE POLICY tickets_all_service ON agentguard.tickets
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

-- =============================================================================
-- ACCESS_GRANTS table
-- - Users can read their own grants
-- - Service role has full access (provisioning agent manages grants)
-- =============================================================================
CREATE POLICY grants_select_own ON agentguard.access_grants
    FOR SELECT TO authenticated
    USING (
        user_id IN (
            SELECT id FROM agentguard.users WHERE email = auth.jwt()->>'email'
        )
    );

CREATE POLICY grants_all_service ON agentguard.access_grants
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

-- =============================================================================
-- AUDIT_EVENTS table
-- - Authenticated users can read audit events (filtered by role in app layer)
-- - Only service role can insert (append-only, no update/delete for anyone)
-- =============================================================================
CREATE POLICY audit_select_authenticated ON agentguard.audit_events
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY audit_insert_service ON agentguard.audit_events
    FOR INSERT TO service_role
    WITH CHECK (true);

-- No UPDATE or DELETE policies — audit log is immutable

-- =============================================================================
-- DOCUMENTS table (RAG vector store)
-- - Authenticated users can read documents (for knowledge base queries)
-- - Only service role can insert/update/delete (RAG pipeline manages docs)
-- =============================================================================
CREATE POLICY documents_select_authenticated ON agentguard.documents
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY documents_insert_service ON agentguard.documents
    FOR INSERT TO service_role
    WITH CHECK (true);

CREATE POLICY documents_update_service ON agentguard.documents
    FOR UPDATE TO service_role
    USING (true) WITH CHECK (true);

CREATE POLICY documents_delete_service ON agentguard.documents
    FOR DELETE TO service_role
    USING (true);
