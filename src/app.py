import streamlit as st

from prompt_generator import (
    PromptRequest,
    build_prompt,
    evaluate_prompt_quality,
    get_target_options,
    save_generated_prompt,
)


st.set_page_config(page_title="Prompt-Generator", layout="centered")

st.title("Prompt-Generator für Tutor, Engineer und Tester")
st.write(
    "Erzeuge strukturierte Prompts für eine einmalige LLM-Antwort oder einen planbaren Agent-Workflow."
)

prompt_type = st.selectbox(
    "Prompt-Typ",
    options=["LLM", "Agent"],
    help="Wähle zuerst den Prompt-Typ. Danach werden nur relevante Felder angezeigt.",
)

persona_name = st.selectbox(
    "Persona auswählen",
    options=["tutor", "engineer", "tester"],
)

target_options = get_target_options(persona_name)

target_key = st.selectbox(
    "Zieltyp auswählen",
    options=list(target_options.keys()),
    format_func=lambda key: target_options[key],
)

llm_role = ""
llm_context = ""
llm_task = ""
llm_requirements = ""
llm_output_format = ""
llm_examples = ""
agent_goal = ""
agent_context = ""
agent_constraints = ""
agent_workflow = ""
agent_verification = ""
agent_done_when = ""

if prompt_type == "LLM":
    st.subheader("LLM-Felder")
    llm_role = st.text_input(
        "Rolle / Persona",
        placeholder="z. B. Senior Python Tutor mit Fokus auf didaktische Klarheit",
        help="Welche Perspektive oder Expertise soll das Modell einnehmen?",
    )
    llm_context = st.text_area(
        "Kontext",
        placeholder="z. B. Lern-App für Erstsemester, begrenzte Zeit, vorhandenes Vorwissen ...",
        help="Welche Hintergrundinformationen braucht das Modell?",
        height=110,
    )
    llm_task = st.text_area(
        "Aufgabe",
        placeholder="z. B. Erkläre Rekursion mit einem einfachen Python-Beispiel",
        help="Was soll konkret erledigt oder erklärt werden?",
        height=110,
    )
    llm_requirements = st.text_area(
        "Anforderungen",
        placeholder="z. B. deutsch, prägnant, fachlich korrekt, mit 3 Bullet-Points",
        help="Welche fachlichen, sprachlichen oder technischen Bedingungen gelten?",
        height=110,
    )
    llm_output_format = st.text_input(
        "Output-Format",
        placeholder="z. B. Markdown mit H2-Überschriften und Tabelle",
        help="Wie soll die Antwort strukturiert sein?",
    )
    llm_examples = st.text_area(
        "Optional: Beispiele",
        placeholder="Beispiel-Eingabe oder Beispiel-Ausgabe",
        help="Optional: Zeige ein Beispiel für gewünschte Ein- oder Ausgabe",
        height=100,
    )
else:
    st.subheader("Agent-Felder")
    agent_goal = st.text_area(
        "Ziel",
        placeholder="z. B. Ersetze die alte Prompt-Maske durch eine typabhängige Feldlogik",
        help="Welche konkrete Änderung oder welches Ergebnis soll erreicht werden?",
        height=100,
    )
    agent_context = st.text_area(
        "Kontext",
        placeholder="z. B. Dateien src/app.py und src/prompt_generator.py, bestehende Streamlit-UI ...",
        help="Welche Dateien, UI-Bereiche, bestehenden Komponenten oder Annahmen sind relevant?",
        height=110,
    )
    agent_constraints = st.text_area(
        "Constraints",
        placeholder="z. B. kein Backend-Umbau, kein neues Framework, nur minimale UI-Änderung",
        help="Welche Technologien, Architekturregeln oder Verbote gelten?",
        height=100,
    )
    agent_workflow = st.text_area(
        "Arbeitsweise / Schritte",
        placeholder="1) analysieren 2) planen 3) umsetzen 4) prüfen",
        help="Wie soll der Agent vorgehen? Erst analysieren, dann planen, dann umsetzen?",
        height=110,
    )
    agent_verification = st.text_area(
        "Verifikation",
        placeholder="z. B. pytest, UI-Check, manuelle Smoke-Tests",
        help="Wie prüft der Agent, dass die Änderung wirklich funktioniert?",
        height=100,
    )
    agent_done_when = st.text_area(
        "Done-When / Abschlusskriterium",
        placeholder="z. B. alle Tests grün, Felder dynamisch sichtbar, Vorschau und Qualitätscheck korrekt",
        help="Woran erkennt man, dass die Aufgabe abgeschlossen ist?",
        height=100,
    )

