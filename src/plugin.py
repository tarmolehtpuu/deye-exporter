import logging
from typing import List

from deye_config import DeyeEnv
from deye_events import DeyeEventProcessor
from server import Server
from prometheus import Registry

logger = logging.getLogger("DeyePluginPrometheus")


class DeyePlugin:
    def __init__(self, _):
        logger.info("Prometheus plugin starting")

        self.addr = DeyeEnv.string("PLUGIN_PROMETHEUS_LISTEN_ADDR", "0.0.0.0")
        self.port = DeyeEnv.integer("PLUGIN_PROMETHEUS_LISTEN_PORT", 9010)

        self.prometheus = Registry()

        self.server = Server(self.addr, self.port, self.prometheus)
        self.server.start()

        logger.info("Prometheus plugin started")

    def get_event_processors(self) -> List[DeyeEventProcessor]:
        return [self.prometheus]
