import streamlit as st
import pandas as pd
from pathlib import Path

from auth.auth import is_logged_in, current_user

st.set_page_config(
    page_title="Import Excel | HR Training Dashboard",
    page_icon="📥",
    layout="wide",
)

st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #f4f9fd !important;
    color-scheme: light !important;
}
.stApp {
    background: linear-gradient(135deg, #f7fbff 0%, #edf6ff 52%, #e5f0fa 100%) !important;
}
h1, h2, h3, p, label, .stCaption {
    color: #173f5c !important;
}
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
.stButton > button,
.stDownloadButton > button {
    border-radius: 9px !important;
    font-weight: 700 !important;
    background: #13233f !important;
    color: #ffffff !important;
    border: 1px solid #13233f !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #1d355d !important;
    color: #ffffff !important;
}
[data-testid="stAlert"] {
    color: #173f5c !important;
    background: #eef6fc !important;
    border: 1px solid #c8dceb !important;
}
</style>
""",
    unsafe_allow_html=True,
)

if not is_logged_in():
    st.warning("Please log in from the Home page to access Import Excel.")
    st.stop()

user = current_user() or {}
name = user.get("full_name") or user.get("username") or "User"

st.title("Import Excel")
st.caption(
    f"Welcome, {name}. Upload an Excel or CSV file to review it before importing."
)

uploaded = st.file_uploader(
    "Choose an Excel or CSV file",
    type=["xlsx", "xls", "csv"],
)

if uploaded:
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)

        st.success(
            f"{uploaded.name} loaded successfully — "
            f"{len(df):,} rows × {len(df.columns):,} columns."
        )

        st.subheader("Preview")
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)

        st.subheader("Column names")
        st.write(", ".join(str(c) for c in df.columns))

        st.download_button(
            "Download cleaned preview as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{Path(uploaded.name).stem}_preview.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.info(
            "The file is currently previewed only. Database insertion is not "
            "performed automatically, so the existing training-record schema "
            "is preserved."
        )

    except Exception as exc:
        st.error("Unable to read this file.")
        st.caption(str(exc))
