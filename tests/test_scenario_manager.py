from pathlib import Path
import pytest

from scenario_manager import ScenarioManager


def test_create_scenario(tmp_path: Path) -> None:
    manager = ScenarioManager(tmp_path)
    scenario = manager.create_scenario(
        name="user_conversation",
        content="Ich spreche mit einem fachlichen Ansprechpartner und erhebe die Anforderung.",
        description="Initiale Version für Anforderungsaufnahme.",
    )

    assert scenario.name == "user_conversation"
    assert scenario.current_version == "v1.0"
    assert "v1.0" in scenario.versions
    assert scenario.versions["v1.0"].content.startswith("Ich spreche")


def test_update_scenario_creates_new_version(tmp_path: Path) -> None:
    manager = ScenarioManager(tmp_path)
    manager.create_scenario(
        name="user_conversation",
        content="Erste Version.",
        description="Initiale Version.",
    )

    updated = manager.update_scenario(
        name="user_conversation",
        content="Zweite Version mit Ergänzungen.",
        description="Erweiterte Version.",
    )

    assert updated.current_version == "v2.0"
    assert "v2.0" in updated.versions
    assert updated.versions["v2.0"].content == "Zweite Version mit Ergänzungen."


def test_get_scenario_returns_current_and_specific_versions(tmp_path: Path) -> None:
    manager = ScenarioManager(tmp_path)
    manager.create_scenario(
        name="user_conversation",
        content="Inhalt v1.",
        description="Version 1.",
    )
    manager.update_scenario(
        name="user_conversation",
        content="Inhalt v2.",
        description="Version 2.",
    )

    current = manager.get_scenario("user_conversation")
    assert current is not None
    assert current.version == "v2.0"
    assert current.content == "Inhalt v2."

    first = manager.get_scenario("user_conversation", "v1.0")
    assert first is not None
    assert first.content == "Inhalt v1."


def test_list_scenarios(tmp_path: Path) -> None:
    manager = ScenarioManager(tmp_path)
    manager.create_scenario("scenario_one", "A", "A1")
    manager.create_scenario("scenario_two", "B", "B1")

    names = manager.list_scenarios()
    assert set(names) == {"scenario_one", "scenario_two"}


def test_create_duplicate_scenario_raises_error(tmp_path: Path) -> None:
    manager = ScenarioManager(tmp_path)
    manager.create_scenario("duplicate", "A", "A1")

    with pytest.raises(ValueError, match="existiert bereits"):
        manager.create_scenario("duplicate", "B", "B2")


def test_persistence_loads_saved_scenario(tmp_path: Path) -> None:
    manager = ScenarioManager(tmp_path)
    manager.create_scenario(
        name="persistent",
        content="Persistenter Inhalt.",
        description="Initial.",
    )

    manager = ScenarioManager(tmp_path)
    scenario = manager.get_scenario("persistent")

    assert scenario is not None
    assert scenario.content == "Persistenter Inhalt."
