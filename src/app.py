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

st.title("Prompt-Generator")
st.write("Reduzierte, klare UI mit Startpunkten und Live-Qualitätsfeedback.")

FIELD_SEPARATOR = {
    "llm_role": " | ",
    "llm_output_format": " | ",
    "llm_context": "\n",
    "agent_workflow": "\n",
    "agent_verification": "\n",
}

START_POINTS = {
    "leer": {
        "label": "Leer starten",
        "persona": "engineer",
        "llm": {},
        "agent": {},
    },
    "tutor": {
        "label": "Tutor (didaktisch)",
        "persona": "tutor",
        "llm": {
            "llm_role": "Didaktisch starker Tutor",
            "llm_context": "Für Studierende mit Grundkenntnissen; klare und verständliche Erklärungen.",
            "llm_requirements": "Klare Struktur, nachvollziehbare Sprache, fachlich korrekt.",
            "llm_output_format": "Definition, Beispiel, Erklärung",
        },
        "agent": {
            "agent_workflow": "1) Problem didaktisch einordnen 2) Schritte klar strukturieren 3) Lösung iterativ prüfen",
            "agent_verification": "Verifiziere Verständlichkeit mit konkretem Vorher/Nachher-Beispiel.",
        },
    },
    "engineer": {
        "label": "Engineer (technisch präzise)",
        "persona": "engineer",
        "llm": {
            "llm_role": "Präziser Software Engineer",
            "llm_requirements": "klare Struktur, technische Korrektheit",
            "llm_output_format": "strukturierte Lösung mit Begründung",
        },
        "agent": {
            "agent_workflow": "1) Analyse 2) Plan 3) minimal-invasive Umsetzung 4) Verifikation",
            "agent_verification": "Prüfe Verhalten mit reproduzierbaren Schritten und Tests.",
        },
    },
    "tester": {
        "label": "Tester (kritisch, edge-case fokussiert)",
        "persona": "tester",
        "llm": {
            "llm_role": "Kritischer Tester mit Fokus auf Edge Cases",
            "llm_requirements": "Explizite Annahmen, Risikofokus, Grenzfälle priorisieren.",
            "llm_output_format": "Risiken, Testfälle, erwartete Ergebnisse",
        },
        "agent": {
            "agent_workflow": "1) Risiken identifizieren 2) kritische Pfade priorisieren 3) edge-case-orientiert prüfen",
            "agent_verification": "Nutze negative Tests, Edge Cases und klare Reproduktionsschritte.",
        },
    },
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


def apply_start_point(start_key: str, prompt_type: str) -> None:
    if start_key == "leer":
        return

    scope = START_POINTS[start_key][prompt_type]
    for field_key, value in scope.items():
        st.session_state[field_key] = value


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

start_key = st.selectbox(
    "Startpunkt wählen",
    options=list(START_POINTS.keys()),
    format_func=lambda key: START_POINTS[key]["label"],
    help="Ein Startpunkt befüllt passende Felder als intelligente Voreinstellung.",
)

if st.button("Startpunkt anwenden"):
    apply_start_point(start_key, prompt_type.lower())
    st.rerun()

persona_name = START_POINTS[start_key]["persona"]
target_options = get_target_options(persona_name)

target_key = st.selectbox(
    "Zieltyp auswählen",
    options=list(target_options.keys()),
    format_func=lambda key: target_options[key],
)

st.caption(
    "Alle vorausgefüllten Werte sind editierbar. Der Startpunkt ist ein Default, keine zusätzliche Persona-Auswahl."
)

if prompt_type == "LLM":
    st.subheader("LLM-Felder")

    render_prefill_controls("llm_role", "Rolle", "llm")
    st.text_input(
        "Rolle",
        key="llm_role",
        placeholder="z. B. Präziser Software Engineer",
        help="Welche Perspektive oder Expertise soll das Modell einnehmen?",
    )

    render_prefill_controls("llm_context", "Kontext", "llm")
    st.text_area(
        "Kontext",
        key="llm_context",
        placeholder="z. B. für Studierende mit Grundkenntnissen",
        help="Kurzer Rahmen: Zielgruppe, Umgebung, relevante Randbedingungen.",
        height=110,
    )

    st.text_area(
        "Aufgabe",
        key="llm_task",
        placeholder="z. B. Erkläre Rekursion mit einem einfachen Python-Beispiel",
        help="Die zentrale Aufgabe möglichst konkret formulieren.",
        height=110,
    )
    st.text_area(
        "Anforderungen",
        key="llm_requirements",
        placeholder="z. B. fachlich korrekt, klar strukturiert, kurze Sätze",
        help="Qualitäts- oder Stilkriterien, die explizit eingehalten werden sollen.",
        height=110,
    )

    render_prefill_controls("llm_output_format", "Output-Format", "llm")
    st.text_input(
        "Output-Format",
        key="llm_output_format",
        placeholder="z. B. Definition, Beispiel, Erklärung",
        help="Wie die Antwort sichtbar strukturiert sein soll.",
    )
else:
    st.subheader("Agent-Felder")
    st.text_area(
        "Ziel",
        key="agent_goal",
        placeholder="z. B. Vereinfachte Prompt-UI mit Startpunkten statt Persona-Feld",
        help="Konkretes Ergebnis, das der Agent erreichen soll.",
        height=100,
    )
    st.text_area(
        "Kontext",
        key="agent_context",
        placeholder="z. B. Streamlit-UI in src/app.py, bestehende Prompt-Logik beibehalten",
        help="Relevante Dateien, Rahmenbedingungen und Annahmen.",
        height=110,
    )
    st.text_area(
        "Constraints",
        key="agent_constraints",
        placeholder="z. B. keine Backend-Änderung, keine neuen Features",
        help="Was darf nicht geändert werden oder ist fest vorgegeben?",
        height=100,
    )

    render_prefill_controls("agent_workflow", "Arbeitsweise", "agent")
    st.text_area(
        "Arbeitsweise",
        key="agent_workflow",
        placeholder="1) analysieren 2) planen 3) umsetzen 4) prüfen",
        help="Vorgehensmodell mit klaren Schritten.",
        height=110,
    )

    render_prefill_controls("agent_verification", "Verifikation", "agent")
    st.text_area(
        "Verifikation",
        key="agent_verification",
        placeholder="z. B. pytest, UI-Check, manuelle Smoke-Tests",
        help="Wie wird überprüft, dass das Ziel erreicht wurde?",
        height=100,
    )

filename = st.text_input(
    "Dateiname für den generierten Prompt",
    value=f"{start_key}_{target_key}_{prompt_type.lower()}_prompt_v1.md",
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
    agent_goal=st.session_state.get("agent_goal", "").strip(),
    agent_context=st.session_state.get("agent_context", "").strip(),
    agent_constraints=st.session_state.get("agent_constraints", "").strip(),
    agent_workflow=st.session_state.get("agent_workflow", "").strip(),
    agent_verification=st.session_state.get("agent_verification", "").strip(),
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

with st.expander("Feldlogik (reduziert)"):
    st.markdown(
        """
**LLM:** Rolle, Kontext, Aufgabe, Anforderungen, Output-Format

**Agent:** Ziel, Kontext, Constraints, Arbeitsweise, Verifikation

**Startpunkt-Logik:**
- *Leer starten*: keine Vorausfüllung
- *Tutor / Engineer / Tester*: befüllen mehrere Felder als editierbare Defaults

**Vorlagen-Logik:**
- Vorlagen bleiben erhalten, wirken aber nur auf einzelne Felder.
        """
    )

with st.expander("Beispiel: Vorher / Nachher UI"):
    st.markdown(
        """
**Vorher:**
- Persona auswählen
- Vorlage wählen
- zusätzliche optionale Felder (z. B. Beispiele, Done-When)

**Nachher:**
- Prompt-Typ
- Startpunkt wählen
- reduzierte Kernfelder je Modus
- feldbezogene Vorlagen
- Live-Vorschau + Qualitätsfeedback
        """
    )

if st.button("Prompt generieren"):
    output_path = save_generated_prompt(preview_prompt, filename)

    st.subheader("Generierter Prompt")
    st.code(preview_prompt, language="markdown")
    st.success(f"Prompt gespeichert unter: {output_path}")
