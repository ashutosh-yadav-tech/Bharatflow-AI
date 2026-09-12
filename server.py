import json
import mimetypes
import os
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from data_generator import HUBS, ROUTES, generate_shipment
from detection import evaluate_shipment
from scoring import compute_priority_score
from agent import run_investigation, MODEL_NAME
from evaluation import run_evaluation
import audit

session_shipments = []
session_diagnoses = {}

if not session_shipments:
    for _ in range(6):
        session_shipments.append(generate_shipment(exception_prob=0.4))


def get_shipment_rows():
    rows = []
    for s in session_shipments:
        rep = evaluate_shipment(s)
        has_diag = s.id in session_diagnoses
        diag = session_diagnoses.get(s.id)
        rows.append({
            "id": s.id,
            "route_name": s.route_name,
            "path": s.path,
            "current_hub": s.current_hub,
            "destination": s.destination,
            "priority": s.priority,
            "declared_value_inr": s.declared_value_inr,
            "dwell_hours_actual": rep["dwell_hours_actual"],
            "dwell_hours_baseline_mean": rep["dwell_hours_baseline_mean"],
            "dwell_hours_baseline_std": rep["dwell_hours_baseline_std"],
            "dwell_zscore": rep["dwell_zscore"],
            "dwell_deviation_pct": rep["dwell_deviation_pct"],
            "worst_transit_hop": rep["worst_transit_hop"],
            "worst_transit_zscore": rep["worst_transit_zscore"],
            "is_flagged": rep["is_flagged"],
            "priority_score": compute_priority_score(rep) if rep["is_flagged"] else 0.0,
            "investigated": has_diag,
            "diagnosis": diag,
        })
    rows.sort(key=lambda r: (r["is_flagged"], r["priority_score"]), reverse=True)
    return rows


class BharatFlowHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            has_key = bool(os.environ.get("GROQ_API_KEY"))
            hubs_payload = {h: {"lat": lat, "lon": lon} for h, (lat, lon) in HUBS.items()}
            return self._send_json({
                "status": "online",
                "has_api_key": has_key,
                "model_name": MODEL_NAME,
                "engine_label": f"Groq LLM ({MODEL_NAME})" if has_key else "Rule-based Fallback",
                "hubs": hubs_payload,
                "routes": ROUTES,
                "shipment_count": len(session_shipments),
            })

        elif path == "/api/shipments":
            return self._send_json({
                "shipments": get_shipment_rows(),
                "total": len(session_shipments),
            })

        elif path == "/api/audit":
            logs = audit.fetch_log(limit=150)
            return self._send_json({"logs": logs})

        web_dir = os.path.join(os.path.dirname(__file__), "web")
        req_path = path.lstrip("/") or "index.html"
        file_path = os.path.abspath(os.path.join(web_dir, req_path))

        if not file_path.startswith(web_dir) or not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(web_dir, "index.html")

        if os.path.exists(file_path) and not os.path.isdir(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"
            if file_path.endswith(".css"):
                content_type = "text/css; charset=utf-8"
            elif file_path.endswith(".js"):
                content_type = "application/javascript; charset=utf-8"
            elif file_path.endswith(".html"):
                content_type = "text/html; charset=utf-8"

            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error reading file: {e}")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/api/shipments/generate":
            count = int(payload.get("count", 5))
            exc_prob = float(payload.get("exception_prob", 0.35))
            count = max(1, min(count, 30))
            new_ships = []
            for _ in range(count):
                s = generate_shipment(exception_prob=exc_prob)
                session_shipments.append(s)
                new_ships.append(s.id)
            return self._send_json({
                "message": f"Generated {count} shipment events.",
                "new_shipment_ids": new_ships,
                "shipments": get_shipment_rows(),
            })

        elif path == "/api/shipments/clear":
            session_shipments.clear()
            session_diagnoses.clear()
            return self._send_json({
                "message": "Session shipments and diagnoses cleared.",
                "shipments": [],
            })

        elif path == "/api/investigate":
            shipment_id = payload.get("shipment_id")
            mode = payload.get("mode", "live")
            if not shipment_id:
                return self._send_json({"error": "Missing shipment_id"}, status=400)

            target = next((s for s in session_shipments if s.id == shipment_id), None)
            if not target:
                return self._send_json({"error": f"Shipment {shipment_id} not found"}, status=404)

            report = evaluate_shipment(target)
            diagnosis = run_investigation(target, report, mode=mode)
            session_diagnoses[target.id] = diagnosis
            audit.log_investigation(target, report, diagnosis)

            return self._send_json({
                "shipment_id": target.id,
                "report": report,
                "diagnosis": diagnosis,
            })

        elif path == "/api/evaluate":
            try:
                n_eval = int(payload.get("count", 5))
                n_eval = max(3, min(n_eval, 10))
                results = run_evaluation(n_shipments=n_eval)
                return self._send_json(results)
            except Exception as e:
                print(f"[Evaluation Error] {e}")
                return self._send_json({"error": f"Evaluation pipeline error: {str(e)}"}, status=500)

        elif path == "/api/audit/clear":
            audit.clear_log()
            return self._send_json({"message": "Audit log cleared."})

        else:
            self.send_error(404, "Unknown API endpoint")


def run_server(port=8000):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, BharatFlowHandler)
    print(f"[BharatFlow Server] Serving at http://localhost:{port} (PID {os.getpid()})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
