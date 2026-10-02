"""Number, duration and text formatting for the analysis pages."""

import html

import numpy as np
import pandas as pd


def esc(value) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return html.escape(str(value))


def fmt_eur(value) -> str:
    if value is None or pd.isna(value):
        return "–"
    return f"{value:,.0f} €"


def fmt_eur_short(value) -> str:
    if value is None or pd.isna(value):
        return "–"
    if abs(value) >= 1e6:
        return f"{value / 1e6:.1f} M€"
    if abs(value) >= 1e4:
        return f"{value / 1e3:.0f} k€"
    return fmt_eur(value)


def fmt_minutes(value) -> str:
    if value is None or pd.isna(value):
        return "–"
    m = int(round(value))
    return f"{m // 60} h {m % 60:02d}" if m >= 60 else f"{m} min"


def fmt_int(value) -> str:
    return f"{value:,.0f}"
