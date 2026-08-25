import os
from pathlib import Path

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
# CUSTOM CSS
# ============================================================

def inject_custom_css():

    st.markdown(
        """
        <style>

        /* ==================================================
           MAIN APPLICATION BACKGROUND
           ================================================== */

        .stApp {
            background:
                linear-gradient(
                    135deg,
                    #f8fbff 0%,
                    #eef6ff 45%,
                    #e7f1ff 100%
                ) !important;
        }


        /* ==================================================
           MAIN CONTENT
           ================================================== */

        .main .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }


        /* ==================================================
           TITLE
           ================================================== */

        .app-title {
            font-size: 42px;
            font-weight: 800;
            color: #083b66 !important;
            margin-bottom: 8px;
            letter-spacing: -1px;
        }

        .app-subtitle {
            font-size: 18px;
            color: #46627c !important;
            margin-bottom: 25px;
        }


        /* ==================================================
           WELCOME BANNER
           ================================================== */

        .welcome-box {
            background:
                linear-gradient(
                    135deg,
                    #0b4778,
                    #1468a5
                );
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 30px;
            box-shadow:
                0 10px 30px rgba(13, 71, 115, 0.18);
        }

        .welcome-title {
            color: white !important;
            font-size: 27px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .welcome-text {
            color: #eaf6ff !important;
            font-size: 16px;
        }


        /* ==================================================
           DASHBOARD CARDS
           ================================================== */

        .dashboard-card {
            background:
                linear-gradient(
                    145deg,
                    #123f68,
                    #195d91
                );
            border-radius: 18px;
            padding: 27px;
            min-height: 190px;
            box-shadow:
                0 10px 25px rgba(16, 62, 98, 0.18);
            border: 1px solid rgba(255,255,255,0.15);
            margin-bottom: 20px;
        }

        .dashboard-card-icon {
            font-size: 30px;
            margin-bottom: 8px;
        }

        .dashboard-card-title {
            color: white !important;
            font-size: 21px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .dashboard-card-text {
            color: #e9f5ff !important;
            font-size: 15px;
            line-height: 1.6;
        }


        /* ==================================================
           AUTH CARD
           ================================================== */

        .auth-card {
            background: white;
            border-radius: 20px;
            padding: 32px;
            box-shadow:
                0 15px 40px rgba(21, 75, 115, 0.15);
            border: 1px solid #d8e8f5;
        }


        /* ==================================================
           STREAMLIT BUTTONS
           ================================================== */

        .stButton > button {
            border-radius: 10px;
            border: none;
            font-weight: 700;
            min-height: 42px;
        }

        .stButton > button[kind="primary"] {
            background: #0d5c91 !important;
            color: white !important;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #082d4c 0%,
                    #0b416b 100%
                ) !important;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.10) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.18) !important;
        }


        /* ==================================================
           SIDEBAR USER CARD
           ================================================== */

        .sidebar-user {
            background: rgba(255,255,255,0.10);
            border-radius: 14px;
            padding: 16px;
            margin-top: 20px;
            margin-bottom: 15px;
        }

        .sidebar-user-name {
            font-size: 17px;
            font-weight: 700;
            color: white !important;
        }

        .sidebar-user-role {
            font-size: 13px;
            color: #d8edff !important;
            margin-top: 4px;
        }


        /* ==================================================
           DIVIDER
           ================================================== */

        .blue-divider {
            height: 2px;
            background: linear-gradient(
                90deg,
                #1a78b5,
                transparent
            );
            margin: 20px 0;
        }


        /* ==================================================
           DATAFRAME / INPUTS
           ================================================== */

        div[data-baseweb="input"] {
            border-radius: 8px;
        }

        div[data-baseweb="select"] {
            border-radius: 8px;
        }


        /* ==================================================
           DARK MODE COMPATIBILITY
           ================================================== */

        @media (prefers-color-scheme: dark) {

            .stApp {
                background:
                    linear-gradient(
                        135deg,
                        #111827 0%,
                        #17263a 50%,
                        #102b45 100%
                    ) !important;
            }

            .app-title {
                color: #67c7ff !important;
            }

            .app-subtitle {
                color: #c7d9e8 !important;
            }

            .auth-card {
                background: #182638 !important;
                border: 1px solid #2e4c66 !important;
            }

            .welcome-box {
                background:
                    linear-gradient(
                        135deg,
                        #0b4778,
                        #1468a5
                    ) !important;
            }

            .dashboard-card {
                background:
                    linear-gradient(
                        145deg,
                        #173f61,
                        #205f8e
                    ) !important;
            }

            label,
            .stMarkdown,
            .stText,
            p {
                color: #e8f3fb;
            }
        }


        /* ==================================================
           HIDE STREAMLIT BRANDING
           ================================================== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

try:

    init_db()

except Exception as e:

    st.error(
        "Unable to connect to the HR database."
    )

    st.markdown(
        """
        Please check that your Streamlit secret contains:

        ```toml
        [postgres]
        url = "YOUR_NEON_DATABASE_URL"
        ```
        """
    )

    with st.expander("Technical error details"):
        st.exception(e)

    st.stop()


# ============================================================
# PAGE DISCOVERY
# ============================================================

def discover_pages():

    pages = []

    pages_directory = Path(__file__).parent / "pages"

    if not pages_directory.exists():
        return pages

    for file in sorted(pages_directory.glob("*.py")):

        filename = file.stem

        # Ignore special files
        if filename.startswith("_"):
            continue

        # ---------------------------------------------
        # Convert filename into readable title
        # ---------------------------------------------

        title = filename

        # Remove leading numbers
        title = title.lstrip("0123456789")

        # Remove leading separators
        title = title.lstrip("_- ")

        # Replace underscores and hyphens
        title = title.replace("_", " ")
        title = title.replace("-", " ")

        title = title.strip()

        # ---------------------------------------------
        # Fix common page names
        # ---------------------------------------------

        lower_title = title.lower()

        if "dashboard" in lower_title:
            title = "Dashboard"

        elif "data entry" in lower_title:
            title = "Data Entry"

        elif "record" in lower_title:
            title = "Records"

        elif "account" in lower_title:
            title = "My Account"

        elif "training" in lower_title:
            title = "Training"

        pages.append(
            {
                "path": str(file),
                "title": title,
            }
        )

    return pages


# ============================================================
# STREAMLIT NAVIGATION
# ============================================================

def create_navigation():

    discovered_pages = discover_pages()

    navigation = {}

    # Home
    navigation["Home"] = [
        st.Page(
            "app.py",
            title="Home",
            icon="🏠",
            default=True,
        )
    ]

    # Existing pages
    page_items = []

    for page in discovered_pages:

        # Do not add app.py itself
        if Path(page["path"]).resolve() == Path(__file__).resolve():
            continue

        icon = "📄"

        title_lower = page["title"].lower()

        if "dashboard" in title_lower:
            icon = "📊"

        elif "data" in title_lower:
            icon = "📝"

        elif "record" in title_lower:
            icon = "📁"

        elif "account" in title_lower:
            icon = "👤"

        page_items.append(
            st.Page(
                page["path"],
                title=page["title"],
                icon=icon,
            )
        )

    if page_items:
        navigation["HR Management"] = page_items

    return navigation


# ============================================================
# LOGIN / SIGNUP PAGE
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

    left, mid, right = st.columns(
        [1, 1.35, 1]
    )

    with mid:

        st.markdown(
            '<div class="auth-card">',
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(
            [
                "🔐 Log in",
                "👤 Create account",
            ]
        )

        # ====================================================
        # LOGIN
        # ====================================================

        with tab_login:

            st.markdown(
                "### Welcome back"
            )

            st.caption(
                "Enter your username/email and password."
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
                    "🔐 Log in",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:

                if not identifier or not password:

                    st.error(
                        "Please enter both username/email and password."
                    )

                else:

                    try:

                        user = authenticate(
                            identifier,
                            password
                        )

                        if user:

                            login_user(user)

                            st.success(
                                "Login successful!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Invalid username/email or password."
                            )

                    except Exception as e:

                        st.error(
                            "Unable to log in. "
                            "Please try again."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.exception(e)

        # ====================================================
        # SIGNUP
        # ====================================================

        with tab_signup:

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
                    help=(
                        "Use lowercase letters, numbers, "
                        "'.' or '_'."
                    ),
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
                    "👤 Create account",
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
                            "Account created successfully! "
                            "Please use the Log in tab."
                        )

                    except ValueError as e:

                        st.error(
                            str(e)
                        )

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
# HOME DASHBOARD
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
        "user"
    )

    # ========================================================
    # WELCOME BANNER
    # ========================================================

    st.markdown(
        f"""
        <div class="welcome-box">

            <div class="welcome-title">
                📊 HR Training Dashboard
            </div>

            <div class="welcome-text">
                Welcome back, <strong>{full_name}</strong> 👋
                <br>
                Manage training programmes, participants,
                records and company-wide training performance.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # DASHBOARD CARDS
    # ========================================================

    pages = discover_pages()

    dashboard_page = None
    data_page = None
    records_page = None
    account_page = None

    for page in pages:

        title = page["title"].lower()

        if "dashboard" in title:
            dashboard_page = page["path"]

        elif "data" in title:
            data_page = page["path"]

        elif "record" in title:
            records_page = page["path"]

        elif "account" in title:
            account_page = page["path"]

    # ========================================================
    # CARD 1
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="dashboard-card">

                <div class="dashboard-card-icon">
                    📊
                </div>

                <div class="dashboard-card-title">
                    Training Dashboard
                </div>

                <div class="dashboard-card-text">
                    View company-wide training KPIs,
                    trends, costs, participation and
                    training performance.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if dashboard_page:

            if st.button(
                "Open Dashboard →",
                key="open_dashboard",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    dashboard_page
                )

    # ========================================================
    # CARD 2
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
                    Add new training programmes,
                    participants, dates, locations,
                    costs and training hours.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if data_page:

            if st.button(
                "Add Training →",
                key="open_data",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    data_page
                )

    # ========================================================
    # CARD 3
    # ========================================================

    with col3:

        st.markdown(
            """
            <div class="dashboard-card">

                <div class="dashboard-card-icon">
                    📁
                </div>

                <div class="dashboard-card-title">
                    Training Records
                </div>

                <div class="dashboard-card-text">
                    Browse, edit, export and manage
                    existing training records.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if records_page:

            if st.button(
                "View Records →",
                key="open_records",
                use_container_width=True,
                type="primary",
            ):

                st.switch_page(
                    records_page
                )

    # ========================================================
    # USER INFORMATION
    # ========================================================

    st.write("")

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

    # ========================================================
    # ACCOUNT BUTTON
    # ========================================================

    if account_page:

        st.write("")

        if st.button(
            "👤 Open My Account",
            use_container_width=True,
        ):

            st.switch_page(
                account_page
            )

    st.caption(
        "Use the sidebar to navigate between HR Training pages."
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
        ""
    )

    role = user.get(
        "role",
        "user"
    )

    with st.sidebar:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:10px 0 15px 0;
                font-size:28px;
            ">
                📊
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:20px;
                font-weight:800;
                color:white;
                margin-bottom:20px;
            ">
                HR Training
            </div>
            """,
            unsafe_allow_html=True,
        )

        # User card

        st.markdown(
            f"""
            <div class="sidebar-user">

                <div class="sidebar-user-name">
                    👤 {full_name}
                </div>

                <div class="sidebar-user-role">
                    @{username} · {role.title()}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="blue-divider"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "🏠 Home",
            use_container_width=True,
        ):

            st.switch_page(
                "app.py"
            )

        # ----------------------------------------------
        # Dynamic page links
        # ----------------------------------------------

        pages = discover_pages()

        for page in pages:

            page_path = page["path"]

            if Path(page_path).resolve() == Path(__file__).resolve():
                continue

            title = page["title"]
            title_lower = title.lower()

            icon = "📄"

            if "dashboard" in title_lower:
                icon = "📊"

            elif "data" in title_lower:
                icon = "📝"

            elif "record" in title_lower:
                icon = "📁"

            elif "account" in title_lower:
                icon = "👤"

            if st.button(
                f"{icon} {title}",
                key=f"sidebar_{page_path}",
                use_container_width=True,
            ):

                st.switch_page(
                    page_path
                )

        st.write("")

        if st.button(
            "🚪 Log out",
            use_container_width=True,
        ):

            logout_user()

            st.rerun()


# ============================================================
# APPLICATION START
# ============================================================

if not is_logged_in():

    render_login_signup()

else:

    render_sidebar()

    render_home()
