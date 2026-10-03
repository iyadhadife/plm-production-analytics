"""Workforce: age pyramid, succession risk, certifications coverage and weekly rotations."""

import pandas as pd

from app.analytics.constants import COLORS as C
from app.analytics.model import Model
from app.analytics.model.staff import rotations
from app.analytics.rendering.components import card, grid, insights, kpis, table
from app.analytics.rendering.layout import BAR_LINE, layout
from app.analytics.rendering.page import page

LEVELS = ["Beginner", "Confirmed", "Expert"]
LEVEL_COLOR = {"Beginner": C["s2"], "Confirmed": C["s1"], "Expert": C["s3"]}
RETIREMENT_AGE = 55
AGE_BINS = [19, 25, 30, 35, 40, 45, 50, 55, 61]


def render(model: Model) -> str:
    staff = model.staff
    stations = _station_risk(staff, model.ops)
    rot = rotations(staff)

    figures = {"fig_a": _age_pyramid(staff), "fig_c": _certifications(staff)}
    rotation_card = ""
    if not rot.empty:
        figures["fig_r"] = _rotation_heatmap(rot)
        rotation_card = card("Weekly rotations (ERP)", "Operators rotating onto each station, week by week. "
                             "Gaps = stations that never receive reinforcement.", "fig_r", height=360)

    body = (
        _kpis(staff, stations) + _insights(staff, stations, rot)
        + grid(
            card("Age pyramid by experience level", f"Dashed line = {RETIREMENT_AGE} years: experts beyond it will "
                 "leave within ten years.", "fig_a", height=420),
            card("Certifications coverage", "Operators holding each certification (ERP « Habilitations »).",
                 "fig_c", height=420),
        )
        + rotation_card
        + card("Stations with a succession or skills risk",
               "Home teams with no expert, or whose experts are all close to retirement, ranked by overrun (MES).",
               inner=_risk_table(stations))
    )
    return page("Workforce & succession risk",
                "Who builds the aircraft: age and experience of the operators (ERP), certifications, rotations, "
                "and the stations where know-how could be lost, linked to their performance (MES).",
                ["ERP", "MES"], body, figures)


def _station_risk(staff: pd.DataFrame, ops: pd.DataFrame) -> pd.DataFrame:
    teams = staff.dropna(subset=["station"]).groupby("station").agg(
        operators=("id", "count"),
        experts=("level", lambda s: int((s == "Expert").sum())),
        avg_age=("age", "mean"),
    )
    seniors = staff[(staff["level"] == "Expert") & (staff["age"] >= RETIREMENT_AGE)].groupby("station").size()
    teams["senior_experts"] = seniors.reindex(teams.index).fillna(0).astype(int)
    teams = teams.reset_index()
    teams["station"] = teams["station"].astype(int)
    teams = teams.merge(ops[["station", "step", "overrun_pct"]], on="station", how="left")
    teams["risk"] = "OK"
    teams.loc[(teams["experts"] > 0) & (teams["experts"] == teams["senior_experts"]), "risk"] = "Experts near retirement"
    teams.loc[teams["experts"] == 0, "risk"] = "No expert"
    return teams


def _kpis(staff: pd.DataFrame, stations: pd.DataFrame) -> str:
    seniors = int((staff["age"] >= RETIREMENT_AGE).sum())
    experts = staff[staff["level"] == "Expert"]
    return kpis([
        ("Headcount", str(len(staff)), f"{staff['station'].nunique()} home stations"),
        ("Average age", f"{staff['age'].mean():.0f} yrs", f"{seniors} operators aged {RETIREMENT_AGE}+"),
        ("Experts", f"{len(experts) / len(staff) * 100:.0f} %",
         f"{int((experts['age'] >= RETIREMENT_AGE).sum())} of them aged {RETIREMENT_AGE}+"),
        ("Average hourly cost", f"{staff['hourly_cost'].mean():.2f} €", "ERP"),
        ("Stations without expert", str(int((stations["risk"] == "No expert").sum())), "home team only"),
        ("Qualifications", str(staff["qualification"].nunique()), "distinct ERP job titles"),
    ])


def _age_pyramid(staff: pd.DataFrame) -> dict:
    labels = [f"{lo + 1}-{hi}" for lo, hi in zip(AGE_BINS[:-1], AGE_BINS[1:])]
    bands = pd.cut(staff["age"], AGE_BINS, labels=labels)
    counts = pd.crosstab(bands, staff["level"]).reindex(index=labels, columns=LEVELS, fill_value=0)
    traces = [{"type": "bar", "name": level, "x": labels, "y": counts[level],
               "marker": {"color": LEVEL_COLOR[level], "line": BAR_LINE},
               "hovertemplate": f"<b>%{{x}} yrs</b><br>{level}: %{{y}}<extra></extra>"} for level in LEVELS]
    # boundary between the band ending at RETIREMENT_AGE and the next one (categorical axis positions)
    retirement = AGE_BINS.index(RETIREMENT_AGE) - 0.5
    shapes = [{"type": "line", "x0": retirement, "x1": retirement, "yref": "paper", "y0": 0, "y1": 1,
               "line": {"color": C["muted"], "dash": "dash"}}]
    return {"data": traces, "layout": layout(
        showlegend=True, barmode="stack", bargap=0.2, shapes=shapes,
        xaxis={"title": {"text": "Age band"}}, yaxis={"title": {"text": "Operators"}})}


