from dataclasses import dataclass
from pathlib import Path

from prompt_builder import PROMPTS_DIR, load_text_file


GENERATED_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "generated_prompts"


@dataclass
class PromptRequest:
    persona_name: str
    target_key: str
    goal: str
    requirements: str
    scenario: str
    prompt_type: str = "llm"


@dataclass
class QualityCheckResult:
    score: int
    max_score: int
    feedback: list[str]
    suggestion: str


TARGET_LABELS = {
    "tutor": {
        "explain_concept": "Explain concept",
    },
    "engineer": {
        "create_new_feature": "Create new feature",
        "refactor_code": "Refactor existing code",
        "explain_code": "Explain code",
    },
    "tester": {
        "review_code": "Review code",
    },
}

PERSONA_FILE_MAP = {
    "tutor": PROMPTS_DIR / "system" / "persona_tutor.md",
    "engineer": PROMPTS_DIR / "system" / "persona_engineer.md",
    "tester": PROMPTS_DIR / "system" / "persona_tester.md",
}

TASK_FILE_MAP = {
    "tutor": {
        "explain_concept": PROMPTS_DIR / "tasks" / "explain_concept_v1.md",
    },
    "engineer": {
        "create_new_feature": PROMPTS_DIR / "tasks" / "engineer_prompt_create_feature_v1.md",
        "refactor_code": PROMPTS_DIR / "tasks" / "engineer_prompt_refactor_code_v1.md",
        "explain_code": PROMPTS_DIR / "tasks" / "engineer_prompt_explain_code_v1.md",
    },
    "tester": {
        "review_code": PROMPTS_DIR / "tasks" / "review_code_v1.md",
    },
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


def get_target_options(persona_name: str) -> dict[str, str]:
    if persona_name not in TARGET_LABELS:
        raise ValueError(f"Unbekannte Persona: {persona_name}")
    return TARGET_LABELS[persona_name]


def load_task_template(persona_name: str, target_key: str) -> str:
    if persona_name not in TASK_FILE_MAP:
        raise ValueError(f"Keine Task-Datei für Persona: {persona_name}")
    persona_tasks = TASK_FILE_MAP[persona_name]
    if target_key not in persona_tasks:
        raise ValueError(
            f"Unbekanntes Ziel '{target_key}' für Persona: {persona_name}"
        )
    return load_text_file(persona_tasks[target_key])


def load_shared_rules(persona_name: str) -> list[str]:
    files = list(SHARED_FILES)
    if persona_name == "engineer":
        files.extend(ENGINEER_ONLY_FILES)
    return [load_text_file(path) for path in files]


def build_prompt(request: PromptRequest) -> str:
    persona_text = load_persona(request.persona_name)
    task_text = load_task_template(request.persona_name, request.target_key)
    shared_rules = load_shared_rules(request.persona_name)
    target_label = get_target_options(request.persona_name).get(
        request.target_key, request.target_key
    )

    normalized_prompt_type = request.prompt_type.lower().strip()
    if normalized_prompt_type == "agent":
        request_block = _build_agent_request_block(request, target_label)
    else:
        request_block = _build_llm_request_block(request, target_label)

    sections = [persona_text, task_text, *shared_rules, request_block]

    return "\n\n".join(section.strip() for section in sections if section and section.strip())


def evaluate_prompt_quality(request: PromptRequest) -> QualityCheckResult:
    normalized_prompt_type = request.prompt_type.lower().strip()
    if normalized_prompt_type == "agent":
        return _evaluate_agent_prompt_quality(request)
    return _evaluate_llm_prompt_quality(request)


def save_generated_prompt(prompt_text: str, filename: str) -> Path:
    GENERATED_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GENERATED_PROMPTS_DIR / filename
    output_path.write_text(prompt_text, encoding="utf-8")
    return output_path


def _build_llm_request_block(request: PromptRequest, target_label: str) -> str:
    output_format = _extract_output_format(request.requirements)
    sections = [
        "Prompt-Typ: LLM (einmalige Antwort)",
        "Rolle:",
        f"- Persona: {request.persona_name}",
        f"- Zieltyp: {target_label}",
        "Kontext:",
        request.scenario or "Nicht angegeben.",
        "Aufgabe:",
        request.goal or "Nicht angegeben.",
        "Anforderungen:",
        request.requirements or "Keine spezifischen Anforderungen angegeben.",
        "Output-Format:",
        output_format,
        "Meta-Regel: Liefere genau eine strukturierte, abgeschlossene Antwort.",
    ]
    return "\n".join(sections)


def _build_agent_request_block(request: PromptRequest, target_label: str) -> str:
    workflow = _derive_agent_workflow(request.goal, target_label)
    sections = [
        "Prompt-Typ: Agent (iterativer Arbeitsprozess)",
        "Ziel:",
        request.goal or "Nicht angegeben.",
        "Kontext:",
        request.scenario or "Nicht angegeben.",
        "Constraints:",
        request.requirements or "Keine Constraints angegeben.",
        "Arbeitsweise (Schritte / Iteration):",
        workflow,
        "Output pro Schritt:",
        "- Schrittziel",
        "- Ergebnis/Artefakt",
        "- Kurze Begründung",
        "- Nächster Schritt",
        "Meta-Regel: Eine explizite Arbeitsweise mit klaren Schritten ist verpflichtend.",
    ]
    return "\n".join(sections)


def _derive_agent_workflow(goal: str, target_label: str) -> str:
    if not goal.strip():
        return "- Schritt 1: Ziel präzisieren.\n- Schritt 2: Lösungsweg definieren.\n- Schritt 3: Ergebnis prüfen."
    return (
        f"- Schritt 1: Ziel '{goal.strip()}' in Teilschritte für '{target_label}' zerlegen.\n"
        "- Schritt 2: Erste Iteration ausführen und Zwischenergebnis dokumentieren.\n"
        "- Schritt 3: Ergebnis gegen Constraints prüfen und überarbeiten.\n"
        "- Schritt 4: Finales Ergebnis + offene Risiken ausgeben."
    )


def _extract_output_format(requirements: str) -> str:
    normalized_requirements = requirements.lower()
    format_keywords = ["format", "json", "markdown", "liste", "tabelle", "struktur"]
    if any(keyword in normalized_requirements for keyword in format_keywords):
        return requirements
    return "Bitte als klar gegliederte Markdown-Antwort ausgeben."


def _evaluate_llm_prompt_quality(request: PromptRequest) -> QualityCheckResult:
    feedback: list[str] = []
    score = 0
    max_score = 3

    if request.goal.strip():
        score += 1
        feedback.append("🟢 Ziel vorhanden.")
    else:
        feedback.append("🔴 Kritisch: Ziel fehlt.")

    requirement_text = request.requirements.strip()
    format_keywords = ["format", "json", "markdown", "liste", "tabelle", "struktur"]
    if any(keyword in requirement_text.lower() for keyword in format_keywords):
        score += 1
        feedback.append("🟢 Output-Format erkannt.")
    else:
        feedback.append("🟡 Hinweis: Kein klares Output-Format erkannt.")

    if len(request.scenario.strip()) >= 20:
        score += 1
        feedback.append("🟢 Kontext ist ausreichend detailliert.")
    else:
        feedback.append("🟡 Hinweis: Kontext ist sehr kurz.")

    if not request.goal.strip():
        suggestion = "Präzisiere das Ziel mit einem gewünschten Ergebnis und Erfolgskriterium."
    elif not any(keyword in requirement_text.lower() for keyword in format_keywords):
        suggestion = "Füge ein konkretes Output-Format hinzu (z. B. Markdown-Liste oder JSON-Schema)."
    else:
        suggestion = "Erweitere den Kontext um Zielgruppe oder Einsatzsituation für präzisere Antworten."

    return QualityCheckResult(
        score=score, max_score=max_score, feedback=feedback, suggestion=suggestion
    )


def _evaluate_agent_prompt_quality(request: PromptRequest) -> QualityCheckResult:
    feedback: list[str] = []
    score = 0
    max_score = 3

    workflow = _derive_agent_workflow(request.goal, request.target_key).strip()
    if workflow:
        score += 1
        feedback.append("🟢 Arbeitsweise (Schritte/Iteration) ist definiert.")
    else:
        feedback.append("🔴 Kritisch: Keine Arbeitsweise definiert.")

    if request.requirements.strip():
        score += 1
        feedback.append("🟢 Constraints sind vorhanden.")
    else:
        feedback.append("🟡 Warnung: Keine Constraints angegeben.")

    if len(request.goal.strip()) >= 20:
        score += 1
        feedback.append("🟢 Ziel ist präzise genug.")
    else:
        feedback.append("🟡 Warnung: Ziel ist noch vage.")

    if not request.requirements.strip():
        suggestion = "Ergänze klare Constraints (z. B. Technologien, Grenzen, Qualitätskriterien)."
    elif len(request.goal.strip()) < 20:
        suggestion = "Präzisiere das Ziel mit messbaren Ergebnissen statt allgemeiner Formulierungen."
    else:
        suggestion = "Definiere für jeden Schritt ein Prüfkriterium, um Iterationen gezielt zu steuern."

    return QualityCheckResult(
        score=score, max_score=max_score, feedback=feedback, suggestion=suggestion
    )
