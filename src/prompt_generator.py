from dataclasses import dataclass
from pathlib import Path

from prompt_builder import PROMPTS_DIR, load_text_file


GENERATED_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "generated_prompts"


@dataclass
class PromptRequest:
    persona_name: str
    target_key: str
    prompt_type: str = "llm"
    goal: str = ""
    requirements: str = ""
    scenario: str = ""
    llm_role: str = ""
    llm_context: str = ""
    llm_task: str = ""
    llm_requirements: str = ""
    llm_output_format: str = ""
    llm_examples: str = ""
    agent_goal: str = ""
    agent_context: str = ""
    agent_constraints: str = ""
    agent_workflow: str = ""
    agent_verification: str = ""
    agent_done_when: str = ""


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

    return "\n\n".join(
        section.strip() for section in sections if section and section.strip()
    )


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
    role = request.llm_role.strip() or request.persona_name
    context = request.llm_context.strip() or request.scenario.strip() or "Nicht angegeben."
    task = request.llm_task.strip() or request.goal.strip() or "Nicht angegeben."
    requirements = (
        request.llm_requirements.strip()
        or request.requirements.strip()
        or "Keine spezifischen Anforderungen angegeben."
    )
    output_format = request.llm_output_format.strip() or _extract_output_format(requirements)

    sections = [
        "Prompt-Typ: LLM (einmalige Antwort)",
        "Rolle:",
        f"- Persona: {role}",
        f"- Zieltyp: {target_label}",
        "Kontext:",
        context,
        "Aufgabe:",
        task,
        "Anforderungen:",
        requirements,
        "Output-Format:",
        output_format,
    ]

    if request.llm_examples.strip():
        sections.extend(["Beispiele (optional):", request.llm_examples.strip()])

    sections.append(
        "Meta-Regel: Liefere genau eine strukturierte, abgeschlossene Antwort mit minimaler Ambiguität."
    )
    return "\n".join(sections)


def _build_agent_request_block(request: PromptRequest, target_label: str) -> str:
    goal = request.agent_goal.strip() or request.goal.strip() or "Nicht angegeben."
    context = request.agent_context.strip() or request.scenario.strip() or "Nicht angegeben."
    constraints = (
        request.agent_constraints.strip()
        or request.requirements.strip()
        or "Keine Constraints angegeben."
    )
    workflow = request.agent_workflow.strip() or _derive_agent_workflow(goal, target_label)
    verification = request.agent_verification.strip() or "Keine Verifikation definiert."
    done_when = request.agent_done_when.strip() or "Kein Abschlusskriterium definiert."

    sections = [
        "Prompt-Typ: Agent (iterativer Arbeitsprozess)",
        "Ziel:",
        goal,
        "Kontext:",
        context,
        "Constraints:",
        constraints,
        "Arbeitsweise:",
        workflow,
        "Verifikation:",
        verification,
        "Done when:",
        done_when,
        "Meta-Regel: Trenne Planung und Umsetzung explizit und dokumentiere jede Iteration nachvollziehbar.",
    ]
    return "\n".join(sections)


def _derive_agent_workflow(goal: str, target_label: str) -> str:
    if not goal.strip() or goal.strip() == "Nicht angegeben.":
        return (
            "1) Ziel schärfen und Scope bestätigen.\n"
            "2) Plan mit klaren Schritten erstellen.\n"
            "3) Umsetzung pro Schritt durchführen.\n"
            "4) Ergebnis mit Verifikation prüfen."
        )
    return (
        f"1) Analysiere das Ziel '{goal.strip()}' für '{target_label}'.\n"
        "2) Erstelle einen Plan mit nachvollziehbaren Teilschritten.\n"
        "3) Setze die Teilschritte nacheinander um und dokumentiere Entscheidungen.\n"
        "4) Verifiziere das Ergebnis und liefere offene Risiken + nächste Schritte."
    )


def _extract_output_format(requirements: str) -> str:
    normalized_requirements = requirements.lower()
    format_keywords = ["format", "json", "markdown", "liste", "tabelle", "struktur"]
    if any(keyword in normalized_requirements for keyword in format_keywords):
        return requirements
    return "Bitte als klar gegliederte Markdown-Antwort ausgeben."


def _is_general_requirement_text(text: str) -> bool:
    normalized = text.lower().strip()
    if not normalized:
        return True
    generic_terms = ["gut", "präzise", "klar", "hochwertig", "sauber", "professionell"]
    token_count = len([token for token in normalized.split() if token])
    if token_count < 4:
        return True
    return all(term in normalized for term in generic_terms[:2])


