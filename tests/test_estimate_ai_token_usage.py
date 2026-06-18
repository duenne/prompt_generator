from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "estimate_ai_token_usage.py"
    )
    spec = importlib.util.spec_from_file_location(
        "estimate_ai_token_usage",
        module_path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_extract_usage_metrics_reads_nested_usage_fields() -> None:
    module = load_module()

    payload = {
        "type": "response_item",
        "payload": {
            "usage": {
                "input_tokens": 100,
                "output_tokens": 20,
                "cached_input_tokens": 5,
                "reasoning_tokens": 7,
                "total_tokens": 132,
            }
        },
    }

    result = module.extract_usage_metrics(payload)

    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 20
    assert result["cached_input_tokens"] == 5
    assert result["reasoning_tokens"] == 7
    assert result["total_tokens"] == 132


def test_estimate_event_char_counts_uses_safe_string_fields() -> None:
    module = load_module()

    payload = {
        "message": "abcd",
        "last_agent_message": "abcdefgh",
        "summary": "ignored because higher priority field exists",
    }

    input_chars, output_chars = module.estimate_event_char_counts(payload)

    assert input_chars == 4
    assert output_chars == 8


def test_analyze_session_file_falls_back_to_character_estimate(tmp_path: Path) -> None:
    module = load_module()
    session_file = tmp_path / "rollout-2026-06-18T10-00-00-test.jsonl"
    rows = [
        {
            "type": "session_meta",
            "timestamp": "2026-06-18T10:00:00Z",
            "payload": {"model": "gpt-5-codex"},
        },
        {
            "type": "event_msg",
            "timestamp": "2026-06-18T10:01:00Z",
            "payload": {"message": "abcdefgh"},
        },
        {
            "type": "response_item",
            "timestamp": "2026-06-18T10:01:05Z",
            "payload": {"last_agent_message": "abcdefghijkl"},
        },
    ]
    session_file.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    result = module.analyze_session_file(session_file)

    assert result["model"] == "gpt-5-codex"
    assert result["estimated"] == "true"
    assert result["estimation_method"] == "message_chars_div_4"
    assert result["confidence"] == "medium"
    assert result["input_tokens"] == "2"
    assert result["output_tokens"] == "3"
    assert result["total_tokens"] == "5"


def test_analyze_history_file_counts_entries_without_exposing_text(tmp_path: Path) -> None:
    module = load_module()
    history_file = tmp_path / "history.jsonl"
    rows = [
        {"session_id": "a", "text": "x", "ts": "2026-06-17T10:00:00Z"},
        {"session_id": "a", "text": "y", "ts": "2026-06-17T10:05:00Z"},
        {"session_id": "b", "text": "z", "ts": "2026-06-18T10:05:00Z"},
    ]
    history_file.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    result = module.analyze_history_file(history_file)

    assert result["entries"] == 3
    assert result["unique_sessions"] == 2
    assert result["first_timestamp"] == "2026-06-17T10:00:00Z"
    assert result["last_timestamp"] == "2026-06-18T10:05:00Z"
