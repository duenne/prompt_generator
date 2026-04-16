import streamlit as st

from prefill_support import get_field_templates, load_prompt_history
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

FIELD_SEPARATOR = {
    "llm_role": " | ",
    "llm_output_format": " | ",
    "llm_context": "\n",
    "agent_workflow": "\n",
    "agent_verification": "\n",
}


def merge_prefill(field_key: str, incoming_text: str) -> None:
    incoming = incoming_text.strip()
    if not incoming:
        return

    existing = st.session_state.get(field_key, "").strip()
    if not existing:
        st.session_state[field_key] = incoming
        return

    if incoming in existing:
        return

    separator = FIELD_SEPARATOR.get(field_key, "\n")
    st.session_state[field_key] = f"{existing}{separator}{incoming}".strip()


def render_prefill_controls(field_key: str, label: str, prompt_type: str) -> None:
    templates = get_field_templates(prompt_type, field_key)
    history_entries = [
        entry
        for entry in load_prompt_history()
        if entry.prompt_type == prompt_type and entry.fields.get(field_key, "").strip()
    ]

    if not templates and not history_entries:
        return

    st.caption(f"Vorausfüllung für **{label}**: optional, transparent, editierbar")
    left_col, right_col = st.columns(2)

    if templates:
        template_state_key = f"{field_key}_template_select"
        left_col.selectbox(
            "Vorlage wählen",
            options=["– keine Vorlage –", *templates],
            key=template_state_key,
        )
        if left_col.button("Vorlage einfügen", key=f"{field_key}_template_apply"):
            selected_template = st.session_state.get(template_state_key, "")
            if selected_template != "– keine Vorlage –":
                merge_prefill(field_key, selected_template)
                st.rerun()

    if history_entries:
        history_labels = [f"{entry.filename}" for entry in history_entries]
        history_map = {
            f"{entry.filename}": entry.fields.get(field_key, "") for entry in history_entries
        }
        history_state_key = f"{field_key}_history_select"
        right_col.selectbox(
            "Aus früherem Prompt übernehmen",
            options=["– keine Auswahl –", *history_labels],
            key=history_state_key,
        )
        if right_col.button("Auswahl übernehmen", key=f"{field_key}_history_apply"):
            selected_history = st.session_state.get(history_state_key, "")
            if selected_history != "– keine Auswahl –":
                merge_prefill(field_key, history_map[selected_history])
                st.rerun()


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

if prompt_type == "LLM":
    st.subheader("LLM-Felder")

    render_prefill_controls("llm_role", "Rolle / Persona", "llm")
    st.text_input(
        "Rolle / Persona",
        key="llm_role",
        placeholder="z. B. Senior Python Tutor mit Fokus auf didaktische Klarheit",
        help="Welche Perspektive oder Expertise soll das Modell einnehmen?",
    )

    render_prefill_controls("llm_context", "Kontext", "llm")
    st.text_area(
        "Kontext",
        key="llm_context",
        placeholder="z. B. Lern-App für Erstsemester, begrenzte Zeit, vorhandenes Vorwissen ...",
        help="Welche Hintergrundinformationen braucht das Modell?",
        height=110,
    )

    st.text_area(
        "Aufgabe",
        key="llm_task",
        placeholder="z. B. Erkläre Rekursion mit einem einfachen Python-Beispiel",
        help="Was soll konkret erledigt oder erklärt werden?",
        height=110,
    )
    st.text_area(
        "Anforderungen",
        key="llm_requirements",
        placeholder="z. B. deutsch, prägnant, fachlich korrekt, mit 3 Bullet-Points",
        help="Welche fachlichen, sprachlichen oder technischen Bedingungen gelten?",
        height=110,
    )

    render_prefill_controls("llm_output_format", "Output-Format", "llm")
    st.text_input(
        "Output-Format",
        key="llm_output_format",
        placeholder="z. B. Markdown mit H2-Überschriften und Tabelle",
        help="Wie soll die Antwort strukturiert sein?",
    )

    st.text_area(
        "Optional: Beispiele",
        key="llm_examples",
        placeholder="Beispiel-Eingabe oder Beispiel-Ausgabe",
        help="Optional: Zeige ein Beispiel für gewünschte Ein- oder Ausgabe",
        height=100,
    )

    st.info(
        "Automatische Vorausfüllung ist bewusst nur für strukturierende Felder aktiv. "
        "Fachliche Anforderungen und projektspezifische Inhalte bleiben manuell beim Nutzer."
    )

