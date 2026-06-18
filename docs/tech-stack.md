# Technologiestack

## Überblick

Der aktuelle Stack lässt sich aus `pyproject.toml`, `requirements.txt` und dem Quellcode ableiten.

| Bereich | Technologie | Beleg |
| --- | --- | --- |
| Programmiersprache | Python 3.11+ | `pyproject.toml` |
| UI | Streamlit | `pyproject.toml`, `src/app.py` |
| Umgebungsvariablen | python-dotenv | `requirements.txt`, `src/app.py` |
| Persistenzdienst | Supabase | `requirements.txt`, `src/app.py` |
| PostgreSQL-Zugriff | psycopg2-binary | `requirements.txt`, `src/app.py` |
| Test-Framework | pytest | `pyproject.toml`, `tests/` |
| Paketierung | setuptools | `pyproject.toml` |
| Dokumentation | MkDocs Material | neue Dokumentationsstruktur |

## Stack-Einordnung

### Anwendung

- Python-only Stack
- UI ohne separate Frontend-Build-Chain
- direkte Anwendungslogik in Python-Modulen

### Persistenz

- Supabase für externe Speicherung
- PostgreSQL-Zugriff für DDL-Initialisierung

### Qualitätssicherung

- pytest
- JUnit-XML
- Coverage-XML

## Technische Beobachtungen

- `pyproject.toml` und `requirements.txt` sind derzeit nicht vollständig konsistent.
- Die Architektur ist bewusst schlank und MVP-orientiert.
- Es gibt keine Hinweise auf Containerisierung oder Infrastructure as Code.