def _certifications(staff: pd.DataFrame) -> dict:
    certs = staff[["level", "certifications"]].dropna(subset=["certifications"]).copy()
    certs["cert"] = certs["certifications"].astype(str).str.replace(" Certifié", "", regex=False).str.split(",")
    certs = certs.explode("cert", ignore_index=True)
    certs["cert"] = certs["cert"].str.strip()
    certs = certs[certs["cert"] != ""]
    by_level = pd.crosstab(certs["cert"], certs["level"]).reindex(columns=LEVELS, fill_value=0)
    by_level = by_level.loc[by_level.sum(axis=1).sort_values().index]
    traces = [{"type": "bar", "orientation": "h", "name": level, "y": by_level.index, "x": by_level[level],
               "marker": {"color": LEVEL_COLOR[level], "line": BAR_LINE},
               "hovertemplate": f"<b>%{{y}}</b><br>{level}: %{{x}}<extra></extra>"} for level in LEVELS]
    return {"data": traces, "layout": layout(showlegend=True, barmode="stack", bargap=0.3, margin={"l": 120},
                                             xaxis={"title": {"text": "Certified operators"}},
                                             yaxis={"automargin": True})}


def _rotation_heatmap(rot: pd.DataFrame) -> dict:
    counts = rot.groupby(["week", "station"]).size().unstack(fill_value=0)
    stations = range(int(rot["station"].min()), int(rot["station"].max()) + 1)
    counts = counts.reindex(columns=stations, fill_value=0)
    return {
        "data": [{"type": "heatmap", "z": counts.values, "x": [f"S{s:02d}" for s in counts.columns],
                  "y": [f"Week {w}" for w in counts.index],
                  "colorscale": [[i / (len(C["seq"]) - 1), c] for i, c in enumerate(C["seq"])],
                  "xgap": 2, "ygap": 2, "colorbar": {"title": {"text": "ops"}, "thickness": 10},
                  "hovertemplate": "<b>%{x}</b> · %{y}<br>%{z} rotating operator(s)<extra></extra>"}],
        "layout": layout(margin={"l": 70, "b": 60}, xaxis={"gridcolor": "rgba(0,0,0,0)", "tickangle": -60,
                                                           "tickfont": {"size": 9}},
                         yaxis={"gridcolor": "rgba(0,0,0,0)", "autorange": "reversed"}),
    }


def _risk_table(stations: pd.DataFrame) -> str:
    risky = stations[stations["risk"] != "OK"].sort_values("overrun_pct", ascending=False)
    if risky.empty:
        return '<p class="note">Every home team has at least one expert below retirement age.</p>'
    df = pd.DataFrame({
        "Station": risky["station"], "Step": risky["step"].fillna("–"), "Risk": risky["risk"],
        "Operators": risky["operators"], "Experts": risky["experts"], "Avg age": risky["avg_age"],
        "Overrun": risky["overrun_pct"],
    })
    return table(df, {"Avg age": lambda v: f"{v:.0f}",
                      "Overrun": lambda v: f"+{v:.0f} %" if pd.notna(v) else "–"}, bar_col="Overrun")


def _insights(staff: pd.DataFrame, stations: pd.DataFrame, rot: pd.DataFrame) -> str:
    experts = staff[staff["level"] == "Expert"]
    senior_share = (experts["age"] >= RETIREMENT_AGE).mean() * 100 if len(experts) else 0
    no_expert = stations[stations["risk"] == "No expert"]
    by_risk = stations.groupby(stations["risk"] == "No expert")["overrun_pct"].median()
    lines = [
        f"<b>{senior_share:.0f} % of the experts</b> are aged {RETIREMENT_AGE} or more: plan tutoring and "
        "knowledge transfer to Confirmed operators now.",
        f"<b>{len(no_expert)} station(s)</b> have no expert in their home team"
        + (f": {', '.join(f'S{int(s):02d}' for s in no_expert['station'].head(12))}." if len(no_expert) else "."),
    ]
    if True in by_risk.index and False in by_risk.index:
        lines.append(f"Median overrun without an expert: <b>+{by_risk[True]:.0f} %</b> vs +{by_risk[False]:.0f} % "
                     "with at least one.")
    if not rot.empty:
        covered = rot["station"].nunique()
        lines.append(f"Rotations cover <b>{covered} stations</b> over {rot['week'].nunique()} weeks "
                     f"({len(rot)} assignments): use them to bring experts onto the stations listed below.")
    return insights(lines)

