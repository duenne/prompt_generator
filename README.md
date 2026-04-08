# Prompt-Generator Anwendung mit Versionierung & Testing

Dieses Repository zeigt ein vollständiges, lokal laufendes Arbeitsmodell für **versionierte, testbare Prompts** in einem Softwareprojekt.

Das Beispiel orientiert sich an einem Team, das eine Lern-App entwickelt und dafür drei Prompt-Typen nutzt:

- **Tutor** für Erklärungen
- **Engineer** für Codegenerierung
- **Tester** für Codeanalyse, Testideen und Feedback

Die Anwendung in diesem Repository erzeugt solche Prompts aus wiederverwendbaren Bausteinen, speichert sie lokal und macht sie damit **Git-ready**.

---

## Ziel des Repositories

Dieses Projekt soll nicht nur eine kleine App liefern, sondern eine **konkrete Arbeitsweise** zeigen:

1. Prompts als Code behandeln
2. Prompts modular strukturieren
3. Prompts versionieren
4. Prompts systematisch testen
5. Prompts iterativ verbessern
6. Prompts nutzen, um mit einem LLM strukturierter Software zu entwickeln

---

## Was im Repository enthalten ist

```text
prompt-generator-repo/
├── prompts/
│   ├── system/
│   │   ├── persona_tutor.md
│   │   ├── persona_engineer.md
│   │   └── persona_tester.md
│   ├── shared/
│   │   ├── coding_rules.md
│   │   ├── naming_conventions.md
│   │   ├── output_format_default.md
│   │   └── style_rules.md
│   └── tasks/
│       ├── explain_concept_v1.md
│       ├── generate_python_code_v1.md
│       └── review_code_v1.md
├── src/
│   ├── app.py
│   ├── llm_workflow_example.py
│   ├── prompt_builder.py
│   └── prompt_generator.py
├── tests/
│   ├── prompt_cases/
│   │   ├── engineer_case_notes_cleaner.json
│   │   ├── tester_case_code_review.json
│   │   └── tutor_case_recursion.json
│   ├── test_prompt_builder.py
│   └── test_prompt_generator.py
├── generated_prompts/
├── docs/
│   ├── prompt_eval_log.md
│   └── pull_request_template.md
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Schnellstart

### 1. Repository herunterladen und in VS Code öffnen

- Lade dieses Repository herunter.
- Entpacke es lokal.
- Öffne den Ordner in **VS Code**.

### 2. Virtuelle Umgebung anlegen

#### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Abhängigkeiten installieren

```bash
pip install -e .
```

Optional für Entwicklung:

```bash
pip install -e .[dev]
```

### 4. Streamlit-App starten

```bash
streamlit run src/app.py
```

Danach öffnet sich lokal eine kleine Web-Oberfläche, mit der du Prompts generieren und abspeichern kannst.

### 5. Tests ausführen

```bash
pytest
```

---

# Die Prozedur der Anwendung

Der Kern dieses Repositories ist nicht nur die UI, sondern die **Prozedur**, nach der ein Team mit Prompts arbeitet. Genau diese Prozedur bildet die Anwendung ab.

## Schritt 1: Persona definieren

Zuerst wird festgelegt, **welche Rolle** das LLM einnehmen soll.

Im Repository gibt es dafür drei System-Prompts:

- `prompts/system/persona_tutor.md`
- `prompts/system/persona_engineer.md`
- `prompts/system/persona_tester.md`

Diese Dateien enthalten **stabile Rollenbeschreibungen**, die in vielen Aufgaben wiederverwendet werden können.

### Beispiel

- Der **Tutor** erklärt Konzepte klar, didaktisch und mit Beispielen.
- Der **Engineer** schreibt sauberen Python-Code mit Naming Conventions und Tests.
- Der **Tester** analysiert Code kritisch, benennt Risiken und formuliert Testfälle.

---

## Schritt 2: Wiederverwendbare Regeln trennen

Nicht alle Teile eines Prompts ändern sich pro Anfrage. Deshalb gibt es im Repository **gemeinsame Prompt-Bausteine** in `prompts/shared/`.

Dort liegen zum Beispiel:

- Coding Rules
- Naming Conventions
- Stilregeln
- Output-Format

Dadurch wird verhindert, dass dieselben Regeln ständig kopiert werden.

### Beispiel

`prompts/shared/coding_rules.md` enthält Anforderungen wie:

- Python 3.11
- `snake_case`
- kleine Funktionen
- pytest-Tests
- Standardbibliothek bevorzugen

---

## Schritt 3: Konkrete Aufgabe formulieren

Die variable Aufgabe wird in der App eingegeben:

- Persona
- Ziel
- Anforderungen
- Szenario

Die App setzt diese Informationen mit den modularen Prompt-Bausteinen zu einem vollständigen Prompt zusammen.

### Beispiel

Persona: `engineer`

Ziel:
> Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen.

Anforderungen:
> Nutze Python 3.11, snake_case, kleine Funktionen und pytest-Tests.

Szenario:
> Die Funktion wird in einer lokalen Lern-App genutzt, um Rohtext vor einer Zusammenfassung zu normalisieren.

---

## Schritt 4: Prompt generieren

Die Datei `src/prompt_generator.py` lädt:

- die Persona-Datei,
- passende Shared Rules,
- und die dynamischen Eingaben.

Anschließend erzeugt sie einen strukturierten Prompt-Text.

Die Web-Oberfläche in `src/app.py` macht genau diesen Schritt nutzbar.

---

## Schritt 5: Prompt speichern und versionieren

Generierte Prompts werden in `generated_prompts/` gespeichert.

Das ist absichtlich **Git-freundlich** gedacht:

- Prompts können gelesen werden
- Prompts können verglichen werden
- Prompts können committed werden
- Prompt-Versionen bleiben nachvollziehbar

### Benennung

Verwende möglichst sprechende Namen wie:

- `engineer_notes_cleaner_v1.md`
- `tutor_recursion_explainer_v1.md`
- `tester_markdown_validator_v2.md`

---

## Schritt 6: Prompt an ein LLM senden

Dieses Repository ist absichtlich **LLM-agnostisch**. Es erzwingt keine konkrete API.

Die Datei `src/llm_workflow_example.py` zeigt aber das Muster:

1. Prompt generieren
2. an ein LLM schicken
3. Antwort entgegennehmen
4. Code oder Bericht speichern

So bleibt das System lokal, einfach und austauschbar.

---

## Schritt 7: Ergebnis prüfen

Danach beginnt der wichtigste Teil: **Bewerten statt nur Generieren**.

Für Tutor-, Engineer- und Tester-Prompts sollte man immer prüfen:

- Ist die Ausgabe fachlich korrekt?
- Ist das Format stabil?
- Sind Regeln eingehalten?
- Ist der Code testbar?
- Sind Benennungen konsistent?
- Fehlen Randfälle?

Im Repository gibt es dafür:

- Beispiel-Testfälle in `tests/prompt_cases/`
- automatisierte Tests für den Prompt-Aufbau
- ein Evaluationslog in `docs/prompt_eval_log.md`

---

## Schritt 8: Prompt verbessern

Wenn ein Prompt noch nicht gut genug ist, wird er **iterativ verbessert**.

Typische Verbesserungen:

- Aufgabe präzisieren
- Kontext ergänzen
- Format fester definieren
- Regeln schärfen
- Qualitätskriterien klarer machen

Wichtig ist: **kleine Änderungen statt chaotischer Großumbau**.

---

## Schritt 9: Änderungen committen

Prompt-Änderungen werden wie Code versioniert.

### Gute Commit-Messages

```bash
git commit -m "add initial tutor prompt"
git commit -m "improve engineer prompt with stricter output format"
git commit -m "add tester workflow and prompt evaluation cases"
```

### Schlechte Commit-Messages

```bash
git commit -m "update"
git commit -m "final"
git commit -m "stuff changed"
```

---

## Schritt 10: Im Team reviewen

Für Teamarbeit sollte jede relevante Prompt-Änderung per Pull Request geprüft werden.

Nutze dafür die Vorlage in `docs/pull_request_template.md`.

Reviewer sollten prüfen:

- Ist die Änderung klar begründet?
- Verbessert sich die Prompt-Struktur?
- Ist das Ausgabeformat stabiler?
- Wurden Beispiele oder Tests ergänzt?
- Ist die Änderung klein und nachvollziehbar?

---

# Konkreter Workflow in diesem Repository

So kann ein Team mit dem Repository praktisch arbeiten:

## Workflow A: Tutor-Prompt

1. App starten
2. Persona `tutor` auswählen
3. Ziel eingeben, z. B. „Erkläre Rekursion“
4. Anforderungen ergänzen, z. B. „mit Beispiel und typischen Fehlern“
5. Szenario ergänzen, z. B. „für Studierende im ersten Semester“
6. Prompt generieren
7. Prompt speichern
8. an ein LLM senden
9. Qualität der Erklärung prüfen
10. falls nötig, Persona oder Regeln verbessern

## Workflow B: Engineer-Prompt

1. Persona `engineer` auswählen
2. Ziel definieren, z. B. „Schreibe eine Funktion zur Bereinigung von Vorlesungsnotizen“
3. Anforderungen definieren, z. B. „Python 3.11, snake_case, pytest-Tests“
4. Szenario angeben
5. Prompt generieren und speichern
6. an LLM senden
7. generierten Code lokal speichern
8. Tests ausführen
9. Tester-Prompt für Review nutzen
10. Prompt iterativ verbessern

## Workflow C: Tester-Prompt

1. Persona `tester` auswählen
2. Ziel formulieren, z. B. „Analysiere den generierten Notes-Cleaner“
3. Anforderungen ergänzen, z. B. „nenne Randfälle und mache Verbesserungsvorschläge“
4. Szenario angeben
5. Prompt generieren
6. LLM gibt strukturierten Testbericht aus
7. Bericht dokumentieren
8. Engineer-Prompt oder Code überarbeiten

---

# Architekturidee des Projekts

## `src/prompt_builder.py`

Enthält Hilfsfunktionen zum Laden von Prompt-Dateien.

## `src/prompt_generator.py`

Enthält die Kernlogik:

- Persona laden
- Shared Rules laden
- Eingaben kombinieren
- vollständigen Prompt erzeugen
- Prompt speichern

## `src/app.py`

Die Streamlit-Oberfläche für lokale Nutzung.

## `src/llm_workflow_example.py`

Zeigt, wie der generierte Prompt in einen LLM-Workflow eingebunden werden kann.

## `tests/`

Stellt sicher, dass der Prompt-Aufbau reproduzierbar und stabil bleibt.

---

# Typische Lernziele mit diesem Repository

Nach dem Durcharbeiten dieses Projekts sollten Studierende verstehen:

- warum Prompts wie Code behandelt werden sollten,
- wie man Prompts modularisiert,
- wie man Prompt-Bausteine versioniert,
- wie man klare Personas formuliert,
- wie man Prompts testbar macht,
- wie man LLM-gestützte Codearbeit strukturierter organisiert,
- und wie man aus losem Experimentieren einen nachvollziehbaren Workflow macht.

---

# Empfohlene nächste Schritte

1. Starte die App lokal.
2. Generiere je einen Tutor-, Engineer- und Tester-Prompt.
3. Lege zwei Versionen für denselben Use Case an.
4. Vergleiche die Ergebnisse.
5. Dokumentiere Beobachtungen in `docs/prompt_eval_log.md`.
6. Committe nur kleine, nachvollziehbare Änderungen.
7. Nutze Pull Requests für größere Prompt-Verbesserungen.

---

# Fazit

Dieses Repository ist absichtlich einfach gehalten, aber fachlich sauber strukturiert.

Es zeigt ein belastbares Grundmodell:

- **Prompts generieren**
- **Prompts modular speichern**
- **Prompts versionieren**
- **Prompts testen**
- **Prompts für Tutor, Engineer und Tester nutzen**
- **Prompts iterativ verbessern**

Damit wird aus spontanem „vibe coding“ ein kontrollierbarer Entwicklungsprozess.
