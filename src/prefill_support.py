from __future__ import annotations

import re
from dataclasses import dataclass
from prompt_generator import GENERATED_PROMPTS_DIR


FIELD_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "llm": {
        "llm_role": [
            "Didaktisch starker Tutor für Informatik-Studierende",
            "Präziser Software Engineer",
            "Strenger Tester mit Fokus auf Edge Cases",
        ],
        "llm_context": [
            "Erkläre auf Bachelor-Niveau mit klarer Struktur.",
            "Nutze kurze Abschnitte und konkrete Beispiele.",
            "Berücksichtige, dass der Nutzer Grundkenntnisse hat.",
        ],
        "llm_output_format": [
            "Antwort in 3 Abschnitten: Definition, Beispiel, Fallstricke.",
            "Antworte als nummerierte Liste.",
            "Gib zuerst die Kurzfassung, dann die Details.",
        ],
    },
    "agent": {
        "agent_workflow": [
            "Zuerst analysieren, dann planen, dann minimal umsetzen.",
            "Nur eine Atomic Capability pro Iteration.",
            "Nach jedem Schritt die nächste kleinste sinnvolle Verbesserung wählen.",
        ],
        "agent_verification": [
            "Zeige vorher/nachher Verhalten.",
            "Beschreibe, wie ein Nutzer die Änderung testen kann.",
            "Prüfe, ob die Änderung wirklich die Prompt-Qualität verbessert.",
        ],
    },
}


@dataclass
class PromptHistoryEntry:
    filename: str
    prompt_type: str
    fields: dict[str, str]


def get_field_templates(prompt_type: str, field_key: str) -> list[str]:
    normalized_prompt_type = prompt_type.lower().strip()
    return FIELD_TEMPLATES.get(normalized_prompt_type, {}).get(field_key, [])


def load_prompt_history(limit: int = 30) -> list[PromptHistoryEntry]:
    if not GENERATED_PROMPTS_DIR.exists():
        return []

    files = sorted(
        GENERATED_PROMPTS_DIR.glob("*.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]

    entries: list[PromptHistoryEntry] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        entries.append(
            PromptHistoryEntry(
                filename=path.name,
                prompt_type=_detect_prompt_type(text),
                fields=_extract_prompt_fields(text),
            )
        )
    return entries


def _detect_prompt_type(prompt_text: str) -> str:
    if "Prompt-Typ: Agent" in prompt_text:
        return "agent"
    return "llm"


def _extract_prompt_fields(prompt_text: str) -> dict[str, str]:
    prompt_type = _detect_prompt_type(prompt_text)
    if prompt_type == "agent":
        return {
            "agent_goal": _extract_between(prompt_text, "Ziel:\n", "\nKontext:"),
            "agent_context": _extract_between(prompt_text, "Kontext:\n", "\nConstraints:"),
            "agent_constraints": _extract_between(prompt_text, "Constraints:\n", "\nArbeitsweise:"),
            "agent_workflow": _extract_between(prompt_text, "Arbeitsweise:\n", "\nVerifikation:"),
            "agent_verification": _extract_between(prompt_text, "Verifikation:\n", "\nMeta-Regel:"),
        }

    role_match = re.search(r"Rolle:\n(.+)", prompt_text)
    return {
        "llm_role": role_match.group(1).strip() if role_match else "",
        "llm_context": _extract_between(prompt_text, "Kontext:\n", "\nAufgabe:"),
        "llm_task": _extract_between(prompt_text, "Aufgabe:\n", "\nAnforderungen:"),
        "llm_requirements": _extract_between(prompt_text, "Anforderungen:\n", "\nOutput-Format:"),
        "llm_output_format": _extract_between(
            prompt_text,
            "Output-Format:\n",
            "\nBeispiele (optional):",
            fallback_end="\nMeta-Regel:",
        ),
        "llm_examples": _extract_between(prompt_text, "Beispiele (optional):\n", "\nMeta-Regel:"),
    }


def _extract_between(
    text: str,
    start: str,
    end: str,
    fallback_end: str | None = None,
) -> str:
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.S)
    if match:
        return match.group(1).strip()
    if fallback_end:
        fallback_match = re.search(
            re.escape(start) + r"(.*?)" + re.escape(fallback_end),
            text,
            re.S,
        )
        if fallback_match:
            return fallback_match.group(1).strip()
    return ""
