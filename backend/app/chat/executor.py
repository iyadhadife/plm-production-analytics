"""Execution of the generated pandas code."""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def run_generated_code(code: str, frames: dict[str, pd.DataFrame]):
    """
    Run the code and return its `result` variable.

    Warning: the code comes from an LLM and runs with full Python rights —
    only expose this endpoint on a trusted network.
    """
    scope = {"dataframes": frames, "pd": pd, "np": np, "datetime": datetime, "timedelta": timedelta, "result": None}
    exec(code, scope)  # noqa: S102 - intentional, see docstring
    return scope.get("result")
