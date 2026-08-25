import streamlit as st

from database.db import init_db
from auth.auth import authenticate, create_user, login_user, logout_user, is_logged_in, current_user
from utils.styles import inject_css

st.set_page_config(
    page_title="HR Training Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded" if is_logged_in() else "collapsed",
)
inject_css()

# Create tables / seed first admin on first ever run. Cheap no-op after that.
try:
    init_db()
except Exception as e:
    st.error(
        "Could not connect to the database. Check that `postgres.url` is set "
        "correctly in `.streamlit/secrets.toml` (or the app's Secrets on Streamlit "
        "Community Cloud)."
    )
    st.exception(e)
    st.stop()


def render_login_signup():
    st.markdown('<div class="app-title">🏋️ HR Training Dashboard</div>', unsafe_allow_html=True)
    st.caption("Training records, sign in to continue.")
    st.write("")

    left, mid, right = st.columns([1, 1.3, 1])
    with mid:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Log in", "Create account"])

        with tab_login:
            with st.form("login_form"):
                identifier = st.text_input("Username or email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log in", use_container_width=True)
            if submitted:
                if not identifier or not password:
                    st.error("Please enter both fields.")
                else:
                    user = authenticate(identifier, password)
                    if user:
                        login_user(user)
                        st.rerun()
                    else:
                        st.error("Invalid username/email or password.")

        with tab_signup:
            with st.form("signup_form"):
                full_name = st.text_input("Full name")
                username = st.text_input("Username", help="Lowercase letters, numbers, '.' and '_' only")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password", help="At least 8 characters")
                confirm = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        create_user(username, email, full_name, password)
                        st.success("Account created! Please log in from the **Log in** tab.")
                    except ValueError as e:
                        st.error(str(e))
        st.markdown("</div>", unsafe_allow_html=True)


def render_home():
    user = current_user()
    st.markdown('<div class="app-title">🏋️ HR Training Dashboard</div>', unsafe_allow_html=True)
    st.write(f"Welcome back, **{user['full_name']}** 👋")
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**📊 Dashboard**\n\nCompany-wide training KPIs, trends and cost breakdowns.")
    with c2:
        st.info("**📝 Data Entry**\n\nLog a new training programme and its participants.")
    with c3:
        st.info("**📁 Records**\n\nBrowse, edit, export or (admin) delete existing records.")
    st.caption("Use the sidebar to navigate between pages.")

    with st.sidebar:
        st.write(f"👤 **{user['full_name']}**")
        st.caption(f"@{user['username']} · {user['role']}")
        if st.button("Log out", use_container_width=True):
            logout_user()
            st.rerun()


if is_logged_in():
    render_home()
else:
    render_login_signup()
