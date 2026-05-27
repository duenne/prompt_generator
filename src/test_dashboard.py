import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

import streamlit as st

TEST_RESULTS_DIR = Path("test_results")
JUNIT_PATH = TEST_RESULTS_DIR / "latest_junit.xml"
COVERAGE_PATH = TEST_RESULTS_DIR / "latest_coverage.xml"
META_PATH = TEST_RESULTS_DIR / "latest_meta.json"


def _safe_float(value: str | None, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_meta(path: Path = META_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def parse_junit_xml(path: Path = JUNIT_PATH) -> dict:
    if not path.exists():
        return {"available": False, "message": "Noch kein Testlauf vorhanden", "summary": {}, "testcases": []}
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return {"available": False, "message": "JUnit-XML konnte nicht gelesen werden.", "summary": {}, "testcases": []}

    testsuite = root.find("testsuite") if root.tag == "testsuites" else root
    if testsuite is None:
        return {"available": False, "message": "JUnit-XML enthält keine Testsuite.", "summary": {}, "testcases": []}

    tests = int(testsuite.attrib.get("tests", 0))
    failures = int(testsuite.attrib.get("failures", 0))
    errors = int(testsuite.attrib.get("errors", 0))
    skipped = int(testsuite.attrib.get("skipped", 0))
    passed = max(tests - failures - errors - skipped, 0)
    duration = _safe_float(testsuite.attrib.get("time"))

    cases = []
    for case in testsuite.findall("testcase"):
        status = "passed"
        if case.find("failure") is not None:
            status = "failed"
        elif case.find("error") is not None:
            status = "error"
        elif case.find("skipped") is not None:
            status = "skipped"

        cases.append(
            {
                "name": case.attrib.get("name", ""),
                "classname": case.attrib.get("classname", ""),
                "status": status,
                "duration_s": _safe_float(case.attrib.get("time")),
            }
        )

    return {
        "available": True,
        "message": "",
        "summary": {
            "tests": tests,
            "passed": passed,
            "failed": failures,
            "errors": errors,
            "skipped": skipped,
            "duration_s": duration,
        },
        "testcases": cases,
    }


def parse_coverage_xml(path: Path = COVERAGE_PATH) -> dict:
    if not path.exists():
        return {"available": False, "message": "Keine Coverage-Datei vorhanden.", "total": None, "modules": []}
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return {"available": False, "message": "Coverage-XML konnte nicht gelesen werden.", "total": None, "modules": []}

    line_rate = _safe_float(root.attrib.get("line-rate"), default=-1)
    total_coverage = None if line_rate < 0 else round(line_rate * 100, 2)

    modules = []
    for package in root.findall("./packages/package"):
        package_rate = round(_safe_float(package.attrib.get("line-rate")) * 100, 2)
        modules.append(
            {
                "module": package.attrib.get("name", ""),
                "line_coverage_percent": package_rate,
            }
        )

    return {"available": True, "message": "", "total": total_coverage, "modules": modules}


def _get_git_info() -> tuple[str | None, str | None]:
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return commit, branch
    except Exception:
        return None, None


def run_local_tests() -> tuple[int, str]:
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        f"--junitxml={JUNIT_PATH}",
        "--cov=src",
        f"--cov-report=xml:{COVERAGE_PATH}",
        "--cov-report=term",
    ]
    process = subprocess.run(command, capture_output=True, text=True)

    git_commit, git_branch = _get_git_info()
    meta = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": " ".join(command),
        "returncode": process.returncode,
        "python_version": sys.version,
        "platform": platform.platform(),
    }
    if git_commit:
        meta["git_commit"] = git_commit
    if git_branch:
        meta["git_branch"] = git_branch

    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return process.returncode, process.stdout + "\n" + process.stderr


def render_test_dashboard() -> None:
    st.title("Test-Dashboard")

    if os.getenv("ENABLE_LOCAL_TEST_RUNNER", "").lower() == "true":
        if st.button("Tests lokal ausführen"):
            with st.spinner("Führe Tests aus..."):
                returncode, output = run_local_tests()
            if returncode == 0:
                st.success("Testlauf erfolgreich abgeschlossen.")
            else:
                st.warning(f"Testlauf beendet mit Exit-Code {returncode}.")
            st.code(output)

    junit_data = parse_junit_xml()
    coverage_data = parse_coverage_xml()
    meta = load_meta()

    tabs = st.tabs(["Übersicht", "Einzeltests", "Coverage", "Nächste Schritte"])

    with tabs[0]:
        if not junit_data["available"]:
            st.info("Noch kein Testlauf vorhanden")
            st.warning(junit_data["message"])
        summary = junit_data.get("summary", {})

        col1, col2, col3 = st.columns(3)
        col1.metric("Tests", summary.get("tests", 0))
        col2.metric("Passed", summary.get("passed", 0))
        col3.metric("Failed", summary.get("failed", 0))

        col4, col5, col6 = st.columns(3)
        col4.metric("Errors", summary.get("errors", 0))
        col5.metric("Skipped", summary.get("skipped", 0))
        col6.metric("Dauer (s)", round(summary.get("duration_s", 0.0), 2))

        st.markdown("### Letzter Lauf")
        st.write(f"Zeitpunkt (UTC): {meta.get('timestamp_utc', 'unbekannt')}")
        st.write(f"Exit-Code: {meta.get('returncode', 'unbekannt')}")
        st.write(f"Befehl: {meta.get('command', 'unbekannt')}")

        if coverage_data["available"] and coverage_data["total"] is not None:
            st.metric("Gesamt-Coverage (%)", coverage_data["total"])

    with tabs[1]:
        if junit_data["testcases"]:
            st.dataframe(junit_data["testcases"], use_container_width=True)
        else:
            st.info("Keine Einzeltests verfügbar.")

    with tabs[2]:
        if coverage_data["available"]:
            if coverage_data["modules"]:
                st.dataframe(coverage_data["modules"], use_container_width=True)
            else:
                st.info("Keine Modul-Coverage gefunden.")
        else:
            st.info(coverage_data["message"])

    with tabs[3]:
        st.markdown("### Priorisierte nächste Testverbesserungen")
        st.markdown(
            "1. `test_save_generated_prompt_creates_file_in_generated_prompts`\n"
            "2. `test_scenario_manager_skips_or_reports_corrupt_json`\n"
            "3. `test_load_prompt_history_orders_by_mtime_and_applies_limit`\n"
            "4. CI-Artefakte dauerhaft speichern\n"
            "5. Testlauf-Historie aufbauen\n"
            "6. Flaky-Test-Indikatoren ergänzen\n"
            "7. Mock-Supabase vs. Real-Supabase im Report sichtbar machen"
        )
