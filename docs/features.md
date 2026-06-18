# Funktionsumfang

## Überblick

Der aktuelle Funktionsumfang ergibt sich aus den Python-Modulen, Tests und der bestehenden Dokumentation.

## Kernfunktionen

| Funktion | Beleg |
| --- | --- |
| Laden von Personas | `src/prompt_generator.py` |
| Laden von Shared Rules | `src/prompt_generator.py` |
| Laden von Task-Templates | `src/prompt_generator.py` |
| Zusammenbau vollständiger Prompts | `src/prompt_generator.py` |
| Unterstützung für LLM- und Agent-Prompts | `src/prompt_generator.py`, `src/app.py` |
| Live-Qualitätsbewertung | `src/prompt_generator.py`, `src/app.py` |
| lokale Speicherung generierter Prompts | `src/prompt_generator.py` |
| Persistenz in Supabase | `src/app.py` |
| Test-Dashboard | `src/test_dashboard.py` |
| Prefill- und Verlaufshilfen | `src/prefill_support.py`, `src/app.py` |

## UI-bezogene Funktionen der Streamlit-App

Aus `src/app.py` ist ersichtlich:

- Auswahl eines Prompt-Typs
- Auswahl eines Startpunkts
- Anzeige einer Live-Vorschau
- Live-Qualitätscheck
- Seite zum Speichern von Prompts
- Seite zum Testen der Datenbankverbindung
- Seite für Testresultate

## Persistenz und Versionierung

Das Repository enthält zwei Speicherebenen:

1. **Dateibasiert** über `generated_prompts/`
2. **datenbankbasiert** über `prompts` und `prompt_versions`

## Qualitäts- und Testunterstützung

- Unit-Tests für Prompt-Aufbau und Hilfslogik
- Tests für Datenbankfluss mit Fake-Objekten
- Parsing von JUnit- und Coverage-Artefakten
- dokumentierte Known Issues und ADRs

## Nicht belegbare oder nur teilweise belegbare Funktionen

- echte LLM-Ausführung über eine integrierte API
- Mehrbenutzerbetrieb
- produktiver Cloud-Deployment-Workflow

Diese Punkte sollten derzeit nicht als vorhandene Features beschrieben werden.
