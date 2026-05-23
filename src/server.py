import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from prometheus import Registry

logger = logging.getLogger("DeyePluginPrometheus")


def _handle_healthz(_: Registry) -> tuple[int, str, str]:
    return 200, "text/plain", "Healthy!"


def _handle_metrics(prometheus: Registry) -> tuple[int, str, str]:
    metrics = prometheus.metrics()
    payload = str(metrics) if metrics else ""
    return 200, "text/plain; version=0.0.4; charset=utf-8", payload


def _handle_readyz(prometheus: Registry) -> tuple[int, str, str]:
    if prometheus.is_ready():
        return 200, "text/plain", "Ready!"
    return 503, "text/plain", "NOT READY (Waiting for inverter)"


_ROUTES = {
    "/healthz": _handle_healthz,
    "/metrics": _handle_metrics,
    "/readyz": _handle_readyz,
}


# noinspection PyTypeChecker
class Server:
    def __init__(self, address: str, port: int, prometheus: Registry):
        self.address = address
        self.port = port
        self.prometheus = prometheus

    def start(self):
        prometheus = self.prometheus

        # noinspection PyPep8Naming,PyShadowingBuiltins
        class HTTPRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path in _ROUTES:
                    status, content_type, body = _ROUTES[self.path](prometheus)
                    self.send_response(status)
                    self.send_header("Content-type", content_type)
                    self.end_headers()
                    self.wfile.write(body.encode("utf-8"))
                else:
                    self.send_error(404, "Not Found")
                    self.end_headers()

            def log_message(self, format, *args):
                logger.debug(format, *args)

        http = HTTPServer((self.address, self.port), HTTPRequestHandler)

        thread = threading.Thread(target=http.serve_forever)
        thread.start()

        logger.info("HTTP Server started %s:%d", self.address, self.port)
