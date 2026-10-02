"""Plain HTML preview of an uploaded Excel file."""

import pandas as pd

from app.reports.html import esc

MAX_ROWS = 1000

CSS = """
<style>
  .excel-table { width: 100%; border-collapse: collapse; font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  .excel-table th { background-color: #4c6ef5; color: white; padding: 12px; text-align: left; font-weight: 600;
    border: 1px solid #dee2e6; position: sticky; top: 0; z-index: 10; }
  .excel-table td { padding: 10px 12px; border: 1px solid #dee2e6; text-align: left; }
  .excel-table tbody tr:nth-child(odd) { background-color: #f8f9fa; }
  .excel-table tbody tr:hover { background-color: #e7f5ff; }
  .table-info { margin-bottom: 20px; padding: 12px 16px; background-color: #e7f5ff;
    border-left: 4px solid #4c6ef5; border-radius: 4px; font-size: 13px; }
</style>
"""


def render_excel_table(df: pd.DataFrame, filename: str) -> str:
    df = df.head(MAX_ROWS)
    info = (f'<div class="table-info"><strong>📊 {esc(filename)}</strong> | '
            f"Rows: {len(df)} | Columns: {len(df.columns)}</div>")
    return CSS + info + df.to_html(classes="excel-table", border=0, index=False)
