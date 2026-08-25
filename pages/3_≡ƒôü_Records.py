import pandas as pd
import streamlit as st

from auth.auth import require_login, is_admin
from utils.styles import inject_css
from utils.helpers import load_records, update_record, delete_record, TRAINING_TYPES, QUARTERS

st.set_page_config(page_title="Records", page_icon="📁", layout="wide")
inject_css()
require_login()

st.markdown('<div class="app-title">Training Records</div>', unsafe_allow_html=True)
st.write("")

df = load_records()
if df.empty:
    st.info("No records yet. Add some from the **Data Entry** page.")
    st.stop()

search = st.text_input("🔎 Search by programme name, location or participant")
if search:
    mask = (
        df["programme_name"].str.contains(search, case=False, na=False)
        | df["location"].str.contains(search, case=False, na=False)
        | df["participant_names"].str.contains(search, case=False, na=False)
    )
    df = df[mask]

display_cols = [
    "id", "programme_name", "from_date", "to_date", "quarter", "training_type",
    "location", "participants_count", "training_hours", "total_hours",
    "training_cost", "participant_names",
]
st.dataframe(
    df[display_cols].rename(columns={
        "id": "ID", "programme_name": "Programme", "from_date": "From", "to_date": "To",
        "quarter": "Q", "training_type": "Type", "location": "Location",
        "participants_count": "Participants", "training_hours": "Hrs/Session",
        "total_hours": "Total Hrs", "training_cost": "Cost (Rs.)",
        "participant_names": "Participant Names",
    }),
    use_container_width=True,
    hide_index=True,
    height=420,
)

st.download_button(
    "⬇️ Export filtered records as CSV",
    data=df[display_cols].to_csv(index=False).encode("utf-8"),
    file_name="training_records_export.csv",
    mime="text/csv",
    use_container_width=True,
)

st.divider()
st.subheader("Edit or delete a record")

record_id = st.selectbox(
    "Select a record by ID",
    options=df["id"].tolist(),
    format_func=lambda i: f"#{i} — {df.loc[df['id'] == i, 'programme_name'].values[0]}",
)
row = df[df["id"] == record_id].iloc[0]

with st.form("edit_form"):
    c1, c2 = st.columns(2)
    with c1:
        programme_name = st.text_input("Programme Name", value=row["programme_name"])
        from_dt = st.date_input("From Date", value=row["from_date"].date())
        to_date_default = row["to_date"].date() if pd.notna(row["to_date"]) else row["from_date"].date()
        to_dt = st.date_input("To Date", value=to_date_default)
        training_type = st.selectbox("Type", TRAINING_TYPES, index=TRAINING_TYPES.index(row["training_type"]) if row["training_type"] in TRAINING_TYPES else 0)
        quarter = st.selectbox("Quarter", QUARTERS, index=QUARTERS.index(row["quarter"]) if row["quarter"] in QUARTERS else 0)
    with c2:
        location = st.text_input("Location", value=row["location"])
        training_hours = st.number_input("Training Hours (per session)", min_value=0.0, step=0.5, value=float(row["training_hours"]))
        participants_count = st.number_input("No. of Participants", min_value=0, step=1, value=int(row["participants_count"]))
        training_cost = st.number_input("Training Cost (Rs.)", min_value=0.0, step=500.0, value=float(row["training_cost"]))
    participant_names = st.text_area("Names of Participants", value=row["participant_names"] or "")

    col_save, col_delete = st.columns(2)
    with col_save:
        save = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
    with col_delete:
        delete = st.form_submit_button(
            "🗑️ Delete Record", use_container_width=True,
            disabled=not is_admin(),
        )

if save:
    update_record(
        record_id,
        {
            "programme_name": programme_name.strip(),
            "from_date": from_dt,
            "to_date": to_dt,
            "quarter": quarter,
            "training_type": training_type,
            "location": location.strip(),
            "participant_names": participant_names.strip(),
            "training_cost": training_cost,
            "training_hours": training_hours,
            "participants_count": participants_count,
        },
    )
    st.success("Record updated.")
    st.rerun()

if delete:
    if is_admin():
        delete_record(record_id)
        st.success("Record deleted.")
        st.rerun()
    else:
        st.error("Only admin accounts can delete records.")

if not is_admin():
    st.caption("ℹ️ Deleting records is restricted to admin accounts.")
