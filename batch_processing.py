<<<<<<< HEAD
"""Helpers for reading uploaded query files."""

from __future__ import annotations

from io import StringIO

import pandas as pd


QUERY_COLUMN_NAMES = ("query", "question", "instruction", "text", "message")


def extract_queries(uploaded_file) -> list[str]:
    suffix = uploaded_file.name.lower().rsplit(".", 1)[-1]
    if suffix == "txt":
        content = uploaded_file.getvalue().decode("utf-8-sig")
        return [line.strip() for line in content.splitlines() if line.strip()]
    if suffix == "csv":
        frame = pd.read_csv(StringIO(uploaded_file.getvalue().decode("utf-8-sig")))
        normalized = {str(column).strip().lower(): column for column in frame.columns}
        selected = next(
            (normalized[name] for name in QUERY_COLUMN_NAMES if name in normalized),
            None,
        )
        if selected is None:
            text_columns = frame.select_dtypes(include="object").columns.tolist()
            selected = text_columns[0] if text_columns else frame.columns[0]
        return [str(value).strip() for value in frame[selected].dropna() if str(value).strip()]
    raise ValueError("Only .txt and .csv files are supported.")
=======
"""Helpers for reading uploaded query files."""

from __future__ import annotations

from io import StringIO

import pandas as pd


QUERY_COLUMN_NAMES = ("query", "question", "instruction", "text", "message")


def extract_queries(uploaded_file) -> list[str]:
    suffix = uploaded_file.name.lower().rsplit(".", 1)[-1]
    if suffix == "txt":
        content = uploaded_file.getvalue().decode("utf-8-sig")
        return [line.strip() for line in content.splitlines() if line.strip()]
    if suffix == "csv":
        frame = pd.read_csv(StringIO(uploaded_file.getvalue().decode("utf-8-sig")))
        normalized = {str(column).strip().lower(): column for column in frame.columns}
        selected = next(
            (normalized[name] for name in QUERY_COLUMN_NAMES if name in normalized),
            None,
        )
        if selected is None:
            text_columns = frame.select_dtypes(include="object").columns.tolist()
            selected = text_columns[0] if text_columns else frame.columns[0]
        return [str(value).strip() for value in frame[selected].dropna() if str(value).strip()]
    raise ValueError("Only .txt and .csv files are supported.")
>>>>>>> d2d00eb93c1bfae679456e0d88680c0ac6f2a87b
