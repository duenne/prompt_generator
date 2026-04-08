from dataclasses import dataclass
from pathlib import Path

from prompt_builder import PROMPTS_DIR, load_text_file


GENERATED_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "generated_prompts"


@dataclass
class PromptRequest:
    persona_name: str
    goal: str
    requirements: str
    scenario: str


PERSONA_FILE_MAP = {
    "tutor": PROMPTS_DIR / "system" / "persona_tutor.md",
    "engineer": PROMPTS_DIR / "system" / "persona_engineer.md",
    "tester": PROMPTS_DIR / "system" / "persona_tester.md",
}

TASK_FILE_MAP = {
    "tutor": PROMPTS_DIR / "tasks" / "explain_concept_v1.md",
    "engineer": PROMPTS_DIR / "tasks" / "generate_python_code_v1.md",
    "tester": PROMPTS_DIR / "tasks" / "review_code_v1.md",
}

SHARED_FILES = [
    PROMPTS_DIR / "shared" / "style_rules.md",
    PROMPTS_DIR / "shared" / "naming_conventions.md",
    PROMPTS_DIR / "shared" / "output_format_default.md",
]

ENGINEER_ONLY_FILES = [
    PROMPTS_DIR / "shared" / "coding_rules.md",
]


def load_persona(persona_name: str) -> str:
    if persona_name not in PERSONA_FILE_MAP:
        raise ValueError(f"Unbekannte Persona: {persona_name}")
    return load_text_file(PERSONA_FILE_MAP[persona_name])


def load_task_template(persona_name: str) -> str:
    if persona_name not in TASK_FILE_MAP:
        raise ValueError(f"Keine Task-Datei für Persona: {persona_name}")
    return load_text_file(TASK_FILE_MAP[persona_name])


def load_shared_rules(persona_name: str) -> list[str]:
    files = list(SHARED_FILES)
    if persona_name == "engineer":
        files.extend(ENGINEER_ONLY_FILES)
    return [load_text_file(path) for path in files]


def build_prompt(request: PromptRequest) -> str:
    persona_text = load_persona(request.persona_name)
    task_text = load_task_template(request.persona_name)
    shared_rules = load_shared_rules(request.persona_name)

    sections = [
        persona_text,
        task_text,
        *shared_rules,
        "Konkrete Anfrage:",
        f"Ziel: {request.goal}",
        f"Anforderungen: {request.requirements}",
        f"Szenario: {request.scenario}",
    ]

    return "\n\n".join(section.strip() for section in sections if section and section.strip())


def save_generated_prompt(prompt_text: str, filename: str) -> Path:
    GENERATED_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GENERATED_PROMPTS_DIR / filename
    output_path.write_text(prompt_text, encoding="utf-8")
    return output_path
