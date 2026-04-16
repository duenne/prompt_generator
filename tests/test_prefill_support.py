from prefill_support import _extract_prompt_fields, _extract_between, get_field_templates


def test_get_field_templates_contains_structuring_blocks() -> None:
    assert "Didaktisch" in get_field_templates("llm", "llm_role")[0]
    assert get_field_templates("agent", "agent_workflow")


def test_extract_prompt_fields_for_llm_prompt() -> None:
    prompt_text = """Prompt-Typ: LLM (einmalige Antwort)
Rolle:
Präziser Software Engineer
Zieltyp: Explain code
Kontext:
Nutze kurze Abschnitte und konkrete Beispiele.
Aufgabe:
Erkläre die bestehende Funktion Schritt für Schritt.
Anforderungen:
Nenne Trade-offs und Randfälle.
Output-Format:
Antworte als nummerierte Liste.
Meta-Regel: Liefere genau eine strukturierte, abgeschlossene Antwort mit minimaler Ambiguität.
"""

    fields = _extract_prompt_fields(prompt_text)

    assert fields["llm_role"] == "Präziser Software Engineer"
    assert "kurze Abschnitte" in fields["llm_context"]
    assert fields["llm_output_format"] == "Antworte als nummerierte Liste."


def test_extract_prompt_fields_for_agent_prompt() -> None:
    prompt_text = """Prompt-Typ: Agent (iterativer Arbeitsprozess)
Ziel:
Verbessere den aktuellen Flow ohne komplettes Redesign.
Kontext:
Nutze den bestehenden Screen und vermeide große Refactorings.
Constraints:
Keine Backend-Integration.
Arbeitsweise:
Zuerst analysieren, dann planen, dann minimal umsetzen.
Verifikation:
Zeige vorher/nachher Verhalten.
Meta-Regel: Trenne Planung und Umsetzung explizit und dokumentiere jede Iteration nachvollziehbar.
"""

    fields = _extract_prompt_fields(prompt_text)

    assert "Flow" in fields["agent_goal"]
    assert fields["agent_workflow"].startswith("Zuerst analysieren")
    assert fields["agent_verification"] == "Zeige vorher/nachher Verhalten."


def test_extract_between_with_fallback() -> None:
    text = "Output-Format:\nA\nMeta-Regel: X"

    assert _extract_between(text, "Output-Format:\n", "\nBeispiele (optional):", fallback_end="\nMeta-Regel:") == "A"
