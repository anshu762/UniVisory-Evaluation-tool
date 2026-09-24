CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY,
    student_name TEXT NOT NULL,
    parent_name TEXT NOT NULL,
    parent_phone TEXT NOT NULL,
    parent_email TEXT NOT NULL,
    competition TEXT NOT NULL,
    stage TEXT NOT NULL,
    grade TEXT NOT NULL DEFAULT '',
    country TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    evidence TEXT NOT NULL DEFAULT '',
    constraints TEXT NOT NULL DEFAULT '',
    short_report JSONB NOT NULL,
    full_report JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'under_mentor_review',
    mentor_released BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS evaluations_created_at_idx
    ON evaluations (created_at DESC);

CREATE INDEX IF NOT EXISTS evaluations_status_idx
    ON evaluations (status);

CREATE INDEX IF NOT EXISTS evaluations_competition_idx
    ON evaluations (competition);