"""Summary of one assembly step: parts, people, costs and times."""

import pandas as pd

from app.processing import columns as col
from app.processing.costs import UNIT_COST, labour_by_person, parts_with_cost
from app.processing.joins import PERSON_NAME
from app.processing.parsing import to_timedelta
from app.reports.html import TABLE_ATTRS, esc, fmt_duration, fmt_eur, fmt_hours, header_row, message

CARD = (
    "flex:1 1 220px;border:1px solid #ddd;border-radius:6px;padding:12px;"
    "background:#fafafa;box-shadow:0 1px 3px rgba(0,0,0,0.06);"
)
ROW = "display:flex; gap:16px; flex-wrap:wrap; margin-bottom:16px;"


def render_step_details(mes: pd.DataFrame, plm: pd.DataFrame, erp: pd.DataFrame, step: str) -> str:
    ops = mes[mes[col.MES_STEP].astype(str).str.strip() == step.strip()].copy()
    if ops.empty:
        return message(f"No MES data for step: {step}")

    parts = parts_with_cost(ops, plm)
    part_cost = parts[UNIT_COST].sum()
    people = labour_by_person(ops, erp).sort_values("cost", ascending=False)
    labour_cost = people["cost"].sum()

    planned = _total_time(ops, col.MES_PLANNED_TIME)
    actual = _total_time(ops, col.MES_ACTUAL_TIME)
    cad_cols = [c for c in ops.columns if "cao" in c.lower()]
    cad = _total_time(ops, cad_cols[0]) if cad_cols else None

    cost_cards = [
        ("Number of parts", str(len(parts))),
        ("Parts cost", fmt_eur(part_cost)),
        ("Number of people", str(len(people))),
        ("Labour cost", fmt_eur(labour_cost)),
        ("Total cost", f'<span style="color:#c0392b;">{fmt_eur(part_cost + labour_cost)}</span>'),
    ]
    time_cards = [
        ("Total planned time", _time_value(planned)),
        ("Total actual time", _time_value(actual)),
        ("Total CAD time", _time_value(cad)),
    ]

    return f"""
<div style="font-family:Arial, sans-serif; max-width:1100px;">
  <h2>Assembly step: <span style="color:#0050b3;">{esc(step)}</span></h2>
  <p style="margin-top:0;color:#666;">Summary of parts, people, costs and times.</p>
  {_card_row(cost_cards, big=True)}
  {_card_row(time_cards, big=False)}
  <h3>People involved</h3>
  {_people_table(people)}
</div>
"""


def _total_time(ops: pd.DataFrame, column: str):
    if column not in ops.columns:
        return None
    return ops[column].apply(to_timedelta).sum()


def _time_value(td) -> str:
    hours = td.total_seconds() / 3600 if td is not None and pd.notna(td) else 0
    return f'{fmt_duration(td)}<div style="font-size:11px;color:#555;font-weight:normal;">({fmt_hours(hours)})</div>'


def _card_row(cards: list[tuple[str, str]], big: bool) -> str:
    size = "font-size:22px;" if big else ""
    cells = "".join(
        f'<div style="{CARD}"><div style="color:#777;font-size:12px;">{label}</div>'
        f'<div style="{size}font-weight:bold;">{value}</div></div>'
        for label, value in cards
    )
    return f'<div style="{ROW}">{cells}</div>'


def _people_table(people: pd.DataFrame) -> str:
    rows = "".join(
        f"""<tr>
  <td>{esc(p[PERSON_NAME])}</td>
  <td style="text-align:center;">{esc(col.EXPERIENCE_LABELS.get(p['level'], p['level']))}</td>
  <td style="text-align:right;">{fmt_hours(p['hours'])}</td>
  <td style="text-align:right;">{fmt_eur(p['hourly_rate'])}</td>
  <td style="text-align:right;font-weight:bold;">{fmt_eur(p['cost'])}</td>
</tr>"""
        for _, p in people.iterrows()
    )
    if not rows:
        rows = ('<tr><td colspan="5" style="text-align:center;color:#888;">'
                "No usable labour data for this step.</td></tr>")
    header = header_row(["Name", "Level", "Planned hours", "Hourly rate", "Cost"])
    return f"<table {TABLE_ATTRS}>{header}{rows}</table>"
