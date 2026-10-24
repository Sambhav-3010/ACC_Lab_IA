from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
import numpy as np
import pandas as pd
from .config import scenario_spec
from .model import load_or_train
from .workload import generate_workload


@dataclass
class Server:
    capacity: float
    active_work: float = 0.0
    active_requests: int = 0

    @property
    def cpu(self):
        return min(1.5, self.active_work / (self.capacity * 1000.0))

    def step(self, dt):
        self.active_work = max(0.0, self.active_work - self.capacity * 1000.0 * dt)
        if self.active_work == 0:
            self.active_requests = 0


def _choose(policy, servers, predictions, cursor):
    if policy == "round_robin":
        return (cursor + 1) % len(servers)
    if policy == "least_loaded":
        return min(range(len(servers)), key=lambda i: servers[i].cpu)
    scores = [0.5 * (predictions[i] if predictions[i] is not None else servers[i].cpu) + 0.5 * servers[i].cpu for i in range(len(servers))]
    safe = [i for i in range(len(servers)) if (predictions[i] if predictions[i] is not None else servers[i].cpu) < 0.8 and servers[i].cpu < 0.8]
    return min(safe or range(len(servers)), key=lambda i: scores[i])


def run(policy="ml_predictive", scenario="E3", duration=None, seed=101):
    cfg = scenario_spec(scenario)
    workload = generate_workload(scenario, duration, seed)
    model_path = Path(__file__).resolve().parents[1] / "models" / "load_predictor.joblib"
    model = load_or_train(model_path)
    servers = [Server(float(cap)) for cap in cfg["capacities"]]
    rows, route_times, cursor, last_time = [], [], -1, 0.0
    for _, request in workload.iterrows():
        arrival = float(request.arrival_time)
        elapsed = max(0.0, arrival - last_time)
        for server in servers:
            server.step(elapsed)
        last_time = arrival
        predictions = []
        for server in servers:
            prediction = float(model.predict([[server.cpu, server.cpu, 0.0, server.active_requests, request.arrival_rate, server.capacity]])[0]) if policy == "ml_predictive" else None
            predictions.append(prediction)
        started = perf_counter()
        selected = _choose(policy, servers, predictions, cursor)
        route_times.append((perf_counter() - started) * 1e6)
        cursor = selected
        server = servers[selected]
        service_time = float(request.work_cpu_ms / (server.capacity * 1000.0))
        server.active_work += float(request.work_cpu_ms)
        server.active_requests += 1
        rows.append({"time": arrival, "request_id": int(request.request_id), "server": f"S{selected}", "policy": policy, "cpu_before": server.cpu, "prediction": predictions[selected], "latency_s": service_time + max(0, server.active_requests - 1) * 0.02, "overloaded": int(server.cpu >= 0.8)})
    frame = pd.DataFrame(rows)
    duration_value = duration or cfg["duration_s"]
    counts = frame["server"].value_counts().reindex([f"S{i}" for i in range(len(servers))], fill_value=0) if not frame.empty else pd.Series(dtype=float)
    avg_count = counts.mean() if len(counts) else 1
    metrics = {"policy": policy, "scenario": scenario, "seed": seed, "requests": len(frame), "avg_latency_s": float(frame.latency_s.mean()) if not frame.empty else 0.0, "p95_latency_s": float(frame.latency_s.quantile(.95)) if not frame.empty else 0.0, "throughput_rps": float(len(frame) / max(duration_value, 1)), "overload_events": int(frame.overloaded.sum()) if not frame.empty else 0, "imbalance_cv": float(counts.std(ddof=0) / avg_count) if len(counts) else 0.0, "route_time_us": float(np.mean(route_times)) if route_times else 0.0, "server_counts": counts.to_dict()}
    return metrics, frame


def run_comparison(scenario="E3", duration=None, seed=101):
    results, details = [], {}
    for policy in ("round_robin", "least_loaded", "ml_predictive"):
        metrics, frame = run(policy, scenario, duration, seed)
        results.append(metrics)
        details[policy] = frame
    return pd.DataFrame(results), details
