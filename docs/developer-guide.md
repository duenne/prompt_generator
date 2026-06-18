# Entwicklerdokumentation

## Überblick

Diese Seite beschreibt, wie das Repository technisch aufgebaut ist und wo Erweiterungen typischerweise vorgenommen werden.

## Zentrale Verzeichnisse

| Pfad | Rolle |
| --- | --- |
| `prompts/system/` | Rollenbeschreibungen |
| `prompts/shared/` | wiederverwendbare Regeln |
| `prompts/tasks/` | aufgabenspezifische Templates |
| `src/` | Python-Anwendungslogik |
| `tests/` | automatisierte Tests |
| `generated_prompts/` | lokale Ausgabe generierter Prompt-Dateien |
| `test_results/` | Testartefakte für Dashboard und Auswertung |

## Neue Prompt-Bausteine ergänzen

### Neue Persona

1. Datei unter `prompts/system/` anlegen
2. `PERSONA_FILE_MAP` in `src/prompt_generator.py` ergänzen
3. passende Zieltypen und Task-Zuordnungen ergänzen
4. Tests für erwartete Struktur ergänzen

### Neues Task-Template

1. Markdown-Datei unter `prompts/tasks/` anlegen
2. `TASK_FILE_MAP` erweitern
3. bei Bedarf `TARGET_LABELS` ergänzen
4. Prompt-Generator-Tests anpassen

## Wichtige Python-Module

### `src/prompt_generator.py`

Kernmodul für:

- Laden der Prompt-Bausteine
- Zusammensetzen der finalen Prompts
- Qualitätsbewertung
- Speichern generierter Dateien

### `src/app.py`

Enthält:

- Streamlit-Oberfläche
- Eingabefelder und Startpunkte
- DB-Testseite
- Speicherseite
- Einbindung des Test-Dashboards

### `src/test_dashboard.py`

Enthält:

- Parsing von JUnit-XML
- Parsing von Coverage-XML
- optionales Ausführen lokaler Tests

## Teststrategie im Repository

Bei Änderungen an Kernlogik sollten mindestens die betroffenen `pytest`-Tests ausgeführt werden. Besonders relevant sind:

- `tests/test_prompt_generator.py`
- `tests/test_prompt_builder.py`
- `tests/test_prefill_support.py`
- `tests/test_app_db_flow.py`

## Hinweise für Änderungen

- Das Repository enthält derzeit zwei App-Dateien; Änderungen sollten klar auf `src/app.py` oder die Root-Datei bezogen sein.
- Aussagen zu Zielgruppe, Produktreife oder persönlichem Beitrag sollten nur ergänzt werden, wenn sie fachlich belegbar sind.
- `.env` gehört nicht ins Repository.
