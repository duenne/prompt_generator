# Problem und Motivation

## Ausgangslage

Das Repository enthält ein Lern- und Demonstrationsprojekt für den Umgang mit Prompts in Softwareprojekten. Aus dem `README.md` ist ersichtlich, dass nicht nur einzelne Prompts erzeugt werden sollen, sondern eine **Arbeitsweise** dokumentiert wird.

## Welches Problem adressiert das Projekt?

Aus dem Repository ist ableitbar, dass unstrukturierte Prompt-Nutzung mehrere Nachteile hat:

| Problem | Ableitung aus dem Repository |
| --- | --- |
| Prompts werden leicht dupliziert | Es gibt gemeinsame Regeln unter `prompts/shared/`, was auf bewusste Wiederverwendung hindeutet. |
| Änderungen sind schwer nachvollziehbar | Das README betont Versionierung und Git-freundliche Speicherung. |
| Qualitätskriterien bleiben uneinheitlich | Es gibt explizite Regeln, Personas und Qualitätschecks in `src/prompt_generator.py`. |
| Prompt-Verbesserungen sind schwer reviewbar | Das Repository enthält ein PR-Template und ein Prompt-Evaluationslog. |
| Ergebnisse hängen zu stark von spontanen Texteingaben ab | Die App strukturiert Eingaben in feste Felder und bewertet sie live. |

## Motivation des Ansatzes

Das Repository enthält mehrere Hinweise darauf, dass Prompts ähnlich wie Quellcode behandelt werden sollen:

- klare Rollenbilder
- wiederverwendbare Bausteine
- reproduzierbare Struktur
- versionierbare Dateien
- Tests für die Kernlogik

## Warum ist das technisch relevant?

Für Teams oder Lernende wird Prompt-Arbeit belastbarer, wenn:

- Regeln nicht in jedem Prompt neu formuliert werden müssen
- Änderungen klein und prüfbar bleiben
- Qualität nicht nur gefühlt, sondern anhand fester Kriterien diskutiert wird
- Artefakte in Git, Tests und Dokumentation eingebunden werden können

## Abgrenzung

Das Repository enthält keine fest integrierte LLM-API. Der aktuelle Stand legt nahe, dass die Erzeugung und Strukturierung von Prompts im Vordergrund steht, nicht der Betrieb eines vollständigen produktiven KI-Backends.
