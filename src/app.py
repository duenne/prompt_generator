import streamlit as st

from prompt_generator import PromptRequest, build_prompt, save_generated_prompt


st.set_page_config(page_title="Prompt-Generator", layout="centered")

st.title("Prompt-Generator für Tutor, Engineer und Tester")
st.write(
    "Erzeuge strukturierte, versionierbare Prompts für ein LLM-gestütztes Lern-App-Projekt."
)

persona_name = st.selectbox(
    "Persona auswählen",
    options=["tutor", "engineer", "tester"],
)

goal = st.text_input(
    "Ziel",
    placeholder="z. B. Erkläre Rekursion oder schreibe eine Funktion zur Bereinigung von Notizen",
)

requirements = st.text_area(
    "Anforderungen",
    placeholder="z. B. mit Beispiel, Python 3.11, pytest-Tests, klare Struktur ...",
    height=140,
)

scenario = st.text_area(
    "Szenario",
    placeholder="z. B. Teil einer Lern-App für Studierende im ersten Semester",
    height=140,
)

filename = st.text_input(
    "Dateiname für den generierten Prompt",
    value=f"{persona_name}_prompt_v1.md",
)

if st.button("Prompt generieren"):
    request = PromptRequest(
        persona_name=persona_name,
        goal=goal.strip(),
        requirements=requirements.strip(),
        scenario=scenario.strip(),
    )

    prompt_text = build_prompt(request)
    output_path = save_generated_prompt(prompt_text, filename)

    st.subheader("Generierter Prompt")
    st.code(prompt_text, language="markdown")
    st.success(f"Prompt gespeichert unter: {output_path}")
