from pathlib import Path
import html
import re

import pandas as pd
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

# The app uses st.navigation + a custom text-only sidebar.
try:
    st.set_option("client.showSidebarNavigation", False)
except Exception:
    pass


# ============================================================
# GLOBAL LIGHT THEME
# ============================================================

def inject_css():
    st.markdown(
        """
<style>
/* =========================================================
   FORCE A LIGHT, CONSISTENT THEME
   ========================================================= */

html, body, [data-testid="stAppViewContainer"] {
    background: #f4f9fd !important;
}

.stApp {
    background: linear-gradient(
        135deg,
        #f7fbff 0%,
        #edf6ff 52%,
        #e5f0fa 100%
    ) !important;
    color: #173f5c !important;
}

:root,
html {
    color-scheme: light !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #f4f9fd !important;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit's automatic page list.
   The application has its own navigation. */
[data-testid="stSidebarNav"] {
    display: none !important;
}

#MainMenu,
footer {
    visibility: hidden !important;
}

header {
    background: transparent !important;
}

/* =========================================================
   REMOVE UNWANTED STREAMLIT FORM HINTS / TOOLTIPS
   ========================================================= */

[data-testid="InputInstructions"],
div[data-testid="InputInstructions"],
[data-testid="stTooltipIcon"],
[data-testid="stTextInput"] [data-testid="InputInstructions"],
[data-testid="stTextInput"] small {
    display: none !important;
}

/* =========================================================
   PAGE TITLE
   ========================================================= */

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

/* =========================================================
   AUTHENTICATION
   ========================================================= */

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
    font-size: 15px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #087ea4 !important;
}

/* =========================================================
   INPUTS — ALWAYS LIGHT WITH DARK TEXT
   ========================================================= */

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label {
    color: #173f5c !important;
    font-weight: 700 !important;
}

div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: #ffffff !important;
    border: 1px solid #aebfd0 !important;
    border-radius: 9px !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
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

/* Password visibility button */
div[data-baseweb="input"] button,
div[data-baseweb="base-input"] button {
    color: #173f5c !important;
}

/* =========================================================
   BUTTONS
   ========================================================= */

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

/* Dark boxes remain dark, but their text is always readable. */
.stButton > button:not([kind="primary"]),
.stDownloadButton > button {
    background: #13233f !important;
    color: #ffffff !important;
    border: 1px solid #13233f !important;
}

.stButton > button:not([kind="primary"]):hover,
.stDownloadButton > button:hover {
    background: #1d355d !important;
    color: #ffffff !important;
    border-color: #1d355d !important;
}

/* Excel dropzone: dark box with white text on the light page. */
section[data-testid="stFileUploaderDropzone"] {
    background: #13233f !important;
    border: 1px solid #2b4168 !important;
    border-radius: 12px !important;
}

section[data-testid="stFileUploaderDropzone"] * {
    color: #ffffff !important;
}

section[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;
    color: #13233f !important;
    border: 1px solid #d5e2ef !important;
}

section[data-testid="stFileUploaderDropzone"] small {
    color: #d9e7f5 !important;
}

/* =========================================================
   HOME / DASHBOARD CARDS
   ========================================================= */

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

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #d2e1ed !important;
    border-radius: 17px !important;
    box-shadow: 0 7px 22px rgba(15, 69, 105, 0.08) !important;
}

/* =========================================================
   WELCOME BANNER
   ========================================================= */

.welcome-box {
    background: linear-gradient(
        135deg,
        #0a4778 0%,
        #12699f 100%
    ) !important;
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

/* =========================================================
   METRICS
   ========================================================= */

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

/* =========================================================
   ALERTS / EXPANDERS — LIGHT AND READABLE
   ========================================================= */

[data-testid="stAlert"] {
    color: #173f5c !important;
    background: #eef6fc !important;
    border: 1px solid #c8dceb !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div {
    color: #173f5c !important;
}

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #d7e5ef !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary {
    color: #173f5c !important;
}

/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #073556 0%,
        #0a4772 58%,
        #0b507e 100%
    ) !important;
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

section[data-testid="stSidebar"] a {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    box-sizing: border-box !important;
    background: rgba(0, 0, 0, 0.22) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 9px !important;
    padding: 10px 12px !important;
    margin: 0 0 7px 0 !important;
    text-decoration: none !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] a:hover {
    background: rgba(255, 255, 255, 0.16) !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] a[aria-current="page"] {
    background: rgba(255, 255, 255, 0.22) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.30) !important;
}

.sidebar-divider {
    height: 1px;
    background: rgba(255,255,255,0.18);
    margin: 17px 0;
}

/* =========================================================
   GENERAL TEXT
   ========================================================= */

.stMarkdown,
.stMarkdown p,
.stCaption,
.stCaption p {
    color: #294a63;
}

/* Never switch this app into a dark CSS theme based on the
   user's operating-system/browser preference. */
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
    st.stop()


# ============================================================
# SESSION / AUTH HELPERS
# ============================================================

def remember_login(user):
    """Keep a small local session copy as a compatibility bridge
    for existing pages that use Streamlit session_state."""
    st.session_state["hr_logged_in"] = True
    st.session_state["hr_user"] = user
    st.session_state["logged_in"] = True
    st.session_state["user"] = user


def clear_login():
    for key in [
        "hr_logged_in",
        "hr_user",
        "logged_in",
        "user",
    ]:
        st.session_state.pop(key, None)


def get_logged_user():
    """Prefer the existing auth module, then fall back to the
    session bridge created above."""
    try:
        user = current_user()
        if user:
            return user
    except Exception:
        pass

    user = st.session_state.get("hr_user")
    return user if isinstance(user, dict) else None


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


def discover_pages():
    """Return existing Streamlit page files with their display titles."""
    discovered = []
    for path in page_files():
        discovered.append({
            "path": str(path),
            "title": page_title(path),
        })
    return discovered


def find_page(*keywords):
    for path in page_files():
        lower = path.stem.lower()
        if all(keyword.lower() in lower for keyword in keywords):
            return str(path)

    for keyword in keywords:
        for path in page_files():
            if keyword.lower() in path.stem.lower():
                return str(path)

    return None


def go_to(path):
    """Switch to a page registered by st.navigation."""
    if not path:
        st.warning("This page is not available yet.")
        return

    try:
        project_root = Path(__file__).parent.resolve()
        target = Path(path).resolve()
        relative = target.relative_to(project_root)
        st.switch_page(str(relative).replace("\\", "/"))
    except Exception:
        try:
            st.switch_page(str(path))
        except Exception:
            st.error("Unable to open this page. Please check the page filename.")


# ============================================================
# EXCEL IMPORT
# ============================================================

def render_import_excel():
    st.markdown(
        '<div class="home-card-title">📥 Import Excel</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="home-card-text">'
        'Upload an Excel or CSV file and review it before using it in the training system.'
        '</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Choose an Excel/CSV file",
        type=["xlsx", "xls", "csv"],
        key="home_excel_upload",
    )

    if uploaded is None:
        st.caption("Supported formats: .xlsx, .xls and .csv")
        return

    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)

        st.success(
            f"{uploaded.name} loaded successfully — "
            f"{len(df):,} rows × {len(df.columns):,} columns."
        )

        st.dataframe(
            df.head(50),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download preview as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{Path(uploaded.name).stem}_preview.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.info(
            "The file is previewed safely first. Database insertion is not performed "
            "automatically because the existing training-table schema must be preserved."
        )

    except Exception as e:
        st.error("The selected file could not be read.")
        st.caption(str(e))


# ============================================================
# LOGIN / SIGNUP
# ============================================================

def render_login_signup():

    st.markdown(
        '<div class="app-title">📊 HR Training Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="app-subtitle">'
        'Training management system — sign in to continue.'
        '</div>',
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.05, 1])

    with center:
        st.markdown('<div class="auth-area">', unsafe_allow_html=True)

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
                            remember_login(user)
                            st.success("Login successful.")
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password.")

                    except Exception:
                        st.error("Unable to log in. Please try again.")

            st.write("")
            if st.button(
                "📥  Import Excel",
                key="auth_import_login",
                use_container_width=True,
            ):
                st.warning("Please sign in first. Import Excel is available from the Home page.")

        # ----------------------------------------------------
        # CREATE ACCOUNT
        # ----------------------------------------------------

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

                elif not re.fullmatch(r"[a-z0-9._-]{3,30}", username):
                    st.error(
                        "Username must contain 3–30 lowercase letters, "
                        "numbers, dots, underscores or hyphens."
                    )

                elif not email or not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+",
                    email,
                ):
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

                        # Clear form values so the new account is not
                        # accidentally submitted again.
                        for key in [
                            "signup_full_name",
                            "signup_username",
                            "signup_email",
                            "signup_password",
                            "signup_confirm",
                        ]:
                            st.session_state.pop(key, None)

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

            st.write("")
            if st.button(
                "📥  Import Excel",
                key="auth_import_signup",
                use_container_width=True,
            ):
                st.warning("Please sign in first. Import Excel is available from the Home page.")

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    """Shared sidebar shown on every signed-in page."""
    user = get_logged_user()

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

        nav_items = [
            ("Home", PAGE_BY_TITLE.get("Home")),
            ("Dashboard", PAGE_BY_TITLE.get("Dashboard")),
            ("Data Entry", PAGE_BY_TITLE.get("Data Entry")),
            ("Import Excel", PAGE_BY_TITLE.get("Import Excel")),
            ("Records", PAGE_BY_TITLE.get("Records")),
            ("My Account", PAGE_BY_TITLE.get("My Account")),
        ]

        for label, page in nav_items:
            if page is not None:
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
            try:
                logout_user()
            finally:
                clear_login()
                st.rerun()


# ============================================================
# HOME
# ============================================================

def render_home():

    user = get_logged_user()

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
            <div class="welcome-title">
                📊 HR Training Dashboard
            </div>
            <div class="welcome-text">
                Welcome back, <strong>{safe_name}</strong> 👋<br>
                Manage training programmes, participants, records
                and company-wide training performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # DASHBOARD
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
                '<div class="home-card-text">'
                'View company-wide KPIs, training hours, programmes, '
                'participants, costs and trends.'
                '</div>',
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
            else:
                st.caption("Dashboard page not found.")

    # --------------------------------------------------------
    # DATA ENTRY
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
                '<div class="home-card-text">'
                'Add new training programmes, participants, dates, '
                'locations, costs and training hours.'
                '</div>',
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
            else:
                st.caption("Data Entry page not found.")

    # --------------------------------------------------------
    # RECORDS
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
                '<div class="home-card-text">'
                'Browse, edit, export and manage existing training records.'
                '</div>',
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
            else:
                st.caption("Records page not found.")

    # --------------------------------------------------------
    # IMPORT EXCEL — ALWAYS VISIBLE AFTER LOGIN
    # --------------------------------------------------------

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
            '<div class="home-card-text">'
            'Import existing training information from Excel or CSV.'
            '</div>',
            unsafe_allow_html=True,
        )

        if import_page:
            if st.button(
                "Open Import Excel →",
                key="home_import_page",
                use_container_width=True,
                type="primary",
            ):
                go_to(import_page)
        else:
            st.caption(
                "No separate Import page was found, so the built-in uploader is available below."
            )

        # Built-in uploader is also available when there is no
        # dedicated Import page.
        if not import_page or st.session_state.get("open_excel_import", False):
            render_import_excel()

    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Logged-in User", full_name)

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

    if account_page:
        st.write("")
        if st.button(
            "👤  Open My Account",
            key="home_account",
            use_container_width=True,
        ):
            go_to(account_page)


# ============================================================
# NAVIGATION / APPLICATION
# ============================================================

HOME_PAGE = st.Page(
    render_home,
    title="Home",
    icon=None,
    default=True,
)

PAGE_BY_TITLE = {"Home": HOME_PAGE}
NAVIGATION_PAGES = [HOME_PAGE]

for _page_info in discover_pages():
    _page_path = _page_info["path"]

    if Path(_page_path).resolve() == Path(__file__).resolve():
        continue

    _title = _page_info["title"]
    if _title in PAGE_BY_TITLE:
        continue

    _page = st.Page(
        _page_path,
        title=_title,
        icon=None,
    )
    PAGE_BY_TITLE[_title] = _page
    NAVIGATION_PAGES.append(_page)

# Hide Streamlit's built-in page navigation. The custom sidebar is used.
pg = st.navigation(NAVIGATION_PAGES, position="hidden")

try:
    logged_in = bool(is_logged_in())
except Exception:
    logged_in = False

if logged_in or get_logged_user():
    render_sidebar()
    pg.run()
else:
    render_login_signup()
