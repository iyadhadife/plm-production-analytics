"""MES side of the model: one row per operation, enriched with its parts and team."""

import pandas as pd

from app.analytics.classification import incident_family
from app.analytics.constants import CRITICALITY_WEIGHT, HIGH_CRITICALITY, NO_PARTS
from app.processing import columns as col
from app.processing.parsing import to_minutes, to_time


def build_operations(mes: pd.DataFrame, plm: pd.DataFrame, teams: pd.DataFrame):
    """Return (ops, consumption) where consumption has one row per consumed part."""
    ops = _base_operations(mes)
    consumption = _consumption(ops, plm)
    ops = ops.merge(_parts_by_station(consumption), on="station", how="left")
    ops = ops.merge(teams, on="station", how="left")

    ops["parts_value"] = ops["parts_value"].fillna(0)
    ops["max_criticality"] = ops["max_criticality"].fillna(NO_PARTS)
    ops["planned_labour_cost"] = ops["team_hourly_cost"] * ops["planned_min"] / 60
    ops["actual_labour_cost"] = ops["team_hourly_cost"] * ops["actual_min"] / 60
    ops["labour_overrun_cost"] = ops["actual_labour_cost"] - ops["planned_labour_cost"]
    # exposure: value of the parts tied up x hours of delay (EUR.h)
    ops["exposure_eur_h"] = ops["parts_value"] * ops["overrun_min"] / 60
    ops["label"] = "S" + ops["station"].astype(str).str.zfill(2) + " · " + ops["step"].astype(str)
    return ops, consumption[["station", "step", "code"]]


def _base_operations(mes: pd.DataFrame) -> pd.DataFrame:
    ops = pd.DataFrame({
        "station": mes[col.MES_STATION],
        "step": mes[col.MES_STEP],
        "references": mes[col.MES_REFERENCES],
        "incident": mes[col.MES_INCIDENT],
        "root_cause": mes[col.MES_ROOT_CAUSE],
        "planned_min": mes[col.MES_PLANNED_TIME].apply(to_minutes),
        "actual_min": mes[col.MES_ACTUAL_TIME].apply(to_minutes),
    })
    ops["overrun_min"] = ops["actual_min"] - ops["planned_min"]
    ops["overrun_pct"] = ops["overrun_min"] / ops["planned_min"] * 100

    dates = pd.to_datetime(mes[col.MES_DATE])
    times = mes[col.MES_START_TIME].apply(to_time)
    ops["start"] = [pd.Timestamp.combine(d.date(), t) if t else pd.NaT for d, t in zip(dates, times)]
    ops["end"] = ops["start"] + pd.to_timedelta(ops["actual_min"], unit="m")
    ops["incident_family"] = ops["incident"].apply(incident_family)
    return ops


def _consumption(ops: pd.DataFrame, plm: pd.DataFrame) -> pd.DataFrame:
    long = ops[["station", "step", "references"]].copy()
    long["code"] = long["references"].fillna("").astype(str).str.split(";")
    long = long.explode("code")
    long["code"] = long["code"].str.strip()
    return long[long["code"] != ""].merge(plm, on="code", how="left")


def _parts_by_station(consumption: pd.DataFrame) -> pd.DataFrame:
    agg = consumption.groupby("station").agg(
        parts_value=("unit_cost", "sum"),
        mass_kg=("mass_kg", "sum"),
        max_crit_weight=("crit_weight", "max"),
        max_lead_days=("max_lead_days", "max"),
        ref_count=("code", "nunique"),
        critical_parts=("criticality", lambda s: int(s.isin(HIGH_CRITICALITY).sum())),
        cad_hours=("cad_hours", "sum"),
        suppliers=("supplier", lambda s: ", ".join(sorted(set(s.dropna())))),
        parts=("code", lambda s: ", ".join(f"{c}×{n}" for c, n in s.value_counts().items())),
    ).reset_index()
    by_weight = {w: label for label, w in CRITICALITY_WEIGHT.items()}
    agg["max_criticality"] = agg["max_crit_weight"].map(by_weight)
    return agg
