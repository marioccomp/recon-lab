CREATE TABLE IF NOT EXISTS reconciliation_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    internal_file TEXT NOT NULL,
    external_file TEXT NOT NULL,
    output_path TEXT,
    summary JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reconciliation_results (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) NOT NULL REFERENCES reconciliation_runs(run_id) ON DELETE CASCADE,
    operation_id VARCHAR(100),
    has_difference BOOLEAN NOT NULL,
    difference_count INTEGER NOT NULL,
    internal_amount NUMERIC(18, 2),
    external_amount NUMERIC(18, 2),
    amount_difference NUMERIC(18, 2),
    internal_status VARCHAR(50),
    external_status VARCHAR(50),
    internal_date DATE,
    external_date DATE,
    internal_occurrences INTEGER,
    external_occurrences INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reconciliation_issues (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) NOT NULL REFERENCES reconciliation_runs(run_id) ON DELETE CASCADE,
    operation_id VARCHAR(100),
    issue_type VARCHAR(50) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);