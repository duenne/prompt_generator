from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_COLUMNS = [
    "date",
    "source",
    "tool",
    "interface",
    "task",
    "model",
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "reasoning_tokens",
    "total_tokens",
    "estimation_method",
    "confidence",
    "estimated",
    "notes",
]

MANUAL_COLUMNS = [
    "date",
    "tool",
    "interface",
    "task",
    "model",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "source_of_numbers",
    "estimated",
    "notes",
]

TOKEN_FIELDS = [
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "reasoning_tokens",
    "total_tokens",
]


def extract_usage_metrics(obj: Any) -> dict[str, int]:
    totals = {field: 0 for field in TOKEN_FIELDS}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for field in TOKEN_FIELDS:
                value = node.get(field)
                if isinstance(value, (int, float)):
                    totals[field] += int(value)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj)
    return totals


def estimate_event_char_counts(payload: dict[str, Any]) -> tuple[int, int]:
    input_keys = ["message", "input"]
    output_keys = ["last_agent_message", "output", "content", "summary"]

    def first_string(keys: list[str]) -> int:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str):
                return len(value)
        return 0

    return first_string(input_keys), first_string(output_keys)


def analyze_history_file(history_path: Path) -> dict[str, Any]:
    summary = {
        "entries": 0,
        "unique_sessions": 0,
        "first_timestamp": "",
        "last_timestamp": "",
    }
    if not history_path.exists():
        return summary

    session_ids: set[str] = set()
    timestamps: list[str] = []

    with history_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            summary["entries"] += 1
            session_id = obj.get("session_id")
            if isinstance(session_id, str) and session_id:
                session_ids.add(session_id)
            timestamp = obj.get("ts")
            if isinstance(timestamp, str) and timestamp:
                timestamps.append(timestamp)
            elif isinstance(timestamp, (int, float)):
                timestamps.append(
                    datetime.fromtimestamp(
                        float(timestamp) / 1000 if float(timestamp) > 10_000_000_000 else float(timestamp),
                        tz=timezone.utc,
                    ).isoformat()
                )

    summary["unique_sessions"] = len(session_ids)
    if timestamps:
        summary["first_timestamp"] = min(timestamps)
        summary["last_timestamp"] = max(timestamps)
    return summary


def extract_date_from_path(session_path: Path) -> str:
    parts = session_path.parts
    if len(parts) >= 4:
        for i in range(len(parts) - 3):
            y, m, d = parts[i : i + 3]
            if len(y) == 4 and y.isdigit() and len(m) == 2 and m.isdigit() and len(d) == 2 and d.isdigit():
                return f"{y}-{m}-{d}"
    return datetime.fromtimestamp(
        session_path.stat().st_mtime,
        tz=timezone.utc,
    ).strftime("%Y-%m-%d")


def analyze_session_file(session_path: Path) -> dict[str, str]:
    row, _exact_usage, _models = analyze_session_file_detailed(session_path)
    return row


