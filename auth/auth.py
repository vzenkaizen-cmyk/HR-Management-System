"""
Authentication: signup, login, password hashing, and session-state helpers.
Passwords are hashed with bcrypt — never stored or compared in plain text.
"""

import re
import bcrypt
import streamlit as st
from sqlalchemy import text

from database.db import get_engine


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or "") is not None


def username_or_email_exists(username: str, email: str) -> bool:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM users WHERE username = :u OR email = :e"),
            {"u": username, "e": email},
        ).first()
    return row is not None


def create_user(username: str, email: str, full_name: str, password: str, role: str = "user"):
    """Create a new user account. Raises ValueError on validation failure."""
    username = username.strip().lower()
    email = email.strip().lower()

    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters.")
    if not re.match(r"^[a-z0-9_.]+$", username):
        raise ValueError("Username may only contain lowercase letters, numbers, '.' and '_'.")
    if not is_valid_email(email):
        raise ValueError("Please enter a valid email address.")
    if not full_name.strip():
        raise ValueError("Full name is required.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if username_or_email_exists(username, email):
        raise ValueError("That username or email is already registered.")

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO users (username, email, full_name, password_hash, role)
                VALUES (:username, :email, :full_name, :password_hash, :role)
                """
            ),
            {
                "username": username,
                "email": email,
                "full_name": full_name.strip(),
                "password_hash": hash_password(password),
                "role": role,
            },
        )


def authenticate(username_or_email: str, password: str):
    """Return the user row (dict) if credentials are valid, else None."""
    identifier = username_or_email.strip().lower()
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM users WHERE username = :u OR email = :u"),
            {"u": identifier},
        ).mappings().first()

    if row and verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def login_user(user: dict):
    st.session_state["auth_user"] = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user["role"],
    }


def logout_user():
    st.session_state.pop("auth_user", None)


def current_user():
    return st.session_state.get("auth_user")


def is_logged_in() -> bool:
    return "auth_user" in st.session_state


def is_admin() -> bool:
    user = current_user()
    return bool(user and user.get("role") == "admin")


def require_login():
    """Call at the top of every page. Stops rendering if not logged in."""
    if not is_logged_in():
        st.warning("Please log in from the **Home** page to access this section.")
        st.stop()


def change_password(user_id: int, new_password: str):
    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :ph WHERE id = :id"),
            {"ph": hash_password(new_password), "id": user_id},
        )
