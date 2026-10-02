"""360° overview: KPIs, planned-vs-actual S-curve, delay by step, top exposure."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C, HIGH_CRITICALITY
from app.analytics.model import Model
from app.analytics.rendering.components import card, grid, insights, kpis, table
from app.analytics.rendering.formatters import esc, fmt_eur, fmt_eur_short, fmt_int, fmt_minutes
from app.analytics.rendering.layout import layout
from app.analytics.rendering.page import page


def render(model: Model) -> str:
    ops = model.ops.sort_values("start").copy()
    by_step = _delay_by_step(ops)
    top = ops.sort_values("exposure_eur_h", ascending=False).head(8)

    body = (
        _kpis(ops, model.staff) + _insights(ops, by_step, top)
        + grid(
            card("S-curve: cumulative planned vs actual time",
                 "The gap between the two curves is the schedule drift accumulated on the line.", "fig_s"),
            card("Delay by assembly step", "Hover a bar for parts value (PLM) and labour overrun (ERP).",
                 "fig_e", height=max(420, 22 * len(by_step))),
        )
        + card("Top 8 operations by exposure",
               "Exposure = value of the parts tied up (PLM) × hours of delay (MES). "
               "This is where a delay costs the most in locked-up cash.", inner=_top_table(top))
    )
    return page("360° overview — MES × PLM × ERP",
                "Overview linking actual execution (MES), part value and criticality (PLM) "
                "and teams and their costs (ERP).",
                ["MES", "PLM", "ERP"], body, {"fig_s": _s_curve(ops), "fig_e": _step_chart(by_step)})


def _kpis(ops: pd.DataFrame, staff: pd.DataFrame) -> str:
    planned, actual = ops["planned_min"].sum(), ops["actual_min"].sum()
    late = int((ops["overrun_min"] > 0).sum())
    return kpis([
        ("Actual vs planned time", fmt_minutes(actual),
         f"planned {fmt_minutes(planned)} · +{(actual / planned - 1) * 100:.0f} %"),
        ("Late operations", f"{late}/{len(ops)}", f"{late / len(ops) * 100:.0f} % of MES operations"),
        ("Labour overrun cost", fmt_eur(ops["labour_overrun_cost"].sum()), "ERP hourly cost × minutes of delay"),
        ("Parts value committed", fmt_eur_short(ops["parts_value"].sum()), "PLM purchase cost × MES references"),
        ("Operations with a critical part", str(int(ops["max_criticality"].isin(HIGH_CRITICALITY).sum())),
         "High or Critical criticality (PLM)"),
        ("Operators assigned", str(int(ops["operators"].sum())), f"{len(staff)} people in the ERP"),
    ])


def _s_curve(ops: pd.DataFrame) -> dict:
    cum_planned = ops["planned_min"].cumsum() / 60
    cum_actual = ops["actual_min"].cumsum() / 60
    x = list(range(1, len(ops) + 1))
    hover = [f"{esc(label)}<br>{start:%d/%m %H:%M}" for label, start in zip(ops["label"], ops["start"])]

    def line(name, y, color):
        return {"type": "scatter", "mode": "lines", "name": name, "x": x, "y": y,
                "line": {"color": color, "width": 2}, "customdata": hover,
                "hovertemplate": f"%{{customdata}}<br>{name}: %{{y:.1f}} h<extra></extra>"}

    drift = cum_actual.iloc[-1] - cum_planned.iloc[-1]
    return {
        "data": [line("Cumulative planned", cum_planned, C["s1"]), line("Cumulative actual", cum_actual, C["s2"])],
        "layout": layout(
            showlegend=True, hovermode="x unified",
            xaxis={"title": {"text": "Operations in chronological order (MES)"}},
            yaxis={"title": {"text": "Cumulative hours"}},
            annotations=[{"x": x[-1], "y": cum_actual.iloc[-1], "xanchor": "right", "yanchor": "bottom",
                          "text": f"+{drift:.1f} h drift", "showarrow": False,
                          "font": {"color": C["text"], "size": 12}}]),
    }


def _delay_by_step(ops: pd.DataFrame) -> pd.DataFrame:
    steps = ops.groupby("step").agg(
        delay=("overrun_min", "sum"), planned=("planned_min", "sum"), value=("parts_value", "sum"),
        overrun_cost=("labour_overrun_cost", "sum"), count=("station", "count"),
    ).reset_index()
    steps["delay_pct"] = steps["delay"] / steps["planned"] * 100
    return steps.sort_values("delay")


def _step_chart(steps: pd.DataFrame) -> dict:
    return {
        "data": [{
            "type": "bar", "orientation": "h", "y": steps["step"], "x": steps["delay"],
            "marker": {"color": C["s1"], "line": {"color": C["surface"], "width": 1}},
            "customdata": np.stack([steps["delay_pct"], steps["value"], steps["overrun_cost"], steps["count"]], axis=1),
            "hovertemplate": "<b>%{y}</b><br>%{x:.0f} min of delay (+%{customdata[0]:.0f} %)"
                             "<br>%{customdata[3]} operation(s)<br>Parts value: %{customdata[1]:,.0f} €"
                             "<br>Labour overrun: %{customdata[2]:,.0f} €<extra></extra>",
        }],
        "layout": layout(margin={"l": 280}, xaxis={"title": {"text": "Cumulative minutes of delay"}},
                         yaxis={"automargin": True}, bargap=0.25),
    }


def _top_table(top: pd.DataFrame) -> str:
    df = pd.DataFrame({
        "Station": top["station"], "Step": top["step"], "Delay": top["overrun_min"],
        "Parts value": top["parts_value"], "Max criticality": top["max_criticality"],
        "Team (ERP)": top["levels"], "Exposure (€·h)": top["exposure_eur_h"],
    })
    return table(df, {"Delay": fmt_minutes, "Parts value": fmt_eur, "Exposure (€·h)": fmt_int},
                 bar_col="Exposure (€·h)")


def _insights(ops: pd.DataFrame, steps: pd.DataFrame, top: pd.DataFrame) -> str:
    planned, actual = ops["planned_min"].sum(), ops["actual_min"].sum()
    late = int((ops["overrun_min"] > 0).sum())
    worst = steps.sort_values("delay", ascending=False).iloc[0]
    first = top.iloc[0]
    return insights([
        f"The line has accumulated <b>{fmt_minutes(actual - planned)}</b> of drift "
        f"(+{(actual / planned - 1) * 100:.0f} %): <b>{late} operations out of {len(ops)}</b> exceed their "
        "planned time — the delay is systemic, not occasional.",
        f"The <b>{esc(worst['step'])}</b> step accounts for the most lost minutes ({worst['delay']:.0f} min).",
        f"The direct labour overrun stays small ({fmt_eur(ops['labour_overrun_cost'].sum())}), but delays tie up "
        f"high-value parts: station <b>{int(first['station'])}</b> ({esc(first['step'])}) holds "
        f"{fmt_eur(first['parts_value'])} of parts during {fmt_minutes(first['overrun_min'])} of delay.",
    ])
