"""Supply risk: parts that can stop the line, and supplier concentration."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C, CRITICALITY_COLOR, CRITICALITY_ORDER
from app.analytics.model import Model
from app.analytics.rendering.components import card, insights, table
from app.analytics.rendering.formatters import esc
from app.analytics.rendering.layout import BAR_LINE, bubble_sizes, layout
from app.analytics.rendering.page import page

LONG_LEAD_DAYS = 25


def render(model: Model) -> str:
    parts = model.parts[model.parts["qty_used"] > 0].copy()
    suppliers = supplier_exposure(parts)

    body = (
        _insights(parts, suppliers)
        + card("Parts risk matrix", "Size = quantity consumed in the MES; colour = PLM criticality. "
               "Top right: expensive parts with long lead times.", "fig_r", height=520)
        + card("Top 10 parts to secure", inner=_top_table(parts))
        + card("Exposure by supplier", "Share of the value of consumed parts (log scale).", "fig_f",
               height=max(420, 26 * len(suppliers)))
    )
    return page("Supply risk & suppliers",
                "Links part attributes (criticality, lead time, cost, supplier — PLM) to their actual use on the line "
                "(MES) to target the parts that can stop production.",
                ["PLM", "MES"], body, {"fig_r": _risk_matrix(parts), "fig_f": _supplier_chart(suppliers)})


def supplier_exposure(parts: pd.DataFrame) -> pd.DataFrame:
    return parts.groupby("supplier").agg(
        value=("used_value", "sum"), lead=("max_lead_days", "max"),
        refs=("code", "nunique"), stations=("station_count", "sum"),
    ).reset_index().sort_values("value")


def _risk_matrix(parts: pd.DataFrame) -> dict:
    _, ref = bubble_sizes(parts["qty_used"], 40)
    traces = []
    for crit in CRITICALITY_ORDER:
        sub = parts[parts["criticality"] == crit]
        if sub.empty:
            continue
        sizes, _ = bubble_sizes(sub["qty_used"], 40)
        traces.append({
            "type": "scatter", "mode": "markers+text", "name": f"{crit} criticality",
            "x": sub["max_lead_days"], "y": sub["unit_cost"],
            "text": [code if weight >= 3 else "" for code, weight in zip(sub["code"], sub["crit_weight"])],
            "textposition": "top center", "textfont": {"size": 10, "color": C["text2"]},
            "marker": {"size": sizes, "sizemode": "area", "sizeref": ref, "sizemin": 6,
                       "color": CRITICALITY_COLOR[crit], "opacity": 0.85, "line": BAR_LINE},
            "customdata": np.stack([sub["code"], sub["name"], sub["supplier"], sub["qty_used"],
                                    sub["station_count"], sub["lead_time"]], axis=1),
            "hovertemplate": "<b>%{customdata[0]} · %{customdata[1]}</b><br>Supplier: %{customdata[2]}"
                             "<br>Lead time: %{customdata[5]}<br>Unit cost: %{y:,.0f} €"
                             "<br>Used %{customdata[3]}× on %{customdata[4]} station(s)<extra></extra>",
        })
    return {"data": traces, "layout": layout(
        showlegend=True, xaxis={"title": {"text": "Max supply lead time (days) — PLM"}},
        yaxis={"title": {"text": "Unit cost (€, log scale) — PLM"}, "type": "log"})}


def _supplier_chart(suppliers: pd.DataFrame) -> dict:
    total = suppliers["value"].sum()
    return {
        "data": [{"type": "bar", "orientation": "h", "y": suppliers["supplier"], "x": suppliers["value"],
                  "marker": {"color": C["s1"], "line": BAR_LINE},
                  "text": [f"{v / total * 100:.0f} %" for v in suppliers["value"]], "textposition": "outside",
                  "cliponaxis": False, "textfont": {"color": C["text2"], "size": 11},
                  "customdata": np.stack([suppliers["lead"], suppliers["refs"], suppliers["stations"]], axis=1),
                  "hovertemplate": "<b>%{y}</b><br>%{x:,.0f} € consumed<br>Max lead time: %{customdata[0]:.0f} d"
                                   "<br>%{customdata[1]} refs · %{customdata[2]} dependent stations<extra></extra>"}],
        "layout": layout(margin={"l": 200, "r": 50}, yaxis={"automargin": True}, bargap=0.3,
                         xaxis={"title": {"text": "Value consumed on the line (€) — PLM × MES"}, "type": "log"}),
    }


def _top_table(parts: pd.DataFrame) -> str:
    top = parts.sort_values("risk_score", ascending=False).head(10)
    df = pd.DataFrame({
        "Ref.": top["code"], "Name": top["name"], "Supplier": top["supplier"], "Criticality": top["criticality"],
        "Max lead (d)": top["max_lead_days"], "Dependent stations": top["station_count"],
        "Avg station overrun": top["avg_overrun_pct"], "Risk score": top["risk_score"],
    })
    return table(df, {
        "Max lead (d)": lambda v: f"{v:.0f}",
        "Avg station overrun": lambda v: f"+{v:.0f} %" if pd.notna(v) else "–",
        "Risk score": lambda v: f"{v:.0f}",
    }, bar_col="Risk score")


def _insights(parts: pd.DataFrame, suppliers: pd.DataFrame) -> str:
    total = suppliers["value"].sum()
    biggest = suppliers.sort_values("value", ascending=False).iloc[0]
    critical_long = parts[(parts["crit_weight"] >= 3) & (parts["max_lead_days"] >= LONG_LEAD_DAYS)]
    return insights([
        f"<b>{esc(biggest['supplier'])}</b> accounts for {biggest['value'] / total * 100:.0f} % of the consumed value "
        f"with lead times up to {biggest['lead']:.0f} days: a strong concentration of risk on a single supplier.",
        f"<b>{len(critical_long)} references</b> combine High/Critical criticality and a lead time ≥ "
        f"{LONG_LEAD_DAYS} days: " + ", ".join(esc(c) for c in critical_long["code"])
        + " → safety stock or dual sourcing recommended.",
        "Risk score = criticality × relative lead time × number of stations depending on the part (0-100).",
    ])
