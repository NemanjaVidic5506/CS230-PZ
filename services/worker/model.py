import json, os
from sklearn.datasets import make_regression, fetch_openml
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score, accuracy_score
from sklearn.model_selection import train_test_split
import numpy as np

MODELS_DIR = os.getenv("MODELS_DIR", "/data/models")
os.makedirs(MODELS_DIR, exist_ok=True)

def _save_model(task_id: str, payload: dict):
    path = os.path.join(MODELS_DIR, f"{task_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return path

def train_regression_synthetic(task_id, n_samples=1000, n_features=20, noise=0.1, random_state=42):
    X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=noise, random_state=random_state)
    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    result = {
        "type": "synthetic_regression",
        "coef": model.coef_.tolist(),
        "intercept": float(model.intercept_),
        "r2_train": float(r2),
        "n_samples": int(n_samples),
        "n_features": int(n_features),
        "noise": float(noise),
    }
    _save_model(task_id, result)
    return result

def train_openml_dataset(task_id, dataset="diabetes", target=None):
    ds = fetch_openml(name=dataset, as_frame=True)
    X = ds.data
    y = ds.target if target is None else ds.frame[target]
    try:
        y_float = y.astype(float)
        task = "regression"
    except Exception:
        task = "classification"

    if task == "regression":
        X_train, X_test, y_train, y_test = train_test_split(X, y.astype(float), test_size=0.2, random_state=42)
        model = LinearRegression().fit(X_train, y_train)
        r2 = r2_score(y_test, model.predict(X_test))
        result = {
            "type": "openml_regression",
            "dataset": dataset,
            "target": target or (getattr(ds.target, "name", "target")),
            "r2_test": float(r2),
            "coef": getattr(model, "coef_", np.array([])).tolist(),
            "intercept": float(getattr(model, "intercept_", 0.0)),
            "n_features": int(X.shape[1]),
            "n_samples": int(X.shape[0]),
        }
        _save_model(task_id, result)
        return result
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y.astype(str), test_size=0.2, random_state=42, stratify=None)
        model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
        acc = accuracy_score(y_test, model.predict(X_test))
        result = {
            "type": "openml_classification",
            "dataset": dataset,
            "target": target or (getattr(ds.target, "name", "target")),
            "accuracy_test": float(acc),
            "coef_shape": list(getattr(model, "coef_", np.zeros((1, X.shape[1]))).shape),
            "n_features": int(X.shape[1]),
            "n_samples": int(X.shape[0]),
        }
        _save_model(task_id, result)
        return result
