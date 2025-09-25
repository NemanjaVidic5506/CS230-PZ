from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from celery import Celery
import os
from sklearn.datasets import fetch_openml
import pandas as pd

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, GATEWAY_HOST, GATEWAY_PORT, MODELS_DIR
from middleware import RequestLogger
from models import upsert_job, set_job_result, list_jobs

app = Flask(__name__)
CORS(app)
RequestLogger(app)

celery = Celery(app.name, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.conf.update(task_routes={
    "tasks.train_synthetic": {"queue": "ml"},
    "tasks.train_openml": {"queue": "ml"}
})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs")
def create_job():
    payload = request.get_json(force=True, silent=True) or {}
    job_type = payload.get("job_type", "synthetic")
    if job_type == "openml":
        params = {
            "dataset": payload.get("dataset", "diabetes"),
            "target": payload.get("target", None),
        }
        task = celery.send_task("tasks.train_openml", kwargs=params, queue="ml")
    else:
        params = {
            "n_samples": int(payload.get("n_samples", 1000)),
            "n_features": int(payload.get("n_features", 20)),
            "noise": float(payload.get("noise", 0.1)),
            "random_state": int(payload.get("random_state", 42)),
        }
        task = celery.send_task("tasks.train_synthetic", kwargs=params, queue="ml")

    upsert_job(task.id, job_type, params, "PENDING")
    return jsonify({"task_id": task.id, "status": "queued"}), 202

@app.get("/jobs/<task_id>")
def get_job(task_id):
    res = celery.AsyncResult(task_id)
    state = res.state
    resp = {"task_id": task_id, "state": state}
    if res.successful():
        result = res.get()
        resp["result"] = result
        set_job_result(task_id, "SUCCESS", result)
    elif res.failed():
        resp["error"] = str(res.result)
        set_job_result(task_id, "FAILURE", {"error": str(res.result)})
    return jsonify(resp)

@app.get("/jobs")
def jobs_list():
    return jsonify(list_jobs())

@app.post("/jobs/<task_id>/cancel")
def cancel_job(task_id):
    try:
        celery.control.revoke(task_id, terminate=True)
        return {"task_id": task_id, "status": "revoked"}
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}, 400

@app.get("/models/<task_id>")
def download_model(task_id):
    path = os.path.join(MODELS_DIR, f"{task_id}.json")
    if not os.path.exists(path):
        return {"error": "model not found", "path": path}, 404
    return send_file(path, as_attachment=True, download_name=f"{task_id}.json", mimetype="application/json")

@app.get("/external/preview")
def external_preview():
    name = request.args.get("name", "diabetes")
    n = int(request.args.get("n", 5))
    ds = fetch_openml(name=name, as_frame=True)
    df = pd.concat([ds.data, ds.target.rename("target")], axis=1)
    preview = df.head(n).to_dict(orient="records")
    cols = list(df.columns)
    return jsonify({"dataset": name, "columns": cols, "preview": preview})

if __name__ == "__main__":
    app.run(host=GATEWAY_HOST, port=GATEWAY_PORT)
