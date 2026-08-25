"""
Authentication: signup, login, password hashing, and session-state helpers.

Passwords are hashed with bcrypt and are never stored in plain text.
"""

import re

import bcrypt
import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database.db import get_engine


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(plain_password: str) -> str:
    """Hash a password using bcrypt."""
    if not isinstance(plain_password, str):
        raise ValueError("Password must be a string.")

    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:
    """Verify a plain password against a bcrypt hash."""

    if not plain_password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDATION
# ============================================================

def is_valid_email(email: str) -> bool:
    """Validate email format."""

    if not email:
        return False

    return re.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email
    ) is not None


def validate_username(username: str) -> str:
    """Validate and normalize username."""

    username = (username or "").strip().lower()

    if not username:
        raise ValueError("Username is required.")

    if len(username) < 3:
        raise ValueError(
            "Username must be at least 3 characters."
        )

    if len(username) > 50:
        raise ValueError(
            "Username must not exceed 50 characters."
        )

    if not re.match(r"^[a-z0-9_.]+$", username):
        raise ValueError(
            "Username may only contain lowercase letters, "
            "numbers, '.' and '_'."
        )

    return username


def validate_email(email: str) -> str:
    """Validate and normalize email."""

    email = (email or "").strip().lower()

    if not is_valid_email(email):
        raise ValueError(
            "Please enter a valid email address."
        )

    if len(email) > 120:
        raise ValueError(
            "Email address is too long."
        )

    return email


def validate_full_name(full_name: str) -> str:
    """Validate full name."""

    full_name = (full_name or "").strip()

    if not full_name:
        raise ValueError(
            "Full name is required."
        )

    if len(full_name) > 120:
        raise ValueError(
            "Full name must not exceed 120 characters."
        )

    return full_name


def validate_password(password: str) -> str:
    """Validate password."""

    if not password:
        raise ValueError(
            "Password is required."
        )

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    return password


# ============================================================
# USER CHECKS
# ============================================================

def username_or_email_exists(
    username: str,
    email: str
) -> bool:
    """Check whether username or email already exists."""

    username = username.strip().lower()
    email = email.strip().lower()

    engine = get_engine()

    with engine.connect() as conn:

        row = conn.execute(
            text(
                """
                SELECT id
                FROM users
                WHERE username = :username
                   OR email = :email
                LIMIT 1
                """
            ),
            {
                "username": username,
                "email": email,
            },
        ).first()

    return row is not None


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    username: str,
    email: str,
    full_name: str,
    password: str,
    role: str = "user"
):
    """
    Create a new user account.

    The current database contains both:
        name
        full_name

    Therefore both columns are populated.
    """

    # ----------------------------
    # Validate inputs
    # ----------------------------

    username = validate_username(username)
    email = validate_email(email)
    full_name = validate_full_name(full_name)
    password = validate_password(password)

    role = (role or "user").strip().lower()

    if role not in ("user", "admin"):
        role = "user"

    # ----------------------------
    # Check duplicate user
    # ----------------------------

    if username_or_email_exists(username, email):
        raise ValueError(
            "That username or email is already registered."
        )

    # ----------------------------
    # Hash password
    # ----------------------------

    password_hash = hash_password(password)

    # ----------------------------
    # Insert user
    # ----------------------------

    engine = get_engine()

    try:

        with engine.begin() as conn:

            conn.execute(
                text(
                    """
                    INSERT INTO users
                    (
                        username,
                        email,
                        name,
                        full_name,
                        password_hash,
                        role
                    )
                    VALUES
                    (
                        :username,
                        :email,
                        :name,
                        :full_name,
                        :password_hash,
                        :role
                    )
                    """
                ),
                {
                    "username": username,
                    "email": email,
                    "name": full_name,
                    "full_name": full_name,
                    "password_hash": password_hash,
                    "role": role,
                },
            )

    except IntegrityError as e:

        error_message = str(e).lower()

        if "username" in error_message:
            raise ValueError(
                "That username is already registered."
            )

        if "email" in error_message:
            raise ValueError(
                "That email address is already registered."
            )

        raise ValueError(
            "Unable to create the account. "
            "Please check the database configuration."
        )


# ============================================================
# AUTHENTICATE
# ============================================================

def authenticate(
    username_or_email: str,
    password: str
):
    """
    Authenticate a user.

    Returns:
        dict -> successful login
        None -> invalid credentials
    """

    identifier = (
        username_or_email or ""
    ).strip().lower()

    if not identifier or not password:
        return None

    engine = get_engine()

    with engine.connect() as conn:

        row = conn.execute(
            text(
                """
                SELECT
                    id,
                    username,
                    email,
                    name,
                    full_name,
                    password_hash,
                    role,
                    created_at
                FROM users
                WHERE username = :identifier
                   OR email = :identifier
                LIMIT 1
                """
            ),
            {
                "identifier": identifier
            },
        ).mappings().first()

    if not row:
        return None

    stored_hash = row.get("password_hash")

    if not stored_hash:
        return None

    if not verify_password(
        password,
        stored_hash
    ):
        return None

    return dict(row)


# ============================================================
# LOGIN
# ============================================================

def login_user(user: dict):
    """Store authenticated user in Streamlit session state."""

    st.session_state["auth_user"] = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": (
            user.get("full_name")
            or user.get("name")
            or ""
        ),
        "role": user.get("role", "user"),
    }


# ============================================================
# LOGOUT
# ============================================================

def logout_user():
    """Log out the current user."""

    st.session_state.pop(
        "auth_user",
        None
    )


# ============================================================
# CURRENT USER
# ============================================================

def current_user():
    """Return currently logged-in user."""

    return st.session_state.get(
        "auth_user"
    )


def is_logged_in() -> bool:
    """Return True if a user is logged in."""

    return (
        "auth_user" in st.session_state
        and st.session_state["auth_user"] is not None
    )


# ============================================================
# ADMIN
# ============================================================

def is_admin() -> bool:
    """Return True if current user is an administrator."""

    user = current_user()

    if not user:
        return False

    return user.get("role") == "admin"


# ============================================================
# LOGIN REQUIREMENT
# ============================================================

def require_login():
    """
    Call at the top of protected pages.
    Stops rendering if the user is not logged in.
    """

    if not is_logged_in():

        st.warning(
            "Please log in from the **Home** page "
            "to access this section."
        )

        st.stop()


# ============================================================
# PASSWORD CHANGE
# ============================================================

def change_password(
    user_id: int,
    new_password: str
):
    """Change the password of an existing user."""

    new_password = validate_password(
        new_password
    )

    password_hash = hash_password(
        new_password
    )

    engine = get_engine()

    with engine.begin() as conn:

        result = conn.execute(
            text(
                """
                UPDATE users
                SET password_hash = :password_hash
                WHERE id = :user_id
                """
            ),
            {
                "password_hash": password_hash,
                "user_id": user_id,
            },
        )

        if result.rowcount == 0:
            raise ValueError(
                "User account was not found."
            )
