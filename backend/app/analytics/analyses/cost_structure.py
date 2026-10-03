"""Cost structure: parts vs labour per step, supplier/part breakdown and cost density."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C, CRITICALITY_COLOR, CRITICALITY_ORDER
from app.analytics.model import Model
from app.analytics.rendering.components import card, grid, insights, kpis, table
from app.analytics.rendering.formatters import esc, fmt_eur, fmt_eur_short, fmt_int
from app.analytics.rendering.layout import BAR_LINE, bubble_sizes, layout
from app.analytics.rendering.page import page


def render(model: Model) -> str:
    ops, parts = model.ops, model.parts[model.parts["qty_used"] > 0].copy()
    steps = _cost_by_step(ops)

    body = (
        _kpis(ops, parts) + _insights(ops, steps, parts)
        + card("Cost of each assembly step", "Parts (PLM) + planned labour + labour overrun (ERP hourly cost × MES "
               "time). Log scale: parts dominate by several orders of magnitude.", "fig_s",
               height=max(440, 24 * len(steps)))
        + grid(
            card("Where the money goes: supplier → part", "Value consumed on the line (PLM cost × MES quantity). "
                 "Click a supplier to zoom in.", "fig_t", height=480),
            card("Cost density of the parts", "Unit cost vs mass (log scales); colour = PLM criticality, size = quantity used. "
                 "Top left: expensive per kg (engines, electronics).", "fig_d", height=480),
        )
        + card("Top 10 parts by consumed value", inner=_top_parts(parts))
    )
    return page("Cost structure — parts vs labour",
                "Breaks down the cost of one aircraft: purchased parts (PLM) and labour (ERP hourly cost × MES time), "
                "step by step and supplier by supplier.",
                ["MES", "PLM", "ERP"], body,
                {"fig_s": _step_chart(steps), "fig_t": _treemap(parts), "fig_d": _density(parts)})


def _cost_by_step(ops: pd.DataFrame) -> pd.DataFrame:
    steps = ops.groupby("step").agg(
        parts=("parts_value", "sum"), planned_labour=("planned_labour_cost", "sum"),
        overrun_labour=("labour_overrun_cost", "sum"), count=("station", "count"),
    ).reset_index()
    steps["total"] = steps[["parts", "planned_labour", "overrun_labour"]].sum(axis=1)
    return steps.sort_values("total")


def _kpis(ops: pd.DataFrame, parts: pd.DataFrame) -> str:
    parts_cost = ops["parts_value"].sum()
    labour = ops["actual_labour_cost"].sum()
    total = parts_cost + labour
    mass = (parts["qty_used"] * parts["mass_kg"]).sum()
    return kpis([
        ("Cost of one aircraft", fmt_eur_short(total), "parts + actual labour"),
        ("Purchased parts", fmt_eur_short(parts_cost), f"{parts_cost / total * 100:.2f} % of the total"),
        ("Actual labour", fmt_eur(labour), f"{labour / total * 100:.2f} % of the total"),
        ("Labour overrun", fmt_eur(ops["labour_overrun_cost"].sum()),
         f"+{ops['labour_overrun_cost'].sum() / ops['planned_labour_cost'].sum() * 100:.0f} % vs planned labour"),
        ("Assembled mass", f"{fmt_int(mass)} kg", f"{fmt_eur(parts_cost / mass)} per kg" if mass else ""),
        ("Design effort", f"{fmt_int(parts['cad_hours'].sum())} h", "PLM CAD hours of the parts used"),
    ])


def _step_chart(steps: pd.DataFrame) -> dict:
    def bar(name, column, color):
        return {"type": "bar", "orientation": "h", "name": name, "y": steps["step"], "x": steps[column],
                "marker": {"color": color, "line": BAR_LINE},
                "hovertemplate": f"<b>%{{y}}</b><br>{name}: %{{x:,.0f}} €<extra></extra>"}

    return {
        "data": [bar("Parts (PLM)", "parts", C["s1"]), bar("Planned labour", "planned_labour", C["s3"]),
                 bar("Labour overrun", "overrun_labour", C["s2"])],
        "layout": layout(showlegend=True, barmode="group", bargap=0.2, margin={"l": 280},
                         xaxis={"type": "log", "title": {"text": "€ (log scale)"}}, yaxis={"automargin": True}),
    }


def _treemap(parts: pd.DataFrame) -> dict:
    suppliers = parts.groupby("supplier")["used_value"].sum()
    ids = ["root"] + [f"s:{s}" for s in suppliers.index] + [f"p:{c}" for c in parts["code"]]
    labels = ["All suppliers"] + list(suppliers.index) + [f"{c} · {n}" for c, n in zip(parts["code"], parts["name"])]
    parents = [""] + ["root"] * len(suppliers) + [f"s:{s}" for s in parts["supplier"]]
    values = [suppliers.sum()] + list(suppliers.values) + list(parts["used_value"])
    colors = ([C["surface"]] + [C["seq"][4]] * len(suppliers)
              + [CRITICALITY_COLOR.get(c, C["muted"]) for c in parts["criticality"]])
    return {
        "data": [{"type": "treemap", "ids": ids, "labels": labels, "parents": parents, "values": values,
                  "branchvalues": "total", "marker": {"colors": colors, "line": {"color": C["surface"], "width": 1}},
                  "textinfo": "label+percent root", "maxdepth": 2,
                  "hovertemplate": "<b>%{label}</b><br>%{value:,.0f} €<br>%{percentRoot:.1%} of the total"
                                   "<extra></extra>"}],
        "layout": layout(margin={"l": 4, "r": 4, "t": 4, "b": 4}),
    }


def _density(parts: pd.DataFrame) -> dict:
    data = parts[(parts["mass_kg"] > 0) & (parts["unit_cost"] > 0)]
    _, ref = bubble_sizes(data["qty_used"], 36)
    traces = []
    for crit in CRITICALITY_ORDER:
        sub = data[data["criticality"] == crit]
        if sub.empty:
            continue
        sizes, _ = bubble_sizes(sub["qty_used"], 36)
        traces.append({
            "type": "scatter", "mode": "markers", "name": crit, "x": sub["mass_kg"], "y": sub["unit_cost"],
            "marker": {"size": sizes, "sizemode": "area", "sizeref": ref, "sizemin": 6,
                       "color": CRITICALITY_COLOR[crit], "opacity": 0.85, "line": BAR_LINE},
            "customdata": np.stack([sub["code"], sub["name"], sub["unit_cost"] / sub["mass_kg"], sub["qty_used"]],
                                   axis=1),
            "hovertemplate": "<b>%{customdata[0]} · %{customdata[1]}</b><br>%{x:,.1f} kg · %{y:,.0f} €"
                             "<br>%{customdata[2]:,.0f} €/kg · used %{customdata[3]}×<extra></extra>",
        })
    return {"data": traces, "layout": layout(
        showlegend=True, xaxis={"type": "log", "title": {"text": "Mass (kg, log) — PLM"}},
        yaxis={"type": "log", "title": {"text": "Unit cost (€, log) — PLM"}})}


def _top_parts(parts: pd.DataFrame) -> str:
    top = parts.sort_values("used_value", ascending=False).head(10)
    total = parts["used_value"].sum()
    df = pd.DataFrame({
        "Ref.": top["code"], "Name": top["name"], "Supplier": top["supplier"], "Criticality": top["criticality"],
        "Qty used": top["qty_used"], "Unit cost": top["unit_cost"], "€/kg": top["unit_cost"] / top["mass_kg"],
        "Share": top["used_value"] / total * 100, "Consumed value": top["used_value"],
    })
    return table(df, {"Unit cost": fmt_eur, "€/kg": fmt_int, "Share": lambda v: f"{v:.1f} %",
                      "Consumed value": fmt_eur}, bar_col="Consumed value")


def _insights(ops: pd.DataFrame, steps: pd.DataFrame, parts: pd.DataFrame) -> str:
    top_step = steps.sort_values("total", ascending=False).iloc[0]
    ranked = parts.sort_values("used_value", ascending=False)
    cum = ranked["used_value"].cumsum() / ranked["used_value"].sum()
    n80 = int((cum < 0.8).sum()) + 1
    overrun_step = steps.sort_values("overrun_labour", ascending=False).iloc[0]
    return insights([
        f"<b>{n80} references out of {len(parts)}</b> make up 80 % of the parts value: cost reduction and "
        f"negotiation efforts should focus on them ({', '.join(esc(c) for c in ranked['code'].head(n80))}).",
        f"The <b>{esc(top_step['step'])}</b> step is the most expensive ({fmt_eur_short(top_step['total'])}).",
        f"Labour is marginal next to parts, but its overrun is concentrated on <b>{esc(overrun_step['step'])}</b> "
        f"({fmt_eur(overrun_step['overrun_labour'])}): reducing delays there has the best labour payback.",
    ])
