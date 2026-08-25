"""Shared CSS + small UI helpers so every page looks consistent."""

import streamlit as st

ACCENTS = ["#22d3c3", "#f0b429", "#4d8dfc", "#4d8dfc", "#7c6ef2", "#f0b429", "#f2568b"]


def inject_css():
    st.markdown(
        """
        <style>
        #MainMenu, footer, header {visibility: hidden;}

        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1300px;}

        /* KPI cards */
        .kpi-card {
            background: #151b2b;
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            border-left: 5px solid var(--accent, #22d3c3);
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            height: 100%;
        }
        .kpi-label {
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #9aa4b8;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #f2f4f8;
            line-height: 1.15;
        }
        .kpi-sub {
            font-size: 0.78rem;
            color: #7d879c;
            margin-top: 0.25rem;
        }

        /* Filter bar */
        .filter-bar {
            background: #10162a;
            border-radius: 14px;
            padding: 1.1rem 1.3rem 0.4rem 1.3rem;
            margin-bottom: 1.4rem;
            border: 1px solid #1f2a45;
        }
        .filter-label {
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            color: #7d879c;
            font-weight: 700;
            margin-bottom: -0.6rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f2f4f8;
            margin-bottom: 0.1rem;
        }
        .section-sub {
            font-size: 0.82rem;
            color: #7d879c;
            margin-bottom: 0.8rem;
        }

        .auth-card {
            background: #151b2b;
            border-radius: 16px;
            padding: 2rem 2.2rem;
            border: 1px solid #1f2a45;
        }

        div[data-testid="stForm"] {
            background: #151b2b;
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            border: 1px solid #1f2a45;
        }

        .app-title {
            font-size: 1.9rem;
            font-weight: 800;
            background: linear-gradient(90deg, #22d3c3, #4d8dfc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str, accent: str):
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{accent}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, sub: str = ""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)
