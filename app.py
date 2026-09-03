from pathlib import Path
import html
import re

import pandas as pd
import streamlit as st

from database.db import init_db, run_query, run_write
from auth.auth import (
    authenticate,
    create_user,
    login_user,
    logout_user,
    is_logged_in,
    current_user,
    change_password,
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HR Training Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    st.set_option("client.showSidebarNavigation", False)
except Exception:
    pass


# ============================================================
# LIGHT THEME / UI
# ============================================================

def inject_css():
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
    background: #f4f9fd !important;
    color: #173f5c !important;
}

.stApp {
    background: linear-gradient(135deg,#f7fbff 0%,#edf6ff 52%,#e5f0fa 100%) !important;
    color: #173f5c !important;
}

:root, html {
    color-scheme: light !important;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}

#MainMenu, footer {
    visibility: hidden !important;
}

header {
    background: transparent !important;
}

/* Remove unwanted Streamlit input hints */
[data-testid="InputInstructions"],
div[data-testid="InputInstructions"],
[data-testid="stTooltipIcon"],
[data-testid="stTextInput"] [data-testid="InputInstructions"],
[data-testid="stTextInput"] small {
    display: none !important;
}

/* Typography */
h1, h2, h3, h4,
.stMarkdown, .stMarkdown p,
.stCaption, .stCaption p,
[data-testid="stText"],
[data-testid="stMarkdownContainer"] {
    color: #173f5c !important;
}

.app-title {
    color: #073b66 !important;
    font-size: 42px !important;
    font-weight: 800 !important;
    line-height: 1.15 !important;
    margin-bottom: 6px !important;
}

.app-subtitle {
    color: #365c76 !important;
    font-size: 17px !important;
    font-weight: 500 !important;
    margin-bottom: 22px !important;
}

/* Authentication */
.auth-area {
    max-width: 470px;
    margin: 18px auto 0 auto;
}

.auth-heading {
    color: #0b3e63 !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    margin-bottom: 4px !important;
}

.auth-description {
    color: #527089 !important;
    font-size: 14px !important;
    margin-bottom: 18px !important;
}

button[data-baseweb="tab"] {
    color: #214d6b !important;
    font-weight: 750 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #087ea4 !important;
}

/* Inputs */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label,
.stDateInput label,
.stFileUploader label {
    color: #173f5c !important;
    font-weight: 700 !important;
}

div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #aebfd0 !important;
    border-radius: 9px !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
[data-testid="stDateInput"] input {
    background: #ffffff !important;
    color: #172b3d !important;
    -webkit-text-fill-color: #172b3d !important;
    caret-color: #0879a5 !important;
}

div[data-baseweb="input"] input::placeholder,
div[data-baseweb="base-input"] input::placeholder {
    color: #73879a !important;
    opacity: 1 !important;
}

/* Selectbox text */
div[data-baseweb="select"] * {
    color: #173f5c !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
    min-height: 43px !important;
    border-radius: 9px !important;
    font-weight: 750 !important;
}

/* Primary */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: #0879a5 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid #0879a5 !important;
}

.stButton > button[kind="primary"] *,
.stFormSubmitButton > button[kind="primary"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    background: #075f82 !important;
    border-color: #075f82 !important;
}

/* Secondary/dark buttons */
.stButton > button:not([kind="primary"]),
.stDownloadButton > button {
    background: #13233f !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid #13233f !important;
}

.stButton > button:not([kind="primary"]) *,
.stDownloadButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button:not([kind="primary"]):hover,
.stDownloadButton > button:hover {
    background: #1d355d !important;
    border-color: #1d355d !important;
}

/* File uploader */
section[data-testid="stFileUploaderDropzone"] {
    background: #13233f !important;
    border: 1px solid #2b4168 !important;
    border-radius: 12px !important;
}

section[data-testid="stFileUploaderDropzone"] *,
section[data-testid="stFileUploaderDropzone"] span,
section[data-testid="stFileUploaderDropzone"] small,
section[data-testid="stFileUploaderDropzone"] p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

section[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;
    color: #13233f !important;
    -webkit-text-fill-color: #13233f !important;
    border: 1px solid #d5e2ef !important;
}

section[data-testid="stFileUploaderDropzone"] button * {
    color: #13233f !important;
    -webkit-text-fill-color: #13233f !important;
}

