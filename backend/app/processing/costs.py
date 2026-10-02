"""Part and labour cost aggregations shared by the step reports."""

import pandas as pd

from app.processing import columns as col
from app.processing.joins import (
    PART_CODE, PERSON_NAME, as_station, explode_references, expand_rotation, plm_by_part_code,
)
from app.processing.parsing import to_number, to_timedelta

PLANNED_TD = "planned_td"
UNIT_COST = "unit_cost"


def parts_with_cost(mes: pd.DataFrame, plm: pd.DataFrame) -> pd.DataFrame:
    """One row per consumed part with its numeric purchase cost in UNIT_COST."""
    parts = explode_references(mes)
    plm = plm_by_part_code(plm)
    keep = [c for c in (PART_CODE, col.PLM_UNIT_COST) if c in plm.columns]
    parts = parts.merge(plm[keep], on=PART_CODE, how="left")
    parts[UNIT_COST] = to_number(parts[col.PLM_UNIT_COST]) if col.PLM_UNIT_COST in parts else float("nan")
    return parts


def labour_by_person(mes: pd.DataFrame, erp: pd.DataFrame, group_by: list[str] | None = None) -> pd.DataFrame:
    """
    Planned hours and labour cost per operator (and per `group_by` columns).

    Operators are matched to MES operations through the weekly ERP rotation
    (an operator scheduled on a station works on every operation of that station).
    Columns: *group_by, person_name, hours, hourly_rate, level, cost.
    """
    group_by = group_by or []
    out_cols = [*group_by, PERSON_NAME, "hours", "hourly_rate", "level", "cost"]

    staff = expand_rotation(erp)
    if staff.empty or col.ERP_HOURLY_COST not in staff.columns:
        return pd.DataFrame(columns=out_cols)

    ops = mes.copy()
    ops[col.MES_STATION] = as_station(ops[col.MES_STATION])
    ops[PLANNED_TD] = ops[col.MES_PLANNED_TIME].apply(to_timedelta)

    staff_cols = [col.MES_STATION, PERSON_NAME, col.ERP_HOURLY_COST]
    if col.ERP_EXPERIENCE in staff.columns:
        staff_cols.append(col.ERP_EXPERIENCE)
    merged = ops.merge(staff[staff_cols], on=col.MES_STATION, how="left", suffixes=("", "_ERP"))
    merged["rate"] = to_number(merged[col.ERP_HOURLY_COST])
    merged = merged.dropna(subset=[*group_by, PERSON_NAME, PLANNED_TD, "rate"])
    if merged.empty:
        return pd.DataFrame(columns=out_cols)

    level_col = col.ERP_EXPERIENCE if col.ERP_EXPERIENCE in merged.columns else PERSON_NAME
    people = (
        merged.groupby([*group_by, PERSON_NAME])
        .agg(duration=(PLANNED_TD, "sum"), hourly_rate=("rate", "first"), level=(level_col, "first"))
        .reset_index()
    )
    if level_col == PERSON_NAME:
        people["level"] = ""
    people["hours"] = people["duration"].dt.total_seconds() / 3600
    people["cost"] = people["hours"] * people["hourly_rate"]
    return people[out_cols]
