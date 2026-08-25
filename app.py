from pathlib import Path
import html
import re

import streamlit as st

from database.db import init_db
from auth.auth import (
    authenticate,
    create_user,
    login_user,
    logout_user,
    is_logged_in,
    current_user,
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HR Training Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

def inject_css():
    st.markdown(
        """
<style>
/* ---------- APP ---------- */
.stApp {
    background: linear-gradient(135deg, #f7fbff 0%, #edf6ff 52%, #e5f0fa 100%) !important;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit's automatic page list because this app has its own navigation. */
[data-testid="stSidebarNav"] {
    display: none !important;
}

#MainMenu,
footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

/* ---------- MAIN TITLE ---------- */
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

/* ---------- WELCOME ---------- */
.welcome-box {
    background: linear-gradient(135deg, #0a4778 0%, #12699f 100%);
    border-radius: 18px;
    padding: 27px 30px;
    margin: 8px 0 24px 0;
    box-shadow: 0 10px 28px rgba(7, 59, 102, 0.16);
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

/* ---------- AUTH ---------- */
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

/* Tabs must remain clearly clickable. */
button[data-baseweb="tab"] {
    color: #214d6b !important;
    font-weight: 750 !important;
    font-size: 15px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #087ea4 !important;
}

/* ---------- INPUTS ---------- */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label {
    color: #173f5c !important;
    font-weight: 700 !important;
}

div[data-baseweb="input"] {
    background: #ffffff !important;
    border: 1px solid #aebfd0 !important;
    border-radius: 9px !important;
}

div[data-baseweb="input"] input {
    background: #ffffff !important;
    color: #172b3d !important;
    -webkit-text-fill-color: #172b3d !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #73879a !important;
    opacity: 1 !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button,
.stFormSubmitButton > button {
    min-height: 43px !important;
    border-radius: 9px !important;
    font-weight: 750 !important;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: #0879a5 !important;
    color: #ffffff !important;
    border: 1px solid #0879a5 !important;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    background: #075f82 !important;
    border-color: #075f82 !important;
}

/* ---------- HOME CARDS ---------- */
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

.home-card-icon {
    font-size: 31px !important;
    margin-bottom: 7px;
}

/* Streamlit bordered containers used as cards. */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #d2e1ed !important;
    border-radius: 17px !important;
    box-shadow: 0 7px 22px rgba(15, 69, 105, 0.08) !important;
}

/* ---------- METRICS ---------- */
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

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #073556 0%, #0a4772 58%, #0b507e 100%) !important;
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
    color: #a9d7f4 !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin: 10px 0 7px 3px;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.11) !important;
    border-radius: 9px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.25) !important;
}

.sidebar-divider {
    height: 1px;
    background: rgba(255,255,255,0.18);
    margin: 17px 0;
}

/* ---------- NORMAL TEXT ---------- */
.stMarkdown,
.stMarkdown p,
.stCaption,
.stCaption p {
    color: #294a63;
}

/* ---------- DARK MODE ---------- */
@media (prefers-color-scheme: dark) {
    .stApp {
        background: linear-gradient(135deg, #101923 0%, #152b3d 55%, #102c44 100%) !important;
    }

    .app-title {
        color: #73ceff !important;
    }

    .app-subtitle {
        color: #d7eaf7 !important;
    }

    .auth-heading {
        color: #eaf7ff !important;
    }

    .auth-description {
        color: #c6dce9 !important;
    }

    button[data-baseweb="tab"] {
        color: #d8edf8 !important;
    }

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label {
        color: #e7f4fb !important;
    }

    div[data-baseweb="input"] {
        background: #ffffff !important;
    }

    div[data-baseweb="input"] input {
        color: #172b3d !important;
        -webkit-text-fill-color: #172b3d !important;
    }

    .home-card-title {
        color: #ffffff !important;
    }

    .home-card-text {
        color: #dcecf6 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #18364f !important;
        border-color: #2e5876 !important;
    }

    [data-testid="stMetric"] {
        background: #18364f !important;
        border-color: #2e5876 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #c7dce9 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
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
except Exception as e:
    st.error("Unable to connect to the HR database.")
    with st.expander("Technical details"):
        st.exception(e)
    st.stop()


# ============================================================
# PAGE HELPERS
# ============================================================

def page_files():
    pages_dir = Path(__file__).parent / "pages"

    if not pages_dir.exists():
        return []

    return sorted(
        [
            p for p in pages_dir.glob("*.py")
            if not p.name.startswith("_")
        ]
    )


def page_title(path):
    name = Path(path).stem
    name = name.lstrip("0123456789")
    name = name.lstrip("_- ")
    name = name.replace("_", " ").replace("-", " ").strip()

    lower = name.lower()

    if "dashboard" in lower:
        return "Dashboard"
    if "data" in lower:
        return "Data Entry"
    if "record" in lower:
        return "Records"
    if "account" in lower:
        return "My Account"
    if "import" in lower:
        return "Import Excel"

    return name.title()


def find_page(*keywords):
    for path in page_files():
        lower = path.stem.lower()
        if all(keyword.lower() in lower for keyword in keywords):
            return str(path)

    # If multiple keywords are too restrictive, try any keyword.
    for keyword in keywords:
        for path in page_files():
            if keyword.lower() in path.stem.lower():
                return str(path)

    return None


def go_to(path):
    if path:
        st.switch_page(path)
    else:
        st.warning("This page is not available yet.")


# ============================================================
# LOGIN / SIGNUP
# ============================================================

def render_login_signup():

    st.markdown(
        '<div class="app-title">📊 HR Training Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="app-subtitle">Training management system — sign in to continue.</div>',
        unsafe_allow_html=True,
    )

    # No HTML auth-card wrapper here.
    # This removes the unwanted empty white box and prevents
    # HTML source from appearing as visible code.

    _, center, _ = st.columns([1, 1.05, 1])

    with center:

        st.markdown(
            '<div class="auth-area">',
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(
            ["🔐 Log in", "👤 Create account"]
        )

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        with login_tab:

            st.markdown(
                '<div class="auth-heading">Welcome back</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="auth-description">Enter your username or email and password.</div>',
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
                            st.success("Login successful.")
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password.")

                    except Exception as e:
                        st.error("Unable to log in. Please try again.")

                        with st.expander("Technical details"):
                            st.exception(e)

        # ----------------------------------------------------
        # CREATE ACCOUNT
        # ----------------------------------------------------

        with signup_tab:

            st.markdown(
                '<div class="auth-heading">Create your account</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="auth-description">Register to access the HR Training Dashboard.</div>',
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

                # Basic validation before touching the database.
                if not full_name:
                    st.error("Please enter your full name.")

                elif not username:
                    st.error("Please enter a username.")

                elif not re.fullmatch(r"[a-z0-9._-]{3,30}", username):
                    st.error(
                        "Username must contain 3–30 lowercase letters, "
                        "numbers, dots, underscores or hyphens."
                    )

                elif not email or "@" not in email:
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
                            "You can now log in."
                        )

                    except ValueError as e:
                        st.error(str(e))

                    except Exception as e:
                        st.error(
                            "Unable to create the account. "
                            "Please check the database connection."
                        )

                        with st.expander("Technical details"):
                            st.exception(e)

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    user = current_user()

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

    dashboard_page = find_page("dashboard")
    data_page = find_page("data")
    records_page = find_page("record")
    account_page = find_page("account")
    import_page = find_page("import")

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
    <div class="sidebar-user-name">👤 {html.escape(str(full_name))}</div>
    <div class="sidebar-user-role">@{html.escape(str(username))} · {html.escape(str(role).title())}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">Navigation</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "🏠   Home",
            key="sidebar_home",
            use_container_width=True,
        ):
            go_to("app.py")

        if dashboard_page:
            if st.button(
                "📊   Dashboard",
                key="sidebar_dashboard",
                use_container_width=True,
                type="primary",
            ):
                go_to(dashboard_page)

        if data_page:
            if st.button(
                "📝   Data Entry",
                key="sidebar_data",
                use_container_width=True,
            ):
                go_to(data_page)

        if import_page:
            if st.button(
                "📥   Import Excel",
                key="sidebar_import",
                use_container_width=True,
            ):
                go_to(import_page)

        if records_page:
            if st.button(
                "📁   Records",
                key="sidebar_records",
                use_container_width=True,
            ):
                go_to(records_page)

        if account_page:
            if st.button(
                "👤   My Account",
                key="sidebar_account",
                use_container_width=True,
            ):
                go_to(account_page)

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "🚪   Log out",
            key="sidebar_logout",
            use_container_width=True,
        ):
            logout_user()
            st.rerun()


# ============================================================
# HOME
# ============================================================

def render_home():

    user = current_user()

    if not user:
        return

    full_name = (
        user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    role = user.get("role", "user")

    dashboard_page = find_page("dashboard")
    data_page = find_page("data")
    records_page = find_page("record")
    account_page = find_page("account")
    import_page = find_page("import")

    safe_name = html.escape(str(full_name))

    st.markdown(
        f"""
<div class="welcome-box">
    <div class="welcome-title">📊 HR Training Dashboard</div>
    <div class="welcome-text">
        Welcome back, <strong>{safe_name}</strong> 👋<br>
        Manage training programmes, participants, records and company-wide training performance.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # DASHBOARD CARD
    # --------------------------------------------------------

    with col1:

        with st.container(border=True):

            st.markdown(
                '<div class="home-card-icon">📊</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-title">Training Dashboard</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-text">View company-wide KPIs, training hours, programmes, participants, costs and trends.</div>',
                unsafe_allow_html=True,
            )

            st.write("")

            if dashboard_page:
                if st.button(
                    "Open Dashboard →",
                    key="home_dashboard",
                    use_container_width=True,
                    type="primary",
                ):
                    go_to(dashboard_page)

    # --------------------------------------------------------
    # DATA ENTRY CARD
    # --------------------------------------------------------

    with col2:

        with st.container(border=True):

            st.markdown(
                '<div class="home-card-icon">📝</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-title">Data Entry</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-text">Add new training programmes, participants, dates, locations, costs and training hours.</div>',
                unsafe_allow_html=True,
            )

            st.write("")

            if data_page:
                if st.button(
                    "Add Training →",
                    key="home_data",
                    use_container_width=True,
                    type="primary",
                ):
                    go_to(data_page)

    # --------------------------------------------------------
    # RECORDS CARD
    # --------------------------------------------------------

    with col3:

        with st.container(border=True):

            st.markdown(
                '<div class="home-card-icon">📁</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-title">Training Records</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-text">Browse, edit, export and manage existing training records.</div>',
                unsafe_allow_html=True,
            )

            st.write("")

            if records_page:
                if st.button(
                    "View Records →",
                    key="home_records",
                    use_container_width=True,
                    type="primary",
                ):
                    go_to(records_page)

    # --------------------------------------------------------
    # IMPORT EXCEL
    # --------------------------------------------------------

    if import_page:

        st.write("")

        with st.container(border=True):

            st.markdown(
                '<div class="home-card-icon">📥</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-title">Import Excel</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="home-card-text">Import existing training data from an Excel file using the dedicated import page.</div>',
                unsafe_allow_html=True,
            )

            if st.button(
                "Import Excel →",
                key="home_import",
                use_container_width=True,
                type="primary",
            ):
                go_to(import_page)

    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Logged-in User",
            full_name,
        )

    with c2:
        st.metric(
            "Username",
            f"@{user.get('username', '')}",
        )

    with c3:
        st.metric(
            "Access Level",
            str(role).title(),
        )

    # Account button
    if account_page:

        st.write("")

        if st.button(
            "👤  Open My Account",
            key="home_account",
            use_container_width=True,
        ):
            go_to(account_page)


# ============================================================
# APPLICATION
# ============================================================

if is_logged_in():
    render_sidebar()
    render_home()
else:
    render_login_signup()
