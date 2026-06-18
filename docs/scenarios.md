# Nutzungsszenarien

## Überblick

Das `README.md` beschreibt mehrere typische Nutzungsszenarien, die sich direkt auf die im Repository vorhandenen Personas und Task-Templates beziehen.

## Szenario 1: Tutor-Prompt

Typischer Ablauf:

1. Persona `Tutor` verwenden
2. fachliches Thema definieren
3. Anforderungen wie Beispiele oder typische Fehler ergänzen
4. Prompt generieren
5. Ergebnis fachlich und didaktisch prüfen

## Szenario 2: Engineer-Prompt

Typischer Ablauf:

1. Persona `Engineer` verwenden
2. technische Aufgabe konkret beschreiben
3. Anforderungen wie Python-Version, Naming oder Tests angeben
4. Prompt generieren
5. resultierenden Code prüfen und weiterentwickeln

## Szenario 3: Tester-Prompt

Typischer Ablauf:

1. Persona `Tester` verwenden
2. zu prüfenden Code oder Prompt-Kontext beschreiben
3. Risiken, Randfälle und Review-Fokus angeben
4. strukturierten Test- oder Review-Bericht erzeugen

## Szenario 4: Iterative Prompt-Verbesserung

Aus dem Repository ist ersichtlich, dass Prompt-Arbeit nicht als Einmalschritt gedacht ist. Ein plausibler Ablauf ist:

1. erste Version erzeugen
2. Ergebnis beurteilen
3. Anforderungen oder Format schärfen
4. neue Version speichern
5. Unterschiede dokumentieren oder reviewen

## Szenarien im Code

Zusätzlich enthält `src/llm_workflow_example.py` einen Beispielablauf für einen Engineer-Use-Case rund um die Bereinigung von Vorlesungsnotizen.