def analyze_session_file_detailed(session_path: Path) -> tuple[dict[str, str], bool, list[str]]:
    usage_totals = {field: 0 for field in TOKEN_FIELDS}
    exact_usage = False
    model_counter: Counter[str] = Counter()
    provider_counter: Counter[str] = Counter()
    input_chars = 0
    output_chars = 0
    event_count = 0

    with session_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue

            event_count += 1
            metrics = extract_usage_metrics(obj)
            if any(value > 0 for value in metrics.values()):
                exact_usage = True
                for field, value in metrics.items():
                    usage_totals[field] += value

            payload = obj.get("payload")
            if isinstance(payload, dict):
                model = payload.get("model")
                provider = payload.get("model_provider")
                if isinstance(model, str) and model:
                    model_counter[model] += 1
                if isinstance(provider, str) and provider:
                    provider_counter[provider] += 1
                chars_in, chars_out = estimate_event_char_counts(payload)
                input_chars += chars_in
                output_chars += chars_out

    if exact_usage:
        input_tokens = usage_totals["input_tokens"]
        output_tokens = usage_totals["output_tokens"]
        cached_input_tokens = usage_totals["cached_input_tokens"]
        reasoning_tokens = usage_totals["reasoning_tokens"]
        total_tokens = usage_totals["total_tokens"]
        if total_tokens == 0:
            total_tokens = (
                input_tokens
                + output_tokens
                + cached_input_tokens
                + reasoning_tokens
            )
        estimation_method = "metadata_usage_fields"
        confidence = "high"
        estimated = "false"
    elif input_chars or output_chars:
        input_tokens = math.ceil(input_chars / 4)
        output_tokens = math.ceil(output_chars / 4)
        cached_input_tokens = 0
        reasoning_tokens = 0
        total_tokens = input_tokens + output_tokens
        estimation_method = "message_chars_div_4"
        confidence = "medium"
        estimated = "true"
    else:
        file_bytes = session_path.stat().st_size
        total_tokens = math.ceil(file_bytes / 4)
        input_tokens = ""
        output_tokens = ""
        cached_input_tokens = ""
        reasoning_tokens = ""
        estimation_method = "file_bytes_div_4"
        confidence = "low"
        estimated = "true"

    date = extract_date_from_path(session_path)
    if date.isdigit():
        date = ""
    model = model_counter.most_common(1)[0][0] if model_counter else "unknown"
    provider = provider_counter.most_common(1)[0][0] if provider_counter else "unknown"

    row = {
        "date": date,
        "source": "local_codex_cli",
        "tool": "Codex",
        "interface": "cli",
        "task": "Local Codex CLI session",
        "model": model,
        "input_tokens": str(input_tokens) if input_tokens != "" else "",
        "output_tokens": str(output_tokens) if output_tokens != "" else "",
        "cached_input_tokens": str(cached_input_tokens) if cached_input_tokens != "" else "",
        "reasoning_tokens": str(reasoning_tokens) if reasoning_tokens != "" else "",
        "total_tokens": str(total_tokens),
        "estimation_method": estimation_method,
        "confidence": confidence,
        "estimated": estimated,
        "notes": (
            "Session file structurally analyzed without exporting prompt or response content; "
            f"events={event_count}; model_provider={provider}"
        ),
    }
    return row, exact_usage, list(model_counter.keys())


def find_local_sources(project_root: Path) -> dict[str, Path]:
    home = Path.home()
    return {
        "home_codex": home / ".codex",
        "home_sessions": home / ".codex" / "sessions",
        "home_history": home / ".codex" / "history.jsonl",
        "project_codex": project_root / ".codex",
        "project_agents": project_root / ".agents",
    }


def list_session_files(sessions_root: Path) -> list[Path]:
    if not sessions_root.exists():
        return []
    return sorted(sessions_root.rglob("*.jsonl"))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def ensure_manual_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return

    rows = [
        {
            "date": "2026-06-18",
            "tool": "ChatGPT",
            "interface": "web",
            "task": "Tutorial und MkDocs-Prompts",
            "model": "TODO",
            "input_tokens": "TODO",
            "output_tokens": "TODO",
            "total_tokens": "TODO",
            "source_of_numbers": "manual estimate",
            "estimated": "true",
            "notes": "TODO: aus Chatverlauf oder Account-Usage ergänzen",
        },
        {
            "date": "2026-06-18",
            "tool": "Codex",
            "interface": "web",
            "task": "Repository-Dokumentation",
            "model": "TODO",
            "input_tokens": "TODO",
            "output_tokens": "TODO",
            "total_tokens": "TODO",
            "source_of_numbers": "manual estimate",
            "estimated": "true",
            "notes": "TODO: aus Web-Interface oder manueller Schätzung ergänzen",
        },
        {
            "date": "2026-06-18",
            "tool": "Claude",
            "interface": "web",
            "task": "Review der Dokumentation",
            "model": "TODO",
            "input_tokens": "TODO",
            "output_tokens": "TODO",
            "total_tokens": "TODO",
            "source_of_numbers": "manual estimate",
            "estimated": "true",
            "notes": "TODO: aus Claude Usage oder manueller Schätzung ergänzen",
        },
    ]

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANUAL_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _to_int(value: str) -> int | None:
    if not value:
        return None
    if value == "TODO":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def load_manual_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    summary = {
        "entries": len(rows),
        "input_tokens_known": 0,
        "output_tokens_known": 0,
        "cached_input_tokens_known": 0,
        "reasoning_tokens_known": 0,
        "input_tokens_estimated": 0,
        "output_tokens_estimated": 0,
        "cached_input_tokens_estimated": 0,
        "reasoning_tokens_estimated": 0,
        "total_tokens_known": 0,
        "total_tokens_estimated": 0,
        "estimated_rows": 0,
        "exact_rows": 0,
        "date_min": "",
        "date_max": "",
    }

    dates = [row["date"] for row in rows if row.get("date")]
    if dates:
        summary["date_min"] = min(dates)
        summary["date_max"] = max(dates)

    for row in rows:
        estimated = row.get("estimated", "").lower() == "true"
        if estimated:
            summary["estimated_rows"] += 1
        else:
            summary["exact_rows"] += 1

        input_tokens = _to_int(row.get("input_tokens", ""))
        output_tokens = _to_int(row.get("output_tokens", ""))
        cached_input_tokens = _to_int(row.get("cached_input_tokens", ""))
        reasoning_tokens = _to_int(row.get("reasoning_tokens", ""))
        total_tokens = _to_int(row.get("total_tokens", ""))

        if input_tokens is not None:
            if estimated:
                summary["input_tokens_estimated"] += input_tokens
            else:
                summary["input_tokens_known"] += input_tokens
        if output_tokens is not None:
            if estimated:
                summary["output_tokens_estimated"] += output_tokens
            else:
                summary["output_tokens_known"] += output_tokens
        if cached_input_tokens is not None:
            if estimated:
                summary["cached_input_tokens_estimated"] += cached_input_tokens
            else:
                summary["cached_input_tokens_known"] += cached_input_tokens
        if reasoning_tokens is not None:
            if estimated:
                summary["reasoning_tokens_estimated"] += reasoning_tokens
            else:
                summary["reasoning_tokens_known"] += reasoning_tokens
        if total_tokens is not None:
            if estimated:
                summary["total_tokens_estimated"] += total_tokens
            else:
                summary["total_tokens_known"] += total_tokens

    return summary