/* Home cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #d2e1ed !important;
    border-radius: 17px !important;
    box-shadow: 0 7px 22px rgba(15,69,105,0.08) !important;
}

.home-card-icon {
    font-size: 31px !important;
    margin-bottom: 7px;
}

.home-card-title {
    color: #083b66 !important;
    font-size: 21px !important;
    font-weight: 800 !important;
}

.home-card-text {
    color: #49677c !important;
    font-size: 14px !important;
    line-height: 1.55 !important;
    min-height: 70px;
}

/* Welcome */
.welcome-box {
    background: linear-gradient(135deg,#0a4778 0%,#12699f 100%) !important;
    border-radius: 18px;
    padding: 27px 30px;
    margin: 8px 0 24px 0;
    box-shadow: 0 10px 28px rgba(7,59,102,0.16);
}

.welcome-title {
    color: #ffffff !important;
    font-size: 27px !important;
    font-weight: 800 !important;
    margin-bottom: 7px;
}

.welcome-text {
    color: #eef8ff !important;
    font-size: 16px !important;
    line-height: 1.55 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #d7e5ef !important;
    border-radius: 13px !important;
    padding: 15px !important;
}

[data-testid="stMetricLabel"] {
    color: #527089 !important;
}

[data-testid="stMetricValue"] {
    color: #0b3d63 !important;
}

/* Alerts */
[data-testid="stAlert"] {
    color: #173f5c !important;
    background: #eef6fc !important;
    border: 1px solid #c8dceb !important;
}

[data-testid="stAlert"] * {
    color: #173f5c !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border: 1px solid #d2e1ed !important;
    border-radius: 10px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#073556 0%,#0a4772 58%,#0b507e 100%) !important;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

.sidebar-brand {
    text-align: center;
    padding: 8px 3px 16px 3px;
}

.sidebar-brand-icon {
    font-size: 31px;
    line-height: 1.1;
}

.sidebar-brand-title {
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    margin-top: 5px;
}

.sidebar-user {
    background: rgba(255,255,255,0.11);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 13px;
    padding: 13px;
    margin: 4px 0 17px 0;
}

.sidebar-user-name {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 800;
}

.sidebar-user-role {
    color: #d8efff !important;
    font-size: 12px;
    margin-top: 4px;
}

.sidebar-section {
    color: #b9e4ff !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin: 10px 0 7px 3px;
}

/* Page links: force nested text to white */
section[data-testid="stSidebar"] [data-testid="stPageLink"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    background: rgba(255,255,255,0.07) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 9px !important;
    margin-bottom: 7px !important;
    text-decoration: none !important;
}

section[data-testid="stSidebar"] [data-testid="stPageLink"] *,
section[data-testid="stSidebar"] [data-testid="stPageLink"] a *,
section[data-testid="stSidebar"] [data-testid="stPageLink"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover,
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,0.18) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    text-align: left !important;
    justify-content: flex-start !important;
}

section[data-testid="stSidebar"] .stButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.sidebar-divider {
    height: 1px;
    background: rgba(255,255,255,0.20);
    margin: 17px 0;
}

/* Data entry form */
.form-section-title {
    color: #083b66 !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    margin-bottom: 10px;
}

.form-note {
    color: #527089 !important;
    font-size: 14px !important;
}

.section-card {
    background: #ffffff;
    border: 1px solid #d2e1ed;
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 16px;
}

/* Dashboard filter area */
.filter-box {
    background: #ffffff;
    border: 1px solid #d2e1ed;
    border-radius: 14px;
    padding: 15px 18px;
    margin-bottom: 18px;
}

        /* ============================================================
           LOGIN PAGE — SIDEBAR AUTH + FULL RIGHT-SIDE STAFF IMAGE
           ============================================================ */

        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,#073556 0%,#0a4772 58%,#0b507e 100%
            ) !important;
        }

        .login-sidebar-header {
            text-align: center;
            padding: 12px 4px 20px 4px;
        }

        .login-sidebar-icon {
            font-size: 34px !important;
            line-height: 1.1;
            margin-bottom: 5px;
        }

        .login-sidebar-title {
            color: #ffffff !important;
            font-size: 20px !important;
            font-weight: 800 !important;
            line-height: 1.25;
        }

        .login-sidebar-subtitle {
            color: #d8efff !important;
            font-size: 12px !important;
            margin-top: 6px;
        }

        section[data-testid="stSidebar"] [data-baseweb="tab-list"] {
            background: transparent !important;
            width: 100% !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="tab"],
        section[data-testid="stSidebar"] button[role="tab"] {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 750 !important;
            background: transparent !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="tab"] *,
        section[data-testid="stSidebar"] button[role="tab"] * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        section[data-testid="stSidebar"] .auth-heading {
            color: #ffffff !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            margin-top: 14px !important;
        }

        section[data-testid="stSidebar"] .auth-description {
            color: #d8efff !important;
            font-size: 13px !important;
            line-height: 1.45 !important;
            margin-bottom: 15px !important;
        }

        section[data-testid="stSidebar"] .stTextInput label {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="input"],
        section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
            background: #ffffff !important;
            border: 1px solid #aebfd0 !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="input"] input,
        section[data-testid="stSidebar"] div[data-baseweb="base-input"] input {
            background: #ffffff !important;
            color: #172b3d !important;
            -webkit-text-fill-color: #172b3d !important;
        }

        section[data-testid="stSidebar"] .stFormSubmitButton > button {
            width: 100% !important;
        }

        .login-staff-image {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .login-staff-image img {
            display: block !important;
            width: 100% !important;
            max-width: none !important;
            height: auto !important;
            margin: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }

</style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# DATABASE
# ============================================================

try:
    init_db()
except Exception:
    st.error(
        "Unable to connect to the HR database. "
        "Please check [postgres].url in Streamlit Secrets."
    )
    st.stop()


# ============================================================
# SESSION HELPERS
# ============================================================

def user_now():
    return current_user()


def require_user():
    user = current_user()
    if not user:
        st.warning("Please log in from the Home page to access this section.")
        st.stop()
    return user


def logout():
    logout_user()
    st.session_state.clear()
    st.rerun()


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_training_records():
    rows = run_query(
        """
        SELECT
            tr.id,
            tr.programme_name,
            tr.from_date,
            tr.to_date,
            tr.quarter,
            tr.training_type,
            tr.location,
            tr.participant_names,
            tr.training_cost,
            tr.training_hours,
            tr.participants_count,
            tr.total_hours,
            tr.created_by,
            tr.created_at,
            COALESCE(u.full_name, u.name, u.username, '') AS created_by_name
        FROM training_records tr
        LEFT JOIN users u ON u.id = tr.created_by
        ORDER BY tr.from_date DESC, tr.id DESC
        """
    )
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return df

    for col in ["from_date", "to_date", "created_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in [
        "training_cost",
        "training_hours",
        "participants_count",
        "total_hours",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def get_locations():
    rows = run_query(
        """
        SELECT DISTINCT location
        FROM training_records
        WHERE location IS NOT NULL
          AND TRIM(location) <> ''
        ORDER BY location
        """
    )
    return [str(r["location"]) for r in rows]


def insert_training_record(
    programme_name,
    from_date,
    to_date,
    quarter,
    training_type,
    location,
    participant_names,
    training_cost,
    training_hours,
    participants_count,
    total_hours,
    created_by,
):
    run_write(
        """
        INSERT INTO training_records (
            programme_name,
            from_date,
            to_date,
            quarter,
            training_type,
            location,
            participant_names,
            training_cost,
            training_hours,
            participants_count,
            total_hours,
            created_by
        )
        VALUES (
            :programme_name,
            :from_date,
            :to_date,
            :quarter,
            :training_type,
            :location,
            :participant_names,
            :training_cost,
            :training_hours,
            :participants_count,
            :total_hours,
            :created_by
        )
        """,
        {
            "programme_name": programme_name,
            "from_date": from_date,
            "to_date": to_date,
            "quarter": quarter,
            "training_type": training_type,
            "location": location,
            "participant_names": participant_names,
            "training_cost": float(training_cost),
            "training_hours": float(training_hours),
            "participants_count": int(participants_count),
            "total_hours": float(total_hours),
            "created_by": created_by,
        },
    )


def update_training_record(
    record_id,
    programme_name,
    from_date,
    to_date,
    quarter,
    training_type,
    location,
    participant_names,
    training_cost,
    training_hours,
    participants_count,
    total_hours,
):
    run_write(
        """
        UPDATE training_records
        SET
            programme_name = :programme_name,
            from_date = :from_date,
            to_date = :to_date,
            quarter = :quarter,
            training_type = :training_type,
            location = :location,
            participant_names = :participant_names,
            training_cost = :training_cost,
            training_hours = :training_hours,
            participants_count = :participants_count,
            total_hours = :total_hours,
            updated_at = NOW()
        WHERE id = :record_id
        """,
        {
            "record_id": record_id,
            "programme_name": programme_name,
            "from_date": from_date,
            "to_date": to_date,
            "quarter": quarter,
            "training_type": training_type,
            "location": location,
            "participant_names": participant_names,
            "training_cost": float(training_cost),
            "training_hours": float(training_hours),
            "participants_count": int(participants_count),
            "total_hours": float(total_hours),
        },
    )


def delete_training_record(record_id):
    run_write(
        "DELETE FROM training_records WHERE id = :record_id",
        {"record_id": record_id},
    )


# ============================================================
# LOGIN / SIGNUP
# ============================================================

def render_login_signup():
    # Keep Log in and Create account in the left sidebar.
    # Staff.png occupies the main/right area.
    with st.sidebar:
        st.markdown(
            """
            <div class="login-sidebar-header">
                <div class="login-sidebar-icon">📊</div>
                <div class="login-sidebar-title">HR Training Dashboard</div>
                <div class="login-sidebar-subtitle">
                    Training management system
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">ACCOUNT ACCESS</div>',
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(
            ["🔐 Log in", "👤 Create account"]
        )

        with login_tab:
            st.markdown(
                '<div class="auth-heading">Welcome back</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="auth-description">'
                'Enter your username or email and password.'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                identifier = st.text_input(
                    "Username or email",
                    placeholder="Enter username or email",
                    key="login_identifier",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                    key="login_password",
                )
                submitted = st.form_submit_button(
                    "Log in",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:
                identifier = identifier.strip()
                if not identifier or not password:
                    st.error("Please enter both username/email and password.")
                else:
                    try:
                        user = authenticate(identifier, password)
                        if user:
                            login_user(user)
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password.")
                    except Exception:
                        st.error("Unable to log in. Please try again.")

        with signup_tab:
            st.markdown(
                '<div class="auth-heading">Create your account</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="auth-description">'
                'Register to access the HR Training Dashboard.'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.form("signup_form", clear_on_submit=False):
                full_name = st.text_input(
                    "Full name",
                    placeholder="e.g. Samoda De Silva",
                    key="signup_full_name",
                )
                username = st.text_input(
                    "Username",
                    placeholder="e.g. samoda",
                    key="signup_username",
                )
                email = st.text_input(
                    "Email",
                    placeholder="name@company.com",
                    key="signup_email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Minimum 8 characters",
                    key="signup_password",
                )
                confirm = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="signup_confirm",
                )

                create_submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True,
                    type="primary",
                )

            if create_submitted:
                full_name = full_name.strip()
                username = username.strip().lower()
                email = email.strip().lower()

                if not full_name:
                    st.error("Please enter your full name.")
                elif not username:
                    st.error("Please enter a username.")
                elif not re.fullmatch(r"[a-z0-9_.]{3,50}", username):
                    st.error(
                        "Username must contain 3–50 lowercase letters, "
                        "numbers, dots or underscores."
                    )
                elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                    st.error("Please enter a valid email address.")
                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        create_user(
                            username=username,
                            email=email,
                            full_name=full_name,
                            password=password,
                        )
                        st.success(
                            "Account created successfully. "
                            "Please use the Log in tab."
                        )
                    except ValueError as e:
                        st.error(str(e))
                    except Exception:
                        st.error(
                            "Unable to create the account. "
                            "Please check the database connection."
                        )

    staff_image = Path("Staff.png")
    if staff_image.exists():
        st.markdown(
            '<div class="login-staff-image">',
            unsafe_allow_html=True,
        )
        st.image(
            str(staff_image),
            use_container_width=True,
        )
        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "Staff.png was not found. Please keep Staff.png in the "
            "same folder as app.py."
        )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    user = user_now()
    if not user:
        return

    full_name = (
        user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )
    username = user.get("username", "")
    role = user.get("role", "user")

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">📊</div>
                <div class="sidebar-brand-title">HR Training Dashboard</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-user">
                <div class="sidebar-user-name">{html.escape(str(full_name))}</div>
                <div class="sidebar-user-role">
                    @{html.escape(str(username))} · {html.escape(str(role).title())}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">Navigation</div>',
            unsafe_allow_html=True,
        )

        for page, label in [
            (HOME_PAGE, "Home"),
            (DASHBOARD_PAGE, "Dashboard"),
            (DATA_ENTRY_PAGE, "Data Entry"),
            (IMPORT_PAGE, "Import Excel"),
            (RECORDS_PAGE, "Records"),
            (ACCOUNT_PAGE, "My Account"),
        ]:
            st.page_link(
                page,
                label=label,
                icon=None,
                use_container_width=True,
            )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button(
            "Log out",
            key="sidebar_logout",
            use_container_width=True,
        ):
            logout()


# ============================================================
# HOME
# ============================================================

def render_home():
    user = require_user()

    full_name = (
        user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    st.markdown(
        f"""
        <div class="welcome-box">
            <div class="welcome-title">📊 HR Training Dashboard</div>
            <div class="welcome-text">
                Welcome back, <strong>{html.escape(str(full_name))}</strong> 👋<br>
                Manage training programmes, participants, records and
                company-wide training performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown('<div class="home-card-icon">📊</div>', unsafe_allow_html=True)
            st.markdown('<div class="home-card-title">Training Dashboard</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="home-card-text">'
                'View company-wide KPIs, training hours, programmes, '
                'participants, costs and trends.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button(
                "Open Dashboard →",
                key="home_dashboard",
                use_container_width=True,
                type="primary",
            ):
                st.switch_page(DASHBOARD_PAGE)

    with c2:
        with st.container(border=True):
            st.markdown('<div class="home-card-icon">📝</div>', unsafe_allow_html=True)
            st.markdown('<div class="home-card-title">Data Entry</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="home-card-text">'
                'Add training programmes, dates, locations, participants, '
                'hours, types and costs.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button(
                "Add Training →",
                key="home_data",
                use_container_width=True,
                type="primary",
            ):
                st.switch_page(DATA_ENTRY_PAGE)

    with c3:
        with st.container(border=True):
            st.markdown('<div class="home-card-icon">📁</div>', unsafe_allow_html=True)
            st.markdown('<div class="home-card-title">Training Records</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="home-card-text">'
                'Browse, edit, export and manage existing training records.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button(
                "View Records →",
                key="home_records",
                use_container_width=True,
                type="primary",
            ):
                st.switch_page(RECORDS_PAGE)

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="home-card-icon">📥</div>', unsafe_allow_html=True)
        st.markdown('<div class="home-card-title">Import Excel</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="home-card-text">'
            'Upload Excel or CSV training information and review it safely.'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "Open Import Excel →",
            key="home_import",
            use_container_width=True,
            type="primary",
        ):
            st.switch_page(IMPORT_PAGE)

    st.write("")
    m1, m2, m3 = st.columns(3)
    df = get_training_records()

    if df.empty:
        m1.metric("Training Programmes", 0)
        m2.metric("Participants", 0)
        m3.metric("Training Hours", "0.0")
    else:
        m1.metric("Training Programmes", f"{len(df):,}")
        m2.metric("Participants", f"{int(df['participants_count'].sum()):,}")
        m3.metric("Training Hours", f"{df['total_hours'].sum():,.1f}")


# ============================================================
# DATA ENTRY
# ============================================================

def render_data_entry():
    user = require_user()

    st.title("Add a Training Record")
    st.caption(
        "Fill in the details below. Total hours are calculated automatically "
        "as training hours × participants."
    )

    locations = get_locations()

    with st.container(border=True):
        st.markdown(
            '<div class="form-section-title">Training information</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            programme_name = st.text_input(
                "Name of the Programme *",
                placeholder="e.g. Leadership Development Programme",
                key="entry_programme",
            )

            from_date = st.date_input(
                "From Date *",
                key="entry_from_date",
            )

            to_date = st.date_input(
                "To Date",
                key="entry_to_date",
            )

            training_type = st.selectbox(
                "Type *",
                ["Technical", "Soft Skill", "Compliance", "Other"],
                key="entry_type",
            )

            quarter = st.selectbox(
                "Quarter *",
                ["Q1", "Q2", "Q3", "Q4"],
                key="entry_quarter",
            )

        with col2:
            location_mode = st.selectbox(
                "Location *",
                ["Select existing location", "+ Add new location"],
                key="entry_location_mode",
            )

            if location_mode == "+ Add new location":
                location = st.text_input(
                    "New location name *",
                    placeholder="e.g. Head Office",
                    key="entry_new_location",
                )
            else:
                if locations:
                    location = st.selectbox(
                        "Select location *",
                        locations,
                        key="entry_location_existing",
                    )
                else:
                    location = ""
                    st.info("No locations exist yet. Select '+ Add new location'.")

            training_hours = st.number_input(
                "Training Hours (per session) *",
                min_value=0.0,
                step=0.25,
                format="%.2f",
                key="entry_training_hours",
            )

            participants_count = st.number_input(
                "No. of Participants *",
                min_value=0,
                step=1,
                key="entry_participants_count",
            )

            training_cost = st.number_input(
                "Training Cost (Rs.) *",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key="entry_training_cost",
            )

        participant_names = st.text_area(
            "Participant Names",
            placeholder="Optional — enter names separated by commas",
            key="entry_participant_names",
        )

        total_hours = float(training_hours) * int(participants_count)

        st.info(
            f"Calculated total training hours: **{total_hours:,.2f} hours**"
        )

        submitted = st.button(
            "Save Training Record",
            type="primary",
            use_container_width=True,
            key="save_training_record",
        )

    if submitted:
        clean_programme = programme_name.strip()
        clean_location = location.strip() if isinstance(location, str) else ""

        if not clean_programme:
            st.error("Please enter the programme name.")
            return

        if not clean_location:
            st.error("Please select or enter a location.")
            return

        if to_date < from_date:
            st.error("To Date cannot be earlier than From Date.")
            return

        if participants_count <= 0:
            st.error("Number of participants must be at least 1.")
            return

        if training_hours <= 0:
            st.error("Training hours must be greater than 0.")
            return

        try:
            insert_training_record(
                programme_name=clean_programme,
                from_date=from_date,
                to_date=to_date,
                quarter=quarter,
                training_type=training_type,
                location=clean_location,
                participant_names=participant_names.strip(),
                training_cost=training_cost,
                training_hours=training_hours,
                participants_count=participants_count,
                total_hours=total_hours,
                created_by=user["id"],
            )
            st.success("Training record saved successfully.")
            st.rerun()
        except Exception as e:
            st.error("Unable to save the training record.")
            st.caption(str(e))


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():
    require_user()

    st.title("Training Dashboard")
    st.caption("Company-wide training KPIs, trends, costs and programme performance.")

    df = get_training_records()

    if df.empty:
        st.info("No training records yet. Add records from the Data Entry page.")
        return

    # Filters
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        locations = ["All Locations"] + sorted(
            df["location"].dropna().astype(str).unique().tolist()
        )
        selected_location = st.selectbox(
            "Location",
            locations,
            key="dash_location",
        )

    with f2:
        years = ["All Years"] + sorted(
            df["from_date"].dropna().dt.year.astype(int).unique().tolist(),
            reverse=True,
        )
        selected_year = st.selectbox(
            "Year",
            years,
            key="dash_year",
        )

    with f3:
        months = ["All Months"] + list(range(1, 13))
        selected_month = st.selectbox(
            "Month",
            months,
            key="dash_month",
        )

    with f4:
        types = ["All Types"] + sorted(
            df["training_type"].dropna().astype(str).unique().tolist()
        )
        selected_type = st.selectbox(
            "Type",
            types,
            key="dash_type",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    filtered = df.copy()

    if selected_location != "All Locations":
        filtered = filtered[filtered["location"] == selected_location]

    if selected_year != "All Years":
        filtered = filtered[filtered["from_date"].dt.year == int(selected_year)]

    if selected_month != "All Months":
        filtered = filtered[filtered["from_date"].dt.month == int(selected_month)]

    if selected_type != "All Types":
        filtered = filtered[filtered["training_type"] == selected_type]

    if filtered.empty:
        st.warning("No records match the selected filters.")
        return

    total_hours = float(filtered["total_hours"].sum())
    programme_count = int(len(filtered))
    participants = int(filtered["participants_count"].sum())
    avg_hours = total_hours / programme_count if programme_count else 0
    total_cost = float(filtered["training_cost"].sum())
    avg_cost = total_cost / programme_count if programme_count else 0
    avg_cost_person = (
        total_cost / participants if participants else 0
    )

    kpis = st.columns(7)
    kpis[0].metric("Total Training Hours", f"{total_hours:,.0f}")
    kpis[1].metric("No. of Programmes", f"{programme_count:,}")
    kpis[2].metric("Participants Attended", f"{participants:,}")
    kpis[3].metric("Avg. Hours / Programme", f"{avg_hours:,.1f}")
    kpis[4].metric("Total Training Cost", f"Rs. {total_cost:,.0f}")
    kpis[5].metric("Avg. Cost / Programme", f"Rs. {avg_cost:,.0f}")
    kpis[6].metric("Avg. Cost / Person", f"Rs. {avg_cost_person:,.0f}")

    st.write("")

    # Monthly trend
    trend = (
        filtered.assign(
            month=filtered["from_date"].dt.to_period("M").astype(str)
        )
        .groupby("month", as_index=False)
        .agg(
            Training_Hours=("total_hours", "sum"),
            Programmes=("id", "count"),
        )
        .sort_values("month")
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Trend — Training Hours")
        if not trend.empty:
            chart_df = trend.set_index("month")[["Training_Hours"]]
            st.line_chart(chart_df, use_container_width=True)
        else:
            st.info("No trend data.")

    with c2:
        st.subheader("Training Hours by Type")
        type_df = (
            filtered.groupby("training_type", as_index=True)["total_hours"]
            .sum()
            .sort_values(ascending=False)
            .to_frame()
        )
        st.bar_chart(type_df, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Training Programmes by Location")
        location_df = (
            filtered.groupby("location", as_index=True)["id"]
            .count()
            .sort_values(ascending=False)
            .to_frame("Programmes")
        )
        st.bar_chart(location_df, use_container_width=True)

    with c4:
        st.subheader("Training Cost by Type")
        cost_type_df = (
            filtered.groupby("training_type", as_index=True)["training_cost"]
            .sum()
            .sort_values(ascending=False)
            .to_frame("Cost")
        )
        st.bar_chart(cost_type_df, use_container_width=True)

    st.subheader("Training Records in Selected Period")
    display_cols = [
        "programme_name",
        "from_date",
        "to_date",
        "quarter",
        "training_type",
        "location",
        "training_hours",
        "participants_count",
        "total_hours",
        "training_cost",
    ]
    st.dataframe(
        filtered[display_cols],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# RECORDS
# ============================================================

def render_records():
    user = require_user()
    df = get_training_records()

    st.title("Training Records")

    if df.empty:
        st.info("No records yet. Add some from the Data Entry page.")
        return

    search = st.text_input(
        "Search",
        placeholder="Search programme, location or type...",
        key="records_search",
    )

    filtered = df.copy()

    if search.strip():
        q = search.strip().lower()
        mask = (
            filtered["programme_name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered["location"].astype(str).str.lower().str.contains(q, na=False)
            | filtered["training_type"].astype(str).str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    st.write(f"Showing **{len(filtered):,}** record(s).")

    export_df = filtered.copy()
    for col in ["from_date", "to_date", "created_at"]:
        if col in export_df.columns:
            export_df[col] = export_df[col].dt.strftime("%Y-%m-%d")

    st.download_button(
        "Download Records as CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="hr_training_records.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.dataframe(
        filtered[
            [
                "id",
                "programme_name",
                "from_date",
                "to_date",
                "quarter",
                "training_type",
                "location",
                "training_hours",
                "participants_count",
                "total_hours",
                "training_cost",
                "created_by_name",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.write("")
    st.subheader("Edit / Manage a Record")

    record_ids = filtered["id"].astype(int).tolist()
    selected_id = st.selectbox(
        "Select record",
        record_ids,
        key="manage_record_id",
    )

    row = df[df["id"] == selected_id].iloc[0]

    with st.expander("Edit selected record", expanded=False):
        c1, c2 = st.columns(2)

        with c1:
            edit_programme = st.text_input(
                "Programme name",
                value=str(row["programme_name"] or ""),
                key=f"edit_programme_{selected_id}",
            )
            edit_from = st.date_input(
                "From date",
                value=row["from_date"].date(),
                key=f"edit_from_{selected_id}",
            )
            edit_to = st.date_input(
                "To date",
                value=(
                    row["to_date"].date()
                    if pd.notna(row["to_date"])
                    else row["from_date"].date()
                ),
                key=f"edit_to_{selected_id}",
            )
            edit_quarter = st.selectbox(
                "Quarter",
                ["Q1", "Q2", "Q3", "Q4"],
                index=["Q1", "Q2", "Q3", "Q4"].index(
                    str(row["quarter"]) if str(row["quarter"]) in ["Q1","Q2","Q3","Q4"] else "Q1"
                ),
                key=f"edit_quarter_{selected_id}",
            )

        with c2:
            edit_type = st.selectbox(
                "Type",
                ["Technical", "Soft Skill", "Compliance", "Other"],
                index=(
                    ["Technical", "Soft Skill", "Compliance", "Other"].index(str(row["training_type"]))
                    if str(row["training_type"]) in ["Technical", "Soft Skill", "Compliance", "Other"]
                    else 0
                ),
                key=f"edit_type_{selected_id}",
            )
            location_options = sorted(set(get_locations() + [str(row["location"])]))
            edit_location = st.selectbox(
                "Location",
                location_options,
                index=location_options.index(str(row["location"])),
                key=f"edit_location_{selected_id}",
            )
            edit_hours = st.number_input(
                "Training hours per session",
                min_value=0.0,
                value=float(row["training_hours"]),
                step=0.25,
                key=f"edit_hours_{selected_id}",
            )
            edit_participants = st.number_input(
                "Participants",
                min_value=0,
                value=int(row["participants_count"]),
                step=1,
                key=f"edit_participants_{selected_id}",
            )

        edit_cost = st.number_input(
            "Training cost (Rs.)",
            min_value=0.0,
            value=float(row["training_cost"]),
            step=1000.0,
            key=f"edit_cost_{selected_id}",
        )

        edit_names = st.text_area(
            "Participant names",
            value=str(row["participant_names"] or ""),
            key=f"edit_names_{selected_id}",
        )

        new_total_hours = float(edit_hours) * int(edit_participants)
        st.info(f"Calculated total hours: **{new_total_hours:,.2f}**")

        b1, b2 = st.columns(2)

        with b1:
            if st.button(
                "Save Changes",
                type="primary",
                use_container_width=True,
                key=f"save_edit_{selected_id}",
            ):
                if edit_to < edit_from:
                    st.error("To Date cannot be earlier than From Date.")
                else:
                    try:
                        update_training_record(
                            record_id=int(selected_id),
                            programme_name=edit_programme.strip(),
                            from_date=edit_from,
                            to_date=edit_to,
                            quarter=edit_quarter,
                            training_type=edit_type,
                            location=edit_location,
                            participant_names=edit_names.strip(),
                            training_cost=edit_cost,
                            training_hours=edit_hours,
                            participants_count=edit_participants,
                            total_hours=new_total_hours,
                        )
                        st.success("Record updated successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error("Unable to update record.")
                        st.caption(str(e))

        with b2:
            if user.get("role") == "admin":
                if st.button(
                    "Delete Record",
                    use_container_width=True,
                    key=f"delete_record_{selected_id}",
                ):
                    try:
                        delete_training_record(int(selected_id))
                        st.success("Record deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error("Unable to delete record.")
                        st.caption(str(e))
            else:
                st.caption("Only administrators can delete records.")


# ============================================================
# IMPORT EXCEL
# ============================================================

def render_import_excel():
    require_user()

    st.title("Import Excel")
    st.caption(
        "Upload an Excel or CSV file, review the data, and optionally import "
        "rows that match the HR training format."
    )

    uploaded = st.file_uploader(
        "Choose an Excel or CSV file",
        type=["xlsx", "xls", "csv"],
        key="excel_upload",
    )

    if uploaded is None:
        st.info(
            "Supported formats: .xlsx, .xls and .csv. "
            "The file is previewed before database changes are made."
        )
        return

    try:
        if uploaded.name.lower().endswith(".csv"):
            imported_df = pd.read_csv(uploaded)
        else:
            imported_df = pd.read_excel(uploaded)

        st.success(
            f"{uploaded.name} loaded successfully — "
            f"{len(imported_df):,} rows × {len(imported_df.columns):,} columns."
        )

        st.subheader("Preview")
        st.dataframe(
            imported_df.head(100),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Column names")
        st.write(", ".join(str(c) for c in imported_df.columns))

        st.download_button(
            "Download preview as CSV",
            data=imported_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{Path(uploaded.name).stem}_preview.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()
        st.subheader("Import into Training Records")

        st.caption(
            "For automatic import, use these columns: "
            "programme_name, from_date, to_date, quarter, training_type, "
            "location, participant_names, training_cost, training_hours, "
            "participants_count."
        )

        required = [
            "programme_name",
            "from_date",
            "training_type",
            "location",
            "training_cost",
            "training_hours",
            "participants_count",
        ]

        normalized = {
            str(c).strip().lower().replace(" ", "_"): c
            for c in imported_df.columns
        }

        missing = [c for c in required if c not in normalized]

        if missing:
            st.warning(
                "Automatic import is unavailable because these columns are missing: "
                + ", ".join(missing)
            )
        else:
            if st.button(
                "Import Valid Rows into Training Records",
                type="primary",
                use_container_width=True,
                key="import_rows_button",
            ):
                user = current_user()
                success_count = 0
                errors = []

                for index, source_row in imported_df.iterrows():
                    try:
                        def val(column, default=""):
                            source_col = normalized.get(column)
                            if source_col is None:
                                return default
                            value = source_row[source_col]
                            return default if pd.isna(value) else value

                        programme = str(val("programme_name")).strip()
                        location = str(val("location")).strip()
                        training_type = str(val("training_type")).strip()

                        from_date = pd.to_datetime(
                            val("from_date"), errors="coerce"
                        )
                        to_date = pd.to_datetime(
                            val("to_date"), errors="coerce"
                        )

                        if pd.isna(from_date):
                            raise ValueError("Invalid from_date")
                        if pd.isna(to_date):
                            to_date = from_date

                        quarter = str(val("quarter", "")).strip()
                        if quarter not in ["Q1", "Q2", "Q3", "Q4"]:
                            quarter = f"Q{((from_date.month - 1) // 3) + 1}"

                        cost = float(val("training_cost", 0) or 0)
                        hours = float(val("training_hours", 0) or 0)
                        participants = int(float(val("participants_count", 0) or 0))
                        names = str(val("participant_names", "")).strip()

                        if not programme or not location:
                            raise ValueError("Programme name/location is empty")
                        if participants <= 0 or hours <= 0:
                            raise ValueError("Participants and hours must be greater than 0")

                        insert_training_record(
                            programme_name=programme,
                            from_date=from_date.date(),
                            to_date=to_date.date(),
                            quarter=quarter,
                            training_type=training_type or "Other",
                            location=location,
                            participant_names=names,
                            training_cost=cost,
                            training_hours=hours,
                            participants_count=participants,
                            total_hours=hours * participants,
                            created_by=user["id"],
                        )
                        success_count += 1

                    except Exception as e:
                        errors.append(f"Row {index + 2}: {e}")

                if success_count:
                    st.success(
                        f"{success_count:,} row(s) imported successfully."
                    )

                if errors:
                    st.warning(
                        f"{len(errors):,} row(s) could not be imported."
                    )
                    st.code("\n".join(errors[:20]))

    except Exception as e:
        st.error("Unable to read the selected file.")
        st.caption(str(e))


# ============================================================
# MY ACCOUNT
# ============================================================

def render_account():
    user = require_user()

    st.title("My Account")

    with st.container(border=True):
        st.subheader("Profile")
        st.write(f"**Name:** {user.get('full_name', '')}")
        st.write(f"**Username:** @{user.get('username', '')}")
        st.write(f"**Email:** {user.get('email', '')}")
        st.write(f"**Role:** {str(user.get('role', 'user')).title()}")

    st.write("")

    with st.container(border=True):
        st.subheader("Change password")

        with st.form("change_password_form"):
            new_password = st.text_input(
                "New password",
                type="password",
                placeholder="Minimum 8 characters",
            )
            confirm_password = st.text_input(
                "Confirm new password",
                type="password",
                placeholder="Re-enter your password",
            )

            submitted = st.form_submit_button(
                "Update password",
                type="primary",
            )

        if submitted:
            if len(new_password) < 8:
                st.error("Password must contain at least 8 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    change_password(int(user["id"]), new_password)
                    st.success("Password updated successfully.")
                except Exception:
                    st.error("Unable to update the password.")


# ============================================================
# PAGE DEFINITIONS
# ============================================================

HOME_PAGE = st.Page(
    render_home,
    title="Home",
    icon=None,
    default=True,
)

DASHBOARD_PAGE = st.Page(
    render_dashboard,
    title="Dashboard",
    icon=None,
)

DATA_ENTRY_PAGE = st.Page(
    render_data_entry,
    title="Data Entry",
    icon=None,
)

IMPORT_PAGE = st.Page(
    render_import_excel,
    title="Import Excel",
    icon=None,
)

RECORDS_PAGE = st.Page(
    render_records,
    title="Records",
    icon=None,
)

ACCOUNT_PAGE = st.Page(
    render_account,
    title="My Account",
    icon=None,
)

NAVIGATION = [
    HOME_PAGE,
    DASHBOARD_PAGE,
    DATA_ENTRY_PAGE,
    IMPORT_PAGE,
    RECORDS_PAGE,
    ACCOUNT_PAGE,
]

pg = st.navigation(NAVIGATION, position="hidden")

# ============================================================
# RUN
# ============================================================

if is_logged_in():
    render_sidebar()
    pg.run()
else:
    # Keep Home as the landing page for logged-out users.
    render_login_signup()
