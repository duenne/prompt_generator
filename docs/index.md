# Prompt Generator Repository

Das Repository enthält eine lokale Python-Anwendung und eine Sammlung versionierbarer Prompt-Bausteine, mit denen **Prompts als Code** behandelt werden können. Der aktuelle Stand kombiniert ein modulares Prompt-System mit einer Streamlit-Oberfläche, optionaler Supabase-Speicherung und einem kleinen Test-Dashboard.

## Kurzbeschreibung

Aus dem Repository ist ersichtlich, dass das Projekt drei wiederverwendbare Rollenbilder für Prompting bereitstellt:

- `Tutor` für fachliche Erklärungen
- `Engineer` für technische Aufgaben wie Feature-Erstellung, Refactoring und Code-Erklärung
- `Tester` für Review, Risikoanalyse und Testideen

Die Prompts werden aus Dateien in `prompts/system/`, `prompts/shared/` und `prompts/tasks/` zusammengesetzt. Dadurch bleiben Regeln, Personas und Aufgabenbausteine getrennt und versionierbar.

## Value Proposition

Das Repository enthält einen konkreten Ansatz, um Prompt-Entwicklung nachvollziehbarer zu machen:

- Prompts werden modular gespeichert
- Regeln und Rollen werden wiederverwendbar gehalten
- Änderungen können getestet und reviewed werden
- generierte Prompts können lokal als Artefakte abgelegt werden

Die genaue Zielgruppe und der fachliche Primärnutzen außerhalb des Lern- und Demonstrationskontexts sollten noch präzisiert werden.

## Projektstatus

Der aktuelle Stand legt nahe, dass es sich um ein **MVP und Lernprojekt** handelt:

- Streamlit-App für Prompt-Erstellung und Prompt-Speicherung
- optionale Supabase-Anbindung für persistente Speicherung
- dokumentierte Architekturentscheidungen und bekannte Probleme
- vorhandene Tests für Kernlogik und Datenbankfluss

## Wichtigste Funktionen

- strukturierter Prompt-Aufbau aus modularen Markdown-Dateien
- Unterstützung für LLM- und Agent-Prompts
- Live-Qualitätsfeedback für Prompt-Eingaben
- lokale Speicherung generierter Prompts
- optionale Speicherung in Supabase mit Versionstabelle
- Test-Dashboard auf Basis von JUnit- und Coverage-Artefakten

## Technologiestack in Kurzform

| Bereich | Stand |
| --- | --- |
| Sprache | Python 3.11+ |
| UI | Streamlit |
| Persistenz | Supabase, PostgreSQL |
| Tests | pytest |
| Konfiguration | `.env`, `python-dotenv` |

## Schnellzugriffe

- [Lokales Setup](setup.md)
- [Architektur](architecture.md)
- [Technologiestack](tech-stack.md)
- [Testing](testing.md)
- [Repository auf GitHub](https://github.com/duenne/prompt_generator.git)

## Mein Beitrag

TODO: fachlich klären

## Hinweise zur Einordnung

Die bestehende Dokumentation im Repository zeigt zwei eng verbundene Perspektiven:

1. ein Lernziel rund um **Prompts als Code**
2. eine konkrete Streamlit-/Supabase-Implementierung, die dieses Lernziel praktisch demonstriert

Diese Projektwebseite ordnet deshalb die Anwendung als **technische Ausprägung des übergeordneten Prompt-Engineering-Ansatzes** ein.
