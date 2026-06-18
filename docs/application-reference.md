# Beitrag für Bewerbungen

## Projektkontext

Das Repository enthält ein Projekt zum Lernziel **Prompts als Code**. Es kombiniert modulare Prompt-Bausteine, eine lokale Streamlit-Anwendung, Tests und dokumentierte Architekturentscheidungen.

## Team und Rolle

TODO: fachlich klären

## Mein Beitrag

TODO: fachlich klären

## Technische Herausforderungen

- Trennung von Personas, Regeln und Task-Templates in eigenständige Dateien
- reproduzierbarer Prompt-Aufbau mit festen Strukturen
- lokale Demonstrierbarkeit über Streamlit statt nur über Skripte
- optionaler Persistenzpfad über Supabase
- Nachvollziehbarkeit von Tests über JUnit- und Coverage-Artefakte

## Entscheidungen und Begründungen

Aus den ADRs und Projektdokumenten sind unter anderem folgende Entscheidungen belegbar:

- Streamlit wurde wegen geringer Komplexität und schneller Iteration gewählt
- Supabase wird direkt aus der App angesprochen
- `DATABASE_URL` bleibt optional
- Versionierung gespeicherter Prompts wird über eine separate Tabelle modelliert

## Was ich gelernt habe

TODO: fachlich klären
