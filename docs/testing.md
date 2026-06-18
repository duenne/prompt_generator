# Testing

## Überblick

Das Repository enthält automatisierte Tests für die Kernlogik sowie eine UI-Seite zur Darstellung von Testresultaten.

## Test-Framework

Aus `pyproject.toml` und den Testdateien ist ersichtlich:

- Test-Framework: `pytest`
- Testpfad: `tests`
- `pythonpath = ["src"]`

## Vorhandene Testbereiche

| Testdatei | Abgedeckter Bereich |
| --- | --- |
| `tests/test_prompt_builder.py` | Laden und Auffinden von Prompt-Dateien |
| `tests/test_prompt_generator.py` | Prompt-Aufbau, Fallbacks, Zieltypen, Qualitätsbewertung |
| `tests/test_prefill_support.py` | Feldvorlagen und Extraktion aus gespeicherten Prompts |
| `tests/test_scenario_manager.py` | Szenario-Versionierung im Dateisystem |
| `tests/test_app_db_flow.py` | Datenbankfluss mit Fake-Objekten und Import-Sicherheit |

## Testbefehle

Einfacher Lauf:

```bash
pytest
```

Lauf mit Dashboard-Artefakten:

```bash
python -m pytest tests --junitxml=test_results/latest_junit.xml --cov=src --cov-report=xml:test_results/latest_coverage.xml --cov-report=term
```

## Test-Dashboard

Aus `src/test_dashboard.py` ist ersichtlich, dass die Anwendung folgende Artefakte lesen kann:

- `test_results/latest_junit.xml`
- `test_results/latest_coverage.xml`
- `test_results/latest_meta.json`

Das Dashboard stellt unter anderem dar:

- Anzahl der Tests
- Passed/Failed/Error/Skipped
- Laufzeit
- Gesamt-Coverage
- einzelne Testfälle

## Qualitätseinordnung

Die vorhandenen Tests sichern zentrale technische Aspekte des Repositorys ab. Aus dem Repository allein ist jedoch keine vollständige Testabdeckung oder formale Qualitätsmetrik für das Gesamtprojekt ableitbar.

## Offene Punkte

- TODO: fachlich klären, ob ein CI-basierter Testlauf ergänzt werden soll
- TODO: fachlich klären, ob zusätzliche Integrationstests für die Streamlit-Oberfläche gewünscht sind
