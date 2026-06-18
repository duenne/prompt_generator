# Schnittstellen

## Überblick

Das Repository enthält mehrere Schnittstellenebenen:

- dateibasierte Prompt-Schnittstellen
- UI-Eingaben in Streamlit
- Umgebungsvariablen
- optionale Datenbankzugriffe über Supabase

## Dateibasierte Eingabeschnittstellen

### Prompt-Dateien

Die Prompt-Bausteine liegen in drei Verzeichnissen:

- `prompts/system/`
- `prompts/shared/`
- `prompts/tasks/`

Diese Dateien werden durch `src/prompt_builder.py` und `src/prompt_generator.py` geladen.

## Interne Python-Schnittstellen

Wichtige Funktionsgrenzen:

| Element | Rolle |
| --- | --- |
| `build_prompt()` | setzt einen vollständigen Prompt zusammen |
| `evaluate_prompt_quality()` | bewertet Eingaben heuristisch |
| `evaluate_prompt_quality_deterministic()` | liefert deterministische Qualitätslücken |
| `save_generated_prompt()` | schreibt Prompt-Artefakte ins Dateisystem |

## Umgebungsvariablen

Aus `.env.example` und `src/app.py`:

| Variable | Zweck |
| --- | --- |
| `SUPABASE_URL` | Basis-URL des Supabase-Projekts |
| `SUPABASE_SERVICE_ROLE_KEY` | Schlüssel für Schreibzugriffe |
| `DATABASE_URL` | PostgreSQL-Verbindung für automatische Tabellenerstellung |
| `ENABLE_LOCAL_TEST_RUNNER` | aktiviert den lokalen Test-Runner im Dashboard |

## Datenbankschnittstelle

Aus `src/app.py` ist ersichtlich:

- Verbindung über `create_client(...)`
- Lese-/Schreibzugriffe auf `prompts`
- Lese-/Schreibzugriffe auf `prompt_versions`
- Testabfrage über `select("id").limit(1)`

## LLM-Schnittstelle

Das Repository enthält keine fest verdrahtete API-Integration zu einem bestimmten Modellanbieter. `src/llm_workflow_example.py` zeigt nur ein mögliches Integrationsmuster.

## Externe Schnittstellen, die aktuell fehlen

- dokumentierte REST-API des Projekts
- CLI mit eigenem Kommandointerface
- CI-basierte Schnittstelle für Dokumentations-Deployment
