from flask import Flask
from middleware import WorkerLogger
app = Flask(__name__)
WorkerLogger(app)
@app.get("/health")
def health():
    return {"status": "worker-ok"}
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
