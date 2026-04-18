import importlib.util
import json
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "simulation.py"
    spec = importlib.util.spec_from_file_location("sl12_dta_simulation", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_writes_relative_outputs(tmp_path):
    module = load_module()

    result = module.main(seed=726, project_root=tmp_path)

    probes_path = tmp_path / "probes_full.json"
    assert probes_path.exists()

    probes = json.loads(probes_path.read_text(encoding="utf-8"))
    assert len(probes) == 12
    assert set(probes) == set(result["results"])
