"""Stations whose operations ran more than 10 minutes late."""

import pandas as pd
import plotly.express as px

from app.processing import columns as col
from app.processing.parsing import to_minutes
from app.reports.html import TABLE_ATTRS, esc, header_row, message

THRESHOLD_MIN = 10


def render_delays(chains: pd.DataFrame) -> str:
    if col.MES_PLANNED_TIME not in chains.columns or col.MES_ACTUAL_TIME not in chains.columns:
        return message(f"Columns '{col.MES_PLANNED_TIME}' or '{col.MES_ACTUAL_TIME}' are missing.")

    df = chains.copy()
    df["delay_min"] = df[col.MES_ACTUAL_TIME].apply(to_minutes) - df[col.MES_PLANNED_TIME].apply(to_minutes)
    late = df[df["delay_min"] > THRESHOLD_MIN]
    if late.empty:
        return f"<p>No delay longer than {THRESHOLD_MIN} minutes.</p>"

    by_station = (
        late.groupby(col.MES_STATION, as_index=False)
        .agg(avg_delay=("delay_min", "mean"), incident=(col.MES_INCIDENT, "first"),
             cause=(col.MES_ROOT_CAUSE, "first"))
        .fillna({"incident": "Not provided", "cause": "Not provided"})
        .sort_values("avg_delay", ascending=False)
    )

    return (
        f'<h2 style="color:black;">Delays longer than {THRESHOLD_MIN} minutes by station</h2>'
        + _table(by_station) + _chart(by_station)
        + f'<p style="margin-top:20px;font-size:0.9rem;color:#666;"><b>Summary:</b> '
        f"{len(by_station)} stations with delays | {len(late)} delayed rows in total</p>"
    )


def _table(by_station: pd.DataFrame) -> str:
    rows = "".join(
        f"""<tr style="color:black;">
  <td style="text-align:center;"><b>{r[col.MES_STATION]}</b></td>
  <td style="text-align:center;font-weight:bold;color:#d32f2f;">{r['avg_delay']:.1f}</td>
  <td>{esc(r['incident'])}</td>
  <td>{esc(r['cause'])}</td>
</tr>"""
        for _, r in by_station.iterrows()
    )
    header = header_row(["Station", "Average delay (min)", "Industrial incident", "Potential cause"])
    return f"<table {TABLE_ATTRS}>{header}{rows}</table>"


def _chart(by_station: pd.DataFrame) -> str:
    data = by_station.sort_values("avg_delay")
    fig = px.bar(
        data, x="avg_delay", y=col.MES_STATION, orientation="h",
        color="avg_delay", color_continuous_scale="Reds",
        labels={col.MES_STATION: "Station", "avg_delay": "Average delay (min)"},
        title=f"Average delay by station (> {THRESHOLD_MIN} min)",
    )
    fig.update_layout(height=max(400, len(data) * 50), margin=dict(l=80, r=50, t=100, b=80),
                      yaxis=dict(type="category"))
    return fig.to_html(full_html=False, include_plotlyjs="cdn")
