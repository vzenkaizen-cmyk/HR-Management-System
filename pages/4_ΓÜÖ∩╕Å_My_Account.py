import streamlit as st
from sqlalchemy import text

from auth.auth import require_login, current_user, change_password, is_admin
from database.db import get_engine
from utils.styles import inject_css

st.set_page_config(page_title="My Account", page_icon="⚙️", layout="wide")
inject_css()
require_login()
user = current_user()

st.markdown('<div class="app-title">My Account</div>', unsafe_allow_html=True)
st.write("")

st.subheader("Profile")
st.write(f"**Name:** {user['full_name']}")
st.write(f"**Username:** @{user['username']}")
st.write(f"**Email:** {user['email']}")
st.write(f"**Role:** {user['role']}")

st.divider()
st.subheader("Change password")
with st.form("change_pw"):
    new_pw = st.text_input("New password", type="password", help="At least 8 characters")
    confirm_pw = st.text_input("Confirm new password", type="password")
    submitted = st.form_submit_button("Update password")
if submitted:
    if new_pw != confirm_pw:
        st.error("Passwords do not match.")
    else:
        try:
            change_password(user["id"], new_pw)
            st.success("Password updated.")
        except ValueError as e:
            st.error(str(e))

if is_admin():
    st.divider()
    st.subheader("👑 Admin — Manage users")
    engine = get_engine()
    with engine.connect() as conn:
        users = conn.execute(
            text("SELECT id, username, email, full_name, role, created_at FROM users ORDER BY created_at")
        ).mappings().all()

    for u in users:
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        c1.write(f"**{u['full_name']}**  \n@{u['username']}")
        c2.write(u["email"])
        c3.write(u["role"])
        with c4:
            if u["id"] != user["id"]:
                new_role = "user" if u["role"] == "admin" else "admin"
                if st.button(f"Make {new_role}", key=f"role_{u['id']}"):
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE users SET role = :r WHERE id = :id"),
                            {"r": new_role, "id": u["id"]},
                        )
                    st.rerun()
