from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def list_markdown_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.md"))
