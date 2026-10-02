"""Reusable HTML blocks: KPI tiles, cards, insight boxes and tables."""

import numpy as np
import pandas as pd

from app.analytics.constants import CRITICALITY_COLOR
from app.analytics.rendering.formatters import esc

CRITICALITY_COLUMNS = {"Criticality", "Max criticality"}


def kpis(items: list[tuple[str, str, str]]) -> str:
    """items = [(label, value, caption)]"""
    cells = "".join(
        f'<div class="kpi"><div class="kpi-label">{esc(label)}</div>'
        f'<div class="kpi-value">{esc(value)}</div><div class="kpi-sub">{esc(caption)}</div></div>'
        for label, value, caption in items
    )
    return f'<div class="kpis">{cells}</div>'


def card(title: str, subtitle: str = "", chart_id: str | None = None, inner: str = "", height: int = 420) -> str:
    chart = f'<div id="{chart_id}" class="chart" style="height:{height}px"></div>' if chart_id else ""
    sub = f'<p class="card-sub">{subtitle}</p>' if subtitle else ""
    return f'<section class="card"><h3>{esc(title)}</h3>{sub}{chart}{inner}</section>'


def grid(*cards: str) -> str:
    return '<div class="grid">' + "".join(cards) + "</div>"


def insights(lines: list[str]) -> str:
    items = "".join(f"<li>{line}</li>" for line in lines)
    return f'<section class="insights"><h3>Key takeaways</h3><ul>{items}</ul></section>'


def criticality_badge(value) -> str:
    color = CRITICALITY_COLOR.get(str(value))
    if not color:
        return esc(value)
    return f'<span class="badge"><i style="background:{color}"></i>{esc(value)}</span>'


def table(df: pd.DataFrame, formats: dict | None = None, bar_col: str | None = None) -> str:
    """HTML table; `formats` maps column -> formatter, `bar_col` gets an inline bar."""
    formats = formats or {}
    head = "".join(f"<th>{esc(c)}</th>" for c in df.columns)
    vmax = df[bar_col].max() if bar_col and len(df) else None
    rows = []
    for _, row in df.iterrows():
        cells = [_cell(c, row[c], formats, bar_col, vmax) for c in df.columns]
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _cell(column, value, formats, bar_col, vmax) -> str:
    text = formats[column](value) if column in formats else esc(value)
    if column in CRITICALITY_COLUMNS:
        text = criticality_badge(value)
    if column == bar_col and vmax:
        width = max(2, 100 * float(value) / float(vmax)) if pd.notna(value) else 0
        text = f'<div class="cellbar"><span style="width:{width:.0f}%"></span><em>{text}</em></div>'
    numeric = isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool)
    return f'<td class="{"num" if numeric else ""}">{text}</td>'
