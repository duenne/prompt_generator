# Setup

## Voraussetzungen

Aus `pyproject.toml` ist ersichtlich:

- Python `>=3.11`

Zusätzlich sind für den aktuellen MVP sinnvoll:

- eine lokale virtuelle Umgebung
- optional ein Supabase-Projekt für persistente Speicherung

## Repository klonen

```bash
git clone https://github.com/duenne/prompt_generator.git
cd prompt_generator_repo
```

## Virtuelle Umgebung anlegen

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Abhängigkeiten installieren

Im Repository sind zwei Installationspfade dokumentiert.

### Paketbasierter Weg

```bash
pip install -e .
```

Optional für Entwicklung:

```bash
pip install -e .[dev]
```

### Requirements-basierter Weg

```bash
pip install -r requirements.txt
```

## Konfiguration

Die Datei `.env.example` zeigt die erwarteten Variablen:

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

Typischer Start:

```bash
cp .env.example .env
```

Dann die echten Werte eintragen.

## Anwendung lokal starten

Der im Repository dokumentierte Haupteinstiegspunkt ist:

```bash
streamlit run src/app.py
```

## Tests ausführen

Einfacher Testlauf:

```bash
pytest
```

Artefaktbasierter Lauf für das Test-Dashboard:

```bash
python -m pytest tests --junitxml=test_results/latest_junit.xml --cov=src --cov-report=xml:test_results/latest_coverage.xml --cov-report=term
```

## Optional: lokalen Test-Runner in der UI aktivieren

```bash
ENABLE_LOCAL_TEST_RUNNER=true streamlit run src/app.py
```

## Häufige Fehler oder offene Punkte

| Thema | Hinweis |
| --- | --- |
| Datenbanktabellen fehlen | Die Seite "DB-Verbindung testen" enthält Hinweise und SQL zur Initialisierung. |
| `SUPABASE_URL` falsch gesetzt | Laut ADR soll nur die Basis-URL ohne `/rest/v1/` verwendet werden. |
| zwei App-Dateien im Repository | Der aktuelle Stand legt nahe, dass `src/app.py` der Hauptstartpunkt ist. |
| inkonsistente Dependencies | `pyproject.toml` und `requirements.txt` enthalten derzeit unterschiedliche Angaben. |

## Offene Klärung

TODO: fachlich klären: Welcher Installationsweg soll langfristig der offizielle Standard sein?
