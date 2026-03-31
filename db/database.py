"""SQLite database helpers for storing and retrieving survey responses."""

import json
import os
import sqlite3

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "survey_responses.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create the responses table if it doesn't exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            school_board TEXT,
            subjects_taught TEXT,
            grade_levels TEXT,
            experience_years TEXT,
            city_tier TEXT,
            ai_tools_used TEXT,
            discovery_channel TEXT,
            ai_usage_duration TEXT,
            freq_lesson_plans TEXT,
            freq_assessments TEXT,
            freq_personalized TEXT,
            freq_content TEXT,
            freq_admin TEXT,
            freq_engagement TEXT,
            freq_grading TEXT,
            freq_parent_comm TEXT,
            innovative_uses TEXT,
            innovative_desc TEXT,
            impact_learning TEXT,
            impact_engagement TEXT,
            impact_individual TEXT,
            impact_performance TEXT,
            impact_creativity TEXT,
            barriers TEXT,
            support_needed TEXT,
            future_likelihood TEXT,
            future_priority TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_response(data: dict):
    """Insert a single survey response. Lists are JSON-encoded automatically."""
    conn = get_connection()
    processed = {}
    for key, value in data.items():
        if isinstance(value, list):
            processed[key] = json.dumps(value)
        else:
            processed[key] = value

    columns = ", ".join(processed.keys())
    placeholders = ", ".join(["?"] * len(processed))
    values = list(processed.values())

    conn.execute(
        f"INSERT INTO responses ({columns}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
    conn.close()


def get_all_responses() -> pd.DataFrame:
    """Read all responses into a DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM responses ORDER BY submitted_at DESC", conn)
    conn.close()
    return df


def get_response_count() -> int:
    """Return total number of responses."""
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM responses")
    count = cursor.fetchone()[0]
    conn.close()
    return count
