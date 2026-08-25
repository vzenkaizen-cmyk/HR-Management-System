from pathlib import Path
import html

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
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HR Training Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

def inject_css():

    st.markdown(
        """
        <style>

        /* =====================================================
           GLOBAL BACKGROUND
           ===================================================== */

        .stApp {
            background: linear-gradient(
                135deg,
                #f8fbff 0%,
                #edf6ff 50%,
                #e6f1fb 100%
            ) !important;
        }

        .main .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }


        /* =====================================================
           HIDE STREAMLIT DEFAULT PAGE NAVIGATION
           ===================================================== */

        [data-testid="stSidebarNav"] {
            display: none !important;
        }


        /* =====================================================
           HEADER
           ===================================================== */

        header {
            background: transparent !important;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }


        /* =====================================================
           MAIN TITLE
           ===================================================== */

        .app-title {
            color: #073b66 !important;
            font-size: 42px !important;
            font-weight: 800 !important;
            line-height: 1.2 !important;
            margin-bottom: 8px !important;
            letter-spacing: -1px;
        }

        .app-subtitle {
            color: #315875 !important;
            font-size: 17px !important;
            font-weight: 500 !important;
            margin-bottom: 25px !important;
        }


        /* =====================================================
           WELCOME BANNER
           ===================================================== */

        .welcome-box {
            background: linear-gradient(
                135deg,
                #0a4778 0%,
                #12679e 100%
            ) !important;

            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 28px;

            box-shadow:
                0 10px 28px rgba(7, 59, 102, 0.18);
        }

        .welcome-title {
            color: #ffffff !important;
            font-size: 27px !important;
            font-weight: 800 !important;
            margin-bottom: 8px;
        }

        .welcome-text {
            color: #f0f8ff !important;
            font-size: 16px !important;
            line-height: 1.6 !important;
        }


        /* =====================================================
           DASHBOARD CARDS
           ===================================================== */

        .dashboard-card {
            background: #ffffff !important;

            border: 1px solid #d5e5f2 !important;
            border-radius: 18px;

            padding: 25px;

            min-height: 190px;

            box-shadow:
                0 8px 24px rgba(15, 69, 105, 0.10);

            margin-bottom: 12px;
        }

        .dashboard-card:hover {
            box-shadow:
                0 12px 30px rgba(15, 69, 105, 0.17);
        }

        .dashboard-card-icon {
            font-size: 32px !important;
            margin-bottom: 10px;
        }

        .dashboard-card-title {
            color: #083b66 !important;
            font-size: 21px !important;
            font-weight: 800 !important;
            margin-bottom: 9px;
        }

        .dashboard-card-text {
            color: #405b70 !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
        }


        /* =====================================================
           AUTH CARD
           ===================================================== */

        .auth-card {
            background: #ffffff !important;

            border: 1px solid #d5e5f2 !important;

            border-radius: 20px;

            padding: 30px;

            box-shadow:
                0 15px 40px rgba(21, 75, 115, 0.14);
        }


        /* =====================================================
           AUTH HEADINGS
           ===================================================== */

        .auth-card h1,
        .auth-card h2,
        .auth-card h3,
        .auth-card p,
        .auth-card label {
            color: #123b59 !important;
        }


        /* =====================================================
           STREAMLIT TABS
           ===================================================== */

        button[data-baseweb="tab"] {
            color: #234e6b !important;
            font-weight: 700 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #087ea4 !important;
        }


        /* =====================================================
           INPUT LABELS
           ===================================================== */

        .stTextInput label,
        .stTextArea label,
        .stSelectbox label,
        .stNumberInput label {
            color: #123b59 !important;
            font-weight: 700 !important;
        }


        /* =====================================================
           INPUT BOXES
           ===================================================== */

        div[data-baseweb="input"] {
            background: #ffffff !important;
            border: 1px solid #b8cddd !important;
            border-radius: 9px !important;
        }

        div[data-baseweb="input"] input {
            color: #152b3d !important;
            background: #ffffff !important;
            -webkit-text-fill-color: #152b3d !important;
        }

        div[data-baseweb="input"] input::placeholder {
            color: #71869a !important;
            opacity: 1 !important;
        }


        /* =====================================================
           SELECT BOX
           ===================================================== */

        div[data-baseweb="select"] {
            background: #ffffff !important;
            color: #152b3d !important;
        }


        /* =====================================================
           NORMAL TEXT
           ===================================================== */

        .stMarkdown,
        .stMarkdown p,
        .stCaption,
        .stCaption p {
            color: #294a63 !important;
        }


        /* =====================================================
           PRIMARY BUTTONS
           ===================================================== */

        .stButton > button {
            min-height: 43px !important;

            border-radius: 10px !important;

            font-weight: 700 !important;

            border: 1px solid #0a5d91 !important;

            background: #0d5c91 !important;

            color: #ffffff !important;

            box-shadow: none !important;
        }

        .stButton > button:hover {
            background: #084c79 !important;
            border-color: #084c79 !important;
            color: #ffffff !important;
        }


        /* =====================================================
           SIDEBAR
           ===================================================== */

        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #073556 0%,
                #0a4772 55%,
                #0b507e 100%
            ) !important;
        }

        section[data-testid="stSidebar"] > div {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }


        /* =====================================================
           SIDEBAR BRAND
           ===================================================== */

        .sidebar-brand {
            text-align: center;

            padding: 12px 5px 18px 5px;

            color: #ffffff !important;

            font-size: 23px;

            font-weight: 800;
        }

        .sidebar-brand-icon {
            font-size: 31px;
            margin-bottom: 5px;
        }


        /* =====================================================
           SIDEBAR USER
           ===================================================== */

        .sidebar-user {
            background: rgba(255,255,255,0.11) !important;

            border: 1px solid rgba(255,255,255,0.14);

            border-radius: 14px;

            padding: 15px;

            margin: 5px 0 18px 0;
        }

        .sidebar-user-name {
            color: #ffffff !important;
            font-size: 16px;
            font-weight: 800;
        }

        .sidebar-user-role {
            color: #d9efff !important;
            font-size: 13px;
            margin-top: 5px;
        }


        /* =====================================================
           SIDEBAR NAVIGATION BUTTONS
           ===================================================== */

        .sidebar-nav-title {
            color: #a9d7f4 !important;

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 1.3px;

            text-transform: uppercase;

            margin: 12px 0 8px 4px;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.07) !important;

            color: #ffffff !important;

            border: 1px solid rgba(255,255,255,0.10) !important;

            border-radius: 10px !important;

            text-align: left !important;

            justify-content: flex-start !important;

            font-weight: 700 !important;

            margin-bottom: 7px !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.17) !important;

            border-color: rgba(255,255,255,0.25) !important;
        }


        /* =====================================================
           SIDEBAR DASHBOARD BUTTON
           ===================================================== */

        .dashboard-nav-button {
            background: #2b74a8 !important;

            border-radius: 10px;

            padding: 11px 13px;

            margin-bottom: 9px;

            color: #ffffff !important;

            font-weight: 800;

            border: 1px solid rgba(255,255,255,0.15);
        }


        /* =====================================================
           METRICS
           ===================================================== */

        [data-testid="stMetric"] {
            background: #ffffff !important;

            border: 1px solid #d7e6f1 !important;

            border-radius: 14px;

            padding: 16px;

            box-shadow:
                0 6px 18px rgba(12, 67, 105, 0.08);
        }

        [data-testid="stMetricLabel"] {
            color: #527089 !important;
        }

        [data-testid="stMetricValue"] {
            color: #0b3d63 !important;
        }


        /* =====================================================
           DIVIDER
           ===================================================== */

        .blue-divider {
            height: 2px;

            background: linear-gradient(
                90deg,
                #1b79b5,
                rgba(27,121,181,0)
            );

            margin: 22px 0;
        }


        /* =====================================================
           DARK THEME SUPPORT
           ===================================================== */

        @media (prefers-color-scheme: dark) {

            .stApp {
                background: linear-gradient(
                    135deg,
                    #101923 0%,
                    #15283a 50%,
                    #102c44 100%
                ) !important;
            }

            .app-title {
                color: #69c9ff !important;
            }

            .app-subtitle {
                color: #d1e5f3 !important;
            }

            .auth-card {
                background: #182735 !important;
                border-color: #36536a !important;
            }

            .auth-card h1,
            .auth-card h2,
            .auth-card h3,
            .auth-card p,
            .auth-card label {
                color: #eaf6ff !important;
            }

            button[data-baseweb="tab"] {
                color: #d6ebf8 !important;
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
                color: #152b3d !important;
                -webkit-text-fill-color: #152b3d !important;
            }

            .stMarkdown,
            .stMarkdown p,
            .stCaption,
            .stCaption p {
                color: #d9eaf5 !important;
            }

            .dashboard-card {
                background: #18364f !important;
                border-color: #2d5877 !important;
            }

            .dashboard-card-title {
                color: #ffffff !important;
            }

            .dashboard-card-text {
                color: #e1f1fb !important;
            }

            [data-testid="stMetric"] {
                background: #18364f !important;
                border-color: #2d5877 !important;
            }

            [data-testid="stMetricLabel"] {
                color: #c5dcea !important;
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

    st.markdown(
        """
        Make sure your Streamlit Secrets contain:

        ```toml
        [postgres]
        url = "YOUR_NEON_DATABASE_URL"
        ```
        """
    )

    with st.expander("Technical details"):
        st.exception(e)

    st.stop()


# ============================================================
# FIND PAGES
# ============================================================

def find_page(keyword):

    pages_dir = Path(__file__).parent / "pages"

    if not pages_dir.exists():
        return None

    keyword = keyword.lower()

    for file in pages_dir.glob("*.py"):

        filename = file.stem.lower()

        if keyword in filename:
            return str(file)

    return None


def get_page_title(filename):

    if not filename:
        return ""

    name = Path(filename).stem

    # Remove numbers at beginning
    name = name.lstrip("0123456789")

    # Remove separators
    name = name.lstrip("_- ")

    name = name.replace("_", " ")
    name = name.replace("-", " ")

    name = name.strip()

    lower = name.lower()

    if "dashboard" in lower:
        return "Dashboard"

    if "data" in lower:
        return "Data Entry"

    if "record" in lower:
        return "Records"

    if "account" in lower:
        return "My Account"

    return name.title()


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

    st.write("")

    left, center, right = st.columns([1, 1.3, 1])

    with center:

        st.markdown(
            '<div class="auth-card">',
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(
            [
                "🔐 Log in",
                "👤 Create account",
            ]
        )

        # ====================================================
        # LOGIN
        # ====================================================

        with login_tab:

            st.markdown("### Welcome back")

            st.caption(
                "Enter your username or email and password."
            )

            with st.form("login_form"):

                identifier = st.text_input(
                    "Username or email",
                    placeholder="Enter username or email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                )

                submitted = st.form_submit_button(
                    "Log in",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:

                if not identifier or not password:

                    st.error(
                        "Please enter both fields."
                    )

                else:

                    try:

                        user = authenticate(
                            identifier,
                            password,
                        )

                        if user:

                            login_user(user)

                            st.success(
                                "Login successful."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Invalid username/email or password."
                            )

                    except Exception as e:

                        st.error(
                            "Unable to log in."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.exception(e)

        # ====================================================
        # SIGNUP
        # ====================================================

        with signup_tab:

            st.markdown(
                "### Create your account"
            )

            st.caption(
                "Register to access the HR Training Dashboard."
            )

            with st.form("signup_form"):

                full_name = st.text_input(
                    "Full name",
                    placeholder="e.g. Samoda De Silva",
                )

                username = st.text_input(
                    "Username",
                    placeholder="e.g. samoda",
                )

                email = st.text_input(
                    "Email",
                    placeholder="name@company.com",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Minimum 8 characters",
                )

                confirm = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password",
                )

                submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:

                if password != confirm:

                    st.error(
                        "Passwords do not match."
                    )

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
                            "Please log in."
                        )

                    except ValueError as e:

                        st.error(str(e))

                    except Exception as e:

                        st.error(
                            "Unable to create the account."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.exception(e)

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


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

    username = user.get(
        "username",
        "",
    )

    role = user.get(
        "role",
        "user",
    )

    dashboard_page = find_page("dashboard")
    data_page = find_page("data")
    records_page = find_page("record")
    account_page = find_page("account")

    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="sidebar-brand">

                <div class="sidebar-brand-icon">
                    📊
                </div>

                HR Training Dashboard

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        safe_name = html.escape(str(full_name))
        safe_username = html.escape(str(username))
        safe_role = html.escape(str(role.title()))

        st.markdown(
            f"""
            <div class="sidebar-user">

                <div class="sidebar-user-name">
                    👤 {safe_name}
                </div>

                <div class="sidebar-user-role">
                    @{safe_username} · {safe_role}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-nav-title">Navigation</div>',
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # HOME
        # ----------------------------------------------------

        if st.button(
            "🏠   Home",
            key="nav_home",
            use_container_width=True,
        ):

            st.switch_page("app.py")

        # ----------------------------------------------------
        # DASHBOARD
        # ----------------------------------------------------

        if dashboard_page:

            if st.button(
                "📊   Dashboard",
                key="nav_dashboard",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    dashboard_page
                )

        # ----------------------------------------------------
        # DATA ENTRY
        # ----------------------------------------------------

        if data_page:

            if st.button(
                "📝   Data Entry",
                key="nav_data",
                use_container_width=True,
            ):

                st.switch_page(
                    data_page
                )

        # ----------------------------------------------------
        # RECORDS
        # ----------------------------------------------------

        if records_page:

            if st.button(
                "📁   Records",
                key="nav_records",
                use_container_width=True,
            ):

                st.switch_page(
                    records_page
                )

        # ----------------------------------------------------
        # MY ACCOUNT
        # ----------------------------------------------------

        if account_page:

            if st.button(
                "👤   My Account",
                key="nav_account",
                use_container_width=True,
            ):

                st.switch_page(
                    account_page
                )

        st.markdown(
            '<div class="blue-divider"></div>',
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.button(
            "🚪   Log out",
            key="nav_logout",
            use_container_width=True,
        ):

            logout_user()

            st.rerun()


# ============================================================
# HOME
# ============================================================

def render_home():

    user = current_user()

    full_name = (
        user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    role = user.get(
        "role",
        "user",
    )

    dashboard_page = find_page("dashboard")
    data_page = find_page("data")
    records_page = find_page("record")
    account_page = find_page("account")

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    safe_name = html.escape(str(full_name))

    st.markdown(
        f"""
        <div class="welcome-box">

            <div class="welcome-title">
                📊 HR Training Dashboard
            </div>

            <div class="welcome-text">
                Welcome back,
                <strong>{safe_name}</strong> 👋
                <br>
                Manage training programmes,
                participants, records and
                company-wide training performance.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    # ========================================================
    # DASHBOARD
    # ========================================================

    with col1:

        st.markdown(
            """
            <div class="dashboard-card">

                <div class="dashboard-card-icon">
                    📊
                </div>

                <div class="dashboard-card-title">
                    Dashboard
                </div>

                <div class="dashboard-card-text">
                    View company-wide training KPIs,
                    training hours, programmes,
                    participants, costs and trends.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if dashboard_page:

            if st.button(
                "Open Dashboard →",
                key="home_dashboard",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    dashboard_page
                )

    # ========================================================
    # DATA ENTRY
    # ========================================================

    with col2:

        st.markdown(
            """
            <div class="dashboard-card">

                <div class="dashboard-card-icon">
                    📝
                </div>

                <div class="dashboard-card-title">
                    Data Entry
                </div>

                <div class="dashboard-card-text">
                    Add training programmes,
                    participants, dates,
                    locations, costs and
                    training hours.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if data_page:

            if st.button(
                "Add Training →",
                key="home_data",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    data_page
                )

    # ========================================================
    # RECORDS
    # ========================================================

    with col3:

        st.markdown(
            """
            <div class="dashboard-card">

                <div class="dashboard-card-icon">
                    📁
                </div>

                <div class="dashboard-card-title">
                    Records
                </div>

                <div class="dashboard-card-text">
                    Browse, edit, export and
                    manage existing training
                    records.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if records_page:

            if st.button(
                "View Records →",
                key="home_records",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    records_page
                )

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    if account_page:

        st.write("")

        if st.button(
            "👤  My Account",
            key="home_account",
            use_container_width=True,
        ):

            st.switch_page(
                account_page
            )

    # --------------------------------------------------------
    # USER INFO
    # --------------------------------------------------------

    st.markdown(
        '<div class="blue-divider"></div>',
        unsafe_allow_html=True,
    )

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
            role.title(),
        )


# ============================================================
# RUN APPLICATION
# ============================================================

if is_logged_in():

    render_sidebar()
    render_home()

else:

    render_login_signup()