def _is_vague_goal(goal: str) -> bool:
    normalized = goal.lower().strip()
    if len(normalized) < 20:
        return True
    vague_patterns = ["verbessern", "optimieren", "fixen", "anpassen", "etwas"]
    return any(pattern in normalized for pattern in vague_patterns) and len(normalized) < 45


def _evaluate_llm_prompt_quality(request: PromptRequest) -> QualityCheckResult:
    feedback: list[str] = []
    score = 0
    max_score = 4

    task = request.llm_task.strip() or request.goal.strip()
    context = request.llm_context.strip() or request.scenario.strip()
    output_format = request.llm_output_format.strip()
    requirements = request.llm_requirements.strip() or request.requirements.strip()

    if task:
        score += 1
        feedback.append("🟢 Aufgabe vorhanden.")
    else:
        feedback.append("🟠 Warnung: Aufgabe fehlt.")

    if len(context) >= 30:
        score += 1
        feedback.append("🟢 Kontext ausreichend detailliert.")
    else:
        feedback.append("🟠 Warnung: Kontext ist zu knapp.")

    if output_format:
        score += 1
        feedback.append("🟢 Output-Format definiert.")
    else:
        feedback.append("🔵 Hinweis: Kein Output-Format definiert.")

    if requirements and not _is_general_requirement_text(requirements):
        score += 1
        feedback.append("🟢 Anforderungen sind konkret genug.")
    else:
        feedback.append("🔵 Hinweis: Anforderungen sind noch sehr allgemein formuliert.")

    if not task:
        suggestion = "Beschreibe die Aufgabe als konkrete Aktion mit erwartbarem Ergebnis."
    elif len(context) < 30:
        suggestion = "Ergänze den Kontext um Zielgruppe, Einsatzort oder relevante Randbedingungen."
    elif not output_format:
        suggestion = "Definiere ein explizites Ausgabeformat (z. B. Markdown-Gliederung oder JSON-Schema)."
    else:
        suggestion = "Verfeinere die Anforderungen mit fachlichen Details oder Qualitätskriterien."

    return QualityCheckResult(
        score=score,
        max_score=max_score,
        feedback=feedback,
        suggestion=suggestion,
    )


def _evaluate_agent_prompt_quality(request: PromptRequest) -> QualityCheckResult:
    feedback: list[str] = []
    score = 0
    max_score = 5

    goal = request.agent_goal.strip() or request.goal.strip()
    constraints = request.agent_constraints.strip() or request.requirements.strip()
    workflow = request.agent_workflow.strip()
    verification = request.agent_verification.strip()
    done_when = request.agent_done_when.strip()

    if goal and not _is_vague_goal(goal):
        score += 1
        feedback.append("🟢 Ziel ist präzise genug.")
    else:
        feedback.append("🔴 Fehler: Ziel ist zu vage.")

    if constraints:
        score += 1
        feedback.append("🟢 Constraints vorhanden.")
    else:
        feedback.append("🟠 Warnung: Keine Constraints angegeben.")

    if workflow:
        score += 1
        feedback.append("🟢 Arbeitsweise beschrieben.")
    else:
        feedback.append("🔴 Fehler: Keine Arbeitsweise beschrieben.")

    if verification:
        score += 1
        feedback.append("🟢 Verifikation vorhanden.")
    else:
        feedback.append("🔴 Fehler: Keine Verifikation vorhanden.")

    if done_when:
        score += 1
        feedback.append("🟢 Abschlusskriterium definiert.")
    else:
        feedback.append("🟠 Warnung: Kein klares Abschlusskriterium definiert.")

    if not goal or _is_vague_goal(goal):
        suggestion = "Formuliere das Ziel messbar (konkrete Änderung + erwartetes Ergebnis)."
    elif not workflow:
        suggestion = "Beschreibe eine klare Arbeitsweise (Analyse → Plan → Umsetzung → Review)."
    elif not verification:
        suggestion = "Ergänze konkrete Verifikation, z. B. Tests, manuelle Checks oder reproduzierbare Schritte."
    elif not done_when:
        suggestion = "Definiere ein Done-When mit eindeutigem Abschlusskriterium."
    else:
        suggestion = "Ergänze constraints-nahe Prüfschritte pro Iteration, damit das Ergebnis nachvollziehbar bleibt."

    return QualityCheckResult(
        score=score,
        max_score=max_score,
        feedback=feedback,
        suggestion=suggestion,
    )
