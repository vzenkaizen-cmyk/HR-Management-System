"""Data-access helpers for training records (used by Dashboard, Data Entry, Records pages)."""

from datetime import date
import pandas as pd
import streamlit as st
from sqlalchemy import text

from database.db import get_engine

TRAINING_TYPES = ["Technical", "Soft Skill"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]


def quarter_for_date(d: date) -> str:
    return f"Q{((d.month - 1) // 3) + 1}"


@st.cache_data(ttl=60, show_spinner=False)
def load_records() -> pd.DataFrame:
    engine = get_engine()
    df = pd.read_sql(
        "SELECT * FROM training_records ORDER BY from_date DESC, id DESC", engine
    )
    if not df.empty:
        df["from_date"] = pd.to_datetime(df["from_date"])
        df["to_date"] = pd.to_datetime(df["to_date"])
        df["year"] = df["from_date"].dt.year
        df["month"] = df["from_date"].dt.strftime("%b")
        df["month_num"] = df["from_date"].dt.month
    return df


def distinct_locations() -> list[str]:
    df = load_records()
    if df.empty:
        return []
    return sorted(df["location"].dropna().unique().tolist())


def insert_record(data: dict, created_by: int):
    engine = get_engine()
    total_hours = float(data["training_hours"]) * int(data["participants_count"])
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO training_records
                    (programme_name, from_date, to_date, quarter, training_type,
                     location, participant_names, training_cost, training_hours,
                     participants_count, total_hours, created_by)
                VALUES
                    (:programme_name, :from_date, :to_date, :quarter, :training_type,
                     :location, :participant_names, :training_cost, :training_hours,
                     :participants_count, :total_hours, :created_by)
                """
            ),
            {**data, "total_hours": total_hours, "created_by": created_by},
        )
    load_records.clear()


def update_record(record_id: int, data: dict):
    engine = get_engine()
    total_hours = float(data["training_hours"]) * int(data["participants_count"])
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE training_records SET
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
                WHERE id = :id
                """
            ),
            {**data, "total_hours": total_hours, "id": record_id},
        )
    load_records.clear()


def delete_record(record_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM training_records WHERE id = :id"), {"id": record_id})
    load_records.clear()


def apply_filters(df: pd.DataFrame, location, year, month, ttype) -> pd.DataFrame:
    out = df.copy()
    if location and location != "All Locations":
        out = out[out["location"] == location]
    if year and year != "All Years":
        out = out[out["year"] == int(year)]
    if month and month != "All Months":
        out = out[out["month"] == month]
    if ttype and ttype != "All Types":
        out = out[out["training_type"] == ttype]
    return out
