from pathlib import Path
import html
import re
from datetime import date, datetime

import pandas as pd
import streamlit as st

from database.db import init_db, run_query, run_write
from auth.auth import (
    authenticate,
    create_user,
    login_user,
    logout_user,
    is_logged_in,
    current_user,
    change_password,
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

try:
    st.set_option("client.showSidebarNavigation", False)
except Exception:
    pass


# ============================================================
# LIGHT UI
# ============================================================

st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #f4f9fd !important;
    color: #173f5c !important;
}
.stApp {
    background: linear-gradient(135deg,#f7fbff 0%,#edf6ff 52%,#e5f0fa 100%) !important;
}
.main .block-container {
    max-width: none !important;
    width: 100% !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
[data-testid="stSidebarNav"] { display:none !important; }
#MainMenu, footer { visibility:hidden !important; }
header { background:transparent !important; }

h1,h2,h3,h4,h5,h6,
.stMarkdown,.stMarkdown p,.stCaption,.stCaption p,
[data-testid="stMarkdownContainer"] { color:#173f5c !important; }

.app-title { color:#073b66 !important; font-size:42px !important; font-weight:800 !important; }
.app-subtitle { color:#527089 !important; font-size:16px !important; margin-bottom:20px; }

/* Inputs */
.stTextInput label,.stTextArea label,.stSelectbox label,
.stNumberInput label,.stDateInput label,.stFileUploader label {
    color:#173f5c !important; font-weight:700 !important;
}
div[data-baseweb="input"],div[data-baseweb="base-input"],
div[data-baseweb="select"] > div {
    background:#ffffff !important;
    border:1px solid #b8cbd9 !important;
    border-radius:9px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
[data-testid="stDateInput"] input {
    background:#ffffff !important;
    color:#172b3d !important;
    -webkit-text-fill-color:#172b3d !important;
    caret-color:#0879a5 !important;
}
div[data-baseweb="select"] * { color:#173f5c !important; }

/* ============================================================
   DASHBOARD FILTERS — NO ELLIPSIS / FULL SELECTED TEXT
   The six filters are deliberately split into two rows. This gives
   every selectbox enough real width; CSS alone cannot make six long
   labels fit into a narrow single row without clipping.
   ============================================================ */
.st-key-dashboard_filters {
    width: 100% !important;
}

.st-key-dashboard_filters [data-testid="stHorizontalBlock"] {
    width: 100% !important;
    gap: 0.75rem !important;
}

.st-key-dashboard_filters [data-testid="column"] {
    min-width: 0 !important;
}

/* Make every selectbox fill its complete column. */
.st-key-dashboard_filters [data-testid="stSelectbox"],
.st-key-dashboard_filters [data-testid="stSelectbox"] > div,
.st-key-dashboard_filters div[data-baseweb="select"],
.st-key-dashboard_filters div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* BaseWeb creates the visible selected value several levels deep.
   These rules remove its default ellipsis and allow the text to use
   the complete width available before the arrow. */
.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    min-width: 0 !important;
    overflow: visible !important;
}

.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] > div {
    overflow: visible !important;
}

.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] > div:first-child {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    overflow: visible !important;
}

.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] > div:first-child > div {
    max-width: none !important;
    width: auto !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
}

.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] span,
.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] p {
    max-width: none !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
}

/* Keep the arrow area compact; give the wording the available space. */
.st-key-dashboard_filters div[data-baseweb="select"] [role="button"] svg {
    flex: 0 0 auto !important;
}

/* Dropdown options: never truncate long names. */
div[data-baseweb="popover"] {
    max-width: none !important;
}

div[data-baseweb="popover"] [role="listbox"] {
    min-width: max-content !important;
    width: max-content !important;
    max-width: none !important;
}

div[data-baseweb="popover"] [role="option"] {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
}

/* Second-row filters get extra width so long values such as
   "Japanese Management Systems" and "Management Training" remain visible. */
.st-key-dashboard_filters [data-testid="stHorizontalBlock"]:nth-of-type(2) {
    width: 100% !important;
    gap: 0.75rem !important;
}

.st-key-dashboard_filters [data-testid="stHorizontalBlock"]:nth-of-type(2) [data-testid="column"]:nth-child(1),
.st-key-dashboard_filters [data-testid="stHorizontalBlock"]:nth-of-type(2) [data-testid="column"]:nth-child(2) {
    min-width: 0 !important;
}

/* Remove the internal BaseWeb text-width restriction that causes
   Streamlit to render selected values with "...". */
.st-key-dashboard_filters [data-baseweb="select"] > div {
    padding-left: 10px !important;
    padding-right: 8px !important;
    overflow: visible !important;
}

.st-key-dashboard_filters [data-baseweb="select"] [data-baseweb="select"] {
    overflow: visible !important;
}

.st-key-dashboard_filters [data-baseweb="select"] [role="button"] {
    overflow: visible !important;
    text-overflow: clip !important;
}

.st-key-dashboard_filters [data-baseweb="select"] [role="button"] > div {
    overflow: visible !important;
    text-overflow: clip !important;
}

.st-key-dashboard_filters [data-baseweb="select"] [role="button"] > div:first-child {
    min-width: 0 !important;
    max-width: calc(100% - 28px) !important;
    overflow: visible !important;
}

.st-key-dashboard_filters [data-baseweb="select"] [role="button"] > div:first-child > div {
    max-width: none !important;
    width: max-content !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
}

/* Keep the visible control itself wide and compact. */
.st-key-dashboard_filters [data-testid="stSelectbox"] {
    width: 100% !important;
    min-width: 0 !important;
}

.st-key-dashboard_filters [data-testid="stSelectbox"] label {
    white-space: nowrap !important;
}

/* Responsive fallback: on narrower screens stack the filters instead
   of squeezing them until Streamlit clips their text. */
@media (max-width: 1100px) {
    .st-key-dashboard_filters [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
}

@media (max-width: 900px) {
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p {
        white-space: normal !important;
    }
}

/* Buttons */
.stButton > button,.stFormSubmitButton > button,.stDownloadButton > button {
    min-height:42px !important;
    border-radius:9px !important;
    font-weight:750 !important;
}
.stButton > button[kind="primary"],.stFormSubmitButton > button[kind="primary"] {
    background:#0879a5 !important; color:#fff !important;
    -webkit-text-fill-color:#fff !important; border:1px solid #0879a5 !important;
}
.stButton > button[kind="primary"] *,
.stFormSubmitButton > button[kind="primary"] * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}
.stButton > button:not([kind="primary"]),.stDownloadButton > button {
    background:#13233f !important; color:#fff !important;
    -webkit-text-fill-color:#fff !important; border:1px solid #13233f !important;
}
.stButton > button:not([kind="primary"]) *, .stDownloadButton > button * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#073556 0%,#0a4772 58%,#0b507e 100%) !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label { color:#fff !important; }
.sidebar-brand { text-align:center; padding:8px 0 16px; }
.sidebar-brand-icon { font-size:32px; }
.sidebar-brand-title { color:#fff !important; font-size:20px; font-weight:800; }
.sidebar-user {
    background:rgba(255,255,255,.11); border:1px solid rgba(255,255,255,.14);
    border-radius:13px; padding:13px; margin-bottom:16px;
}
.sidebar-user-name { color:#fff !important; font-size:15px; font-weight:800; }
.sidebar-user-role { color:#d8efff !important; font-size:12px; margin-top:4px; }
.sidebar-section { color:#b9e4ff !important; font-size:11px; font-weight:800; letter-spacing:1.2px; margin:10px 0 7px; }
section[data-testid="stSidebar"] .stButton > button {
    background:rgba(255,255,255,.07) !important;
    color:#fff !important; -webkit-text-fill-color:#fff !important;
    border:1px solid rgba(255,255,255,.14) !important;
    text-align:left !important; justify-content:flex-start !important;
    margin-bottom:7px !important;
}
section[data-testid="stSidebar"] .stButton > button * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}
.sidebar-divider { height:1px; background:rgba(255,255,255,.20); margin:17px 0; }

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#fff !important; border:1px solid #d2e1ed !important;
    border-radius:15px !important; box-shadow:0 7px 22px rgba(15,69,105,.07) !important;
}
.welcome-box {
    background:linear-gradient(135deg,#0a4778 0%,#12699f 100%);
    border-radius:18px; padding:26px 30px; margin-bottom:22px;
}
.welcome-title { color:#fff !important; font-size:27px; font-weight:800; }
.welcome-text { color:#eef8ff !important; font-size:16px; line-height:1.55; }

/* Metrics */
[data-testid="stMetric"] {
    background:#fff !important; border:1px solid #d7e5ef !important;
    border-radius:13px !important; padding:14px !important;
}
[data-testid="stMetricLabel"] {
    color:#527089 !important;
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:clip !important;
    line-height:1.15 !important;
}
[data-testid="stMetricValue"] {
    color:#0b3d63 !important;
    font-size:27px !important;
    line-height:1.15 !important;
    white-space:nowrap !important;
    overflow:visible !important;
    text-overflow:clip !important;
}
[data-testid="stMetricValue"] > div {
    white-space:nowrap !important;
    overflow:visible !important;
    text-overflow:clip !important;
}

/* Metric cards: use the full column width and never shorten labels. */
[data-testid="stMetric"] {
    width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    padding: 16px 18px !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] p {
    width: 100% !important;
    max-width: none !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* File uploader */
section[data-testid="stFileUploaderDropzone"] {
    background:#13233f !important; border:1px solid #2b4168 !important;
    border-radius:12px !important;
}
section[data-testid="stFileUploaderDropzone"] * {
    color:#fff !important; -webkit-text-fill-color:#fff !important;
}
section[data-testid="stFileUploaderDropzone"] button {
    background:#fff !important; color:#13233f !important;
    -webkit-text-fill-color:#13233f !important;
}
section[data-testid="stFileUploaderDropzone"] button * {
    color:#13233f !important; -webkit-text-fill-color:#13233f !important;
}

/* Import / formula boxes */
.formula-box {
    background:#eef7fd; border:1px solid #c7deee; border-radius:12px;
    padding:14px 17px; margin:10px 0 17px;
}
.formula-title { color:#0b4d75 !important; font-weight:800; }
.formula-text { color:#173f5c !important; font-size:16px; font-weight:700; margin-top:5px; }
.small-note { color:#527089 !important; font-size:13px; }
.success-box {
    background:#eaf8ef; border:1px solid #b8dfc5; border-radius:12px;
    padding:14px 17px; color:#145c2a !important;
}
</style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# DATABASE
# ============================================================

TRAINING_TYPES = [
    "Technical",
    "Soft Skill",
    "Compliance",
    "Japanese Management Systems",
    "Other",
]

TRAINING_CATEGORIES = [
    "Internal Training",
    "External Training",
    "Overseas Training",
    "Management Training",
]

def ensure_training_schema():
    """Create/upgrade training and budget tables without deleting existing data."""
    migration_sql = r"""
    CREATE TABLE IF NOT EXISTS public.training_records (
        id BIGSERIAL PRIMARY KEY,
        programme_name TEXT,
        from_date DATE,
        to_date DATE,
        quarter VARCHAR(10),
        training_type VARCHAR(100),
        category VARCHAR(100),
        location VARCHAR(255),
        power_plant VARCHAR(255),
        trainer_name TEXT,
        participant_names TEXT,
        training_cost NUMERIC(14,2) DEFAULT 0,
        training_hours NUMERIC(12,2) DEFAULT 0,
        participants_count NUMERIC(12,2) DEFAULT 0,
        total_hours NUMERIC(14,2) DEFAULT 0,
        created_by BIGINT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS public.training_budgets (
        id BIGSERIAL PRIMARY KEY,
        budget_year INTEGER NOT NULL,
        location VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        budget_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
        created_by BIGINT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    DO $$
    BEGIN
        -- -------------------------
        -- training_records columns
        -- -------------------------
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='programme_name'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='program_name'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN program_name TO programme_name;
            ELSIF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='programme'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN programme TO programme_name;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN programme_name TEXT;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='from_date'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='start_date'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN start_date TO from_date;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN from_date DATE;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='to_date'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='end_date'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN end_date TO to_date;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN to_date DATE;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='quarter'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='q'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN q TO quarter;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN quarter VARCHAR(10);
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='training_type'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='type'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN type TO training_type;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN training_type VARCHAR(100);
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='category'
        ) THEN
            ALTER TABLE public.training_records
                ADD COLUMN category VARCHAR(100) DEFAULT 'Internal Training';
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='location'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='loc'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN loc TO location;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN location VARCHAR(255);
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='power_plant'
        ) THEN
            ALTER TABLE public.training_records ADD COLUMN power_plant VARCHAR(255);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='trainer_name'
        ) THEN
            ALTER TABLE public.training_records ADD COLUMN trainer_name TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='participant_names'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='names_of_participants'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN names_of_participants TO participant_names;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN participant_names TEXT;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='participants_count'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='no_of_people_attended'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN no_of_people_attended TO participants_count;
            ELSIF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='no_of_participants'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN no_of_participants TO participants_count;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN participants_count NUMERIC(12,2) DEFAULT 0;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='training_hours'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='hours'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN hours TO training_hours;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN training_hours NUMERIC(12,2) DEFAULT 0;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='training_cost'
        ) THEN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='training_records'
                  AND column_name='cost'
            ) THEN
                ALTER TABLE public.training_records RENAME COLUMN cost TO training_cost;
            ELSE
                ALTER TABLE public.training_records ADD COLUMN training_cost NUMERIC(14,2) DEFAULT 0;
            END IF;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='total_hours'
        ) THEN
            ALTER TABLE public.training_records ADD COLUMN total_hours NUMERIC(14,2) DEFAULT 0;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='created_by'
        ) THEN
            ALTER TABLE public.training_records ADD COLUMN created_by BIGINT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_records'
              AND column_name='created_at'
        ) THEN
            ALTER TABLE public.training_records ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
        END IF;

        -- -------------------------
        -- Safe training type migration
        -- Drop old CHECK BEFORE changing values.
        -- -------------------------
        ALTER TABLE public.training_records
            DROP CONSTRAINT IF EXISTS training_records_training_type_check;

        UPDATE public.training_records
        SET training_type = CASE
            WHEN LOWER(TRIM(training_type)) LIKE '%japanese%' THEN 'Japanese Management Systems'
            WHEN LOWER(TRIM(training_type)) LIKE '%soft%' THEN 'Soft Skill'
            WHEN LOWER(TRIM(training_type)) LIKE '%technical%' OR LOWER(TRIM(training_type)) = 'tech' THEN 'Technical'
            WHEN LOWER(TRIM(training_type)) LIKE '%compliance%' THEN 'Compliance'
            WHEN LOWER(TRIM(training_type)) = 'other' THEN 'Other'
            ELSE 'Other'
        END
        WHERE training_type IS NOT NULL;

        ALTER TABLE public.training_records
            ADD CONSTRAINT training_records_training_type_check
            CHECK (
                training_type IS NULL
                OR training_type IN (
                    'Technical',
                    'Soft Skill',
                    'Compliance',
                    'Japanese Management Systems',
                    'Other'
                )
            );

        -- -------------------------
        -- Safe category migration
        -- Existing records without a category are classified as
        -- Internal Training so all legacy data remains reportable.
        -- -------------------------
        ALTER TABLE public.training_records
            DROP CONSTRAINT IF EXISTS training_records_category_check;

        UPDATE public.training_records
        SET category = CASE
            WHEN LOWER(TRIM(COALESCE(category,''))) LIKE '%external%' THEN 'External Training'
            WHEN LOWER(TRIM(COALESCE(category,''))) LIKE '%overseas%' THEN 'Overseas Training'
            WHEN LOWER(TRIM(COALESCE(category,''))) LIKE '%management%' THEN 'Management Training'
            ELSE 'Internal Training'
        END;

        ALTER TABLE public.training_records
            ADD CONSTRAINT training_records_category_check
            CHECK (
                category IN (
                    'Internal Training',
                    'External Training',
                    'Overseas Training',
                    'Management Training'
                )
            );

        UPDATE public.training_records
        SET total_hours = COALESCE(training_hours,0) * COALESCE(participants_count,0)
        WHERE total_hours IS NULL
           OR total_hours <> COALESCE(training_hours,0) * COALESCE(participants_count,0);

        -- -------------------------
        -- training_budgets columns
        -- -------------------------
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_budgets'
              AND column_name='budget_year'
        ) THEN
            ALTER TABLE public.training_budgets ADD COLUMN budget_year INTEGER;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_budgets'
              AND column_name='location'
        ) THEN
            ALTER TABLE public.training_budgets ADD COLUMN location VARCHAR(255);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_budgets'
              AND column_name='category'
        ) THEN
            ALTER TABLE public.training_budgets ADD COLUMN category VARCHAR(100);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_budgets'
              AND column_name='budget_amount'
        ) THEN
            ALTER TABLE public.training_budgets ADD COLUMN budget_amount NUMERIC(14,2) DEFAULT 0;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_budgets'
              AND column_name='created_by'
        ) THEN
            ALTER TABLE public.training_budgets ADD COLUMN created_by BIGINT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_budgets'
              AND column_name='created_at'
        ) THEN
            ALTER TABLE public.training_budgets ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
        END IF;

        ALTER TABLE public.training_budgets
            DROP CONSTRAINT IF EXISTS training_budgets_category_check;

        UPDATE public.training_budgets
        SET category = CASE
            WHEN LOWER(TRIM(COALESCE(category,''))) LIKE '%external%' THEN 'External Training'
            WHEN LOWER(TRIM(COALESCE(category,''))) LIKE '%overseas%' THEN 'Overseas Training'
            WHEN LOWER(TRIM(COALESCE(category,''))) LIKE '%management%' THEN 'Management Training'
            ELSE 'Internal Training'
        END
        WHERE category IS NULL OR TRIM(category) = ''
           OR category NOT IN (
                'Internal Training',
                'External Training',
                'Overseas Training',
                'Management Training'
           );

        ALTER TABLE public.training_budgets
            ADD CONSTRAINT training_budgets_category_check
            CHECK (
                category IN (
                    'Internal Training',
                    'External Training',
                    'Overseas Training',
                    'Management Training'
                )
            );
    END $$;

    CREATE INDEX IF NOT EXISTS idx_training_records_date
        ON public.training_records(from_date);

    CREATE INDEX IF NOT EXISTS idx_training_records_location
        ON public.training_records(location);

    CREATE INDEX IF NOT EXISTS idx_training_records_category
        ON public.training_records(category);

    CREATE INDEX IF NOT EXISTS idx_training_budgets_year_location_category
        ON public.training_budgets(budget_year, location, category);
    """
    run_write(migration_sql)


try:
    init_db()
    ensure_training_schema()
except Exception as e:
    st.error("Unable to connect to the HR database. Please check your Streamlit Secrets.")
    with st.expander("Technical details"):
        st.exception(e)
    st.stop()


# ============================================================
# ADMIN
# ============================================================

ADMIN_USERNAME = "samodad"
ADMIN_DISPLAY_NAME = "Samoda De Silva"

def ensure_admin_account():
    try:
        run_write(
            "ALTER TABLE public.users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user'"
        )
        run_write(
            """
            UPDATE public.users
            SET role = 'admin'
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(:username))
            """,
            {"username": ADMIN_USERNAME},
        )
    except Exception:
        pass

ensure_admin_account()


# ============================================================
# SESSION / CONSTANTS
# ============================================================

PAGES = [
    "Home",
    "Dashboard",
    "Data Entry",
    "Import Excel",
    "Records",
    "Budget Entry",
    "My Account",
]

KNOWN_LOCATIONS = [
    "HOF", "BBO", "BTO", "BKN", "EME", "MGT", "GNT",
    "HS1", "HS2", "LKM", "MVB", "ORK", "RDP",
    "UDW", "VBL", "WMB"
]

BUDGET_LOCATIONS = KNOWN_LOCATIONS.copy()

KNOWN_POWER_PLANTS = KNOWN_LOCATIONS.copy()
SUPPORTED_YEARS = [2026, 2025, 2024]

if "hr_page" not in st.session_state:
    st.session_state.hr_page = "Home"


def get_user():
    user = None
    try:
        user = current_user()
    except Exception:
        user = None

    if not user:
        user = st.session_state.get("hr_user")

    if not user:
        return None

    try:
        user = dict(user)
    except Exception:
        pass

    username = str(user.get("username", "")).strip().lower()
    if username == ADMIN_USERNAME.lower():
        user["role"] = "admin"
        user.setdefault("full_name", ADMIN_DISPLAY_NAME)

    st.session_state["hr_user"] = user
    return user


def set_logged_user(user):
    try:
        user = dict(user)
    except Exception:
        pass

    if str(user.get("username", "")).strip().lower() == ADMIN_USERNAME.lower():
        user["role"] = "admin"
        user.setdefault("full_name", ADMIN_DISPLAY_NAME)

    st.session_state["hr_user"] = user
    st.session_state["hr_page"] = "Home"


def clear_logged_user():
    for key in ["hr_user", "hr_logged_in", "logged_in", "user"]:
        st.session_state.pop(key, None)
    st.session_state["hr_page"] = "Home"


def require_user():
    user = get_user()
    if not user:
        st.warning("Please log in first.")
        st.stop()
    return user


def require_admin():
    user = require_user()
    if str(user.get("role", "user")).strip().lower() != "admin":
        st.error("Administrator access is required for this section.")
        st.stop()
    return user


def do_logout():
    try:
        logout_user()
    finally:
        clear_logged_user()
        st.rerun()


# ============================================================
# DATABASE HELPERS
# ============================================================

TRAINING_SELECT = """
SELECT
    id,
    programme_name,
    from_date,
    to_date,
    quarter,
    training_type,
    category,
    location,
    power_plant,
    trainer_name,
    participant_names,
    training_cost,
    training_hours,
    participants_count,
    total_hours,
    created_by,
    created_at
FROM training_records
ORDER BY from_date DESC NULLS LAST, id DESC
"""


def get_training_records():
    rows = run_query(TRAINING_SELECT)
    df = pd.DataFrame([dict(r) for r in rows])

    if df.empty:
        return df

    for col, default in [
        ("power_plant", "Not Specified"),
        ("trainer_name", ""),
        ("category", "Internal Training"),
        ("location", "Not Specified"),
    ]:
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default).astype(str).str.strip()
            df.loc[df[col] == "", col] = default

    for col in ["from_date", "to_date", "created_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["training_cost", "training_hours", "participants_count", "total_hours"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["calculated_total_hours"] = (
        df["training_hours"] * df["participants_count"]
    )

    return df


def get_locations():
    rows = run_query(
        """
        SELECT DISTINCT TRIM(location) AS location
        FROM training_records
        WHERE location IS NOT NULL AND TRIM(location) <> ''
        ORDER BY TRIM(location)
        """
    )
    db_locations = [
        str(dict(r).get("location")).strip()
        for r in rows
        if dict(r).get("location")
    ]
    return sorted(set(KNOWN_LOCATIONS + db_locations), key=str.upper)


def get_power_plants():
    rows = run_query(
        """
        SELECT DISTINCT TRIM(power_plant) AS power_plant
        FROM training_records
        WHERE power_plant IS NOT NULL AND TRIM(power_plant) <> ''
        ORDER BY TRIM(power_plant)
        """
    )
    db_plants = [
        str(dict(r).get("power_plant")).strip()
        for r in rows
        if dict(r).get("power_plant")
    ]
    return sorted(set(KNOWN_POWER_PLANTS + db_plants), key=str.upper)


def get_existing_keys():
    rows = run_query(
        """
        SELECT programme_name, from_date, location, COALESCE(power_plant,'') AS power_plant
        FROM training_records
        """
    )
    keys = set()

    for r in rows:
        record = dict(r)
        programme = str(record.get("programme_name") or "").strip().lower()
        location = str(record.get("location") or "").strip().lower()
        power_plant = str(record.get("power_plant") or "").strip().lower()
        dt = pd.to_datetime(record.get("from_date"), errors="coerce")
        date_key = dt.date() if not pd.isna(dt) else None
        keys.add((programme, date_key, location, power_plant))

    return keys


def insert_training_record(
    programme_name,
    from_date,
    to_date,
    quarter,
    training_type,
    category,
    location,
    power_plant,
    trainer_name,
    participant_names,
    training_cost,
    training_hours,
    participants_count,
    total_hours,
    created_by=None,
):
    params = {
        "programme_name": programme_name,
        "from_date": from_date,
        "to_date": to_date,
        "quarter": quarter,
        "training_type": training_type,
        "category": category,
        "location": location,
        "power_plant": power_plant,
        "trainer_name": trainer_name,
        "participant_names": participant_names,
        "training_cost": float(training_cost),
        "training_hours": float(training_hours),
        "participants_count": float(participants_count),
        "total_hours": float(total_hours),
    }

    if created_by is not None:
        try:
            run_write(
                """
                INSERT INTO training_records (
                    programme_name, from_date, to_date, quarter,
                    training_type, category, location, power_plant,
                    trainer_name, participant_names,
                    training_cost, training_hours, participants_count,
                    total_hours, created_by
                )
                VALUES (
                    :programme_name, :from_date, :to_date, :quarter,
                    :training_type, :category, :location, :power_plant,
                    :trainer_name, :participant_names,
                    :training_cost, :training_hours, :participants_count,
                    :total_hours, :created_by
                )
                """,
                {**params, "created_by": created_by},
            )
            return
        except Exception:
            pass

    run_write(
        """
        INSERT INTO training_records (
            programme_name, from_date, to_date, quarter,
            training_type, category, location, power_plant,
            trainer_name, participant_names,
            training_cost, training_hours, participants_count, total_hours
        )
        VALUES (
            :programme_name, :from_date, :to_date, :quarter,
            :training_type, :category, :location, :power_plant,
            :trainer_name, :participant_names,
            :training_cost, :training_hours, :participants_count, :total_hours
        )
        """,
        params,
    )


def update_training_record(
    record_id,
    programme_name,
    from_date,
    to_date,
    quarter,
    training_type,
    category,
    location,
    power_plant,
    trainer_name,
    participant_names,
    training_cost,
    training_hours,
    participants_count,
):
    total_hours = float(training_hours) * float(participants_count)

    run_write(
        """
        UPDATE training_records
        SET
            programme_name = :programme_name,
            from_date = :from_date,
            to_date = :to_date,
            quarter = :quarter,
            training_type = :training_type,
            category = :category,
            location = :location,
            power_plant = :power_plant,
            trainer_name = :trainer_name,
            participant_names = :participant_names,
            training_cost = :training_cost,
            training_hours = :training_hours,
            participants_count = :participants_count,
            total_hours = :total_hours
        WHERE id = :record_id
        """,
        {
            "record_id": int(record_id),
            "programme_name": programme_name,
            "from_date": from_date,
            "to_date": to_date,
            "quarter": quarter,
            "training_type": training_type,
            "category": category,
            "location": location,
            "power_plant": power_plant,
            "trainer_name": trainer_name,
            "participant_names": participant_names,
            "training_cost": float(training_cost),
            "training_hours": float(training_hours),
            "participants_count": float(participants_count),
            "total_hours": total_hours,
        },
    )


def delete_training_record(record_id):
    run_write(
        "DELETE FROM training_records WHERE id = :record_id",
        {"record_id": int(record_id)},
    )


def get_budget_records():
    rows = run_query(
        """
        SELECT
            id,
            budget_year,
            location,
            category,
            budget_amount,
            created_by,
            created_at
        FROM training_budgets
        ORDER BY budget_year DESC, location, category
        """
    )
    df = pd.DataFrame([dict(r) for r in rows])

    if df.empty:
        return df

    df["budget_year"] = pd.to_numeric(df["budget_year"], errors="coerce").fillna(0).astype(int)
    df["budget_amount"] = pd.to_numeric(df["budget_amount"], errors="coerce").fillna(0)
    df["location"] = df["location"].fillna("Not Specified").astype(str).str.strip()
    df["category"] = df["category"].fillna("Internal Training").astype(str).str.strip()

    return df


def save_budget_record(budget_id, budget_year, location, category, budget_amount, created_by=None):
    params = {
        "budget_year": int(budget_year),
        "location": str(location).strip(),
        "category": str(category).strip(),
        "budget_amount": float(budget_amount),
        "created_by": created_by,
    }

    if budget_id:
        run_write(
            """
            UPDATE training_budgets
            SET
                budget_year = :budget_year,
                location = :location,
                category = :category,
                budget_amount = :budget_amount
            WHERE id = :budget_id
            """,
            {**params, "budget_id": int(budget_id)},
        )
        return

    existing = run_query(
        """
        SELECT id
        FROM training_budgets
        WHERE budget_year = :budget_year
          AND LOWER(TRIM(location)) = LOWER(TRIM(:location))
          AND category = :category
        ORDER BY id
        LIMIT 1
        """,
        params,
    )

    if existing:
        existing_id = int(dict(existing[0])["id"])
        save_budget_record(
            existing_id,
            budget_year,
            location,
            category,
            budget_amount,
            created_by,
        )
        return

    run_write(
        """
        INSERT INTO training_budgets (
            budget_year, location, category, budget_amount, created_by
        )
        VALUES (
            :budget_year, :location, :category, :budget_amount, :created_by
        )
        """,
        params,
    )


def delete_budget_record(budget_id):
    run_write(
        "DELETE FROM training_budgets WHERE id = :budget_id",
        {"budget_id": int(budget_id)},
    )


# ============================================================
# EXCEL IMPORT HELPERS
# ============================================================

COLUMN_ALIASES = {
    "programme_name": [
        "name of the programme", "programme name", "program name", "programme"
    ],
    "from_date": ["from date", "date", "start date"],
    "to_date": ["to date", "end date"],
    "quarter": ["q", "quarter"],
    "training_type": ["t/s", "type", "training type"],
    "category": ["category", "training category", "training type category"],
    "participant_names": [
        "names of the participants", "participant names", "participants"
    ],
    "location": ["location", "loc", "site"],
    "power_plant": ["power plant", "powerplant", "plant", "plant name"],
    "trainer_name": [
        "trainer name", "trainer", "trainer's name",
        "trainers name", "facilitator", "facilitator name"
    ],
    "training_cost": ["training cost", "cost"],
    "training_hours": ["training hours", "hours"],
    "participants_count": [
        "no of people attended", "no of participants",
        "participants count", "number of people attended"
    ],
    "total_hours": ["total hours", "total training hours"],
}


def clean_col_name(value):
    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def detect_excel_header(raw):
    for i in range(min(25, len(raw))):
        values = [
            clean_col_name(x)
            for x in raw.iloc[i].tolist()
            if pd.notna(x)
        ]
        joined = " | ".join(values)
        if "name of the programme" in joined and "training hours" in joined:
            return i
    return None


def find_source_column(columns, aliases):
    normalized = {clean_col_name(c): c for c in columns}

    for alias in aliases:
        if alias in normalized:
            return normalized[alias]

    for col in columns:
        c = clean_col_name(col)
        for alias in aliases:
            if alias in c or c in alias:
                return col

    return None


def prepare_excel_dataframe(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        raw = pd.read_csv(uploaded_file, header=None)
    else:
        raw = pd.read_excel(uploaded_file, header=None)

    header_row = detect_excel_header(raw)
    if header_row is None:
        raise ValueError(
            "Could not detect the training table header. "
            "The file should contain columns such as "
            "'Name of the Programme' and 'Training Hours'."
        )

    headers = []
    for i, value in enumerate(raw.iloc[header_row].tolist()):
        if pd.isna(value) or str(value).strip() == "":
            headers.append(f"Unnamed_{i}")
        else:
            headers.append(str(value).strip())

    df = raw.iloc[header_row + 1:].copy()
    df.columns = headers

    programme_col = find_source_column(
        df.columns, COLUMN_ALIASES["programme_name"]
    )
    if programme_col is None:
        raise ValueError("The programme-name column could not be found.")

    df = df[df[programme_col].notna()].copy()
    df = df[df[programme_col].astype(str).str.strip() != ""].copy()

    rename = {}
    for target, aliases in COLUMN_ALIASES.items():
        source = find_source_column(df.columns, aliases)
        if source is not None:
            rename[source] = target

    df = df.rename(columns=rename)

    for required in [
        "programme_name", "from_date", "training_type",
        "location", "training_cost", "training_hours",
        "participants_count"
    ]:
        if required not in df.columns:
            df[required] = None

    optional_defaults = {
        "to_date": None,
        "quarter": None,
        "category": "Internal Training",
        "trainer_name": "",
        "participant_names": "",
        "total_hours": None,
    }

    for col, default in optional_defaults.items():
        if col not in df.columns:
            df[col] = default

    return df.reset_index(drop=True), header_row


def parse_number(value, default=0.0):
    if value is None or pd.isna(value):
        return default

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")
    if not text:
        return default

    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else default


def infer_nearby_year(values, index, fallback_year=2026):
    for distance in range(0, 25):
        for candidate in [index - distance, index + distance]:
            if candidate < 0 or candidate >= len(values):
                continue

            v = values[candidate]

            if isinstance(v, (datetime, date, pd.Timestamp)):
                return pd.Timestamp(v).year

            text = str(v).strip()
            m = re.search(r"(20\d{2})", text)
            if m:
                return int(m.group(1))

    return fallback_year


def parse_date_value(value, default_year=2026):
    if value is None or pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.date()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat", "none"}:
        return None

    cleaned = re.sub(r"[A-Za-z]+", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    iso = re.match(r"^(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", cleaned)
    if iso:
        y, m, d = map(int, iso.groups())
        try:
            return date(y, m, d)
        except ValueError:
            return None

    range_full = re.match(
        r"^(\d{1,2})[/-](\d{1,2})[/-](\d{1,2})[/-](20\d{2})$",
        cleaned,
    )
    if range_full:
        d1, _, mo, y = map(int, range_full.groups())
        try:
            return date(y, mo, d1)
        except ValueError:
            return None

    compact = re.match(r"^(\d{3})[/-](20\d{2})$", cleaned)
    if compact:
        digits, y = compact.groups()
        try:
            return date(int(y), int(digits[1:]), int(digits[0]))
        except ValueError:
            return None

    full = re.match(
        r"^(\d{1,2})[/-](\d{1,2})[/-](20\d{2})$",
        cleaned,
    )
    if full:
        d, mo, y = map(int, full.groups())
        try:
            return date(y, mo, d)
        except ValueError:
            return None

    first = re.search(
        r"(\d{1,2})\s*/\s*(\d{1,2})(?:\s*/\s*(20\d{2}))?",
        cleaned,
    )
    if first:
        d, mo = int(first.group(1)), int(first.group(2))
        y = int(first.group(3)) if first.group(3) else default_year
        try:
            return date(y, mo, d)
        except ValueError:
            return None

    dt = pd.to_datetime(cleaned, errors="coerce", dayfirst=True)
    return None if pd.isna(dt) else dt.date()


def parse_date_range(from_value, to_value, default_year=2026):
    from_date = parse_date_value(from_value, default_year)
    to_date = parse_date_value(to_value, default_year)

    text = (
        ""
        if from_value is None or pd.isna(from_value)
        else str(from_value).strip()
    )

    if not to_date and text:
        cleaned = re.sub(r"[A-Za-z]+", "", text)

        full_range = re.search(
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{1,2})[/-](20\d{2})",
            cleaned,
        )

        if full_range:
            _, d2, mo, y = full_range.groups()
            try:
                to_date = date(int(y), int(mo), int(d2))
            except ValueError:
                to_date = None

        if not to_date:
            matches = re.findall(
                r"(\d{1,2})\s*/\s*(\d{1,2})(?:\s*/\s*(20\d{2}))?",
                cleaned,
            )

            if len(matches) >= 2:
                y = int(matches[0][2]) if matches[0][2] else default_year
                try:
                    to_date = date(
                        y,
                        int(matches[1][1]),
                        int(matches[1][0]),
                    )
                except ValueError:
                    to_date = None

    if from_date and not to_date:
        to_date = from_date

    return from_date, to_date


def normalize_training_type(value):
    text = str(value or "").strip().lower()

    if "japanese" in text:
        return "Japanese Management Systems"
    if "soft" in text:
        return "Soft Skill"
    if "technical" in text or text == "tech":
        return "Technical"
    if "compliance" in text:
        return "Compliance"
    if text == "other":
        return "Other"

    return "Other"


def normalize_category(value):
    text = str(value or "").strip().lower()

    if "external" in text:
        return "External Training"
    if "overseas" in text or "over sea" in text:
        return "Overseas Training"
    if "management" in text:
        return "Management Training"
    if "internal" in text:
        return "Internal Training"

    return "Internal Training"


def normalize_quarter(value, from_date):
    text = str(value or "").strip().upper()

    if text in {"Q1", "Q2", "Q3", "Q4"}:
        return text

    return (
        f"Q{((from_date.month - 1) // 3) + 1}"
        if from_date
        else "Q1"
    )


def transform_import_rows(df):
    rows = []
    errors = []
    raw_dates = df["from_date"].tolist()

    for idx, source in df.iterrows():
        excel_row = idx + 1

        try:
            programme = str(source.get("programme_name") or "").strip()
            if not programme:
                raise ValueError("Programme name is empty")

            year = infer_nearby_year(raw_dates, idx, fallback_year=2026)

            from_date, to_date = parse_date_range(
                source.get("from_date"),
                source.get("to_date"),
                year,
            )

            if from_date is None:
                raise ValueError("Invalid From Date")

            power_plant = str(source.get("power_plant") or "").strip()
            if not power_plant:
                power_plant = "Not Specified"

            location = str(source.get("location") or "").strip()
            if not location:
                location = power_plant

            trainer_name = str(source.get("trainer_name") or "").strip()

            training_hours = parse_number(
                source.get("training_hours"), 0
            )
            participants = parse_number(
                source.get("participants_count"), 0
            )
            cost = parse_number(source.get("training_cost"), 0)

            if training_hours <= 0:
                raise ValueError(
                    "Training Hours must be greater than 0"
                )

            participant_text = str(
                source.get("participant_names") or ""
            ).strip()

            name_count = len(
                [
                    x for x in re.split(r"[,;]", participant_text)
                    if x.strip()
                ]
            )

            if (
                participants <= 0
                or abs(participants - round(participants)) > 0.000001
            ):
                if name_count > 0:
                    participants = float(name_count)
                else:
                    raise ValueError(
                        "No. of people attended is invalid"
                    )
            else:
                participants = float(round(participants))

            total_hours = training_hours * participants

            rows.append(
                {
                    "programme_name": programme,
                    "from_date": from_date,
                    "to_date": to_date,
                    "quarter": normalize_quarter(
                        source.get("quarter"), from_date
                    ),
                    "training_type": normalize_training_type(
                        source.get("training_type")
                    ),
                    "category": normalize_category(
                        source.get("category")
                    ),
                    "trainer_name": trainer_name,
                    "participant_names": participant_text,
                    "location": location,
                    "power_plant": power_plant,
                    "training_cost": cost,
                    "training_hours": training_hours,
                    "participants_count": participants,
                    "total_hours": total_hours,
                }
            )

        except Exception as e:
            errors.append(
                f"Excel row {excel_row + 4}: {e}"
            )

    return pd.DataFrame(rows), errors


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    user = get_user()
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
                <div class="sidebar-user-name">
                    {html.escape(str(full_name))}
                </div>
                <div class="sidebar-user-role">
                    @{html.escape(str(username))} ·
                    {html.escape(str(role).title())}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">Navigation</div>',
            unsafe_allow_html=True,
        )

        icons = {
            "Home": "🏠",
            "Dashboard": "📊",
            "Data Entry": "📝",
            "Import Excel": "📥",
            "Records": "📁",
            "Budget Entry": "💰",
            "My Account": "👤",
        }

        for page in PAGES:
            if st.button(
                f"{icons[page]}   {page}",
                key=f"nav_{page.lower().replace(' ', '_')}",
                use_container_width=True,
            ):
                st.session_state.hr_page = page
                st.rerun()

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Log out",
            key="sidebar_logout",
            use_container_width=True,
        ):
            do_logout()


# ============================================================
# LOGIN / SIGNUP
# ============================================================

def render_login():
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
        login_tab, signup_tab = st.tabs(
            ["🔐 Log in", "👤 Create account"]
        )

        with login_tab:
            st.markdown(
                '<div class="auth-heading">Welcome back</div>',
                unsafe_allow_html=True,
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
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not identifier.strip() or not password:
                    st.error(
                        "Please enter both username/email and password."
                    )
                else:
                    try:
                        user = authenticate(
                            identifier.strip(), password
                        )
                        if user:
                            login_user(user)
                            set_logged_user(user)
                            st.rerun()
                        else:
                            st.error(
                                "Invalid username/email or password."
                            )
                    except Exception:
                        st.error(
                            "Unable to log in. Please try again."
                        )

        with signup_tab:
            st.markdown(
                '<div class="auth-heading">'
                'Create your account'
                '</div>',
                unsafe_allow_html=True,
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
                )
                submitted = st.form_submit_button(
                    "Create account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                full_name = full_name.strip()
                username = username.strip().lower()
                email = email.strip().lower()

                if not full_name:
                    st.error("Please enter your full name.")
                elif not re.fullmatch(
                    r"[a-z0-9._-]{3,50}", username
                ):
                    st.error(
                        "Username must contain 3–50 lowercase "
                        "letters, numbers, dots, underscores or hyphens."
                    )
                elif not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+", email
                ):
                    st.error(
                        "Please enter a valid email address."
                    )
                elif len(password) < 8:
                    st.error(
                        "Password must contain at least 8 characters."
                    )
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
                            "Please use the Log in tab."
                        )
                    except ValueError as e:
                        st.error(str(e))
                    except Exception:
                        st.error(
                            "Unable to create the account. "
                            "Please check the database connection."
                        )


# ============================================================
# HOME
# ============================================================

def render_home():
    user = require_user()

    full_name = (
        user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    st.markdown(
        f"""
        <div class="welcome-box">
            <div class="welcome-title">
                📊 HR Training Dashboard
            </div>
            <div class="welcome-text">
                Welcome back,
                <strong>{html.escape(str(full_name))}</strong> 👋<br>
                Manage training programmes, workers, costs,
                budgets, training hours and company-wide performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    cards = [
        (
            c1, "📊", "Dashboard",
            "View KPIs, training trends, costs and Budget vs Actuals.",
            "Dashboard",
        ),
        (
            c2, "📝", "Data Entry",
            "Add a training programme with Type and Category.",
            "Data Entry",
        ),
        (
            c3, "💰", "Budget Entry",
            "Enter annual training budgets by Location and Category.",
            "Budget Entry",
        ),
    ]

    for col, icon, title, description, target in cards:
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<div style="font-size:30px">{icon}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="font-size:20px;font-weight:800;'
                    f'color:#083b66">{title}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="small-note">{description}</div>',
                    unsafe_allow_html=True,
                )
                st.write("")

                if st.button(
                    f"Open {title} →",
                    key=f"home_{target}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.hr_page = target
                    st.rerun()

    df = get_training_records()
    st.write("")

    if df.empty:
        st.info(
            "No training records are in the database yet. "
            "Use Import Excel or Data Entry."
        )
    else:
        total_hours = float(df["calculated_total_hours"].sum())
        total_workers = float(df["participants_count"].sum())
        total_cost = float(df["training_cost"].sum())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Programmes", f"{len(df):,}")
        m2.metric("Workers Attended", f"{total_workers:,.0f}")
        m3.metric("Total Training Hours", f"{total_hours:,.1f}")
        m4.metric("Training Cost", f"Rs. {total_cost:,.0f}")


# ============================================================
# DATA ENTRY
# ============================================================

def render_data_entry():
    user = require_user()

    st.title("Training Data Entry")
    st.caption(
        "Enter one training programme. "
        "Total training hours are calculated automatically."
    )

    # Budget is maintained separately from Training Cost (Actual).
    # This gives every authenticated user a clear way to enter annual budgets.
    budget_access_col, _ = st.columns([1, 2])
    with budget_access_col:
        if st.button(
            "💰 Open Budget Entry",
            use_container_width=True,
            key="open_budget_entry_from_data_entry",
        ):
            st.session_state.hr_page = "Budget Entry"
            st.rerun()

    st.markdown(
        """
        <div class="formula-box">
            <div class="formula-title">
                Training Hours Calculation
            </div>
            <div class="formula-text">
                Total Training Hours =
                Training Hours per Worker × No. of Workers Attended
            </div>
            <div class="small-note">
                Example: 3 hours × 10 workers =
                30 total training hours (person-hours).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    power_plants = get_power_plants()

    with st.container(border=True):
        left, right = st.columns(2)

        with left:
            programme = st.text_input(
                "Name of the Programme *",
                placeholder="e.g. Leadership Development Programme",
            )

            trainer_name = st.text_input(
                "Trainer's Name *",
                placeholder="e.g. Roshan Siriwardana",
            )

            from_date = st.date_input(
                "From Date *",
                value=date.today(),
            )

            to_date = st.date_input(
                "To Date *",
                value=date.today(),
            )

            training_type = st.selectbox(
                "Type *",
                TRAINING_TYPES,
            )

            category = st.selectbox(
                "Category *",
                TRAINING_CATEGORIES,
            )

            quarter = st.selectbox(
                "Quarter *",
                ["Q1", "Q2", "Q3", "Q4"],
            )

        with right:
            plant_mode = st.selectbox(
                "Power Plant *",
                [
                    "No Power Plant / Not Applicable"
                ] + power_plants + [
                    "+ Add new power plant"
                ],
                key="entry_plant_mode",
            )

            if plant_mode == "+ Add new power plant":
                power_plant = st.text_input(
                    "New power plant name *",
                    placeholder="e.g. BBO",
                )
            elif plant_mode == "No Power Plant / Not Applicable":
                power_plant = "Not Specified"
            else:
                power_plant = plant_mode

            training_hours = st.number_input(
                "Training Hours per Worker *",
                min_value=0.0,
                step=0.5,
                format="%.2f",
            )

            participants = st.number_input(
                "No. of Workers Attended *",
                min_value=0,
                step=1,
                format="%d",
            )

            cost = st.number_input(
                "Training Cost (Rs.)",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
            )

        participant_names = st.text_area(
            "Names of the Participants",
            placeholder="Optional — separate names with commas",
        )

        total_hours = (
            float(training_hours) * float(participants)
        )

        st.markdown(
            f"""
            <div class='formula-box'>
                <div class='formula-text'>
                    {training_hours:,.2f} hours ×
                    {participants:,.1f} workers =
                    {total_hours:,.2f} total training hours
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        save = st.button(
            "Save Training Record",
            type="primary",
            use_container_width=True,
        )

    if save:
        programme = programme.strip()
        trainer_name = trainer_name.strip()
        power_plant = power_plant.strip()

        location = power_plant

        if not programme:
            st.error("Please enter the programme name.")
            return

        if not trainer_name:
            st.error("Please enter the trainer's name.")
            return

        if not power_plant:
            st.error("Please select or enter a power plant.")
            return

        if to_date < from_date:
            st.error(
                "To Date cannot be earlier than From Date."
            )
            return

        if training_hours <= 0:
            st.error(
                "Training Hours per Worker must be greater than 0."
            )
            return

        if participants <= 0:
            st.error(
                "No. of Workers Attended must be greater than 0."
            )
            return

        try:
            insert_training_record(
                programme_name=programme,
                from_date=from_date,
                to_date=to_date,
                quarter=quarter,
                training_type=training_type,
                category=category,
                location=location,
                power_plant=power_plant,
                trainer_name=trainer_name,
                participant_names=participant_names.strip(),
                training_cost=cost,
                training_hours=training_hours,
                participants_count=participants,
                total_hours=total_hours,
                created_by=(user or {}).get("id"),
            )

            st.success(
                "Training record saved successfully."
            )
            st.session_state.hr_page = "Dashboard"
            st.rerun()

        except Exception as e:
            st.error("Unable to save the training record.")
            with st.expander("Technical details"):
                st.exception(e)


# ============================================================
# IMPORT EXCEL
# ============================================================

def render_import_excel():
    user = require_user()

    st.title("Import Excel")
    st.caption(
        "Import the HR Training Records workbook, "
        "recalculate total hours, and open the dashboard."
    )

    st.markdown(
        """
        <div class="formula-box">
            <div class="formula-title">
                Automatic Total Hours Rule
            </div>
            <div class="formula-text">
                Total Training Hours =
                Training Hours per Worker × No. of Workers Attended
            </div>
            <div class="small-note">
                The Excel Total Hours value is not trusted.
                The system recalculates it for every imported row.
                If Category is missing, the record is classified as
                Internal Training.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Choose the Excel file",
        type=["xlsx", "xls", "csv"],
        key="training_import_file",
    )

    if uploaded is None:
        st.info(
            "Upload the HR Training workbook to continue."
        )
        return

    try:
        source_df, header_row = prepare_excel_dataframe(
            uploaded
        )

        st.success(
            f"File loaded successfully — "
            f"{len(source_df):,} training rows detected. "
            f"Header row: {header_row + 1}."
        )

        if "category" not in source_df.columns:
            st.info(
                "No Category column was found. "
                "Imported records will use Internal Training."
            )

        cleaned, validation_errors = transform_import_rows(
            source_df
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Rows detected",
            f"{len(source_df):,}",
        )
        c2.metric(
            "Valid rows",
            f"{len(cleaned):,}",
        )
        c3.metric(
            "Rows with issues",
            f"{len(validation_errors):,}",
        )
        c4.metric(
            "Calculated Hours",
            (
                f"{cleaned['total_hours'].sum():,.1f}"
                if not cleaned.empty
                else "0.0"
            ),
        )

        if not cleaned.empty:
            detected_years = sorted(
                pd.to_datetime(
                    cleaned["from_date"],
                    errors="coerce",
                )
                .dt.year.dropna()
                .astype(int)
                .unique()
                .tolist()
            )

            if detected_years:
                st.info(
                    "Detected training years in this Excel file: "
                    + ", ".join(map(str, detected_years))
                )

        if validation_errors:
            with st.expander(
                f"Review {len(validation_errors)} validation issue(s)"
            ):
                st.code(
                    "\n".join(validation_errors[:50])
                )

        if cleaned.empty:
            st.error(
                "No valid training records were found in this file."
            )
            return

        if "total_hours" in source_df.columns:
            source_total = pd.to_numeric(
                source_df["total_hours"],
                errors="coerce",
            )
            source_hours = pd.to_numeric(
                source_df["training_hours"],
                errors="coerce",
            )
            source_people = pd.to_numeric(
                source_df["participants_count"],
                errors="coerce",
            )

            calculated = source_hours * source_people

            mismatch_count = int(
                ((source_total - calculated).abs() > 0.001).sum()
            )
        else:
            mismatch_count = 0

        if mismatch_count:
            st.warning(
                f"{mismatch_count} row(s) have an Excel "
                f"Total Hours value that does not match "
                f"Training Hours × Workers. "
                f"The system will use the calculated value."
            )

        st.subheader("Cleaned import preview")

        preview = cleaned.copy()
        preview["from_date"] = pd.to_datetime(
            preview["from_date"]
        ).dt.strftime("%Y-%m-%d")
        preview["to_date"] = pd.to_datetime(
            preview["to_date"]
        ).dt.strftime("%Y-%m-%d")

        st.dataframe(
            preview[
                [
                    "programme_name",
                    "from_date",
                    "to_date",
                    "quarter",
                    "training_type",
                    "category",
                    "trainer_name",
                    "location",
                    "training_cost",
                    "training_hours",
                    "participants_count",
                    "total_hours",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=430,
        )

        st.divider()
        st.subheader("Import into Training Records")
        st.caption(
            "Existing records with the same Programme + From Date "
            "+ Location + Power Plant are skipped to prevent "
            "duplicate imports."
        )

        if st.button(
            "Import Excel & Open Dashboard",
            type="primary",
            use_container_width=True,
        ):
            existing_keys = get_existing_keys()
            inserted = 0
            skipped = 0
            failed = []

            for _, row in cleaned.iterrows():
                key = (
                    str(row["programme_name"])
                    .strip()
                    .lower(),
                    row["from_date"],
                    str(row["location"])
                    .strip()
                    .lower(),
                    str(row["power_plant"])
                    .strip()
                    .lower(),
                )

                if key in existing_keys:
                    skipped += 1
                    continue

                try:
                    insert_training_record(
                        programme_name=row["programme_name"],
                        from_date=row["from_date"],
                        to_date=row["to_date"],
                        quarter=row["quarter"],
                        training_type=row["training_type"],
                        category=row["category"],
                        location=row["location"],
                        power_plant=row["power_plant"],
                        trainer_name=row["trainer_name"],
                        participant_names=row["participant_names"],
                        training_cost=row["training_cost"],
                        training_hours=row["training_hours"],
                        participants_count=row["participants_count"],
                        total_hours=row["total_hours"],
                        created_by=(user or {}).get("id"),
                    )

                    inserted += 1
                    existing_keys.add(key)

                except Exception as e:
                    failed.append(
                        f"{row['programme_name']}: {e}"
                    )

            st.session_state["last_import_summary"] = {
                "inserted": inserted,
                "skipped": skipped,
                "failed": len(failed),
                "calculated_hours": float(
                    cleaned["total_hours"].sum()
                ),
            }

            if failed:
                st.session_state["last_import_errors"] = (
                    failed[:30]
                )

            if inserted:
                st.success(
                    f"{inserted:,} training record(s) "
                    f"imported successfully."
                )

            if skipped:
                st.info(
                    f"{skipped:,} existing record(s) "
                    f"skipped to prevent duplicates."
                )

            if failed:
                st.error(
                    f"{len(failed):,} record(s) "
                    f"could not be imported."
                )
                with st.expander("Import errors"):
                    st.code("\n".join(failed[:30]))

            st.session_state.hr_page = "Dashboard"
            st.rerun()

    except Exception as e:
        st.error(
            "The selected Excel file could not be processed."
        )
        with st.expander("Technical details"):
            st.exception(e)


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():
    require_user()

    st.title("Training Dashboard")
    st.caption(
        "Training performance, budget and actual expenditure."
    )

    summary = st.session_state.pop(
        "last_import_summary", None
    )

    if summary:
        st.markdown(
            f"""
            <div class="success-box">
                <strong>Excel import completed.</strong><br>
                Imported: {summary['inserted']:,} ·
                Skipped duplicates: {summary['skipped']:,} ·
                Failed: {summary['failed']:,}<br>
                Recalculated total training hours:
                {summary['calculated_hours']:,.1f}
            </div>
            """,
            unsafe_allow_html=True,
        )

    df = get_training_records()

    if df.empty:
        st.info(
            "No training records are available. "
            "Import the Excel file or add a record from Data Entry."
        )
        return

    # ------------------------------------------------------------
    # MAIN FILTERS
    # ------------------------------------------------------------
    with st.container(border=True, key="dashboard_filters"):
        # Use two rows instead of squeezing six filters into one row.
        # This is the reliable fix for Streamlit/BaseWeb clipping.
        r1 = st.columns([1.35, 1.35, 1.35], gap="small")
        r2 = st.columns([2.05, 1.85, 1.35], gap="small")
        f1, f2, f3 = r1
        f4, f5, f6 = r2

        locations = ["All Locations"] + sorted(
            set(
                KNOWN_LOCATIONS
                + df["location"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            ),
            key=str.upper,
        )

        selected_location = f1.selectbox(
            "Location",
            locations,
            key="dash_location",
        )

        years_in_data = sorted(
            df["from_date"]
            .dropna()
            .dt.year
            .astype(int)
            .unique()
            .tolist(),
            reverse=True,
        )

        years = []
        for y in SUPPORTED_YEARS + years_in_data:
            if y not in years:
                years.append(y)

        selected_year = f2.selectbox(
            "Year",
            ["All Years"] + years,
            key="dash_year",
        )

        quarters = ["All Quarters"] + [
            q
            for q in ["Q1", "Q2", "Q3", "Q4"]
            if q in set(
                df["quarter"]
                .dropna()
                .astype(str)
            )
        ]

        selected_quarter = f3.selectbox(
            "Quarter",
            quarters,
            key="dash_quarter",
        )

        # Always show all configured training types, including
        # Japanese Management Systems even if no record exists yet.
        types_in_data = TRAINING_TYPES.copy()

        selected_type = f4.selectbox(
            "Training Type",
            ["All Types"] + types_in_data,
            key="dash_type",
        )

        # Always show all four required categories, even when
        # a category has no training records yet.
        categories_in_data = TRAINING_CATEGORIES.copy()

        selected_category = f5.selectbox(
            "Category",
            ["All Categories"] + categories_in_data,
            key="dash_category",
        )

        month_options = {
            "All Months": None,
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12,
        }

        selected_month = f6.selectbox(
            "Month",
            list(month_options.keys()),
            key="dash_month",
        )

    filtered = df.copy()

    if selected_location != "All Locations":
        filtered = filtered[
            filtered["location"].astype(str).str.strip()
            == selected_location
        ]

    if selected_year != "All Years":
        filtered = filtered[
            filtered["from_date"].dt.year
            == int(selected_year)
        ]

    if selected_quarter != "All Quarters":
        filtered = filtered[
            filtered["quarter"] == selected_quarter
        ]

    if selected_type != "All Types":
        filtered = filtered[
            filtered["training_type"] == selected_type
        ]

    if selected_category != "All Categories":
        filtered = filtered[
            filtered["category"] == selected_category
        ]

    month_number = month_options[selected_month]
    if month_number is not None:
        filtered = filtered[
            filtered["from_date"].dt.month
            == int(month_number)
        ]

    if filtered.empty:
        st.warning(
            "No records match the selected filters."
        )
    else:
        total_hours = float(
            filtered["calculated_total_hours"].sum()
        )
        programmes = int(len(filtered))
        workers = float(
            filtered["participants_count"].sum()
        )
        total_cost = float(
            filtered["training_cost"].sum()
        )

        avg_hours_per_programme = (
            total_hours / programmes
            if programmes
            else 0
        )

        avg_hours_per_worker = (
            total_hours / workers
            if workers
            else 0
        )

        st.write("")

        # Six metric cards were previously squeezed into one row, which
        # caused Streamlit to truncate labels such as "Workers Attended"
        # and "Avg. Hours / Programme" with "...".
        # Use two rows of three equal-width cards so every label has
        # enough real screen width and remains fully readable.
        k1, k2, k3 = st.columns(3, gap="medium")

        k1.metric(
            "Training Programmes",
            f"{programmes:,}",
        )
        k2.metric(
            "Workers Attended",
            f"{workers:,.0f}",
        )
        k3.metric(
            "Total Training Hours",
            f"{total_hours:,.1f}",
        )

        st.write("")

        k4, k5, k6 = st.columns(3, gap="medium")

        k4.metric(
            "Avg. Hours / Programme",
            f"{avg_hours_per_programme:,.1f}",
        )
        k5.metric(
            "Training Cost",
            f"Rs. {total_cost:,.0f}",
        )
        k6.metric(
            "Hours / Worker",
            f"{avg_hours_per_worker:,.1f}",
        )

        st.write("")

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Monthly Training Hours")

            monthly = (
                filtered.assign(
                    month_num=filtered["from_date"].dt.month,
                    month_name=filtered["from_date"].dt.month_name(),
                    year=filtered["from_date"].dt.year,
                )
                .groupby(
                    ["year", "month_num", "month_name"],
                    as_index=False,
                )["calculated_total_hours"]
                .sum()
                .sort_values(["year", "month_num"])
            )

            if not monthly.empty:
                monthly["Month"] = monthly.apply(
                    lambda r: (
                        f"{r['month_name']} {int(r['year'])}"
                        if filtered["from_date"].dt.year.nunique() > 1
                        else r["month_name"]
                    ),
                    axis=1,
                )

                monthly_chart = monthly.set_index(
                    "Month"
                )[["calculated_total_hours"]]

                monthly_chart.columns = [
                    "Total Training Hours"
                ]

                st.line_chart(
                    monthly_chart,
                    use_container_width=True,
                )

        with c2:
            st.subheader("Training Hours by Type")

            by_type = (
                filtered.groupby("training_type")[
                    "calculated_total_hours"
                ]
                .sum()
                .sort_values(ascending=False)
                .to_frame("Training Hours")
            )

            st.bar_chart(
                by_type,
                use_container_width=True,
            )

        c3, c4 = st.columns(2)

        with c3:
            st.subheader("Programmes by Category")

            by_category = (
                filtered.groupby("category")["id"]
                .count()
                .reindex(
                    TRAINING_CATEGORIES,
                    fill_value=0,
                )
                .to_frame("Programmes")
            )

            st.bar_chart(
                by_category,
                use_container_width=True,
            )

        with c4:
            st.subheader("Training Cost by Category")

            by_cost_category = (
                filtered.groupby("category")[
                    "training_cost"
                ]
                .sum()
                .reindex(
                    TRAINING_CATEGORIES,
                    fill_value=0,
                )
                .to_frame("Actual Cost")
            )

            st.bar_chart(
                by_cost_category,
                use_container_width=True,
            )

    # ------------------------------------------------------------
    # BUDGET VS ACTUAL
    # ------------------------------------------------------------
    st.divider()
    st.header("Budget vs Actuals")
    st.caption(
        "Actuals are calculated from Training Cost. "
        "Budget values come from the separate Budget Entry section. "
        "Use the Location or Category selector below to compare Budget vs Actual."
    )

    budget_df = get_budget_records()

    if budget_df.empty:
        st.info(
            "No budgets have been entered yet. "
            "Use Budget Entry to add budgets by Location "
            "and Category."
        )
    else:
        budget_years = sorted(
            budget_df["budget_year"].unique().tolist(),
            reverse=True,
        )

        default_budget_year = (
            int(selected_year)
            if selected_year != "All Years"
            and int(selected_year) in budget_years
            else budget_years[0]
        )

        b_year = st.selectbox(
            "Budget Year",
            budget_years,
            index=budget_years.index(default_budget_year),
            key="budget_dash_year",
        )

        st.subheader(
            "1. Select Location — Budget vs Actual"
        )

        b1, b2, b3, b4 = st.columns(4)

        # Budget comparison supports all configured company locations.
        budget_df = budget_df[
            budget_df["location"].astype(str).str.strip().isin(BUDGET_LOCATIONS)
        ].copy()

        budget_locations = ["All Locations"] + BUDGET_LOCATIONS

        budget_location = b1.selectbox(
            "Select Location",
            budget_locations,
            key="budget_dash_location",
        )

        location_actual_df = df.copy()
        location_actual_df = location_actual_df[
            location_actual_df["from_date"].dt.year
            == int(b_year)
        ]

        if budget_location != "All Locations":
            location_actual_df = location_actual_df[
                location_actual_df["location"]
                .astype(str)
                .str.strip()
                == budget_location
            ]

        location_budget_df = budget_df[
            budget_df["budget_year"] == int(b_year)
        ].copy()

        if budget_location != "All Locations":
            location_budget_df = location_budget_df[
                location_budget_df["location"]
                .astype(str)
                .str.strip()
                == budget_location
            ]

        location_budget_total = float(
            location_budget_df["budget_amount"].sum()
        )
        location_actual_total = float(
            location_actual_df["training_cost"].sum()
        )
        location_variance = (
            location_budget_total - location_actual_total
        )
        location_utilization = (
            (location_actual_total / location_budget_total) * 100
            if location_budget_total > 0
            else 0
        )

        b1.metric(
            "Budget",
            f"Rs. {location_budget_total:,.0f}",
        )
        b2.metric(
            "Actual",
            f"Rs. {location_actual_total:,.0f}",
        )
        b3.metric(
            "Variance",
            f"Rs. {location_variance:,.0f}",
        )
        b4.metric(
            "Utilization",
            f"{location_utilization:,.1f}%",
        )

        location_categories = pd.DataFrame(
            {
                "Category": TRAINING_CATEGORIES,
                "Budget": [
                    float(
                        location_budget_df.loc[
                            location_budget_df["category"] == cat,
                            "budget_amount",
                        ].sum()
                    )
                    for cat in TRAINING_CATEGORIES
                ],
                "Actual": [
                    float(
                        location_actual_df.loc[
                            location_actual_df["category"] == cat,
                            "training_cost",
                        ].sum()
                    )
                    for cat in TRAINING_CATEGORIES
                ],
            }
        ).set_index("Category")

        st.bar_chart(
            location_categories[
                ["Budget", "Actual"]
            ],
            use_container_width=True,
        )

        st.subheader(
            "2. Select Category — Budget vs Actual"
        )

        c1, c2, c3, c4 = st.columns(4)

        budget_category = c1.selectbox(
            "Select Category",
            ["All Categories"] + TRAINING_CATEGORIES,
            key="budget_dash_category",
        )

        category_budget_df = budget_df[
            budget_df["budget_year"] == int(b_year)
        ].copy()

        category_actual_df = df.copy()
        category_actual_df = category_actual_df[
            category_actual_df["from_date"].dt.year
            == int(b_year)
        ]

        if budget_category != "All Categories":
            category_budget_df = category_budget_df[
                category_budget_df["category"]
                == budget_category
            ]
            category_actual_df = category_actual_df[
                category_actual_df["category"]
                == budget_category
            ]

        category_budget_total = float(
            category_budget_df["budget_amount"].sum()
        )
        category_actual_total = float(
            category_actual_df["training_cost"].sum()
        )
        category_variance = (
            category_budget_total - category_actual_total
        )
        category_utilization = (
            (category_actual_total / category_budget_total) * 100
            if category_budget_total > 0
            else 0
        )

        c1.metric(
            "Budget",
            f"Rs. {category_budget_total:,.0f}",
        )
        c2.metric(
            "Actual",
            f"Rs. {category_actual_total:,.0f}",
        )
        c3.metric(
            "Variance",
            f"Rs. {category_variance:,.0f}",
        )
        c4.metric(
            "Utilization",
            f"{category_utilization:,.1f}%",
        )

        category_locations = (
            sorted(
                set(
                    KNOWN_LOCATIONS
                    + category_budget_df["location"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .tolist()
                    + category_actual_df["location"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .tolist()
                ),
                key=str.upper,
            )
        )

        category_location_df = pd.DataFrame(
            {
                "Location": category_locations,
                "Budget": [
                    float(
                        category_budget_df.loc[
                            category_budget_df["location"]
                            .astype(str)
                            .str.strip()
                            == loc,
                            "budget_amount",
                        ].sum()
                    )
                    for loc in category_locations
                ],
                "Actual": [
                    float(
                        category_actual_df.loc[
                            category_actual_df["location"]
                            .astype(str)
                            .str.strip()
                            == loc,
                            "training_cost",
                        ].sum()
                    )
                    for loc in category_locations
                ],
            }
        ).set_index("Location")

        st.bar_chart(
            category_location_df[
                ["Budget", "Actual"]
            ],
            use_container_width=True,
        )

        budget_summary = pd.DataFrame(
            {
                "Category": TRAINING_CATEGORIES,
                "Budget": [
                    float(
                        budget_df.loc[
                            (budget_df["budget_year"] == int(b_year))
                            & (
                                budget_df["category"] == cat
                            ),
                            "budget_amount",
                        ].sum()
                    )
                    for cat in TRAINING_CATEGORIES
                ],
                "Actual": [
                    float(
                        df.loc[
                            (df["from_date"].dt.year == int(b_year))
                            & (df["category"] == cat),
                            "training_cost",
                        ].sum()
                    )
                    for cat in TRAINING_CATEGORIES
                ],
            }
        )

        budget_summary["Variance"] = (
            budget_summary["Budget"]
            - budget_summary["Actual"]
        )

        budget_summary["Utilization %"] = budget_summary.apply(
            lambda r: (
                (r["Actual"] / r["Budget"]) * 100
                if r["Budget"] > 0
                else 0
            ),
            axis=1,
        )

        st.subheader("Budget vs Actual Summary")
        st.dataframe(
            budget_summary,
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------------
    # TRAINING RECORDS
    # ------------------------------------------------------------
    if not filtered.empty:
        st.subheader("Training Records")

        display = filtered.copy()
        display["from_date"] = (
            display["from_date"].dt.strftime("%Y-%m-%d")
        )
        display["to_date"] = (
            display["to_date"].dt.strftime("%Y-%m-%d")
        )
        display["Total Training Hours"] = (
            display["calculated_total_hours"]
        )

        display = display[
            [
                "programme_name",
                "from_date",
                "to_date",
                "quarter",
                "training_type",
                "category",
                "trainer_name",
                "location",
                "training_hours",
                "participants_count",
                "Total Training Hours",
                "training_cost",
            ]
        ]

        display.columns = [
            "Programme",
            "From Date",
            "To Date",
            "Quarter",
            "Type",
            "Category",
            "Trainer",
            "Location",
            "Hours / Worker",
            "Workers",
            "Total Training Hours",
            "Training Cost (Rs.)",
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download Dashboard Data (CSV)",
            display.to_csv(index=False).encode("utf-8"),
            "training_dashboard.csv",
            "text/csv",
            use_container_width=True,
        )


# ============================================================
# RECORDS
# ============================================================

def render_records():
    user = require_user()

    st.title("Training Records")

    df = get_training_records()

    if df.empty:
        st.info("No training records available.")
        return

    search = st.text_input(
        "Search programme, trainer, location, category or type",
        placeholder="Search...",
    )

    filtered = df.copy()

    if search.strip():
        q = search.strip().lower()

        mask = (
            filtered["programme_name"]
            .astype(str)
            .str.lower()
            .str.contains(q, na=False)
            | filtered["trainer_name"]
            .astype(str)
            .str.lower()
            .str.contains(q, na=False)
            | filtered["location"]
            .astype(str)
            .str.lower()
            .str.contains(q, na=False)
            | filtered["power_plant"]
            .astype(str)
            .str.lower()
            .str.contains(q, na=False)
            | filtered["training_type"]
            .astype(str)
            .str.lower()
            .str.contains(q, na=False)
            | filtered["category"]
            .astype(str)
            .str.lower()
            .str.contains(q, na=False)
        )

        filtered = filtered[mask]

    if filtered.empty:
        st.info("No records match your search.")
        return

    display = filtered.copy()
    display["calculated_total_hours"] = (
        display["training_hours"]
        * display["participants_count"]
    )
    display["from_date"] = (
        display["from_date"].dt.strftime("%Y-%m-%d")
    )
    display["to_date"] = (
        display["to_date"].dt.strftime("%Y-%m-%d")
    )

    display = display[
        [
            "id",
            "programme_name",
            "from_date",
            "to_date",
            "quarter",
            "training_type",
            "category",
            "trainer_name",
            "location",
            "training_hours",
            "participants_count",
            "calculated_total_hours",
            "training_cost",
        ]
    ]

    display.columns = [
        "ID",
        "Programme",
        "From Date",
        "To Date",
        "Quarter",
        "Type",
        "Category",
        "Trainer",
        "Location",
        "Hours / Worker",
        "Workers",
        "Total Training Hours",
        "Cost (Rs.)",
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Records as CSV",
        display.to_csv(index=False).encode("utf-8"),
        "hr_training_records.csv",
        "text/csv",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Edit Record")

    ids = filtered["id"].astype(int).tolist()

    selected_id = st.selectbox(
        "Select record ID",
        ids,
        key="records_selected_id",
    )

    selected_rows = df[df["id"] == selected_id]

    if selected_rows.empty:
        st.warning(
            "The selected record is no longer available."
        )
        return

    row = selected_rows.iloc[0]

    with st.expander("Edit selected record"):
        a, b = st.columns(2)

        with a:
            programme = st.text_input(
                "Programme",
                value=str(
                    row["programme_name"] or ""
                ),
                key=f"ep_{selected_id}",
            )

            from_default = (
                row["from_date"].date()
                if pd.notna(row["from_date"])
                else date.today()
            )

            to_default = (
                row["to_date"].date()
                if pd.notna(row["to_date"])
                else from_default
            )

            from_date = st.date_input(
                "From Date",
                value=from_default,
                key=f"ef_{selected_id}",
            )

            to_date = st.date_input(
                "To Date",
                value=to_default,
                key=f"et_{selected_id}",
            )

            quarter_options = [
                "Q1", "Q2", "Q3", "Q4"
            ]

            quarter = st.selectbox(
                "Quarter",
                quarter_options,
                index=(
                    quarter_options.index(
                        str(row["quarter"])
                    )
                    if str(row["quarter"])
                    in quarter_options
                    else 0
                ),
                key=f"eq_{selected_id}",
            )

        with b:
            current_type = str(
                row["training_type"]
            )

            training_types = TRAINING_TYPES.copy()

            if (
                current_type
                and current_type not in training_types
            ):
                training_types.append(current_type)

            training_type = st.selectbox(
                "Type",
                training_types,
                index=(
                    training_types.index(current_type)
                    if current_type in training_types
                    else 0
                ),
                key=f"ety_{selected_id}",
            )

            current_category = str(
                row["category"]
                or "Internal Training"
            )

            categories = TRAINING_CATEGORIES.copy()

            if (
                current_category
                and current_category not in categories
            ):
                categories.append(current_category)

            category = st.selectbox(
                "Category",
                categories,
                index=(
                    categories.index(current_category)
                    if current_category in categories
                    else 0
                ),
                key=f"ecat_{selected_id}",
            )

            trainer_name = st.text_input(
                "Trainer's Name",
                value=str(
                    row.get("trainer_name", "")
                    or ""
                ),
                key=f"etrainer_{selected_id}",
            )

            current_plant = str(
                row["power_plant"]
                or "Not Specified"
            ).strip()

            existing_plants = (
                ["Not Specified"]
                + get_power_plants()
            )

            if (
                current_plant
                and current_plant not in existing_plants
            ):
                existing_plants.append(current_plant)

            power_plant = st.selectbox(
                "Power Plant",
                existing_plants,
                index=(
                    existing_plants.index(current_plant)
                    if current_plant in existing_plants
                    else 0
                ),
                key=f"eplant_{selected_id}",
            )

            training_hours = st.number_input(
                "Training Hours per Worker",
                min_value=0.0,
                value=float(
                    row["training_hours"]
                ),
                step=0.5,
                key=f"eh_{selected_id}",
            )

            participants = st.number_input(
                "Workers Attended",
                min_value=0,
                value=int(
                    round(
                        float(
                            row["participants_count"]
                        )
                    )
                ),
                step=1,
                format="%d",
                key=f"epeople_{selected_id}",
            )

        cost = st.number_input(
            "Training Cost (Rs.)",
            min_value=0.0,
            value=float(row["training_cost"]),
            step=1000.0,
            key=f"ecost_{selected_id}",
        )

        names = st.text_area(
            "Participant Names",
            value=str(
                row["participant_names"]
                or ""
            ),
            key=f"en_{selected_id}",
        )

        total_hours = (
            training_hours * participants
        )

        st.markdown(
            f"**Total Training Hours = "
            f"{training_hours:,.2f} × "
            f"{participants:,.1f} = "
            f"{total_hours:,.2f}**"
        )

        b1, b2 = st.columns(2)

        with b1:
            if st.button(
                "Save Changes",
                type="primary",
                use_container_width=True,
                key=f"save_{selected_id}",
            ):
                if not programme.strip():
                    st.error(
                        "Programme name cannot be empty."
                    )
                elif not trainer_name.strip():
                    st.error(
                        "Trainer's name cannot be empty."
                    )
                elif not power_plant.strip():
                    st.error(
                        "Please select a power plant."
                    )
                elif to_date < from_date:
                    st.error(
                        "To Date cannot be earlier than From Date."
                    )
                elif (
                    training_hours <= 0
                    or participants <= 0
                ):
                    st.error(
                        "Training Hours and Workers Attended "
                        "must be greater than 0."
                    )
                else:
                    try:
                        update_training_record(
                            selected_id,
                            programme.strip(),
                            from_date,
                            to_date,
                            quarter,
                            training_type,
                            category,
                            power_plant.strip(),
                            power_plant.strip(),
                            trainer_name.strip(),
                            names.strip(),
                            cost,
                            training_hours,
                            participants,
                        )

                        st.success(
                            "Record updated successfully."
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(
                            "Unable to update record."
                        )
                        with st.expander(
                            "Technical details"
                        ):
                            st.exception(e)

        with b2:
            is_admin = (
                str(user.get("role", "user"))
                .strip()
                .lower()
                == "admin"
            )

            if is_admin:
                if st.button(
                    "Delete Record",
                    use_container_width=True,
                    key=f"delete_{selected_id}",
                ):
                    try:
                        delete_training_record(
                            selected_id
                        )
                        st.success(
                            "Record deleted successfully."
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(
                            "Unable to delete record."
                        )
                        with st.expander(
                            "Technical details"
                        ):
                            st.exception(e)
            else:
                st.caption(
                    "Delete is available to administrators only."
                )


# ============================================================
# BUDGET ENTRY
# ============================================================

def render_budget_entry():
    # Budget Entry is available to every authenticated user.
    user = require_user()

    st.title("Training Budget Entry")
    st.caption(
        "Enter and manage separate annual budgets for each location and training category. "
        "This section is available to all logged-in users."
    )

    st.info(
        "Budget Entry is available for all configured locations. "
        "Training Cost is the actual amount used for Budget vs Actual comparison."
    )

    st.markdown(
        """
        <div class="formula-box">
            <div class="formula-title">
                Budget Structure
            </div>
            <div class="formula-text">
                Budget = Year + Location + Category + Budget Amount
            </div>
            <div class="small-note">
                Categories:
                Internal Training · External Training ·
                Overseas Training · Management Training
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Budget Entry supports all configured company locations.
    # BUDGET_LOCATIONS is based on KNOWN_LOCATIONS and therefore includes
    # HOF, BBO, BTO, BKN, EME, MGT, GNT, HS1, HS2, LKM, MVB, ORK,
    # RDP, UDW, VBL and WMB.
    budget_df = get_budget_records()
    locations = BUDGET_LOCATIONS.copy()

    with st.container(border=True):
        st.subheader("Enter / Update Budget")

        c1, c2 = st.columns(2)

        with c1:
            budget_year = st.number_input(
                "Budget Year *",
                min_value=2020,
                max_value=2100,
                value=date.today().year,
                step=1,
                format="%d",
                key="budget_year_entry",
            )

            budget_location = st.selectbox(
                "Location *",
                locations,
                key="budget_location_entry",
            )

        with c2:
            budget_category = st.selectbox(
                "Category *",
                TRAINING_CATEGORIES,
                key="budget_category_entry",
            )

            budget_amount = st.number_input(
                "Budget Amount (Rs.) *",
                min_value=0.0,
                step=10000.0,
                format="%.2f",
                key="budget_amount_entry",
            )

        if st.button(
            "Save Budget",
            type="primary",
            use_container_width=True,
        ):
            if not budget_location.strip():
                st.error(
                    "Please select a location."
                )
            elif budget_amount < 0:
                st.error(
                    "Budget amount cannot be negative."
                )
            else:
                try:
                    save_budget_record(
                        None,
                        budget_year,
                        budget_location,
                        budget_category,
                        budget_amount,
                        user.get("id"),
                    )

                    st.success(
                        "Budget saved successfully. "
                        "If the same Year + Location + Category "
                        "already existed, it was updated."
                    )
                    st.rerun()

                except Exception as e:
                    st.error(
                        "Unable to save the budget."
                    )
                    with st.expander(
                        "Technical details"
                    ):
                        st.exception(e)

    st.divider()
    st.subheader("Existing Budgets")

    budget_df = get_budget_records()

    if budget_df.empty:
        st.info("No budget records have been entered yet.")
        return

    budget_display = budget_df.copy()

    budget_display["Budget Amount (Rs.)"] = (
        budget_display["budget_amount"]
    )

    budget_display = budget_display[
        [
            "id",
            "budget_year",
            "location",
            "category",
            "Budget Amount (Rs.)",
        ]
    ]

    budget_display.columns = [
        "ID",
        "Year",
        "Location",
        "Category",
        "Budget Amount (Rs.)",
    ]

    st.dataframe(
        budget_display,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Budgets as CSV",
        budget_display.to_csv(
            index=False
        ).encode("utf-8"),
        "training_budgets.csv",
        "text/csv",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Edit / Delete Budget")

    budget_ids = (
        budget_df["id"]
        .astype(int)
        .tolist()
    )

    selected_budget_id = st.selectbox(
        "Select Budget ID",
        budget_ids,
        key="selected_budget_id",
    )

    budget_rows = budget_df[
        budget_df["id"] == selected_budget_id
    ]

    if budget_rows.empty:
        return

    budget_row = budget_rows.iloc[0]

    with st.expander("Edit selected budget"):
        ec1, ec2 = st.columns(2)

        with ec1:
            edit_year = st.number_input(
                "Year",
                min_value=2020,
                max_value=2100,
                value=int(
                    budget_row["budget_year"]
                ),
                step=1,
                format="%d",
                key=f"edit_budget_year_{selected_budget_id}",
            )

            # Budget editing supports all configured company locations.
            edit_locations = BUDGET_LOCATIONS.copy()

            current_location = str(
                budget_row["location"]
            ).strip()

            edit_location = st.selectbox(
                "Location",
                edit_locations,
                index=(
                    edit_locations.index(
                        current_location
                    )
                    if current_location
                    in edit_locations
                    else 0
                ),
                key=f"edit_budget_location_{selected_budget_id}",
            )

        with ec2:
            current_category = str(
                budget_row["category"]
            )

            edit_category = st.selectbox(
                "Category",
                TRAINING_CATEGORIES,
                index=(
                    TRAINING_CATEGORIES.index(
                        current_category
                    )
                    if current_category
                    in TRAINING_CATEGORIES
                    else 0
                ),
                key=f"edit_budget_category_{selected_budget_id}",
            )

            edit_amount = st.number_input(
                "Budget Amount (Rs.)",
                min_value=0.0,
                value=float(
                    budget_row["budget_amount"]
                ),
                step=10000.0,
                format="%.2f",
                key=f"edit_budget_amount_{selected_budget_id}",
            )

        ec_save, ec_delete = st.columns(2)

        with ec_save:
            if st.button(
                "Save Budget Changes",
                type="primary",
                use_container_width=True,
                key=f"save_budget_{selected_budget_id}",
            ):
                try:
                    save_budget_record(
                        int(selected_budget_id),
                        edit_year,
                        edit_location,
                        edit_category,
                        edit_amount,
                        user.get("id"),
                    )
                    st.success(
                        "Budget updated successfully."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(
                        "Unable to update budget."
                    )
                    with st.expander(
                        "Technical details"
                    ):
                        st.exception(e)

        with ec_delete:
            if st.button(
                "Delete Budget",
                use_container_width=True,
                key=f"delete_budget_{selected_budget_id}",
            ):
                try:
                    delete_budget_record(
                        selected_budget_id
                    )
                    st.success(
                        "Budget deleted successfully."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(
                        "Unable to delete budget."
                    )
                    with st.expander(
                        "Technical details"
                    ):
                        st.exception(e)


# ============================================================
# ACCOUNT
# ============================================================

def render_account():
    user = require_user()

    st.title("My Account")

    with st.container(border=True):
        st.write(
            f"**Name:** "
            f"{user.get('full_name', user.get('name', ''))}"
        )
        st.write(
            f"**Username:** @{user.get('username', '')}"
        )
        st.write(
            f"**Email:** {user.get('email', '')}"
        )
        st.write(
            f"**Role:** "
            f"{str(user.get('role', 'user')).title()}"
        )

    st.write("")

    with st.container(border=True):
        st.subheader("Change Password")

        with st.form("change_password_form"):
            new_password = st.text_input(
                "New password",
                type="password",
            )
            confirm = st.text_input(
                "Confirm new password",
                type="password",
            )
            submit = st.form_submit_button(
                "Update password",
                type="primary",
            )

        if submit:
            if len(new_password) < 8:
                st.error(
                    "Password must contain at least 8 characters."
                )
            elif new_password != confirm:
                st.error(
                    "Passwords do not match."
                )
            else:
                try:
                    change_password(
                        int(user["id"]),
                        new_password,
                    )
                    st.success(
                        "Password updated successfully."
                    )
                except Exception:
                    st.error(
                        "Unable to update the password."
                    )


# ============================================================
# MAIN
# ============================================================

logged_user = get_user()

if not logged_user:
    render_login()
else:
    render_sidebar()

    page = st.session_state.get(
        "hr_page",
        "Home",
    )

    if page == "Home":
        render_home()
    elif page == "Dashboard":
        render_dashboard()
    elif page == "Data Entry":
        render_data_entry()
    elif page == "Import Excel":
        render_import_excel()
    elif page == "Records":
        render_records()
    elif page == "Budget Entry":
        render_budget_entry()
    elif page == "My Account":
        render_account()
    else:
        st.session_state.hr_page = "Home"
        render_home()
