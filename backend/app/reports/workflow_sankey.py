"""Sankey diagram: assembly step -> station -> part."""

from urllib.parse import unquote

import pandas as pd
import plotly.graph_objects as go

from app.processing import columns as col
from app.processing.joins import PART_CODE
from app.reports.html import esc, message

STEP, STATION = col.MES_STEP, col.MES_STATION


def render_workflow(chains: pd.DataFrame, step: str | None = None, max_nodes: int = 50) -> str:
    df = chains.dropna(subset=[STEP, STATION, PART_CODE]).copy()
    for c in (STEP, STATION, PART_CODE):
        df[c] = df[c].astype(str).str.strip()

    title = "Workflow: step (MES) → station → part"
    if step:
        step = unquote(step).strip()
        df = df[df[STEP] == step]
        if df.empty:
            return message(f"No data for step: {step}")
        title += f" — {esc(step)}"

    steps = _top_values(df, STEP, max_nodes)
    df = df[df[STEP].isin(steps)]
    stations = _top_values(df, STATION, max_nodes)
    df = df[df[STATION].isin(stations)]
    parts = _top_values(df, PART_CODE, max_nodes)
    df = df[df[PART_CODE].isin(parts)]

    labels = ([f"Step: {s}" for s in steps] + [f"Station {s}" for s in stations]
              + [f"Part: {p}" for p in parts])
    index = {("s", s): i for i, s in enumerate(steps)}
    index.update({("p", s): len(steps) + i for i, s in enumerate(stations)})
    index.update({("c", p): len(steps) + len(stations) + i for i, p in enumerate(parts)})

    sources, targets, values = [], [], []
    for (a, b), (ka, kb) in (((STEP, STATION), ("s", "p")), ((STATION, PART_CODE), ("p", "c"))):
        for (va, vb), n in df.groupby([a, b]).size().items():
            sources.append(index[(ka, va)])
            targets.append(index[(kb, vb)])
            values.append(int(n))
    if not sources:
        return message("No links to display.")

    fig = go.Figure(go.Sankey(node=dict(label=labels, pad=15, thickness=15),
                              link=dict(source=sources, target=targets, value=values)))
    fig.update_layout(title_text=title, font_size=10, height=700,
                      margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor="white", paper_bgcolor="white")
    return fig.to_html(full_html=True, include_plotlyjs="cdn")


def _top_values(df: pd.DataFrame, column: str, limit: int) -> list:
    """Distinct values, keeping only the `limit` most frequent when there are too many."""
    values = df[column].unique().tolist()
    if len(values) <= limit:
        return sorted(values) if column == STATION else values
    return df[column].value_counts().head(limit).index.tolist()
