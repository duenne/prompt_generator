from prompt_generator import (
    PromptRequest,
    build_prompt,
    evaluate_prompt_quality,
    get_target_options,
    load_shared_rules,
)


def test_build_prompt_contains_goal_and_scenario() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        goal="Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen.",
        requirements="Python 3.11 und pytest-Tests.",
        scenario="Teil einer lokalen Lern-App.",
    )

    prompt_text = build_prompt(request)

    assert "Prompt-Typ: LLM (einmalige Antwort)" in prompt_text
    assert "- Zieltyp: Create new feature" in prompt_text
    assert "Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen." in prompt_text
    assert "Teil einer lokalen Lern-App." in prompt_text
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


def test_evaluate_prompt_quality_detects_missing_details() -> None:
    request = PromptRequest(
        persona_name="tutor",
        target_key="explain_concept",
        goal="Rekursion",
        requirements="",
        scenario="Kurz",
    )

    result = evaluate_prompt_quality(request)

    assert result.score == 1
    assert result.max_score == 3
    assert any("Kein klares Output-Format erkannt" in item for item in result.feedback)
    assert "Output-Format" in result.suggestion


def test_evaluate_prompt_quality_rewards_structured_input() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        goal="Erstelle eine Funktion, die Vorlesungsnotizen bereinigt und Überschriften extrahiert.",
        requirements="Bitte als Markdown-Liste mit JSON-Beispiel ausgeben.",
        scenario="Die Ausgabe wird in einer Lern-App für Erstsemester angezeigt.",
    )

    result = evaluate_prompt_quality(request)

    assert result.score == 3
    assert result.max_score == 3


def test_build_agent_prompt_uses_agent_structure() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        goal="Implementiere eine Parser-Pipeline für strukturierte Notizen.",
        requirements="Python 3.11, keine externen APIs.",
        scenario="Wird lokal in einer Lern-App ausgeführt.",
        prompt_type="agent",
    )

    prompt_text = build_prompt(request)

    assert "Prompt-Typ: Agent (iterativer Arbeitsprozess)" in prompt_text
    assert "Arbeitsweise (Schritte / Iteration):" in prompt_text
    assert "Output pro Schritt:" in prompt_text
    assert "Constraints:" in prompt_text


def test_evaluate_agent_prompt_quality_detects_missing_constraints() -> None:
    request = PromptRequest(
        persona_name="tester",
        target_key="review_code",
        goal="Code prüfen",
        requirements="",
        scenario="Review für ein internes Tool.",
        prompt_type="agent",
    )

    result = evaluate_prompt_quality(request)

    assert result.max_score == 3
    assert any("Keine Constraints" in item for item in result.feedback)
    assert any("Ziel ist noch vage" in item for item in result.feedback)
