import time, uuid
from flask import request, g
EXCLUDED_PATHS = {"/health"}
class RequestLogger:
    def __init__(self, app):
        self.app = app
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.register_error_handler(Exception, self.handle_error)
    def before_request(self):
        g.start_time = time.time()
        g.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        if request.path not in EXCLUDED_PATHS:
            self.app.logger.info(f"GW - {request.method} {request.path} cid={g.correlation_id}")
    def after_request(self, response):
        dur = int((time.time() - getattr(g, "start_time", time.time()))*1000)
        response.headers["X-Correlation-ID"] = getattr(g, "correlation_id", "-")
        response.headers["X-Response-Time-ms"] = str(dur)
        if request.path not in EXCLUDED_PATHS:
            self.app.logger.info(f"GW - {request.method} {request.path} {response.status_code} in {dur}ms cid={getattr(g,'correlation_id','-')}")
        return response
    def handle_error(self, err):
        self.app.logger.exception(f"GW Unhandled: {err}")
        from flask import jsonify
        return jsonify({"error": str(err), "where": "gateway"}), 500
