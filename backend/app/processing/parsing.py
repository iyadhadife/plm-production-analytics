"""Small converters for the raw values found in the Excel files."""

import datetime as dt
import re

import numpy as np
import pandas as pd


def to_timedelta(value):
    """datetime.time, timedelta or 'HH:MM:SS' -> pd.Timedelta (NaT if unreadable)."""
    if value is None or (isinstance(value, float) and np.isnan(value)) or value == "":
        return pd.NaT
    if isinstance(value, dt.time):
        return pd.Timedelta(hours=value.hour, minutes=value.minute, seconds=value.second)
    try:
        return pd.to_timedelta(str(value))
    except (ValueError, TypeError):
        return pd.NaT


def to_minutes(value) -> float:
    td = to_timedelta(value)
    return np.nan if pd.isna(td) else td.total_seconds() / 60


def to_time(value):
    """datetime.time or a parsable string -> datetime.time (None if unreadable)."""
    if isinstance(value, dt.time):
        return value
    try:
        return pd.to_datetime(str(value)).time()
    except (ValueError, TypeError):
        return None


def parse_lead_time_days(value) -> float:
    """'15-20 jours' or '30 jours' -> upper bound in days (float)."""
    if pd.isna(value):
        return np.nan
    numbers = re.findall(r"(\d+(?:[.,]\d+)?)", str(value))
    return max(float(n.replace(",", ".")) for n in numbers) if numbers else np.nan


def to_number(series: pd.Series) -> pd.Series:
    """Numbers stored as text ('12,5 €', '30 €/h') -> float."""
    cleaned = (
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("€/h", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")
