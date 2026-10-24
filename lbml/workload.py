import numpy as np
import pandas as pd
from .config import scenario_spec


def generate_workload(scenario="E3", duration=None, seed=101):
    cfg = scenario_spec(scenario)
    duration = int(duration or cfg["duration_s"])
    rng = np.random.default_rng(seed)
    rows = []
    request_id = 0
    for second in range(duration):
        if scenario == "E2":
            rate = cfg["base_rate"] + (cfg["peak_rate"] - cfg["base_rate"]) * second / max(duration - 1, 1)
        elif scenario == "E3" and cfg["spike_start"] <= second < cfg["spike_start"] + cfg["spike_duration"]:
            rate = cfg["peak_rate"]
        else:
            rate = cfg["base_rate"]
        for _ in range(rng.poisson(rate)):
            rows.append({"request_id": request_id, "arrival_time": second + float(rng.random()), "work_cpu_ms": float(np.clip(rng.lognormal(np.log(180), 0.65), 35, 1200)), "arrival_rate": rate})
            request_id += 1
    return pd.DataFrame(rows)
