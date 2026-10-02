"""ERP side of the model: operators and home teams per station."""

import pandas as pd

from app.analytics.constants import EXPERIENCE_SCORE
from app.processing import columns as col
from app.processing.columns import EXPERIENCE_LABELS


def build_staff(erp: pd.DataFrame) -> pd.DataFrame:
    staff = pd.DataFrame({
        "id": erp[col.ERP_ID],
        "station": pd.to_numeric(
            erp[col.ERP_HOME_STATION].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
        ).astype("Int64"),
        "full_name": (erp[col.ERP_FIRST_NAME].astype(str) + " " + erp[col.ERP_LAST_NAME].astype(str)).str.strip(),
        "age": erp[col.ERP_AGE],
        "hourly_cost": erp[col.ERP_HOURLY_COST],
        "level": erp[col.ERP_EXPERIENCE].map(EXPERIENCE_LABELS).fillna(erp[col.ERP_EXPERIENCE]),
    })
    staff["exp_score"] = staff["level"].map(EXPERIENCE_SCORE)
    return staff


def team_by_station(staff: pd.DataFrame) -> pd.DataFrame:
    return staff.groupby("station").agg(
        operators=("id", "count"),
        team_hourly_cost=("hourly_cost", "sum"),
        avg_experience=("exp_score", "mean"),
        beginners=("level", lambda s: int((s == "Beginner").sum())),
        experts=("level", lambda s: int((s == "Expert").sum())),
        avg_age=("age", "mean"),
        team=("full_name", ", ".join),
        levels=("level", ", ".join),
    ).reset_index()
