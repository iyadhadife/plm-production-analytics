"""Gantt chart of planned vs actual operations."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C, CRITICALITY_COLOR, CRITICALITY_ORDER
from app.analytics.model import Model
from app.analytics.rendering.components import card, criticality_badge, insights
from app.analytics.rendering.layout import layout
from app.analytics.rendering.page import page

MS_PER_MIN = 60_000


def render(model: Model) -> str:
    ops = model.ops.dropna(subset=["start"]).sort_values("start").copy()
    legend = ('<p class="note">Light bar = planned duration (MES) · thin bar = actual duration, coloured by the '
              "max criticality of the parts (PLM): " + " ".join(criticality_badge(c) for c in CRITICALITY_ORDER)
              + ". Hover to see the team (ERP) and the incident.</p>")
    body = _insights(ops) + card("Operations timeline (planned vs actual Gantt)", chart_id="fig_g",
                                 height=max(600, 19 * len(ops) + 60), inner=legend)
    return page("Production timeline",
                "Gantt chart linking execution (MES), parts criticality (PLM) and teams (ERP), operation by operation.",
                ["MES", "PLM", "ERP"], body, {"fig_g": _gantt(ops)})


def _gantt(ops: pd.DataFrame) -> dict:
    labels = ops["label"].tolist()
    starts = [d.strftime("%Y-%m-%d %H:%M:%S") for d in ops["start"]]
    customdata = np.stack([ops["planned_min"], ops["actual_min"], ops["overrun_pct"], ops["max_criticality"],
                           ops["levels"].fillna("–"), ops["incident"].fillna("–"), ops["parts"].fillna("–")], axis=1)
    hover = ("<b>%{y}</b><br>Planned %{customdata[0]:.0f} min · Actual %{customdata[1]:.0f} min "
             "(+%{customdata[2]:.0f} %)<br>Max criticality: %{customdata[3]}<br>Parts: %{customdata[6]}"
             "<br>Team: %{customdata[4]}<br>Incident: %{customdata[5]}<extra></extra>")
    common = {"type": "bar", "orientation": "h", "y": labels, "base": starts, "customdata": customdata,
              "hovertemplate": hover}
    return {
        "data": [
            {**common, "name": "Planned duration", "x": (ops["planned_min"] * MS_PER_MIN).tolist(), "width": 0.8,
             "marker": {"color": C["seq"][0], "line": {"color": C["seq"][2], "width": 1}}},
            {**common, "name": "Actual duration", "x": (ops["actual_min"] * MS_PER_MIN).tolist(), "width": 0.38,
             "marker": {"color": [CRITICALITY_COLOR.get(c, C["muted"]) for c in ops["max_criticality"]]}},
        ],
        "layout": layout(showlegend=False, barmode="overlay", margin={"l": 330, "t": 10},
                         xaxis={"type": "date", "tickformat": "%d/%m %Hh", "side": "top"},
                         yaxis={"autorange": "reversed", "automargin": True, "tickfont": {"size": 10.5}}),
    }


def _insights(ops: pd.DataFrame) -> str:
    by_day = ops.groupby(ops["start"].dt.date).agg(
        count=("station", "count"), planned=("planned_min", "sum"), actual=("actual_min", "sum")).reset_index()
    busiest = by_day.sort_values("actual", ascending=False).iloc[0]["start"]
    days = " · ".join(f"{r['start']:%d/%m}: {r['count']} ops, +{(r['actual'] / r['planned'] - 1) * 100:.0f} %"
                      for _, r in by_day.iterrows())
    return insights([
        f"Busiest day: <b>{busiest:%d/%m}</b>. {days}",
        "Operations run in series: every minute of delay shifts all the following ones "
        "(see the S-curve in the overview).",
    ])
