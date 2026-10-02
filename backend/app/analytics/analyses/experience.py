"""Does team experience (ERP) explain the overruns measured in the MES?"""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C
from app.analytics.model import Model
from app.analytics.rendering.components import card, grid, insights
from app.analytics.rendering.formatters import esc
from app.analytics.rendering.layout import BAR_LINE, layout
from app.analytics.rendering.page import page

PROFILES = ["With ≥1 beginner", "Confirmed / mixed", "Mostly experts"]
LEVELS = ["Beginner", "Confirmed", "Expert"]


def render(model: Model) -> str:
    ops = model.ops.dropna(subset=["avg_experience", "overrun_pct"]).copy()
    ops["profile"] = ops.apply(team_profile, axis=1)
    x, y = ops["avg_experience"].astype(float).values, ops["overrun_pct"].astype(float).values
    enough = len(ops) > 2
    r = float(np.corrcoef(x, y)[0, 1]) if enough else float("nan")
    slope, intercept = np.polyfit(x, y, 1) if enough else (0, 0)

    body = (
        _insights(ops, r, slope)
        + card("Team experience vs overrun", "Each point = one MES operation; the team comes from the ERP.",
               "fig_s", height=460)
        + grid(
            card("Overrun by team composition", "Boxes = median and quartiles; points = operations.",
                 "fig_b", height=420),
            card("Average hourly cost by level (ERP)", "Compare with the performance gain to decide on staffing.",
                 "fig_l", height=420),
        )
    )
    return page("Team experience vs performance",
                "Do more experienced teams hold their planned times better? Crosses the operators' profile (ERP) "
                "with the measured overruns (MES).", ["MES", "ERP"], body,
                {"fig_s": _scatter(ops, x, y, r, slope, intercept), "fig_b": _boxes(ops),
                 "fig_l": _cost_by_level(model.staff)})


def team_profile(row) -> str:
    if row["beginners"] > 0:
        return PROFILES[0]
    if row["experts"] >= row["operators"] / 2:
        return PROFILES[2]
    return PROFILES[1]


def _scatter(ops, x, y, r, slope, intercept) -> dict:
    xs = [float(x.min()), float(x.max())]
    jitter = np.random.default_rng(7).uniform(-0.03, 0.03, len(ops))
    return {
        "data": [
            {"type": "scatter", "mode": "markers", "name": "Operations", "x": x + jitter, "y": y,
             "marker": {"size": 10, "color": C["s1"], "opacity": 0.8, "line": BAR_LINE},
             "customdata": np.stack([ops["label"], ops["levels"], ops["team_hourly_cost"], x], axis=1),
             "hovertemplate": "<b>%{customdata[0]}</b><br>Overrun: +%{y:.0f} %<br>Team: %{customdata[1]}"
                              "<br>Average score: %{customdata[3]:.2f}<br>Team cost: %{customdata[2]:.2f} €/h"
                              "<extra></extra>"},
            {"type": "scatter", "mode": "lines", "name": "Trend", "x": xs, "y": [slope * v + intercept for v in xs],
             "line": {"color": C["s2"], "width": 2, "dash": "dash"}, "hoverinfo": "skip"},
        ],
        "layout": layout(
            showlegend=True,
            xaxis={"title": {"text": "Average team experience score (1 = Beginner · 3 = Expert) — ERP"}},
            yaxis={"title": {"text": "Overrun of planned time (%) — MES"}},
            annotations=[{"xref": "paper", "yref": "paper", "x": 1, "y": 1, "xanchor": "right", "showarrow": False,
                          "text": f"Pearson r = {r:.2f}", "font": {"color": C["text"], "size": 12}}]),
    }


def _boxes(ops: pd.DataFrame) -> dict:
    traces = []
    for profile, color in zip(PROFILES, [C["s1"], C["s2"], C["s3"]]):
        sub = ops[ops["profile"] == profile]
        if sub.empty:
            continue
        traces.append({"type": "box", "name": f"{profile} (n={len(sub)})", "y": sub["overrun_pct"],
                       "boxpoints": "all", "jitter": 0.4, "pointpos": 0, "marker": {"color": color, "size": 7},
                       "line": {"color": color, "width": 2}, "fillcolor": "rgba(0,0,0,0)",
                       "customdata": sub["label"], "hovertemplate": "%{customdata}<br>+%{y:.0f} %<extra></extra>"})
    return {"data": traces, "layout": layout(yaxis={"title": {"text": "Overrun (%)"}})}


def _cost_by_level(staff: pd.DataFrame) -> dict:
    lvl = staff.groupby("level").agg(cost=("hourly_cost", "mean"), n=("id", "count"),
                                     age=("age", "mean")).reindex(LEVELS)
    return {
        "data": [{"type": "bar", "x": list(lvl.index), "y": lvl["cost"].round(2),
                  "marker": {"color": C["s1"], "line": BAR_LINE},
                  "text": [f"{v:.2f} €/h" for v in lvl["cost"]], "textposition": "outside", "cliponaxis": False,
                  "textfont": {"color": C["text2"]}, "customdata": np.stack([lvl["n"], lvl["age"]], axis=1),
                  "hovertemplate": "<b>%{x}</b><br>%{y:.2f} €/h on average<br>%{customdata[0]} people · "
                                   "%{customdata[1]:.0f} years old on average<extra></extra>"}],
        "layout": layout(margin={"t": 30}, bargap=0.45,
                         yaxis={"title": {"text": "Average hourly cost (€)"}, "range": [0, float(lvl["cost"].max()) * 1.2]}),
    }


def _insights(ops: pd.DataFrame, r: float, slope: float) -> str:
    strength = "weak" if abs(r) < 0.3 else ("moderate" if abs(r) < 0.6 else "strong")
    if strength == "weak":
        first = (f"<b>No clear link</b> between experience and delay (r = {r:.2f}, slope {slope:+.1f} % points per "
                 "level): the home team's experience does not explain the overruns — the delay comes mostly from "
                 "incidents (see the Pareto).")
    else:
        direction = "decrease" if r < 0 else "increase"
        first = (f"<b>{strength.capitalize()}</b> correlation (r = {r:.2f}): as average experience rises, the overrun "
                 f"tends to {direction} ({slope:+.1f} % points per experience level).")
    lines = [first]
    medians = ops.groupby("profile")["overrun_pct"].median()
    if len(medians) > 1:
        lines.append("Median overrun by profile: "
                     + " · ".join(f"{esc(k)} <b>+{v:.0f} %</b>" for k, v in medians.items()) + ".")
    lines.append(f"With {len(ops)} operations, experience explains only part of the delay: cross-check with the "
                 "incident Pareto (equipment, environment) before reassigning teams.")
    lines.append("Home team = the ERP “Poste de montage” column (weekly rotations are ignored here).")
    return insights(lines)
