from http.server import (
    ThreadingHTTPServer,
    SimpleHTTPRequestHandler,
)
from pathlib import Path
from urllib.parse import urlparse
import json
import os


from db import (
    get_evaluation,
    init_db,
    list_evaluations,
    release_evaluation,
)
from engine import KB, evaluate


ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=str(PUBLIC),
            **kwargs,
        )

    def _json(self, status, obj):
        body = json.dumps(
            obj,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.send_header(
            "Cache-Control",
            "no-store",
        )
        self.end_headers()
        self.wfile.write(body)

    def _html(self, status, body):
        encoded = body.encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(encoded)),
        )
        self.send_header(
            "Cache-Control",
            "no-store",
        )
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            return self._json(
                200,
                {
                    "ok": True,
                    "service": "urie's-edge",
                },
            )

        if path == "/api/config":
            return self._json(200, KB)

        if path == "/api/mentor/reports":
            return self._json(
                200,
                list_evaluations(),
            )

        if path.startswith("/api/mentor/reports/"):
            evaluation_id = path.rsplit(
                "/",
                1,
            )[-1]

            if not evaluation_id:
                return self._json(
                    404,
                    {"error": "Report not found"},
                )

            report = get_evaluation(
                evaluation_id
            )

            if not report:
                return self._json(
                    404,
                    {"error": "Report not found"},
                )

            return self._json(200, report)

        if path == "/mentor/reports":
            self.path = "/mentor/reports.html"
            return super().do_GET()

        if path == "/mentor/report":
            self.path = "/mentor/report.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/evaluate":
            try:
                content_length = self.headers.get(
                    "Content-Length"
                )

                if not content_length:
                    return self._json(
                        400,
                        {
                            "error": (
                                "Request body is required"
                            )
                        },
                    )

                try:
                    length = int(
                        content_length
                    )
                except ValueError:
                    return self._json(
                        400,
                        {
                            "error": (
                                "Invalid Content-Length"
                            )
                        },
                    )

                if length <= 0:
                    return self._json(
                        400,
                        {
                            "error": (
                                "Request body is required"
                            )
                        },
                    )

                if length > 700000:
                    return self._json(
                        413,
                        {
                            "error": (
                                "Request too large"
                            )
                        },
                    )

                raw_body = self.rfile.read(length)

                try:
                    payload = json.loads(
                        raw_body
                    )
                except json.JSONDecodeError:
                    return self._json(
                        400,
                        {
                            "error": (
                                "Request body must be valid JSON"
                            )
                        },
                    )

                if not isinstance(payload, dict):
                    return self._json(
                        400,
                        {
                            "error": (
                                "Request body must be a JSON object"
                            )
                        },
                    )

                return self._json(
                    200,
                    evaluate(payload),
                )

            except ValueError as error:
                return self._json(
                    400,
                    {"error": str(error)},
                )

            except RuntimeError as error:
                return self._json(
                    502,
                    {"error": str(error)},
                )

            except Exception as error:
                self.log_error(
                    "Evaluation failure: %s",
                    error,
                )

                return self._json(
                    500,
                    {
                        "error": (
                            "Internal server error"
                        )
                    },
                )

        if (
            path.startswith(
                "/api/mentor/reports/"
            )
            and path.endswith("/release")
        ):
            evaluation_id = path.split("/")[-2]

            if not evaluation_id:
                return self._json(
                    404,
                    {"error": "Report not found"},
                )

            if not release_evaluation(
                evaluation_id
            ):
                return self._json(
                    404,
                    {"error": "Report not found"},
                )

            return self._json(
                200,
                {
                    "ok": True,
                    "status": "released",
                },
            )

        return self._json(
            404,
            {"error": "Not found"},
        )


if __name__ == "__main__":
    init_db()

    port = int(
        os.getenv("PORT", "8000")
    )

    print(
        f"URIE v2 listening on 0.0.0.0:{port}",
        flush=True,
    )

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        Handler,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()










# from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
# from pathlib import Path
# import json, os
# from engine import evaluate, KB
# ROOT=Path(__file__).parent
# class Handler(SimpleHTTPRequestHandler):
#  def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT/'public'),**kw)
#  def _json(self,status,obj):
#   body=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
#  def do_GET(self):
#   if self.path=='/api/config': return self._json(200,KB)
#   return super().do_GET()
#  def do_POST(self):
#   if self.path!='/api/evaluate': return self._json(404,{'error':'not found'})
#   try:
#    n=int(self.headers.get('Content-Length','0')); payload=json.loads(self.rfile.read(n)); return self._json(200,evaluate(payload))
#   except Exception as e: return self._json(400,{'error':str(e)})
# if __name__=='__main__':
#  port=int(os.getenv('PORT','8000')); print(f'URIE v2 http://localhost:{port}'); ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
