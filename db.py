import json
import os
import uuid

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


SCHEMA_SQL = """
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
"""


def database_url():
    value = os.getenv("DATABASE_URL", "").strip()

    if not value:
        raise RuntimeError(
            "DATABASE_URL is missing. Configure PostgreSQL before starting URIE."
        )

    return value


def connection():
    return psycopg.connect(
        database_url(),
        row_factory=dict_row,
        connect_timeout=10,
    )


def init_db():
    with connection() as conn:
        conn.execute(SCHEMA_SQL)
        conn.commit()


def create_evaluation(payload, short_report, full_report):
    evaluation_id = uuid.uuid4()

    values = {
        "id": evaluation_id,
        "student_name": payload["student_name"],
        "parent_name": payload["parent_name"],
        "parent_phone": payload["parent_phone"],
        "parent_email": payload["parent_email"],
        "competition": payload["competition"],
        "stage": payload["stage"],
        "grade": payload.get("grade", ""),
        "country": payload.get("country", ""),
        "content": payload["content"],
        "evidence": payload.get("evidence", ""),
        "constraints": payload.get("constraints", ""),
        "short_report": Jsonb(short_report),
        "full_report": Jsonb(full_report),
    }

    with connection() as conn:
        conn.execute(
            """
            INSERT INTO evaluations (
                id,
                student_name,
                parent_name,
                parent_phone,
                parent_email,
                competition,
                stage,
                grade,
                country,
                content,
                evidence,
                constraints,
                short_report,
                full_report
            )
            VALUES (
                %(id)s,
                %(student_name)s,
                %(parent_name)s,
                %(parent_phone)s,
                %(parent_email)s,
                %(competition)s,
                %(stage)s,
                %(grade)s,
                %(country)s,
                %(content)s,
                %(evidence)s,
                %(constraints)s,
                %(short_report)s,
                %(full_report)s
            )
            """,
            values,
        )
        conn.commit()

    return str(evaluation_id)


def list_evaluations():
    with connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                student_name,
                parent_name,
                parent_email,
                competition,
                stage,
                status,
                mentor_released,
                created_at,
                updated_at
            FROM evaluations
            ORDER BY created_at DESC
            """
        ).fetchall()


def get_evaluation(evaluation_id):
    try:
        parsed_id = uuid.UUID(str(evaluation_id))
    except (ValueError, TypeError, AttributeError):
        return None

    with connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                student_name,
                parent_name,
                parent_phone,
                parent_email,
                competition,
                stage,
                grade,
                country,
                content,
                evidence,
                constraints,
                short_report,
                full_report,
                status,
                mentor_released,
                created_at,
                updated_at
            FROM evaluations
            WHERE id = %s
            """,
            (parsed_id,),
        ).fetchone()


def release_evaluation(evaluation_id):
    try:
        parsed_id = uuid.UUID(str(evaluation_id))
    except (ValueError, TypeError, AttributeError):
        return False

    with connection() as conn:
        result = conn.execute(
            """
            UPDATE evaluations
            SET
                mentor_released = TRUE,
                status = 'released',
                updated_at = NOW()
            WHERE id = %s
            """,
            (parsed_id,),
        )
        conn.commit()

    return result.rowcount == 1