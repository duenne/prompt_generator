from prompt_generator import (
    PromptRequest,
    build_prompt,
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

    assert "Zieltyp: Create new feature" in prompt_text
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
