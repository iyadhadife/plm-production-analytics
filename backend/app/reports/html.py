"""Shared HTML styling and formatting for the reports."""

import html

import pandas as pd

TABLE_ATTRS = (
    'border="1" cellpadding="8" cellspacing="0" '
    'style="border-collapse:collapse; font-family: Arial; width: 100%;"'
)
HEADER_ROW_ATTRS = 'style="background-color:#f0f0f0;font-weight:bold;text-align:center;"'

TABLE_CSS = """
<style>
    table { border-collapse: collapse; font-family: Arial, sans-serif; width: 100%; border: 1px solid #ddd; }
    th { background-color: #f0f0f0; font-weight: bold; text-align: center; padding: 8px; border: 1px solid #ddd; }
    td { padding: 8px; border: 1px solid #ddd; }
    tr:nth-child(even) { background-color: #f9f9f9; }
</style>
"""


def styled_table(df: pd.DataFrame) -> str:
    """pandas.to_html() output with the shared table style."""
    return TABLE_CSS + df.to_html(index=False, escape=False, border=1, justify="center")


def header_row(labels: list[str]) -> str:
    cells = "".join(f"<td>{label}</td>" for label in labels)
    return f"<tr {HEADER_ROW_ATTRS}>{cells}</tr>"


def esc(value) -> str:
    return html.escape(str(value))


def fmt_eur(value: float) -> str:
    return f"{value:,.2f} €"


def fmt_hours(value: float) -> str:
    return f"{value:.2f} h"


def fmt_duration(td) -> str:
    """Timedelta -> 'H:MM:SS' (days folded into hours)."""
    if td is None or pd.isna(td):
        return "-"
    total = int(td.total_seconds())
    return f"{total // 3600}:{total % 3600 // 60:02d}:{total % 60:02d}"


def message(text: str) -> str:
    return f"<p><b>{esc(text)}</b></p>"
