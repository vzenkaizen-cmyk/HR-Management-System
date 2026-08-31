"""
Database layer for the HR Training Dashboard.

Uses SQLAlchemy Core with PostgreSQL (Neon).
"""

import streamlit as st
import bcrypt

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


# ============================================================
# DATABASE SCHEMA
# ============================================================

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    full_name VARCHAR(120),
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
    training_hours NUMERIC(6,2) NOT NULL DEFAULT 0,
    participants_count INTEGER NOT NULL DEFAULT 0,
    total_hours NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_from_date
ON training_records(from_date);

CREATE INDEX IF NOT EXISTS idx_training_type
ON training_records(training_type);

CREATE INDEX IF NOT EXISTS idx_training_power_plant
ON training_records(power_plant);
"""


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    """
    Create and cache the SQLAlchemy engine.

    Streamlit Secrets must contain:

    [postgres]
    url = "postgresql://..."
    """

    db_url = st.secrets["postgres"]["url"]

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )

    return engine


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Create tables if they don't exist.

    Also adds compatibility columns to an existing
    users table created by an earlier version.
    """

    engine = get_engine()

    with engine.begin() as conn:

        # ----------------------------------------------------
        # Create tables
        # ----------------------------------------------------

        for statement in SCHEMA_SQL.strip().split(";\n\n"):

            statement = statement.strip()

            if statement:
                conn.execute(text(statement))

        # ----------------------------------------------------
        # Compatibility for existing Neon database
        # ----------------------------------------------------

        conn.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS username VARCHAR(50)
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS name VARCHAR(120)
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS full_name VARCHAR(120)
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS role VARCHAR(20)
                DEFAULT 'user'
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP
                DEFAULT NOW()
            """)
        )

        # ----------------------------------------------------
        # Keep name and full_name synchronized
        # ----------------------------------------------------

        conn.execute(
            text("""
                UPDATE users
                SET name = COALESCE(name, full_name, username)
                WHERE name IS NULL
            """)
        )

        conn.execute(
            text("""
                UPDATE users
                SET full_name = COALESCE(full_name, name, username)
                WHERE full_name IS NULL
            """)
        )

    # --------------------------------------------------------
    # Create first admin
    # --------------------------------------------------------

    _seed_first_admin(engine)


# ============================================================
# FIRST ADMIN
# ============================================================

def _seed_first_admin(engine):
    """
    Create the first administrator if no users exist.

    Credentials can be configured through Streamlit Secrets:

    [app]
    first_admin_username = "admin"
    first_admin_email = "admin@example.com"
    first_admin_password = "ChangeMe123!"
    first_admin_fullname = "System Administrator"
    """

    with engine.begin() as conn:

        count = conn.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar()

        # Don't create another admin if users already exist
        if count and count > 0:
            return

        # ----------------------------------------------------
        # Read admin configuration
        # ----------------------------------------------------

        app_cfg = st.secrets.get("app", {})

        username = app_cfg.get(
            "first_admin_username",
            "admin"
        )

        email = app_cfg.get(
            "first_admin_email",
            "admin@example.com"
        )

        password = app_cfg.get(
            "first_admin_password",
            "ChangeMe123!"
        )

        full_name = app_cfg.get(
            "first_admin_fullname",
            "System Administrator"
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Generate password hash BEFORE INSERT
        # ----------------------------------------------------

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ----------------------------------------------------
        # Insert admin
        # ----------------------------------------------------

        conn.execute(
            text("""
                INSERT INTO users (
                    username,
                    email,
                    name,
                    full_name,
                    password_hash,
                    role
                )
                VALUES (
                    :username,
                    :email,
                    :name,
                    :full_name,
                    :password_hash,
                    'admin'
                )
                ON CONFLICT (username) DO NOTHING
            """),
            {
                "username": username,
                "email": email,
                "name": full_name,
                "full_name": full_name,
                "password_hash": password_hash,
            },
        )


# ============================================================
# SELECT QUERY
# ============================================================

def run_query(
    sql: str,
    params: dict | None = None
):
    """
    Execute a SELECT query and return rows as dictionaries.
    """

    engine = get_engine()

    with engine.connect() as conn:

        result = conn.execute(
            text(sql),
            params or {}
        )

        return result.mappings().all()


# ============================================================
# INSERT / UPDATE / DELETE
# ============================================================

def run_write(
    sql: str,
    params: dict | None = None
):
    """
    Execute INSERT, UPDATE or DELETE.
    """

    engine = get_engine()

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            params or {}
        )
