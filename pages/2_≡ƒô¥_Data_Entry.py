from datetime import date
import streamlit as st

from auth.auth import require_login, current_user
from utils.styles import inject_css
from utils.helpers import (
    distinct_locations, insert_record,
    TRAINING_TYPES, QUARTERS, quarter_for_date,
)

st.set_page_config(page_title="Data Entry", page_icon="📝", layout="wide")
inject_css()
require_login()

st.markdown('<div class="app-title">Add a Training Record</div>', unsafe_allow_html=True)
st.caption("Fill in the details below. Total hours are calculated automatically as hours × participants.")
st.write("")

existing_locations = distinct_locations()

with st.form("data_entry_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        programme_name = st.text_input("Name of the Programme *")
        from_dt = st.date_input("From Date *", value=date.today())
        to_dt = st.date_input("To Date", value=date.today())
        training_type = st.selectbox("Type *", TRAINING_TYPES)
        quarter = st.selectbox("Quarter *", QUARTERS, index=QUARTERS.index(quarter_for_date(from_dt)))
    with c2:
        loc_choice = st.selectbox("Location *", existing_locations + ["+ Add new location"])
        new_location = ""
        if loc_choice == "+ Add new location":
            new_location = st.text_input("New location name *")
        training_hours = st.number_input("Training Hours (per session) *", min_value=0.0, step=0.5)
        participants_count = st.number_input("No. of Participants *", min_value=0, step=1)
        training_cost = st.number_input("Training Cost (Rs.) *", min_value=0.0, step=500.0)

    participant_names = st.text_area(
        "Names of Participants", placeholder="e.g. Amr, Mafaz, Roshan (comma separated)"
    )

    if training_hours and participants_count:
        st.caption(f"Total hours (auto-calculated): **{training_hours * participants_count:,.1f}**")

    submitted = st.form_submit_button("Save Record", use_container_width=True, type="primary")

if submitted:
    location = new_location.strip() if loc_choice == "+ Add new location" else loc_choice
    errors = []
    if not programme_name.strip():
        errors.append("Programme name is required.")
    if not location:
        errors.append("Location is required.")
    if to_dt < from_dt:
        errors.append("'To Date' cannot be before 'From Date'.")
    if training_hours <= 0:
        errors.append("Training hours must be greater than 0.")
    if participants_count <= 0:
        errors.append("Number of participants must be greater than 0.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        insert_record(
            {
                "programme_name": programme_name.strip(),
                "from_date": from_dt,
                "to_date": to_dt,
                "quarter": quarter,
                "training_type": training_type,
                "location": location,
                "participant_names": participant_names.strip(),
                "training_cost": training_cost,
                "training_hours": training_hours,
                "participants_count": participants_count,
            },
            created_by=current_user()["id"],
        )
        st.success(f"✅ '{programme_name}' saved successfully.")
        st.balloons()
