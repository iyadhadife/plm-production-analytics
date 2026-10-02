"""Priority matrix: overrun (MES) x parts value and criticality (PLM) per operation."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C, CRITICALITY_COLOR, CRITICALITY_ORDER, CRITICALITY_WEIGHT, NO_PARTS
from app.analytics.model import Model
from app.analytics.rendering.components import card, insights, table
from app.analytics.rendering.formatters import fmt_eur
from app.analytics.rendering.layout import bubble_sizes, layout
from app.analytics.rendering.page import page

MIN_PLOT_VALUE = 10  # log axis: clip zero-value operations


def render(model: Model) -> str:
    ops = model.ops.copy()
    ops["plot_value"] = ops["parts_value"].clip(lower=MIN_PLOT_VALUE)
    ops["score"] = priority_score(ops)
    x_median, y_median = float(ops["overrun_pct"].median()), float(ops["plot_value"].median())
    quadrant = ops[(ops["overrun_pct"] >= x_median) & (ops["plot_value"] >= y_median)].sort_values(
        "score", ascending=False)

    body = (
        _insights(quadrant, x_median, y_median)
        + card("Station priority matrix", "Each bubble is one MES operation. Dotted lines are the medians.",
               "fig_m", height=560)
        + card("Top 10 stations to address first", inner=_top_table(ops))
    )
    return page("Risk × value matrix of stations",
                "Crosses execution delay (MES) with the value and criticality of the consumed parts (PLM) and the "
                "team profile (ERP) to decide <b>where to act first</b>.",
                ["MES", "PLM", "ERP"], body, {"fig_m": _figure(ops, x_median, y_median)})


def priority_score(ops: pd.DataFrame) -> pd.Series:
    """50 % overrun rank + 30 % parts value rank + 20 % criticality (0-100)."""
    return (ops["overrun_pct"].rank(pct=True) * 0.5 + ops["parts_value"].rank(pct=True) * 0.3
            + ops["max_criticality"].map(CRITICALITY_WEIGHT).fillna(0) / 4 * 0.2) * 100


def _figure(ops: pd.DataFrame, x_median: float, y_median: float) -> dict:
    _, ref = bubble_sizes(ops["overrun_min"])
    traces = []
    for crit in CRITICALITY_ORDER + [NO_PARTS]:
        sub = ops[ops["max_criticality"] == crit]
        if sub.empty:
            continue
        sizes, _ = bubble_sizes(sub["overrun_min"])
        traces.append({
            "type": "scatter", "mode": "markers",
            "name": f"{crit} criticality" if crit != NO_PARTS else crit,
            "x": sub["overrun_pct"], "y": sub["plot_value"],
            "marker": {"size": sizes, "sizemode": "area", "sizeref": ref, "sizemin": 6,
                       "color": CRITICALITY_COLOR.get(crit, C["muted"]), "opacity": 0.85,
                       "line": {"color": C["surface"], "width": 2}},
            "customdata": np.stack([sub["label"], sub["overrun_min"], sub["parts_value"], sub["levels"].fillna("–"),
                                    sub["incident"].fillna("–"), sub["labour_overrun_cost"]], axis=1),
            "hovertemplate": "<b>%{customdata[0]}</b><br>Overrun: +%{x:.0f} % (%{customdata[1]:.0f} min)"
                             "<br>Parts value: %{customdata[2]:,.0f} €<br>Labour overrun: %{customdata[5]:,.0f} €"
                             "<br>Team: %{customdata[3]}<br>Incident: %{customdata[4]}<extra></extra>",
        })

    dotted = {"color": C["muted"], "width": 1, "dash": "dot"}
    return {"data": traces, "layout": layout(
        showlegend=True,
        xaxis={"title": {"text": "Overrun of planned time (%) — MES"},
               "range": [float(ops["overrun_pct"].min()) * 0.95, float(ops["overrun_pct"].max()) * 1.05]},
        yaxis={"title": {"text": "Value of committed parts (€, log scale) — PLM"}, "type": "log"},
        shapes=[
            {"type": "line", "x0": x_median, "x1": x_median, "yref": "paper", "y0": 0, "y1": 1, "line": dotted},
            {"type": "line", "xref": "paper", "x0": 0, "x1": 1, "y0": y_median, "y1": y_median, "line": dotted},
        ],
        annotations=[
            _corner(1, 1, "<b>PRIORITY 1</b> · high delay + high value", "#d03b3b"),
            _corner(0, 1, "High value, under control", C["muted"]),
            _corner(1, 0, "High delay, low parts stake", C["muted"]),
        ]),
    }


def _corner(x: int, y: int, text: str, color: str) -> dict:
    return {"xref": "paper", "yref": "paper", "x": x, "y": y, "showarrow": False, "text": text,
            "xanchor": "right" if x else "left", "yanchor": "top" if y else "bottom",
            "font": {"color": color, "size": 11}}


def _top_table(ops: pd.DataFrame) -> str:
    top = ops.sort_values("score", ascending=False).head(10)
    df = pd.DataFrame({
        "Station": top["station"], "Step": top["step"], "Overrun": top["overrun_pct"],
        "Parts value": top["parts_value"], "Max criticality": top["max_criticality"],
        "Incident (MES)": top["incident"], "Team exp. (1-3)": top["avg_experience"], "Priority score": top["score"],
    })
    return table(df, {
        "Overrun": lambda v: f"+{v:.0f} %", "Parts value": fmt_eur,
        "Team exp. (1-3)": lambda v: f"{v:.1f}" if pd.notna(v) else "–",
        "Priority score": lambda v: f"{v:.0f}",
    }, bar_col="Priority score")


def _insights(quadrant: pd.DataFrame, x_median: float, y_median: float) -> str:
    stations = ", ".join("S" + str(int(s)) for s in quadrant["station"].head(8))
    return insights([
        f"<b>{len(quadrant)} stations</b> fall in the “Priority 1” quadrant (overrun ≥ {x_median:.0f} % and parts "
        f"value ≥ {fmt_eur(y_median)}): {stations}.",
        "Bubble size = minutes of delay; colour = the most critical part consumed (PLM).",
        "Priority score = 50 % overrun rank + 30 % parts value rank + 20 % criticality.",
    ])
