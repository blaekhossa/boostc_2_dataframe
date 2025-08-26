#!/usr/bin/env python3
from __future__ import annotations
"""
Flatten Boostcamp-style workout JSON into tabular CSV/XLSX.

This script reads an input JSON payload and writes both CSV and XLSX with
a "one row per set" model. Session and exercise fields are propagated
down to each set row. If an exercise has no sets, one row is emitted
for the exercise with set fields blank.

Propagation rules:
- Session-level fields (date key, title, finished_at, etc.) -> every set row.
- Exercise-level fields (id, name, type, source, video, target_type, etc.) -> every set row.
- Set-level fields (value, amount, unit flags, skipped, etc.) remain per-row.
- Historical metrics (archived_*, previous_*) remain per set for analysis.
- Sensible backfills where set fields are missing (e.g., target_type from exercise).

SCHEMA (inferred from sample)
------------------------------------------------
ROOT: Dict[str session_date -> List[Session]]

Session keys:
day, finished_at, id, legacy, name, program_id, records, title, type, user_id, week, workout

Record/Exercise keys:
alternatives, create_from, created_at, custom, equipments, finished_at, id, index, isAddForFuture, keepNote, muscles, muscles_list, name, notes, original, rest_timer, sets, showPrevious, source, superset_target, supersets, target_type, thumbnail, type, uniq, updated_at, user_notes, video

Set keys:
amount, amountEmpty, archived_reps, archived_rpe, archived_time, archived_weight, custom, from, id, intensity, intensity_dependency_exercise, intensity_unit, isCopyLast, isWarmup, maxValue, previous_reps, previous_rpe, previous_time, previous_weight, progressions, setStatus, showPrevious, skipped, source, target, target_max, target_min, target_type, target_unit, target_weight, time_unit, uniq, user_target, value, valueEmpty, weight_unit

"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import pandas as pd

PREFERRED_COLUMNS = [
        "session_date", "exercise_name", "exercise_type",
        "exercise_target_type", "exercise_muscles", "exercise_equipments",
        "set_index", "set_value_weight", "set_amount_reps",
        "set_target_type", "set_weight_unit",
        "archived_rpe", "previous_rpe",
        "archived_reps", "previous_reps",
        "archived_weight", "previous_weight",
    ]

def _safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    val = d.get(key, default)
    return default if val is None else val


def _join_list(val: Optional[Iterable[Any]], sep: str = ", ") -> str:
    if not val:
        return ""
    return sep.join(map(str, val))


def _muscles_simple(ex: Dict[str, Any]) -> str:
    mlist = ex.get("muscles_list")
    if isinstance(mlist, list) and mlist and isinstance(mlist[0], dict):
        parts = []
        for m in mlist:
            if isinstance(m, dict) and m.get("muscle"):
                percent = m.get("percent")
                if percent is not None and percent != "":
                    parts.append(f"{m.get('muscle')} ({percent})")
                else:
                    parts.append(str(m.get("muscle")))
        return ", ".join(parts)
    return _join_list(ex.get("muscles", []))


def flatten_payload(payload: Dict[str, Any], preferred_cols:List[str] = PREFERRED_COLUMNS) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for session_date, sessions in payload.items():
        if not isinstance(sessions, list):
            continue
        for session in sessions:
            session_ctx = {
                "session_date": session_date,
                "session_title": _safe_get(session, "title", ""),
                "session_name": _safe_get(session, "name", ""),
                "session_finished_at": _safe_get(session, "finished_at", ""),
                "program_id": _safe_get(session, "program_id", ""),
                "session_type": _safe_get(session, "type", ""),
                "session_day": _safe_get(session, "day", ""),
                "session_week": _safe_get(session, "week", ""),
            }

            records = session.get("records", [])
            if not isinstance(records, list):
                continue

            for ex in records:
                muscles_str = _muscles_simple(ex)
                ex_ctx = {
                    "exercise_id": _safe_get(ex, "id", ""),
                    "exercise_name": _safe_get(ex, "name", ""),
                    "exercise_type": _safe_get(ex, "type", ""),
                    "exercise_source": _safe_get(ex, "source", ""),
                    "exercise_custom": _safe_get(ex, "custom", ""),
                    "exercise_video": _safe_get(ex, "video", ""),
                    "exercise_thumbnail": _safe_get(ex, "thumbnail", ""),
                    "exercise_target_type": _safe_get(ex, "target_type", ""),
                    "exercise_finished_at": _safe_get(ex, "finished_at", ""),
                    "exercise_muscles": muscles_str,
                    "exercise_equipments": _join_list(ex.get("equipments", [])),
                    "exercise_rest_timer": _safe_get(ex, "rest_timer", ""),
                }

                sets = ex.get("sets", [])
                if not isinstance(sets, list) or not sets:
                    rows.append({**session_ctx, **ex_ctx})
                    continue

                for idx, s in enumerate(sets, start=1):
                    row = {
                        **session_ctx,
                        **ex_ctx,
                        "set_index": idx,
                        "set_value_weight": _safe_get(s, "value", ""),
                        "set_amount_reps": _safe_get(s, "amount", ""),
                        "set_target_type": _safe_get(s, "target_type", ex_ctx["exercise_target_type"]),
                        "set_weight_unit": _safe_get(s, "weight_unit", ""),
                        "set_time_unit": _safe_get(s, "time_unit", ""),
                        "set_custom": _safe_get(s, "custom", ""),
                        "set_source": _safe_get(s, "source", ""),
                        "set_skipped": _safe_get(s, "skipped", ""),
                        "set_isCopyLast": _safe_get(s, "isCopyLast", False),
                        "set_valueEmpty": _safe_get(s, "valueEmpty", ""),
                        "set_amountEmpty": _safe_get(s, "amountEmpty", ""),
                        "archived_rpe": _safe_get(s, "archived_rpe", ""),
                        "previous_rpe": _safe_get(s, "previous_rpe", ""),
                        "archived_reps": _safe_get(s, "archived_reps", ""),
                        "previous_reps": _safe_get(s, "previous_reps", ""),
                        "archived_weight": _safe_get(s, "archived_weight", ""),
                        "previous_weight": _safe_get(s, "previous_weight", ""),
                        "previous_time": _safe_get(s, "previous_time", ""),
                    }
                    rows.append(row)

    df = pd.DataFrame(rows)
    cols = [c for c in preferred_cols if c in df.columns]
    return df[cols]


def run(in_path: Path, csv_out: Path, xlsx_out: Path) -> None:
    with in_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    df = flatten_payload(payload)
    df.to_csv(csv_out, index=False)
    with pd.ExcelWriter(xlsx_out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="workout_sets")


if __name__ == "__main__":
    # Default behavior: read 'example_data_payload.txt' in current dir and write outputs next to it.
    input_path = Path("example_data_payload.txt")
    csv_path = Path("workout_sets.csv")
    xlsx_path = Path("workout_sets.xlsx")
    run(input_path, csv_path, xlsx_path)
