"""
Cross analyses MES × PLM × ERP.

Each analysis returns a standalone HTML page (Plotly.js from CDN) shown in the
frontend iframe. See docs/cross-analyses.md for the method.
"""

from pathlib import Path

from app.analytics.analyses import (
    cost_structure, experience, overview, pareto, priority_matrix, schedule, supply_risk, timeline, workforce,
)
from app.analytics.model import build_model
from app.processing.loader import load_sources

ANALYSES = {
    "overview": overview.render,
    "priority-matrix": priority_matrix.render,
    "pareto": pareto.render,
    "experience": experience.render,
    "supply-risk": supply_risk.render,
    "timeline": timeline.render,
    "cost-structure": cost_structure.render,
    "workforce": workforce.render,
    "schedule": schedule.render,
}


def render_analysis(name: str, folder: Path | None = None) -> str:
    if name not in ANALYSES:
        raise KeyError(f"Unknown analysis: {name}. Available: {', '.join(ANALYSES)}")
    return ANALYSES[name](build_model(*load_sources(folder)))
