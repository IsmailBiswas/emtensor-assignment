"""Helpers for messy real-world CSV values."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def parse_optional_float(value: str | None) -> float | None:
    text = empty_to_none(value)
    if text is None:
        return None
    cleaned = (
        text.replace(",", "")
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("INR", "")
        .strip()
    )
    if not cleaned:
        return None
    return float(cleaned)


def parse_float(value: str | None, *, field: str) -> float:
    parsed = parse_optional_float(value)
    if parsed is None:
        raise ValueError(f"Missing numeric value for {field}")
    return parsed


def parse_optional_int(value: str | None) -> int | None:
    text = empty_to_none(value)
    if text is None:
        return None
    return int(float(text.replace(",", "")))


def parse_int(value: str | None, *, field: str) -> int:
    parsed = parse_optional_int(value)
    if parsed is None:
        raise ValueError(f"Missing integer value for {field}")
    return parsed


_DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
)


def parse_optional_date(value: str | None) -> date | None:
    text = empty_to_none(value)
    if text is None:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_date(value: str | None, *, field: str) -> date:
    parsed = parse_optional_date(value)
    if parsed is None:
        raise ValueError(f"Unparseable date for {field}: {value!r}")
    return parsed


def split_semicolon_ids(value: str | None) -> list[str]:
    text = empty_to_none(value)
    if text is None:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]
