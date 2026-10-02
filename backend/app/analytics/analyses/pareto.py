"""Pareto of incident families and recurring root causes."""

import numpy as np
import pandas as pd

from app.analytics.classification import root_cause_themes
from app.analytics.constants import COLORS as C
from app.analytics.model import Model
from app.analytics.rendering.components import card, grid, insights
from app.analytics.rendering.formatters import esc
from app.analytics.rendering.layout import BAR_LINE, layout
from app.analytics.rendering.page import page

TRANSPARENT = "rgba(0,0,0,0)"


def render(model: Model) -> str:
    ops = model.ops
    families = family_pareto(ops)
    themes = theme_counts(ops)

    body = (
        _insights(families, themes)
        + card("Pareto of incident families (lost minutes)",
               "Dark bars = the families that make up 80 % of the delay (the “vital few”). "
               "Free-text MES incidents are grouped by keyword.", "fig_p", height=440)
        + grid(
            card("Where do incidents happen? (family × step)", "Lost minutes per family and step.",
                 "fig_h", height=480),
            card("Recurring root causes", "Themes extracted from the “Cause Potentielle” column.",
                 "fig_c", height=480),
        )
    )
    return page("Pareto of incidents & root causes",
                "Identifies the few incident families that cause most of the delay (80/20 rule), then their root "
                "causes, with the impact in € (ERP) and in parts value (PLM).",
                ["MES", "PLM", "ERP"], body,
                {"fig_p": _pareto_chart(families), "fig_h": _heatmap(ops, families), "fig_c": _theme_chart(themes)})


def family_pareto(ops: pd.DataFrame) -> pd.DataFrame:
    fam = ops.groupby("incident_family").agg(
        minutes=("overrun_min", "sum"), count=("station", "count"),
        overrun_cost=("labour_overrun_cost", "sum"), value=("parts_value", "sum"),
    ).reset_index().sort_values("minutes", ascending=False).reset_index(drop=True)
    fam["cum_pct"] = fam["minutes"].cumsum() / fam["minutes"].sum() * 100
    # "vital few": the families needed to reach 80 %
    fam["vital"] = fam.index < int((fam["cum_pct"] < 80).sum()) + 1
    return fam


def theme_counts(ops: pd.DataFrame) -> pd.DataFrame:
    rows = [{"theme": theme, "minutes": r["overrun_min"]}
            for _, r in ops.iterrows() for theme in root_cause_themes(r["root_cause"])]
    themes = pd.DataFrame(rows).groupby("theme").agg(minutes=("minutes", "sum"), count=("minutes", "size"))
    return themes.reset_index().sort_values("minutes")


def _pareto_chart(fam: pd.DataFrame) -> dict:
    return {
        "data": [{
            "type": "bar", "x": fam["incident_family"], "y": fam["minutes"],
            "marker": {"color": [C["seq_dark"] if v else C["seq_light"] for v in fam["vital"]], "line": BAR_LINE},
            "text": [f"{c:.0f} % cumulative" for c in fam["cum_pct"]], "textposition": "outside",
            "textfont": {"color": C["text2"], "size": 11}, "cliponaxis": False,
            "customdata": np.stack([fam["count"], fam["overrun_cost"], fam["value"]], axis=1),
            "hovertemplate": "<b>%{x}</b><br>%{y:.0f} min lost · %{customdata[0]} operations"
                             "<br>Labour overrun: %{customdata[1]:,.0f} €<br>Parts affected: "
                             "%{customdata[2]:,.0f} €<extra></extra>",
        }],
        "layout": layout(margin={"b": 120, "t": 30}, yaxis={"title": {"text": "Lost minutes (MES)"}},
                         xaxis={"tickangle": -20, "automargin": True}, bargap=0.3),
    }


def _heatmap(ops: pd.DataFrame, fam: pd.DataFrame) -> dict:
    pivot = ops.pivot_table(index="incident_family", columns="step", values="overrun_min",
                            aggfunc="sum", fill_value=0).loc[fam["incident_family"]]
    scale = [[i / (len(C["seq"]) - 1), c] for i, c in enumerate(C["seq"])]
    return {
        "data": [{"type": "heatmap", "z": pivot.values.round(1), "x": list(pivot.columns), "y": list(pivot.index),
                  "colorscale": scale, "xgap": 2, "ygap": 2,
                  "colorbar": {"title": {"text": "min"}, "thickness": 10},
                  "hovertemplate": "<b>%{y}</b><br>%{x}<br>%{z:.0f} min lost<extra></extra>"}],
        "layout": layout(margin={"l": 250, "b": 170, "t": 10},
                         xaxis={"tickangle": -40, "gridcolor": TRANSPARENT},
                         yaxis={"autorange": "reversed", "gridcolor": TRANSPARENT}),
    }


def _theme_chart(themes: pd.DataFrame) -> dict:
    return {
        "data": [{"type": "bar", "orientation": "h", "y": themes["theme"], "x": themes["count"],
                  "marker": {"color": C["s1"], "line": BAR_LINE}, "customdata": themes["minutes"],
                  "hovertemplate": "<b>%{y}</b><br>Cited in %{x} operations<br>"
                                   "%{customdata:.0f} min of related delay<extra></extra>"}],
        "layout": layout(margin={"l": 240}, xaxis={"title": {"text": "Number of operations citing the cause"}},
                         yaxis={"automargin": True}, bargap=0.3),
    }


def _insights(fam: pd.DataFrame, themes: pd.DataFrame) -> str:
    vital = fam[fam["vital"]]
    top = themes.sort_values("count", ascending=False).iloc[0]
    return insights([
        f"<b>{len(vital)} incident families out of {len(fam)}</b> explain ~80 % of the lost minutes: "
        + ", ".join(f"<b>{esc(f)}</b>" for f in vital["incident_family"]) + ".",
        f"Most cited root cause: <b>{esc(top['theme'])}</b> ({int(top['count'])} operations). "
        "A targeted preventive maintenance / modernisation plan would have the widest effect.",
        "The heatmap shows whether a family is concentrated on one step (local action) "
        "or spread across the line (cross-cutting action).",
    ])
