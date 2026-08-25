"""
Database layer for the HR Training Dashboard.
Uses SQLAlchemy Core against a PostgreSQL (Neon) database.
"""

import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS training_records (
    id SERIAL PRIMARY KEY,
    programme_name VARCHAR(255) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE,
    quarter VARCHAR(5),
    training_type VARCHAR(20) NOT NULL,
    location VARCHAR(100) NOT NULL,
    participant_names TEXT,
    training_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    training_hours NUMERIC(6,2) NOT NULL,
    participants_count INTEGER NOT NULL,
    total_hours NUMERIC(10,2) NOT NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_from_date ON training_records(from_date);
CREATE INDEX IF NOT EXISTS idx_training_type ON training_records(training_type);
CREATE INDEX IF NOT EXISTS idx_training_location ON training_records(location);
"""


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    """Create (and cache) a single SQLAlchemy engine for the app's lifetime."""
    db_url = st.secrets["postgres"]["url"]
    engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=5)
    return engine


def init_db():
    """Create tables if they don't already exist, and seed the first admin user."""
    engine = get_engine()
    with engine.begin() as conn:
        for statement in SCHEMA_SQL.strip().split(";\n\n"):
            if statement.strip():
                conn.execute(text(statement))
    _seed_first_admin(engine)


def _seed_first_admin(engine):
    """If no users exist yet, create the admin account defined in secrets."""
    from auth.auth import hash_password  # local import avoids circular import

    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if count and count > 0:
            return

        app_cfg = st.secrets.get("app", {})
        username = app_cfg.get("first_admin_username", "admin")
        email = app_cfg.get("first_admin_email", "admin@example.com")
        password = app_cfg.get("first_admin_password", "ChangeMe123!")
        full_name = app_cfg.get("first_admin_fullname", "System Administrator")

        conn.execute(
            text(
                """
                INSERT INTO users (username, email, full_name, password_hash, role)
                VALUES (:username, :email, :full_name, :password_hash, 'admin')
                ON CONFLICT (username) DO NOTHING
                """
            ),
            {
                "username": username,
                "email": email,
                "full_name": full_name,
                "password_hash": hash_password(password),
            },
        )


def run_query(sql: str, params: dict | None = None):
    """Run a SELECT and return rows as a list of dict-like Row objects."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return result.mappings().all()


def run_write(sql: str, params: dict | None = None):
    """Run an INSERT/UPDATE/DELETE inside a transaction."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})
