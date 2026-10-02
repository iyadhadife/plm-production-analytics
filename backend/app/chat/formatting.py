"""Human-readable rendering of whatever the generated code put in `result`."""

import pandas as pd

MAX_ROWS = 20


def format_result(result) -> str:
    if result is None:
        return "⚠️ The code ran but returned no result."
    if isinstance(result, str):
        return result
    if isinstance(result, pd.DataFrame):
        return _format_dataframe(result)
    if isinstance(result, list):
        return _format_list(result)
    if isinstance(result, dict):
        return "✅ Result:\n\n" + "".join(f"• {k}: {_value(v)}\n" for k, v in result.items())
    if isinstance(result, (int, float)):
        return f"✅ Result: {_value(result)}"
    return f"✅ Result: {result}"


def _format_dataframe(df: pd.DataFrame) -> str:
    if df.empty:
        return "ℹ️ No result matches your query."
    if len(df) <= MAX_ROWS:
        return "✅ Here are the results:\n\n" + df.to_string(index=False)
    return (f"✅ Found {len(df)} results. Here are the first {MAX_ROWS}:\n\n"
            + df.head(MAX_ROWS).to_string(index=False)
            + f"\n\n... and {len(df) - MAX_ROWS} more.")


def _format_list(items: list) -> str:
    if not items:
        return "ℹ️ No result found."
    lines = []
    for i, item in enumerate(items[:MAX_ROWS], 1):
        if isinstance(item, dict):
            item = " | ".join(f"{k}: {_value(v)}" for k, v in item.items())
        lines.append(f"{i}. {item}")
    text = f"✅ Found {len(items)} result(s):\n\n" + "\n".join(lines)
    if len(items) > MAX_ROWS:
        text += f"\n\n... and {len(items) - MAX_ROWS} more."
    return text


def _value(v) -> str:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{v:,}"
    return str(v)
