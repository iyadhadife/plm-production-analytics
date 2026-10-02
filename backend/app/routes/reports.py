"""Station / step reports built from the MES, PLM and ERP files."""

from flask import Blueprint, jsonify, request

from app.processing import columns as col
from app.processing.joins import build_production_chains
from app.processing.loader import load_sources
from app.reports.delays import render_delays
from app.reports.step_costs import render_step_costs
from app.reports.step_details import render_step_details
from app.reports.team_experience import render_team_experience
from app.reports.workflow_sankey import render_workflow
from app.routes.responses import error, html_response

bp = Blueprint("reports", __name__, url_prefix="/api")


@bp.errorhandler(Exception)
def _processing_error(exc):
    return error(f"Processing error: {exc}", 500)


def _chains():
    return build_production_chains(*load_sources())


@bp.get("/steps")
def list_steps():
    """Assembly step names found in the MES file, in order of appearance."""
    mes, _, _ = load_sources()
    return jsonify(mes[col.MES_STEP].dropna().astype(str).str.strip().unique().tolist())


@bp.get("/reports/step-details")
def step_details():
    step = request.args.get("step", "").strip()
    mes, plm, erp = load_sources()
    if not step or step not in set(mes[col.MES_STEP].astype(str).str.strip()):
        return error("Missing or unknown assembly step")
    return html_response(render_step_details(mes, plm, erp, step))


@bp.get("/reports/step-costs")
def step_costs():
    return html_response(render_step_costs(*load_sources()))


@bp.get("/reports/team-experience")
def team_experience():
    return html_response(render_team_experience(_chains()))


@bp.get("/reports/workflow")
def workflow():
    step = request.args.get("step") or None
    max_nodes = request.args.get("max_nodes", 50, type=int)
    return html_response(render_workflow(_chains(), step=step, max_nodes=max_nodes))


@bp.get("/reports/delays")
def delays():
    return html_response(render_delays(_chains()))
