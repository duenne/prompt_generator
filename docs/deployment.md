# Deployment

## Aktuell belegbarer Stand

Das Repository enthält vor allem Hinweise für den **lokalen Betrieb**. Ein vollständig ausgearbeiteter Deployment-Workflow ist derzeit nicht im Repository enthalten.

## Vorhandene Bausteine

- Streamlit als UI-Framework
- Supabase als externer Persistenzdienst
- `.env.example` für Konfiguration
- dokumentierte Architekturentscheidungen in `docs/DECISIONS_ADR.md`

## Lokale Bereitstellung

Der dokumentierte Betriebsweg ist:

```bash
streamlit run src/app.py
```

## Datenbankbereitstellung

Für die initiale Tabellenerstellung sind zwei Wege dokumentiert:

1. automatisch über `DATABASE_URL`
2. manuell über SQL im Supabase-Dashboard

## Nicht vorhandene Deployment-Artefakte

Im Repository wurden aktuell nicht gefunden:

- `Dockerfile`
- `docker-compose.yml`
- GitHub- oder GitLab-CI für Deployment
- Infrastrukturdefinitionen

## Einordnung

Der aktuelle Stand legt nahe, dass Deployment bisher kein Schwerpunkt des Projekts ist. Für eine spätere Veröffentlichung wären mindestens folgende Entscheidungen zu treffen:

- Zielplattform für Streamlit
- Umgang mit Secrets
- Trennung zwischen lokaler Demo und öffentlichem Betrieb
- Absicherung des Supabase-Zugriffs

## Offene Punkte

TODO: fachlich klären: Soll die Anwendung nur lokal demonstriert oder später öffentlich bereitgestellt werden?
