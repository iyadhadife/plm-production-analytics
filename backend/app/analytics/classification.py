"""Keyword-based grouping of the free-text MES incident and root-cause columns."""

from app.analytics.constants import INCIDENT_FAMILIES, OTHER, ROOT_CAUSE_THEMES


def incident_family(text) -> str:
    lowered = str(text).lower()
    for name, keywords in INCIDENT_FAMILIES:
        if any(k in lowered for k in keywords):
            return name
    return OTHER


def root_cause_themes(text) -> list[str]:
    lowered = str(text).lower()
    return [name for name, keywords in ROOT_CAUSE_THEMES if any(k in lowered for k in keywords)] or [OTHER]