filename = st.text_input(
    "Dateiname für den generierten Prompt",
    value=f"{persona_name}_{target_key}_{prompt_type.lower()}_prompt_v1.md",
)

quality_request = PromptRequest(
    persona_name=persona_name,
    target_key=target_key,
    prompt_type=prompt_type.lower(),
    llm_role=llm_role.strip(),
    llm_context=llm_context.strip(),
    llm_task=llm_task.strip(),
    llm_requirements=llm_requirements.strip(),
    llm_output_format=llm_output_format.strip(),
    llm_examples=llm_examples.strip(),
    agent_goal=agent_goal.strip(),
    agent_context=agent_context.strip(),
    agent_constraints=agent_constraints.strip(),
    agent_workflow=agent_workflow.strip(),
    agent_verification=agent_verification.strip(),
    agent_done_when=agent_done_when.strip(),
)

quality_result = evaluate_prompt_quality(quality_request)
st.subheader("Qualitätscheck (live)")
st.progress(quality_result.score / quality_result.max_score)
st.caption(f"Qualitätsscore: {quality_result.score}/{quality_result.max_score}")
for item in quality_result.feedback:
    st.write(item)
st.info(f"Verbesserungsvorschlag: {quality_result.suggestion}")

st.subheader("Live-Vorschau")
preview_prompt = build_prompt(quality_request)
st.code(preview_prompt, language="markdown")

with st.expander("Feldlogik + Qualitätsregeln"):
    st.markdown(
        """
**Sichtbare Felder pro Modus**
- **LLM:** Rolle/Persona, Kontext, Aufgabe, Anforderungen, Output-Format, optional Beispiele
- **Agent:** Ziel, Kontext, Constraints, Arbeitsweise/Schritte, Verifikation, Done-When

**Qualitätswarnungen (LLM)**
- Warnung bei fehlender Aufgabe
- Warnung bei zu knappem Kontext
- Hinweis bei fehlendem Output-Format
- Hinweis bei zu allgemeinen Anforderungen

**Qualitätswarnungen (Agent)**
- Fehler bei zu vagem Ziel
- Warnung ohne Constraints
- Fehler ohne Arbeitsweise
- Fehler ohne Verifikation
- Warnung ohne Done-When
        """
    )

with st.expander("Beispiele: Vorher / Nachher"):
    st.markdown(
        """
**LLM – Vorher (generisch):**
```text
Bitte erkläre Rekursion.
```
**LLM – Nachher (strukturiert):**
```text
Rolle: Didaktischer Python-Tutor
Kontext: Studierende im 1. Semester, wenig Vorwissen
Aufgabe: Erkläre Rekursion mit einem einfachen Python-Beispiel
Anforderungen: klare Sprache, 3 Kernpunkte, häufige Fehler nennen
Output-Format: Markdown mit H2 und Bullet-Points
```

**Agent – Vorher (vage):**
```text
Mach das Frontend besser.
```
**Agent – Nachher (steuerbar):**
```text
Ziel: Prompt-Typ nach oben verschieben und Felder dynamisch nach LLM/Agent anzeigen
Kontext: Streamlit-UI in src/app.py, Promptaufbau in src/prompt_generator.py
Constraints: kein Backend-Umbau, keine Persistenz, minimal-invasive UI-Anpassung
Arbeitsweise: Analyse -> Plan -> Umsetzung -> Test
Verifikation: pytest + manueller UI-Check auf beide Modi
Done-When: Beide Modi zeigen nur relevante Felder, Vorschau und Quality-Check passen
```
        """
    )

if st.button("Prompt generieren"):
    output_path = save_generated_prompt(preview_prompt, filename)

    st.subheader("Generierter Prompt")
    st.code(preview_prompt, language="markdown")
    st.success(f"Prompt gespeichert unter: {output_path}")
