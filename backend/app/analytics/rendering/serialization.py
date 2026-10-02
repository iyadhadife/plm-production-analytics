"""JSON serialisation of pandas / numpy values for inline Plotly.js figures."""

import datetime as dt
import json

import numpy as np
import pandas as pd


def to_json(obj) -> str:
    return json.dumps(_clean(obj), default=_default, ensure_ascii=False).replace("</", "<\\/")


def _clean(o):
    if isinstance(o, (pd.Series, pd.Index, np.ndarray)):
        o = list(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if np.isnan(o) else float(o)
    if o is pd.NA or o is pd.NaT:
        return None
    if isinstance(o, (pd.Timestamp, dt.datetime)):
        return o.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


def _default(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)
