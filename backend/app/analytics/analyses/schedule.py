"""Schedule reliability: how good are the planned times, and when in the day does the line slip."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C
from app.analytics.model import Model
from app.analytics.rendering.components import card, grid, insights, kpis, table
from app.analytics.rendering.formatters import esc, fmt_minutes
from app.analytics.rendering.layout import BAR_LINE, layout
from app.analytics.rendering.page import page

SHIFT_END_HOUR = 17


def render(model: Model) -> str:
    ops = model.ops.dropna(subset=["start"]).sort_values("start").copy()
    ops["day"] = ops["start"].dt.date
    ops["hour"] = ops["start"].dt.hour
    ratio = ops["actual_min"].sum() / ops["planned_min"].sum()
    days = _by_day(ops, ratio)

    body = (
        _kpis(ops, days, ratio) + _insights(ops, days, ratio)
        + grid(
            card("Planned vs actual time per operation", "Dashed line = plan respected; solid line = the line's "
                 f"actual ratio (×{ratio:.2f}). Points sit on it: the plan is consistently optimistic.", "fig_p"),
            card("Distribution of overruns", "Number of operations per overrun band (MES).", "fig_h"),
        )
        + grid(
            card("Overrun by start hour", "Average overrun of the operations starting in each hour of the shift.",
                 "fig_t", height=380),
            card("End of day: planned vs actual", f"Last operation's end time each day; dotted line = "
                 f"{SHIFT_END_HOUR}:00 end of shift.", "fig_d", height=380),
        )
        + card("Planned times to re-baseline", "Steps whose standard time is the most underestimated: "
               "suggested standard = average actual time.", inner=_rebaseline(ops))
    )
    return page("Schedule reliability",
                "Are the MES standard times realistic? Compares planned and actual durations, looks at when in the "
                "day the line slips and suggests corrected standard times.",
                ["MES"], body,
                {"fig_p": _planned_vs_actual(ops, ratio), "fig_h": _histogram(ops),
                 "fig_t": _by_hour(ops), "fig_d": _day_chart(days)})


def _by_day(ops: pd.DataFrame, ratio: float) -> pd.DataFrame:
    days = ops.groupby("day").agg(first=("start", "min"), last_end=("end", "max"), planned=("planned_min", "sum"),
                                  actual=("actual_min", "sum"), count=("station", "count")).reset_index()
    days["planned_end"] = days["first"] + pd.to_timedelta(days["planned"], unit="m")
    shift_end = pd.to_datetime(days["day"]) + pd.Timedelta(hours=SHIFT_END_HOUR)
    days["overtime_min"] = ((days["last_end"] - shift_end).dt.total_seconds() / 60).clip(lower=0)
    return days


def _kpis(ops: pd.DataFrame, days: pd.DataFrame, ratio: float) -> str:
    within_10 = int((ops["overrun_pct"] <= 10).sum())
    return kpis([
        ("Actual / planned ratio", f"×{ratio:.2f}", "all operations"),
        ("Operations on time (≤ +10 %)", f"{within_10}/{len(ops)}", "MES"),
        ("Median overrun", f"+{ops['overrun_pct'].median():.0f} %",
         f"spread {ops['overrun_pct'].min():.0f}–{ops['overrun_pct'].max():.0f} %"),
        ("Worst operation", f"+{ops['overrun_min'].max():.0f} min", esc(ops.loc[ops["overrun_min"].idxmax(), "label"])),
        ("Overtime after 17:00", fmt_minutes(days["overtime_min"].sum()), f"over {len(days)} days"),
    ])


def _planned_vs_actual(ops: pd.DataFrame, ratio: float) -> dict:
    top = float(ops["actual_min"].max()) * 1.05
    return {
        "data": [
            {"type": "scatter", "mode": "lines", "name": "Plan respected", "x": [0, top], "y": [0, top],
             "line": {"color": C["muted"], "dash": "dash", "width": 1}, "hoverinfo": "skip"},
            {"type": "scatter", "mode": "lines", "name": f"Actual ratio ×{ratio:.2f}", "x": [0, top / ratio],
             "y": [0, top], "line": {"color": C["s2"], "width": 2}, "hoverinfo": "skip"},
            {"type": "scatter", "mode": "markers", "name": "Operations", "x": ops["planned_min"],
             "y": ops["actual_min"], "marker": {"size": 9, "color": C["s1"], "opacity": 0.8, "line": BAR_LINE},
             "customdata": np.stack([ops["label"], ops["overrun_pct"]], axis=1),
             "hovertemplate": "<b>%{customdata[0]}</b><br>Planned %{x:.0f} min · Actual %{y:.0f} min"
                              "<br>+%{customdata[1]:.0f} %<extra></extra>"},
        ],
        "layout": layout(showlegend=True, xaxis={"title": {"text": "Planned time (min)"}, "range": [0, top]},
                         yaxis={"title": {"text": "Actual time (min)"}, "range": [0, top]}),
    }


def _histogram(ops: pd.DataFrame) -> dict:
    return {
        "data": [{"type": "histogram", "x": ops["overrun_pct"], "xbins": {"size": 2.5},
                  "marker": {"color": C["s1"], "line": BAR_LINE},
                  "hovertemplate": "+%{x} %<br>%{y} operation(s)<extra></extra>"}],
        "layout": layout(bargap=0.05, xaxis={"title": {"text": "Overrun (%)"}},
                         yaxis={"title": {"text": "Operations"}}),
    }


def _by_hour(ops: pd.DataFrame) -> dict:
    hours = ops.groupby("hour").agg(overrun=("overrun_pct", "mean"), count=("station", "count")).reset_index()
    return {
        "data": [{"type": "bar", "x": [f"{h:02d}h" for h in hours["hour"]], "y": hours["overrun"],
                  "marker": {"color": C["s1"], "line": BAR_LINE}, "customdata": hours["count"],
                  "text": [f"+{v:.0f} %" for v in hours["overrun"]], "textposition": "outside", "cliponaxis": False,
                  "textfont": {"color": C["text2"], "size": 11},
                  "hovertemplate": "<b>%{x}</b><br>+%{y:.1f} % on average<br>%{customdata} operation(s)"
                                   "<extra></extra>"}],
        "layout": layout(bargap=0.35, margin={"t": 30}, yaxis={"title": {"text": "Average overrun (%)"}}),
    }


def _day_chart(days: pd.DataFrame) -> dict:
    labels = [f"{d:%d/%m}" for d in days["day"]]

    def clock(series):  # time of day on a common reference date, so days share one axis
        return [f"2000-01-01 {t:%H:%M:%S}" for t in series]

    return {
        "data": [
            {"type": "bar", "name": "Planned end", "x": labels, "y": clock(days["planned_end"]),
             "marker": {"color": C["seq"][1]}, "hovertemplate": "%{x} · planned end %{y|%H:%M}<extra></extra>"},
            {"type": "bar", "name": "Actual end", "x": labels, "y": clock(days["last_end"]),
             "marker": {"color": C["s2"]}, "hovertemplate": "%{x} · actual end %{y|%H:%M}<extra></extra>"},
        ],
        "layout": layout(
            showlegend=True, barmode="group", bargap=0.3,
            yaxis={"type": "date", "tickformat": "%H:%M", "range": ["2000-01-01 07:00", "2000-01-01 21:00"]},
            shapes=[{"type": "line", "xref": "paper", "x0": 0, "x1": 1,
                     "y0": f"2000-01-01 {SHIFT_END_HOUR}:00", "y1": f"2000-01-01 {SHIFT_END_HOUR}:00",
                     "line": {"color": C["muted"], "dash": "dot"}}]),
    }


def _rebaseline(ops: pd.DataFrame) -> str:
    steps = ops.groupby("step").agg(count=("station", "count"), planned=("planned_min", "mean"),
                                    actual=("actual_min", "mean"), overrun=("overrun_pct", "mean")).reset_index()
    steps = steps.sort_values("overrun", ascending=False).head(10)
    df = pd.DataFrame({
        "Step": steps["step"], "Operations": steps["count"], "Planned (avg)": steps["planned"],
        "Actual (avg)": steps["actual"], "Suggested standard": np.ceil(steps["actual"]),
        "Overrun": steps["overrun"],
    })
    return table(df, {"Planned (avg)": fmt_minutes, "Actual (avg)": fmt_minutes,
                      "Suggested standard": fmt_minutes, "Overrun": lambda v: f"+{v:.0f} %"}, bar_col="Overrun")


def _insights(ops: pd.DataFrame, days: pd.DataFrame, ratio: float) -> str:
    corr = ops["planned_min"].corr(ops["actual_min"])
    hours = ops.groupby("hour")["overrun_pct"].mean()
    worst_day = days.sort_values("overtime_min", ascending=False).iloc[0]
    return insights([
        (f"Actual and planned times are strongly correlated (r = {corr:.2f}) with a steady factor of "
         f"<b>×{ratio:.2f}</b>: the standards are systematically underestimated, not randomly wrong. "
         "Re-baselining them would make the schedule reliable." if corr >= 0.9 else
         f"Actual vs planned factor: <b>×{ratio:.2f}</b>, but with a weak correlation (r = {corr:.2f}): "
         "overruns come from incidents more than from the standards."),
        f"Overrun peaks for operations starting at <b>{hours.idxmax():02d}h</b> (+{hours.max():.0f} %) and is "
        f"lowest at {hours.idxmin():02d}h (+{hours.min():.0f} %).",
        f"<b>{worst_day['day']:%d/%m}</b> ends the latest, at {worst_day['last_end']:%H:%M} "
        f"vs {worst_day['planned_end']:%H:%M} planned.",
    ])
