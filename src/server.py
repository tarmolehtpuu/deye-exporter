# deye-exporter - Prometheus Exporter for Deye inverters
# Copyright 2026 Tarmo Lehtpuu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from prometheus import PrometheusRegistry

logger = logging.getLogger("DeyePluginPrometheus")


def _handle_healthz(_: PrometheusRegistry) -> tuple[int, str, str]:
    return 200, "text/plain", "Healthy!"


def _handle_metrics(prometheus: PrometheusRegistry) -> tuple[int, str, str]:
    metrics = prometheus.metrics()
    payload = str(metrics) if metrics else ""
    return 200, "text/plain; version=0.0.4; charset=utf-8", payload


def _handle_readyz(prometheus: PrometheusRegistry) -> tuple[int, str, str]:
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
    def __init__(self, address: str, port: int, prometheus: PrometheusRegistry):
        self.address = address
        self.port = port
        self.prometheus = prometheus
        self._http: HTTPServer | None = None
        self._thread: threading.Thread | None = None

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

        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()

        self._http = http
        self._thread = thread

        logger.info("HTTP Server started %s:%d", self.address, self.port)

    def stop(self):
        if not self._http:
            logger.warning("HTTP Server is not running")
            return

        logger.info("Stopping HTTP Server")

        self._http.shutdown()
        self._http.server_close()

        if self._thread:
            self._thread.join(timeout=5)

        self._http = None
        self._thread = None
