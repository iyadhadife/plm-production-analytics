"""Full standalone HTML page (Plotly.js from CDN) for one analysis.

The page defines its colours as CSS tokens (light and dark) and re-themes the
Plotly figures from those tokens, so charts follow the viewer's colour scheme.
"""

from app.analytics.constants import PLOTLY_CDN
from app.analytics.rendering.formatters import esc
from app.analytics.rendering.serialization import to_json

FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600"
         "&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap")

LIGHT = """--bg:#f3f4f2;--surface:#fcfcfb;--fg:#14161a;--fg2:#4f5560;--muted:#868b94;
 --line:#dcdfe3;--grid:#e8eaec;--accent:#2a78d6;--accent-soft:#e6f0fc;--accent-ink:#184f95;--bar:#cde2fb;"""
DARK = """--bg:#121417;--surface:#1a1c1f;--fg:#f2f3f5;--fg2:#b9bec7;--muted:#8a909a;
 --line:#2e3238;--grid:#2a2d32;--accent:#3987e5;--accent-soft:#16273d;--accent-ink:#9ec5f4;--bar:#1c3a63;
 color-scheme:dark;"""

CSS = f"""
:root{{{LIGHT}
 --f-display:"IBM Plex Sans Condensed","Arial Narrow",system-ui,sans-serif;
 --f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
 --f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{DARK}}}}}
:root[data-theme="dark"]{{{DARK}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:14px;line-height:1.5}}
.wrap{{max-width:1280px;margin:0 auto;padding:24px 16px 40px}}
header.page{{display:grid;gap:6px;margin-bottom:18px}}
.eyebrow{{font-family:var(--f-mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
header.page h1{{font-family:var(--f-display);font-size:clamp(24px,3.4vw,34px);line-height:1.1;margin:0;text-wrap:balance}}
header.page p{{margin:0;color:var(--fg2);max-width:80ch}}
.sources{{display:flex;gap:6px;flex-wrap:wrap}}
.sources span{{font:500 11px var(--f-mono);letter-spacing:.04em;padding:2px 8px;border-radius:999px;
 border:1px solid var(--line);color:var(--fg2);background:var(--surface)}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-bottom:16px}}
.kpi{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-width:0}}
.kpi-label{{font-size:12px;color:var(--fg2)}}
.kpi-value{{font-family:var(--f-display);font-size:28px;font-weight:700;margin:2px 0;font-variant-numeric:tabular-nums}}
.kpi-sub{{font-size:11.5px;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:16px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:16px;min-width:0}}
.card h3{{margin:0 0 4px;font-size:15px;font-weight:600}}
.card-sub{{margin:0 0 8px;color:var(--fg2);font-size:12.5px}}
.chart{{width:100%}}
.insights{{background:var(--accent-soft);border-radius:10px;padding:12px 16px;margin-bottom:16px}}
.insights h3{{margin:0 0 4px;font:500 13px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent-ink)}}
.insights ul{{margin:0;padding-left:18px;line-height:1.6}}
.table-wrap{{overflow-x:auto;margin-top:8px}}
table{{border-collapse:collapse;width:100%;font-size:12.5px}}
th{{text-align:left;color:var(--fg2);font-weight:600;border-bottom:1px solid var(--line);padding:7px 8px;white-space:nowrap}}
td{{border-bottom:1px solid var(--grid);padding:6px 8px;vertical-align:top}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;font-family:var(--f-mono);font-size:12px}}
tr:hover td{{background:var(--bg)}}
.badge{{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}}
.badge i{{width:9px;height:9px;border-radius:50%;display:inline-block}}
.cellbar{{position:relative;min-width:110px}}
.cellbar span{{position:absolute;left:0;top:2px;bottom:2px;background:var(--bar);border-radius:0 4px 4px 0}}
.cellbar em{{position:relative;font-style:normal;padding-left:4px}}
.note{{font-size:12px;color:var(--muted);margin-top:6px}}
@media (max-width:600px){{.card{{padding:10px}}.kpi-value{{font-size:22px}}}}
"""

# Re-themes the figures from the CSS tokens (the Python layouts use the light palette).
THEME_JS = """
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const LIGHT_SURFACE = '#fcfcfb', LIGHT_TEXT = '#0b0b0b';
function themed(layout){
  const L = JSON.parse(JSON.stringify(layout));
  const s = css('--surface'), fg2 = css('--fg2'), grid = css('--grid'), line = css('--line');
  L.paper_bgcolor = s; L.plot_bgcolor = s;
  L.font = Object.assign({}, L.font, {color: fg2, family: css('--f-body')});
  for (const ax of ['xaxis','yaxis']) if (L[ax]) {
    if (L[ax].gridcolor !== 'rgba(0,0,0,0)') L[ax].gridcolor = grid;
    L[ax].zerolinecolor = line; L[ax].linecolor = line;
  }
  if (L.legend) L.legend.font = {color: fg2};
  L.hoverlabel = {bgcolor: s, bordercolor: line, font: {color: css('--fg')}};
  (L.annotations || []).forEach(a => { if (a.font && a.font.color === LIGHT_TEXT) a.font.color = css('--fg'); });
  if (window.innerWidth < 700 && L.margin && L.margin.l > 140) L.margin.l = 140;
  return L;
}
function themedData(data){
  const D = JSON.parse(JSON.stringify(data));
  D.forEach(t => { if (t.marker && t.marker.line && t.marker.line.color === LIGHT_SURFACE) t.marker.line.color = css('--surface'); });
  return D;
}
function drawAll(){
  if (!window.Plotly) return;
  for (const [id, f] of Object.entries(FIGS)) {
    const el = document.getElementById(id);
    if (el) Plotly.newPlot(el, themedData(f.data), themed(f.layout), CONFIG);
  }
}
drawAll();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', drawAll);
new MutationObserver(drawAll).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
"""

PLOT_CONFIG = "{responsive:true, displaylogo:false, modeBarButtonsToRemove:['lasso2d','select2d']}"


def page(title: str, intro: str, sources: list[str], body: str, figures: dict[str, dict]) -> str:
    """`figures` maps a chart div id to a {'data': [...], 'layout': {...}} Plotly figure."""
    badges = "".join(f"<span>{esc(s)}</span>" for s in sources)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{FONTS}">
<script src="{PLOTLY_CDN}"></script>
<style>{CSS}</style></head>
<body><div class="wrap">
<header class="page"><div class="eyebrow">Airplus · Cross analysis</div><h1>{esc(title)}</h1>
<div class="sources">{badges}</div><p>{intro}</p></header>
{body}
</div>
<script>
const FIGS = {to_json(figures)};
const CONFIG = {PLOT_CONFIG};
{THEME_JS}
</script>
</body></html>"""
