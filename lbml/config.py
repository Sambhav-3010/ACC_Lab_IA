from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "config" / "spec.toml"


def load_spec() -> dict:
    with SPEC_PATH.open("rb") as handle:
        return tomllib.load(handle)


def scenario_spec(scenario: str) -> dict:
    spec = load_spec()
    if scenario not in spec["scenario"]:
        raise ValueError(f"Unknown scenario {scenario}; choose E1, E2, E3 or E4")
    result = dict(spec["scenario"][scenario])
    result["scenario"] = scenario
    result["capacities"] = result.get("capacities", spec["cluster"]["capacities"])
    return result
