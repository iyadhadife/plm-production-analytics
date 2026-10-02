"""Headcount per week, step and station, split by experience level."""

import pandas as pd

from app.processing import columns as col
from app.processing.joins import PERSON_NAME, WEEK
from app.reports.html import TABLE_ATTRS, esc, header_row, message

STEP, STATION, LEVEL = col.MES_STEP, col.MES_STATION, col.ERP_EXPERIENCE
GREEN, RED = "#c6f7c3", "#f7c3c3"


def render_team_experience(chains: pd.DataFrame) -> str:
    """
    Table Week | Step | Station | Expert | Confirmed | Beginner | Total.
    A row is green when at least a third of the team are experts, red otherwise.
    """
    required = [WEEK, STEP, STATION, PERSON_NAME, LEVEL]
    missing = [c for c in required if c not in chains.columns]
    if missing:
        return message(f"Missing columns: {missing}")

    table = headcount_by_level(chains[required])
    if table.empty:
        return message("No usable week / step / station / experience data.")

    labels = [col.EXPERIENCE_LABELS[lvl] for lvl in col.EXPERIENCE_LEVELS]
    html = (
        "<h3>Headcount by week, assembly step, station and experience level</h3>"
        f"<table {TABLE_ATTRS}>" + header_row(["Week", "Assembly step", "Station", *labels, "Total"])
    )
    for week, week_rows in table.groupby(WEEK):
        html += _week_rows(week, week_rows)
    return html + "</table>"


def headcount_by_level(df: pd.DataFrame) -> pd.DataFrame:
    """Distinct people per (week, step, station), one column per experience level."""
    df = df.dropna().copy()
    df[WEEK] = pd.to_numeric(df[WEEK], errors="coerce")
    df = df.dropna(subset=[WEEK])
    if df.empty:
        return df
    df[WEEK] = df[WEEK].astype(int)
    for c in (STEP, PERSON_NAME, LEVEL):
        df[c] = df[c].astype(str).str.strip()

    counts = (
        df.groupby([WEEK, STEP, STATION, LEVEL])[PERSON_NAME].nunique()
        .unstack(LEVEL, fill_value=0)
        .reindex(columns=col.EXPERIENCE_LEVELS, fill_value=0)
    )
    counts["total"] = counts.sum(axis=1)
    return counts.reset_index().sort_values([WEEK, STEP, STATION])


def _week_rows(week: int, rows: pd.DataFrame) -> str:
    html, first_in_week = "", True
    for step, step_rows in rows.groupby(STEP):
        first_in_step = True
        for _, row in step_rows.iterrows():
            expert, total = int(row["Expert"]), int(row["total"])
            color = GREEN if total > 0 and expert >= total / 3 else RED
            html += f"<tr style='background-color:{color};'>"
            if first_in_week:
                html += f"<td rowspan='{len(rows)}' style='font-weight:bold;vertical-align:top;'>{week}</td>"
                first_in_week = False
            if first_in_step:
                html += f"<td rowspan='{len(step_rows)}' style='vertical-align:top;'>{esc(step)}</td>"
                first_in_step = False
            html += f"<td style='text-align:center;'><b>{row[STATION]}</b></td>"
            html += "".join(f"<td style='text-align:right;'>{int(row[lvl])}</td>" for lvl in col.EXPERIENCE_LEVELS)
            html += f"<td style='text-align:right;font-weight:bold;'>{total}</td></tr>"
    return html
