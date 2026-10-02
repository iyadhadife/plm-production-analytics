"""Reshaping helpers used to join MES, PLM and ERP."""

import re

import numpy as np
import pandas as pd

from app.processing import columns as col

PART_CODE = "part_code"
PERSON_NAME = "person_name"
WEEK = "week"

ROTATION_PATTERN = re.compile(r"Semaine\s*(\d+)\s*:\s*Poste\s*(\d+)", flags=re.I)


def explode_references(mes: pd.DataFrame, keep_without_parts: bool = False) -> pd.DataFrame:
    """
    One row per (operation, consumed part) from the MES 'A511;A337;...' list.
    With `keep_without_parts`, operations without references stay with a NaN part code.
    """
    df = mes.copy()
    df[PART_CODE] = df[col.MES_REFERENCES].fillna("").astype(str).str.split(";")
    df = df.explode(PART_CODE)
    df[PART_CODE] = df[PART_CODE].str.strip().replace("", np.nan)
    if keep_without_parts:
        # drop empty entries ("A1;;A2") but keep one row for operations with no part at all
        has_parts = df.groupby(level=0)[PART_CODE].transform("count") > 0
        return df[df[PART_CODE].notna() | ~has_parts]
    return df.dropna(subset=[PART_CODE])


def plm_by_part_code(plm: pd.DataFrame) -> pd.DataFrame:
    return plm.rename(columns={col.PLM_CODE: PART_CODE})


def add_person_name(erp: pd.DataFrame) -> pd.DataFrame:
    df = erp.copy()
    if {col.ERP_FIRST_NAME, col.ERP_LAST_NAME}.issubset(df.columns):
        df[PERSON_NAME] = (
            df[col.ERP_FIRST_NAME].fillna("").astype(str).str.strip()
            + " "
            + df[col.ERP_LAST_NAME].fillna("").astype(str).str.strip()
        ).str.strip()
    else:
        df[PERSON_NAME] = np.nan
    return df


def expand_rotation(erp: pd.DataFrame) -> pd.DataFrame:
    """
    One row per (operator, week) from the ERP rotation text
    "Semaine 1: Poste 55 | Semaine 3: Poste 50", with the station in MES_STATION.
    """
    rows = []
    if col.ERP_ROTATION in erp.columns:
        for _, row in erp.iterrows():
            rotation = row.get(col.ERP_ROTATION)
            if pd.isna(rotation):
                continue
            for week, station in ROTATION_PATTERN.findall(str(rotation)):
                record = row.to_dict()
                record[WEEK] = int(week)
                record[col.MES_STATION] = int(station)
                rows.append(record)

    long = pd.DataFrame(rows) if rows else pd.DataFrame(columns=[*erp.columns, WEEK, col.MES_STATION])
    long = long.drop(columns=[col.ERP_ROTATION], errors="ignore")
    long = add_person_name(long)
    long[col.MES_STATION] = as_station(long[col.MES_STATION])
    return long


def as_station(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def build_production_chains(mes: pd.DataFrame, plm: pd.DataFrame, erp: pd.DataFrame) -> pd.DataFrame:
    """
    Fully joined table: 1 row = 1 MES operation x 1 consumed part x 1 operator-week
    on that station (operations without parts are kept with a NaN part code). ERP columns that clash with MES get the '_ERP' suffix.
    """
    mes_plm = explode_references(mes, keep_without_parts=True).merge(plm_by_part_code(plm), on=PART_CODE, how="left")
    mes_plm[col.MES_STATION] = as_station(mes_plm[col.MES_STATION])
    return mes_plm.merge(expand_rotation(erp), on=col.MES_STATION, how="left", suffixes=("", "_ERP"))
