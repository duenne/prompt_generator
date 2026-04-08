from pathlib import Path

from prompt_generator import PromptRequest, build_prompt, save_generated_prompt


def save_generated_output(output_text: str, file_name: str, directory_name: str) -> Path:
    output_dir = Path(__file__).resolve().parent.parent / directory_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / file_name
    output_path.write_text(output_text, encoding="utf-8")
    return output_path


def example_engineer_workflow() -> None:
    request = PromptRequest(
        persona_name="engineer",
        target_key="create_new_feature",
        goal="Schreibe eine Python-Funktion zur Bereinigung von Vorlesungsnotizen.",
        requirements="Python 3.11, snake_case, kleine Funktionen, Standardbibliothek, pytest-Tests.",
        scenario="Die Funktion wird in einer lokalen Lern-App eingesetzt, um Rohtext vor dem Zusammenfassen zu normalisieren.",
    )

    prompt_text = build_prompt(request)
    prompt_path = save_generated_prompt(prompt_text, "engineer_notes_cleaner_v1.md")

    print("=== GENERIERTER PROMPT ===")
    print(prompt_text)
    print(f"\nPrompt gespeichert unter: {prompt_path}")

    simulated_llm_output = """def normalize_notes(raw_notes: str) -> str:
    \"\"\"Normalize whitespace and remove empty lines from lecture notes.\"\"\"
    cleaned_lines = []
    for line in raw_notes.splitlines():
        normalized_line = " ".join(line.split())
        if normalized_line:
            cleaned_lines.append(normalized_line)
    return "\\n".join(cleaned_lines)
"""

    code_path = save_generated_output(
        simulated_llm_output,
        "notes_cleaner_example.py",
        "generated_code",
    )
    print(f"Beispielhafter Code gespeichert unter: {code_path}")


if __name__ == "__main__":
    example_engineer_workflow()