def summarize_manual_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_rows = []
    for row in rows:
        if any(_to_int(row.get(field, "")) is not None for field in ["input_tokens", "output_tokens", "total_tokens"]):
            valid_rows.append(row)
    summary = {
        "entries": len(valid_rows),
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "estimated_rows": 0,
    }
    for row in valid_rows:
        summary["input_tokens"] += _to_int(row.get("input_tokens", "")) or 0
        summary["output_tokens"] += _to_int(row.get("output_tokens", "")) or 0
        summary["total_tokens"] += _to_int(row.get("total_tokens", "")) or 0
        if row.get("estimated", "").lower() == "true":
            summary["estimated_rows"] += 1
    return summary


def write_summary(
    summary_path: Path,
    local_summary: dict[str, Any],
    manual_summary: dict[str, Any],
    history_summary: dict[str, Any],
    source_paths: dict[str, Path],
) -> None:
    local_date_range = "TODO: manuell ergänzen"
    if local_summary["date_min"] and local_summary["date_max"]:
        local_date_range = f'{local_summary["date_min"]} bis {local_summary["date_max"]}'

    local_known_total = local_summary["total_tokens_known"]
    local_estimated_total = local_summary["total_tokens_estimated"]
    local_total_display = str(local_known_total + local_estimated_total) if (local_known_total + local_estimated_total) else "0"
    manual_total_display = str(manual_summary["total_tokens"]) if manual_summary["entries"] else "TODO: manuell ergänzen"
    manual_input_display = str(manual_summary["input_tokens"]) if manual_summary["entries"] else "TODO: manuell ergänzen"
    manual_output_display = str(manual_summary["output_tokens"]) if manual_summary["entries"] else "TODO: manuell ergänzen"

    lines = [
        "# Token-Nutzungsstatistik",
        "",
        "Diese Statistik dokumentiert die KI-Nutzung im Projekt. Exakte Werte sind nur dort angegeben, wo sie aus Tool-Metadaten ableitbar waren. Geschätzte Werte sind entsprechend markiert.",
        "",
        "## Zeitraum der Auswertung",
        "",
        f"- Lokale Codex-CLI-Sessions: {local_date_range}",
        f"- Verlaufshistorie (`history.jsonl`): {history_summary['first_timestamp'] or 'unbekannt'} bis {history_summary['last_timestamp'] or 'unbekannt'}",
        "",
        "## Verwendete Quellen",
        "",
        f"- `~/.codex/sessions/`: {'vorhanden' if source_paths['home_sessions'].exists() else 'nicht gefunden'}",
        f"- `~/.codex/history.jsonl`: {'vorhanden' if source_paths['home_history'].exists() else 'nicht gefunden'}",
        f"- Projektpfad `.codex/`: {'vorhanden' if source_paths['project_codex'].exists() else 'nicht gefunden'}",
        f"- Projektpfad `.agents/`: {'vorhanden' if source_paths['project_agents'].exists() else 'nicht gefunden'}",
        f"- Manuelle Web-Schablone: `docs/ai/manual-web-usage-template.csv`",
        "",
        "## Zusammenfassung",
        "",
        "| Quelle | Sessions / Einträge | Input Tokens | Output Tokens | Gesamttokens | Schätzung |",
        "|---|---:|---:|---:|---:|---|",
        f"| Codex CLI lokal | {local_summary['entries']} | {local_summary['input_tokens_known']} | {local_summary['output_tokens_known']} | {local_total_display} | teilweise |",
        f"| Web Interface manuell | {manual_summary['entries']} | {manual_input_display} | {manual_output_display} | {manual_total_display} | ja |",
        "",
        "## Lokale Codex-Auswertung",
        "",
        f"- Erkannte lokale Codex-Sessions: {local_summary['entries']}",
        f"- Exakte Token-Metadaten-Sessions: {local_summary['exact_rows']}",
        f"- Geschätzte Sessions: {local_summary['estimated_rows']}",
        f"- Summe bekannter Input Tokens: {local_summary['input_tokens_known']}",
        f"- Summe geschätzter Input Tokens: {local_summary['input_tokens_estimated']}",
        f"- Summe bekannter Output Tokens: {local_summary['output_tokens_known']}",
        f"- Summe geschätzter Output Tokens: {local_summary['output_tokens_estimated']}",
        f"- Summe bekannter Cached Input Tokens: {local_summary['cached_input_tokens_known']}",
        f"- Summe geschätzter Cached Input Tokens: {local_summary['cached_input_tokens_estimated']}",
        f"- Summe bekannter Reasoning Tokens: {local_summary['reasoning_tokens_known']}",
        f"- Summe geschätzter Reasoning Tokens: {local_summary['reasoning_tokens_estimated']}",
        f"- Summe exakter Gesamttokens: {local_summary['total_tokens_known']}",
        f"- Summe geschätzter Gesamttokens: {local_summary['total_tokens_estimated']}",
        "",
        "## Ergänzende Verlaufshistorie",
        "",
        f"- Einträge in `history.jsonl`: {history_summary['entries']}",
        f"- Eindeutige Session-IDs in `history.jsonl`: {history_summary['unique_sessions']}",
        "- Diese Verlaufshistorie wurde nur als ergänzende Metadatenquelle betrachtet und nicht für Token-Summen verwendet.",
        "",
        "## Methodik",
        "",
        "- Exakte Tokenwerte wurden nur übernommen, wenn sie als Metadatenfelder in lokalen Session-Strukturen vorhanden waren.",
        "- Wenn keine exakten Usage-Felder vorhanden waren, wurde konservativ auf Basis strukturierter Nachrichtenfelder geschätzt.",
        "- Die Hauptschätzung basiert auf `tokens ≈ Zeichen / 4`.",
        "- Wenn nicht einmal geeignete Zeichenlängen verfügbar wären, würde als Fallback `tokens ≈ Bytes / 4` verwendet.",
        "- Prompt- und Antwortinhalte wurden nicht veröffentlicht oder in die Dokumentation übernommen.",
        "",
        "## Grenzen",
        "",
        "- Die lokale Auswertung deckt nur Daten auf diesem Rechner ab.",
        "- Web-Interface-Nutzung muss manuell ergänzt werden.",
        "- Tool-interne Abrechnung kann von lokalen Schätzungen abweichen.",
        "- Cached Input Tokens und Reasoning Tokens sind nur sichtbar, wenn das Tool sie als Metadaten bereitstellt.",
    ]

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_rows(project_root: Path) -> tuple[list[dict[str, str]], dict[str, Any], dict[str, Any], dict[str, Path]]:
    source_paths = find_local_sources(project_root)
    session_files = list_session_files(source_paths["home_sessions"])
    rows = [analyze_session_file(path) for path in session_files]
    local_summary = summarize_rows(rows)
    history_summary = analyze_history_file(source_paths["home_history"])
    return rows, local_summary, history_summary, source_paths


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    docs_ai = project_root / "docs" / "ai"
    token_csv_path = docs_ai / "token-usage.csv"
    summary_path = docs_ai / "token-usage-summary.md"
    manual_template_path = docs_ai / "manual-web-usage-template.csv"

    ensure_manual_template(manual_template_path)
    rows, local_summary, history_summary, source_paths = build_rows(project_root)
    write_csv(token_csv_path, rows)
    manual_rows = load_manual_rows(manual_template_path)
    manual_summary = summarize_manual_rows(manual_rows)
    write_summary(summary_path, local_summary, manual_summary, history_summary, source_paths)

    print(f"Wrote {token_csv_path}")
    print(f"Wrote {summary_path}")
    print(f"Local Codex sessions analyzed: {local_summary['entries']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
