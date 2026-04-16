from prompt_generator import (
    PromptRequest,
    build_prompt,
    evaluate_prompt_quality,
    get_target_options,
    load_shared_rules,
)


def test_build_llm_prompt_contains_structured_sections() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        prompt_type="llm",
        llm_role="Senior Python Engineer",
        llm_context="Teil einer lokalen Lern-App mit Fokus auf Notizverarbeitung.",
        llm_task="Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen.",
        llm_requirements="Python 3.11, präzise, mit Testhinweisen.",
        llm_output_format="Markdown mit Tabelle",
    )

    prompt_text = build_prompt(request)

    assert "Prompt-Typ: LLM (einmalige Antwort)" in prompt_text
    assert "Rolle:\nSenior Python Engineer" in prompt_text
    assert "Aufgabe:" in prompt_text
    assert "Output-Format:" in prompt_text
    assert "Markdown mit Tabelle" in prompt_text
    assert "Coding Rules:" in prompt_text


def test_get_target_options_returns_engineer_targets() -> None:
    target_options = get_target_options("engineer")
    assert "create_new_feature" in target_options
    assert target_options["create_new_feature"] == "Create new feature"


def test_tutor_prompt_does_not_include_engineer_only_rules() -> None:
    shared_rules = load_shared_rules("tutor")
    joined_rules = "\n".join(shared_rules)
    assert "Python 3.11" not in joined_rules


def test_engineer_prompt_includes_coding_rules() -> None:
    shared_rules = load_shared_rules("engineer")
    joined_rules = "\n".join(shared_rules)
    assert "Python 3.11" in joined_rules
    assert "pytest-Tests" in joined_rules


def test_evaluate_llm_prompt_quality_detects_missing_details() -> None:
    request = PromptRequest(
        persona_name="tutor",
        target_key="explain_concept",
        prompt_type="llm",
        llm_task="",
        llm_context="Kurz",
        llm_requirements="gut",
        llm_output_format="",
    )

    result = evaluate_prompt_quality(request)

    assert result.score == 0
    assert result.max_score == 4
    assert any("Aufgabe fehlt" in item for item in result.feedback)
    assert any("Kontext ist zu knapp" in item for item in result.feedback)
    assert any("Kein Output-Format" in item for item in result.feedback)


def test_evaluate_llm_prompt_quality_rewards_structured_input() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        prompt_type="llm",
        llm_task="Erstelle eine Funktion, die Vorlesungsnotizen bereinigt und Überschriften extrahiert.",
        llm_context="Die Ausgabe wird in einer Lern-App für Erstsemester angezeigt und direkt gerendert.",
        llm_requirements="Deutsch, fachlich korrekt, mit Edge-Cases und technischen Randbedingungen.",
        llm_output_format="Markdown mit H2, Bullet-Points und Beispieltabelle.",
    )

    result = evaluate_prompt_quality(request)

    assert result.score == 4
    assert result.max_score == 4


def test_build_agent_prompt_uses_agent_structure() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        prompt_type="agent",
        agent_goal="Implementiere eine Parser-Pipeline für strukturierte Notizen.",
        agent_context="Wird lokal in einer Lern-App ausgeführt.",
        agent_constraints="Python 3.11, keine externen APIs.",
        agent_workflow="1) Analyse 2) Plan 3) Umsetzung 4) Review",
        agent_verification="pytest + manueller Smoke-Test",
    )

    prompt_text = build_prompt(request)

    assert "Prompt-Typ: Agent (iterativer Arbeitsprozess)" in prompt_text
    assert "Arbeitsweise:" in prompt_text
    assert "Verifikation:" in prompt_text
    assert "Done when:" not in prompt_text
    assert "Constraints:" in prompt_text


def test_evaluate_agent_prompt_quality_detects_missing_fields() -> None:
    request = PromptRequest(
        persona_name="tester",
        target_key="review_code",
        prompt_type="agent",
        agent_goal="Code verbessern",
        agent_constraints="",
        agent_workflow="",
        agent_verification="",
    )

    result = evaluate_prompt_quality(request)

    assert result.max_score == 4
    assert any("Ziel ist zu vage" in item for item in result.feedback)
    assert any("Keine Constraints" in item for item in result.feedback)
    assert any("Keine Arbeitsweise" in item for item in result.feedback)
    assert any("Keine Verifikation" in item for item in result.feedback)
