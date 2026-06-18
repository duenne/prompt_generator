# Roadmap

## Einordnung

Die folgenden Punkte leiten sich aus `docs/KNOWN_ISSUES.md`, `docs/CHECKPOINT_PROJEKT_STATUS.md` und der aktuellen Codebasis ab.

## Naheliegende nächste Schritte

### 1. Einstiegspunkt bereinigen

- Klären, ob `src/app.py` der einzige offizielle Startpunkt sein soll
- Root-`app.py` entweder entfernen oder deutlicher als Minimalbeispiel kennzeichnen

### 2. Dependency-Management konsolidieren

- `pyproject.toml` und `requirements.txt` angleichen
- offiziellen Installationsweg definieren

### 3. Dokumentation vervollständigen

- Screenshots ergänzen
- Setup und Deployment weiter präzisieren
- Zielgruppe und Portfolio-Kontext fachlich schärfen

### 4. Qualitätssicherung ausbauen

- CI-Workflow für Tests ergänzen
- optional MkDocs-Build automatisieren
- zusätzliche UI- oder Integrationstests prüfen

### 5. Funktionsumfang vertiefen

Aus den bestehenden Projektdokumenten ergeben sich als mögliche spätere Ausbaurichtung:

- Bearbeiten oder Löschen gespeicherter Prompts
- Versionshistorie pro Prompt sichtbar machen
- Suche oder Filter für Prompt-Listen

## Offene strategische Fragen

- TODO: fachlich klären: Soll das Projekt primär Lernplattform, internes Tool oder Portfolio-Demonstrator sein?
- TODO: fachlich klären: Soll die Supabase-Integration weiter ausgebaut oder bewusst optional bleiben?
