-- Distributed Ledger PostgreSQL Schema
-- Apply with: psql -h postgres.kiloclaw -U kiloclaw -d ledger -f ledger.sql

-- Transactions table (immutable event log)
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    trace_id VARCHAR(64) NOT NULL,
    node VARCHAR(64) NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    cost DECIMAL(15, 2) NOT NULL,
    roi DECIMAL(10, 4) NOT NULL,
    attribution JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transactions_trace ON transactions(trace_id);
CREATE INDEX idx_transactions_node ON transactions(node);
CREATE INDEX idx_transactions_created ON transactions(created_at DESC);

-- Agent performance metrics (aggregated)
CREATE TABLE IF NOT EXISTS agent_metrics (
    id BIGSERIAL PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    total_cost DECIMAL(15, 2) NOT NULL,
    total_transactions INTEGER NOT NULL,
    avg_roi DECIMAL(10, 4) NOT NULL,
    replication_factor INTEGER DEFAULT 1,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_metrics_agent ON agent_metrics(agent_id);
CREATE INDEX idx_agent_metrics_period ON agent_metrics(period_start DESC);

-- Graph edge weights (mutable, for learning)
CREATE TABLE IF NOT EXISTS graph_edges (
    id BIGSERIAL PRIMARY KEY,
    source_node VARCHAR(64) NOT NULL,
    target_node VARCHAR(64) NOT NULL,
    weight DECIMAL(5, 4) NOT NULL DEFAULT 1.0,
    success_count BIGINT DEFAULT 0,
    failure_count BIGINT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source_node, target_node)
);

-- Agent budgets and survival
CREATE TABLE IF NOT EXISTS agent_budgets (
    agent_id VARCHAR(64) PRIMARY KEY,
    allocated_budget DECIMAL(15, 2) NOT NULL,
    spent_budget DECIMAL(15, 2) DEFAULT 0,
    roi_threshold DECIMAL(5, 2) DEFAULT 1.5,
    alive BOOLEAN DEFAULT TRUE,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Exactly-once processing保障
CREATE TABLE IF NOT EXISTS processed_events (
    trace_id VARCHAR(64) PRIMARY KEY,
    node VARCHAR(64) NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Materialized view for real-time ROI
CREATE MATERIALIZED VIEW IF NOT EXISTS agent_roi_summary AS
SELECT 
    agent_id,
    COUNT(*) as transaction_count,
    SUM(total_value) as total_value,
    SUM(total_cost) as total_cost,
    CASE WHEN SUM(total_cost) > 0 THEN SUM(total_value) / SUM(total_cost) ELSE 0 END as roi
FROM (
    SELECT node as agent_id, value as total_value, cost as total_cost
    FROM transactions
) sub
GROUP BY agent_id;

-- Refresh view periodically
CREATE OR REPLACE FUNCTION refresh_roi_summary()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW agent_roi_summary;
END;
$$ LANGUAGE plpgsql;