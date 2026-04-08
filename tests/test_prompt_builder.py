from pathlib import Path

from prompt_builder import PROMPTS_DIR, list_markdown_files, load_text_file


def test_prompts_directory_exists() -> None:
    assert PROMPTS_DIR.exists()


def test_list_markdown_files_returns_markdown_files() -> None:
    system_files = list_markdown_files(PROMPTS_DIR / "system")
    assert system_files
    assert all(path.suffix == ".md" for path in system_files)


def test_load_text_file_reads_markdown_content() -> None:
    tutor_path = PROMPTS_DIR / "system" / "persona_tutor.md"
    content = load_text_file(tutor_path)
    assert "Tutor" in content
    assert isinstance(content, str)
