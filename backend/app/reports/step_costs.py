"""Cost breakdown (parts + labour) for every assembly step."""

import pandas as pd
import plotly.express as px

from app.processing import columns as col
from app.processing.costs import UNIT_COST, labour_by_person, parts_with_cost
from app.processing.joins import PART_CODE, PERSON_NAME
from app.processing.parsing import to_timedelta
from app.reports.html import fmt_duration, fmt_eur, message, styled_table

STEP = col.MES_STEP


def render_step_costs(mes: pd.DataFrame, plm: pd.DataFrame, erp: pd.DataFrame) -> str:
    if col.MES_PLANNED_TIME not in mes.columns:
        return message(f"Column '{col.MES_PLANNED_TIME}' not found. Available columns: {list(mes.columns)}")

    summary = step_cost_summary(mes, plm, erp)
    return f"""
<div style="font-family: Arial, sans-serif;">
  <h2>Cost breakdown by assembly step</h2>
  {styled_table(_display_table(summary))}
  <br/><hr>
  {_pie_chart(summary)}
</div>
"""


def step_cost_summary(mes: pd.DataFrame, plm: pd.DataFrame, erp: pd.DataFrame) -> pd.DataFrame:
    parts = parts_with_cost(mes, plm)
    by_parts = parts.groupby(STEP).agg(parts_cost=(UNIT_COST, "sum"), parts=(PART_CODE, "size"))

    times = mes[[STEP]].assign(planned=mes[col.MES_PLANNED_TIME].apply(to_timedelta))
    by_time = times.groupby(STEP).agg(planned_time=("planned", "sum"))

    people = labour_by_person(mes, erp, group_by=[STEP])
    by_people = people.groupby(STEP).agg(labour_cost=("cost", "sum"), people=(PERSON_NAME, "nunique"))

    summary = by_parts.join(by_time, how="outer").join(by_people, how="outer").reset_index()
    for c in ("parts_cost", "labour_cost", "parts", "people"):
        summary[c] = summary[c].fillna(0)
    summary["planned_hours"] = summary["planned_time"].dt.total_seconds() / 3600
    summary["total_cost"] = summary["parts_cost"] + summary["labour_cost"]
    return summary.sort_values("total_cost", ascending=False).reset_index(drop=True)


def _display_table(summary: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Step": summary[STEP],
        "Planned time": summary["planned_time"].apply(fmt_duration),
        "Planned hours": summary["planned_hours"].map(lambda v: f"{v:.2f} h"),
        "People": summary["people"].astype(int),
        "Parts": summary["parts"].astype(int),
        "Parts cost": summary["parts_cost"].map(fmt_eur),
        "Labour cost": summary["labour_cost"].map(fmt_eur),
        "Total cost": summary["total_cost"].map(fmt_eur),
    })


def _pie_chart(summary: pd.DataFrame) -> str:
    data = summary[summary["total_cost"] > 0]
    if data.empty:
        return "<p>No non-zero total cost to plot.</p>"
    fig = px.pie(data, names=STEP, values="total_cost", title="Share of total cost by assembly step")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=500)
    return fig.to_html(full_html=False, include_plotlyjs="cdn")
