from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Optional


@dataclass
class ScenarioVersion:
    version: str
    content: str
    created_at: datetime
    description: str


@dataclass
class Scenario:
    name: str
    versions: Dict[str, ScenarioVersion]
    current_version: str


class ScenarioManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.scenarios_dir = self.base_dir / "scenarios"
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.scenarios: Dict[str, Scenario] = {}
        self._load_scenarios()

    def _load_scenarios(self) -> None:
        for scenario_file in sorted(self.scenarios_dir.glob("*.json")):
            data = json.loads(scenario_file.read_text(encoding="utf-8"))
            versions = {
                item["version"]: ScenarioVersion(
                    version=item["version"],
                    content=item["content"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    description=item["description"],
                )
                for item in data.get("versions", [])
            }
            if not versions:
                continue
            scenario = Scenario(
                name=data["name"],
                versions=versions,
                current_version=data["current_version"],
            )
            self.scenarios[scenario.name] = scenario

    def create_scenario(self, name: str, content: str, description: str) -> Scenario:
        if name in self.scenarios:
            raise ValueError(f"Szenario '{name}' existiert bereits.")

        version_key = "v1.0"
        scenario_version = ScenarioVersion(
            version=version_key,
            content=content,
            created_at=datetime.now(),
            description=description,
        )

        scenario = Scenario(
            name=name,
            versions={version_key: scenario_version},
            current_version=version_key,
        )
        self.scenarios[name] = scenario
        self._save_scenario(scenario)
        return scenario

    def update_scenario(self, name: str, content: str, description: str) -> Scenario:
        if name not in self.scenarios:
            raise ValueError(f"Szenario '{name}' nicht gefunden.")

        scenario = self.scenarios[name]
        major_version = int(scenario.current_version.lstrip("v").split(".")[0])
        new_version = f"v{major_version + 1}.0"

        scenario_version = ScenarioVersion(
            version=new_version,
            content=content,
            created_at=datetime.now(),
            description=description,
        )
        scenario.versions[new_version] = scenario_version
        scenario.current_version = new_version
        self._save_scenario(scenario)
        return scenario

    def get_scenario(self, name: str, version: Optional[str] = None) -> Optional[ScenarioVersion]:
        scenario = self.scenarios.get(name)
        if scenario is None:
            return None
        selected_version = version or scenario.current_version
        return scenario.versions.get(selected_version)

    def list_scenarios(self) -> List[str]:
        return list(self.scenarios.keys())

    def _save_scenario(self, scenario: Scenario) -> None:
        output = {
            "name": scenario.name,
            "current_version": scenario.current_version,
            "versions": [
                {
                    "version": version.version,
                    "content": version.content,
                    "created_at": version.created_at.isoformat(),
                    "description": version.description,
                }
                for version in scenario.versions.values()
            ],
        }
        scenario_file = self.scenarios_dir / f"{scenario.name}.json"
        scenario_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
