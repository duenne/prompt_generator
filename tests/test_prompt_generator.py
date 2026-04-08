from prompt_generator import PromptRequest, build_prompt, load_shared_rules


def test_build_prompt_contains_goal_and_scenario() -> None:
    request = PromptRequest(
        persona_name="engineer",
        goal="Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen.",
        requirements="Python 3.11 und pytest-Tests.",
        scenario="Teil einer lokalen Lern-App.",
    )

    prompt_text = build_prompt(request)

    assert "Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen." in prompt_text
    assert "Teil einer lokalen Lern-App." in prompt_text
    assert "Coding Rules:" in prompt_text


def test_tutor_prompt_does_not_include_engineer_only_rules() -> None:
    shared_rules = load_shared_rules("tutor")
    joined_rules = "\n".join(shared_rules)
    assert "Python 3.11" not in joined_rules


def test_engineer_prompt_includes_coding_rules() -> None:
    shared_rules = load_shared_rules("engineer")
    joined_rules = "\n".join(shared_rules)
    assert "Python 3.11" in joined_rules
    assert "pytest-Tests" in joined_rules
