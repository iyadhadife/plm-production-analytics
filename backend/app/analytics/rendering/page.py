"""Full standalone HTML page (Plotly.js from CDN) for one analysis."""

from app.analytics.constants import COLORS as C, PLOTLY_CDN
from app.analytics.rendering.formatters import esc
from app.analytics.rendering.serialization import to_json

CSS = f"""
*{{box-sizing:border-box}}
body{{margin:0;padding:24px;background:#f4f3f0;color:{C['text']};
 font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:14px}}
header.page h2{{margin:0 0 4px;font-size:22px}}
header.page p{{margin:0 0 20px;color:{C['text2']};max-width:900px;line-height:1.5}}
.sources{{display:inline-flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}}
.sources span{{font-size:11px;font-weight:600;padding:3px 8px;border-radius:999px;background:#fff;
 border:1px solid {C['border']};color:{C['text2']}}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px}}
.kpi{{background:{C['surface']};border:1px solid {C['border']};border-radius:10px;padding:14px 16px}}
.kpi-label{{font-size:12px;color:{C['text2']}}}
.kpi-value{{font-size:26px;font-weight:650;margin:4px 0;font-variant-numeric:tabular-nums}}
.kpi-sub{{font-size:12px;color:{C['muted']}}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:16px}}
.card{{background:{C['surface']};border:1px solid {C['border']};border-radius:10px;padding:16px;margin-bottom:16px;min-width:0}}
.card h3{{margin:0 0 4px;font-size:15px}}
.card-sub{{margin:0 0 8px;color:{C['text2']};font-size:12.5px;line-height:1.45}}
.insights{{background:#eef5fd;border:1px solid #cde2fb;border-radius:10px;padding:14px 18px;margin-bottom:16px}}
.insights h3{{margin:0 0 6px;font-size:14px;color:#184f95}}
.insights ul{{margin:0;padding-left:18px;line-height:1.6}}
.table-wrap{{overflow-x:auto;margin-top:8px}}
table{{border-collapse:collapse;width:100%;font-size:12.5px}}
th{{text-align:left;color:{C['text2']};font-weight:600;border-bottom:1px solid {C['border']};padding:8px;white-space:nowrap}}
td{{border-bottom:1px solid {C['grid']};padding:7px 8px;vertical-align:top}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
tr:hover td{{background:#f7f6f3}}
.badge{{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}}
.badge i{{width:9px;height:9px;border-radius:50%;display:inline-block}}
.cellbar{{position:relative;min-width:110px}}
.cellbar span{{position:absolute;left:0;top:2px;bottom:2px;background:#cde2fb;border-radius:0 4px 4px 0}}
.cellbar em{{position:relative;font-style:normal;padding-left:4px}}
.note{{font-size:11.5px;color:{C['muted']};margin-top:6px}}
"""

PLOT_CONFIG = "{responsive:true, displaylogo:false, modeBarButtonsToRemove:['lasso2d','select2d']}"


def page(title: str, intro: str, sources: list[str], body: str, figures: dict[str, dict]) -> str:
    """`figures` maps a chart div id to a {'data': [...], 'layout': {...}} Plotly figure."""
    calls = "\n".join(
        f"Plotly.newPlot('{fid}', {to_json(fig['data'])}, {to_json(fig['layout'])}, {PLOT_CONFIG});"
        for fid, fig in figures.items()
    )
    badges = "".join(f"<span>{esc(s)}</span>" for s in sources)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<script src="{PLOTLY_CDN}"></script>
<style>{CSS}</style></head>
<body>
<header class="page"><h2>{esc(title)}</h2><div class="sources">{badges}</div><p>{intro}</p></header>
{body}
<script>
{calls}
</script>
</body></html>"""
