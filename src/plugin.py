import logging
from typing import List

from deye_config import DeyeEnv
from deye_events import DeyeEventProcessor
from metrics import Label
from prometheus import PrometheusRegistry
from server import Server

logger = logging.getLogger("DeyePluginPrometheus")


class DeyePlugin:
    def __init__(self, _):
        logger.info("Prometheus plugin starting")

        # TODO: refuse to start in multi inverter setup
        self.name = DeyeEnv.string("PLUGIN_PROMETHEUS_INVERTER_NAME")
        self.addr = DeyeEnv.string("PLUGIN_PROMETHEUS_LISTEN_ADDR", "0.0.0.0")
        self.port = DeyeEnv.integer("PLUGIN_PROMETHEUS_LISTEN_PORT", 9010)
        self.logger_ip = DeyeEnv.string("DEYE_LOGGER_IP_ADDRESS")
        self.logger_port = DeyeEnv.integer("DEYE_LOGGER_PORT", 8899)

        self.prometheus = PrometheusRegistry(
            [
                Label("logger_ip", self.logger_ip),
                Label("logger_port", self.logger_port),
                Label("inverter", self.name),
            ]
        )
        self.server = Server(self.addr, self.port, self.prometheus)
        self.server.start()

        logger.info("Prometheus plugin started")

    def get_event_processors(self) -> List[DeyeEventProcessor]:
        return [self.prometheus]

    def stop(self):
        self.server.stop()

    @classmethod
    def labels(cls) -> List[Label]:
        label1 = Label("logger_ip", DeyeEnv.string("DEYE_LOGGER_IP_ADDRESS"))
        label2 = Label("logger_port", DeyeEnv.integer("DEYE_LOGGER_PORT", 8899))
        label3 = Label("inverter", "inverter01")
        return [label1, label2, label3]