else:
    st.subheader("Agent-Felder")
    st.text_area(
        "Ziel",
        key="agent_goal",
        placeholder="z. B. Ersetze die alte Prompt-Maske durch eine typabhängige Feldlogik",
        help="Welche konkrete Änderung oder welches Ergebnis soll erreicht werden?",
        height=100,
    )
    st.text_area(
        "Kontext",
        key="agent_context",
        placeholder="z. B. Dateien src/app.py und src/prompt_generator.py, bestehende Streamlit-UI ...",
        help="Welche Dateien, UI-Bereiche, bestehenden Komponenten oder Annahmen sind relevant?",
        height=110,
    )
    st.text_area(
        "Constraints",
        key="agent_constraints",
        placeholder="z. B. kein Backend-Umbau, kein neues Framework, nur minimale UI-Änderung",
        help="Welche Technologien, Architekturregeln oder Verbote gelten?",
        height=100,
    )

    render_prefill_controls("agent_workflow", "Arbeitsweise / Schritte", "agent")
    st.text_area(
        "Arbeitsweise / Schritte",
        key="agent_workflow",
        placeholder="1) analysieren 2) planen 3) umsetzen 4) prüfen",
        help="Wie soll der Agent vorgehen? Erst analysieren, dann planen, dann umsetzen?",
        height=110,
    )

    render_prefill_controls("agent_verification", "Verifikation", "agent")
    st.text_area(
        "Verifikation",
        key="agent_verification",
        placeholder="z. B. pytest, UI-Check, manuelle Smoke-Tests",
        help="Wie prüft der Agent, dass die Änderung wirklich funktioniert?",
        height=100,
    )
    st.text_area(
        "Done-When / Abschlusskriterium",
        key="agent_done_when",
        placeholder="z. B. alle Tests grün, Felder dynamisch sichtbar, Vorschau und Qualitätscheck korrekt",
        help="Woran erkennt man, dass die Aufgabe abgeschlossen ist?",
        height=100,
    )

    st.info(
        "Vorausfüllung fokussiert auf wiederverwendbare Best Practices (Arbeitsweise, Verifikation). "
        "Ziel, produktspezifische Entscheidungen und Fachinhalte werden nicht automatisch ersetzt."
    )

filename = st.text_input(
    "Dateiname für den generierten Prompt",
    value=f"{persona_name}_{target_key}_{prompt_type.lower()}_prompt_v1.md",
)

quality_request = PromptRequest(
    persona_name=persona_name,
    target_key=target_key,
    prompt_type=prompt_type.lower(),
    llm_role=st.session_state.get("llm_role", "").strip(),
    llm_context=st.session_state.get("llm_context", "").strip(),
    llm_task=st.session_state.get("llm_task", "").strip(),
    llm_requirements=st.session_state.get("llm_requirements", "").strip(),
    llm_output_format=st.session_state.get("llm_output_format", "").strip(),
    llm_examples=st.session_state.get("llm_examples", "").strip(),
    agent_goal=st.session_state.get("agent_goal", "").strip(),
    agent_context=st.session_state.get("agent_context", "").strip(),
    agent_constraints=st.session_state.get("agent_constraints", "").strip(),
    agent_workflow=st.session_state.get("agent_workflow", "").strip(),
    agent_verification=st.session_state.get("agent_verification", "").strip(),
    agent_done_when=st.session_state.get("agent_done_when", "").strip(),
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

**Vorausfüllung aktiv für (minimaler Start):**
- **LLM:** Rolle/Persona, Kontext, Output-Format
- **Agent:** Arbeitsweise, Verifikation

**Bewusst ohne Auto-Vorausfüllung:**
- **LLM:** Anforderungen, konkrete Fachinhalte
- **Agent:** Ziel, projektspezifische Anforderungen, individuelle Produktentscheidungen

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
**LLM – Vorher (manuell, ohne Baustein):**
```text
Bitte erkläre Rekursion.
```
**LLM – Nachher (mit strukturierender Vorausfüllung):**
```text
Rolle: Didaktisch starker Tutor für Informatik-Studierende
Kontext: Erkläre auf Bachelor-Niveau mit klarer Struktur.
Aufgabe: Erkläre Rekursion mit einem einfachen Python-Beispiel
Anforderungen: klare Sprache, 3 Kernpunkte, häufige Fehler nennen
Output-Format: Antwort in 3 Abschnitten: Definition, Beispiel, Fallstricke.
```

**Agent – Vorher (vage):**
```text
Mach das Frontend besser.
```
**Agent – Nachher (mit Baustein + Übernahme aus früherem Prompt):**
```text
Ziel: Prompt-Typ nach oben verschieben und Felder dynamisch nach LLM/Agent anzeigen
Kontext: Streamlit-UI in src/app.py, Promptaufbau in src/prompt_generator.py
Constraints: kein Backend-Umbau, keine Persistenz, minimal-invasive UI-Anpassung
Arbeitsweise: Zuerst analysieren, dann planen, dann minimal umsetzen.
Verifikation: Zeige vorher/nachher Verhalten.
Done-When: Beide Modi zeigen nur relevante Felder, Vorschau und Quality-Check passen
```
        """
    )

if st.button("Prompt generieren"):
    output_path = save_generated_prompt(preview_prompt, filename)

    st.subheader("Generierter Prompt")
    st.code(preview_prompt, language="markdown")
    st.success(f"Prompt gespeichert unter: {output_path}")
