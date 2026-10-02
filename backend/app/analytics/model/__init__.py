"""
Joined data model for the cross analyses.

Join keys:
    MES "Référence" (list "A511;A337;...")  ->  PLM "Code / Référence"   (parts)
    MES "Poste" (1..56)                     ->  ERP "Poste de montage"   ("Poste N" = home team)
    MES "Date" + "Heure Début"              ->  actual timeline
"""

from dataclasses import dataclass

import pandas as pd

from app.analytics.model.operations import build_operations
from app.analytics.model.parts import build_parts, prepare_plm
from app.analytics.model.staff import build_staff, team_by_station


@dataclass
class Model:
    ops: pd.DataFrame     # 1 row = 1 MES operation enriched with PLM and ERP
    parts: pd.DataFrame   # 1 row = 1 PLM part enriched with its MES consumption
    staff: pd.DataFrame   # 1 row = 1 ERP operator


def build_model(mes: pd.DataFrame, plm: pd.DataFrame, erp: pd.DataFrame) -> Model:
    staff = build_staff(erp)
    plm = prepare_plm(plm)
    ops, consumption = build_operations(mes, plm, team_by_station(staff))
    return Model(ops=ops, parts=build_parts(plm, consumption, ops), staff=staff)
