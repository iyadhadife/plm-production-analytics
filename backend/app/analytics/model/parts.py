"""PLM side of the model: parts, their consumption on the line and a supply risk score."""

import pandas as pd

from app.analytics.constants import CRITICALITY_LABELS, CRITICALITY_WEIGHT
from app.processing import columns as col
from app.processing.parsing import parse_lead_time_days


def prepare_plm(plm: pd.DataFrame) -> pd.DataFrame:
    p = pd.DataFrame({
        "code": plm[col.PLM_CODE].astype(str).str.strip(),
        "name": plm[col.PLM_NAME],
        "supplier": plm[col.PLM_SUPPLIER],
        "lead_time": plm[col.PLM_LEAD_TIME],
        "criticality": plm[col.PLM_CRITICALITY].map(CRITICALITY_LABELS).fillna(plm[col.PLM_CRITICALITY]),
        "mass_kg": plm[col.PLM_MASS],
        "unit_cost": plm[col.PLM_UNIT_COST],
        "cad_hours": plm[col.PLM_CAD_HOURS],
    })
    p["max_lead_days"] = p["lead_time"].apply(parse_lead_time_days)
    p["crit_weight"] = p["criticality"].map(CRITICALITY_WEIGHT).fillna(0)
    return p.drop_duplicates("code")


def build_parts(plm: pd.DataFrame, consumption: pd.DataFrame, ops: pd.DataFrame) -> pd.DataFrame:
    """`consumption` has one row per (station, step, consumed part code)."""
    usage = consumption.groupby("code").agg(
        qty_used=("station", "size"),
        station_count=("station", "nunique"),
        steps=("step", lambda s: ", ".join(sorted(set(s)))),
    ).reset_index()
    # average overrun of the operations that use the part
    overrun = consumption.merge(ops[["station", "overrun_pct"]], on="station").groupby("code")["overrun_pct"].mean()

    parts = plm.merge(usage, on="code", how="left")
    parts["avg_overrun_pct"] = parts["code"].map(overrun)
    parts[["qty_used", "station_count"]] = parts[["qty_used", "station_count"]].fillna(0).astype(int)
    parts["used_value"] = parts["qty_used"] * parts["unit_cost"]

    # Supply risk score (0-100) = criticality x relative lead time x dependency (number of stations).
    max_days = parts["max_lead_days"].max() or 1
    max_stations = max(parts["station_count"].max(), 1)
    parts["risk_score"] = (
        (parts["crit_weight"] / 4) * (parts["max_lead_days"] / max_days)
        * (0.5 + 0.5 * parts["station_count"] / max_stations) * 100
    ).round(1)
    return parts
