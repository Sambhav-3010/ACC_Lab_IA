from pathlib import Path
import pickle
import numpy as np

try:
    import joblib
    from sklearn.ensemble import RandomForestRegressor
except ImportError:  # Keeps the demo runnable before optional ML wheels are installed.
    joblib = None
    RandomForestRegressor = None


class HeuristicPredictor:
    """Small offline fallback; the normal path uses RandomForestRegressor."""

    def predict(self, rows):
        values = np.asarray(rows, dtype=float)
        cpu, mean, slope, active, rate, capacity = values.T
        return np.clip(cpu * .55 + mean * .25 + slope * 2 + rate / (capacity * 35) + active / 100, 0, 1.5)


def train_model(path: Path, seed=42):
    rng = np.random.default_rng(seed)
    n = 2400
    cpu = rng.uniform(0.05, 0.95, n)
    mean = np.clip(cpu + rng.normal(0, 0.10, n), 0, 1)
    slope = rng.normal(0, 0.08, n)
    active = rng.integers(0, 15, n)
    rate = rng.uniform(2, 20, n)
    capacity = rng.choice([0.5, 1.0, 1.5], n)
    X = np.column_stack([cpu, mean, slope, active, rate, capacity])
    y = np.clip(cpu + slope * 3 + rate / (capacity * 25) + rng.normal(0, 0.035, n), 0, 1.5)
    if RandomForestRegressor is None:
        return HeuristicPredictor()
    model = RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=3, random_state=seed, n_jobs=-1)
    model.fit(X, y)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path) if joblib else path.write_bytes(pickle.dumps(model))
    return model


def load_or_train(path: Path):
    if path.exists() and joblib:
        return joblib.load(path)
    return train_model(path)
