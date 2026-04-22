import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

st.set_page_config(page_title="Prompt Saver", page_icon="💾")
st.title("Minimaler Streamlit Prompt-Saver")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error(
        "Bitte lege eine `.env`-Datei an und setze SUPABASE_URL sowie SUPABASE_SERVICE_ROLE_KEY."
    )
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_prompt(title: str, prompt_text: str) -> tuple[bool, str]:
    if not title.strip() or not prompt_text.strip():
        return False, "Titel und Prompt dürfen nicht leer sein."

    prompt_payload = {
        "title": title.strip(),
        "prompt": prompt_text.strip(),
    }

    response = supabase.table("prompts").insert(prompt_payload).execute()
    if response.error:
        return False, f"Fehler beim Speichern in 'prompts': {response.error.message}"

    prompt_id = response.data[0].get("id")
    if not prompt_id:
        return False, "Fehler: Keine Prompt-ID zurückgegeben."

    version_payload = {
        "prompt_id": prompt_id,
        "prompt": prompt_text.strip(),
        "version_note": "Initiale Version",
    }
    version_response = supabase.table("prompt_versions").insert(version_payload).execute()
    if version_response.error:
        return False, f"Fehler beim Speichern in 'prompt_versions': {version_response.error.message}"

    return True, "Prompt erfolgreich gespeichert."


def list_prompts() -> list[dict]:
    response = supabase.table("prompts").select("*").order("id", desc=False).execute()
    if response.error or response.data is None:
        return []
    return response.data


title = st.text_input("Titel")
prompt_text = st.text_area("Prompt", height=180)

if st.button("Speichern"):
    success, message = save_prompt(title, prompt_text)
    if success:
        st.success(message)
    else:
        st.error(message)

st.markdown("---")
st.subheader("Gespeicherte Prompts")
all_prompts = list_prompts()
if not all_prompts:
    st.info("Keine Prompts gefunden oder Fehler beim Laden.")
else:
    for item in all_prompts:
        st.write(f"**{item.get('title', 'Ohne Titel')}**")
        st.write(item.get("prompt", ""))
        st.write("---")
