"""Query preprocessing shared by the Streamlit inference application."""

from __future__ import annotations

import re


def clean_query(text: str) -> str:
    """Match the lowercasing and placeholder cleaning used before training."""
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@[\w.-]+", " username ", text)
    text = re.sub(r"#[\w.-]+", " hashtag ", text)
    text = re.sub(r"[^a-z0-9'?$%.,!\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
