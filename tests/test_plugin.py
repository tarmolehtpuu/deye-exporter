import json
import os
import time
import unittest
import urllib
import urllib.error
import urllib.request
from pathlib import Path

from deye_config import DeyeConfig
from deye_events import DeyeObservationEvent, DeyeEventList
from deye_mqtt import DeyeMqttClient
from deye_observation import Observation
from deye_plugin_loader import DeyePluginContext
from plugin import DeyePlugin
from test_sensor import TestSensor


class TestPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DEYE_LOGGER_IP_ADDRESS"] = "127.0.0.1"
        os.environ["DEYE_LOGGER_IP_PORT"] = "8899"
        os.environ["DEYE_LOGGER_SERIAL_NUMBER"] = "1234"
        os.environ["PLUGIN_PROMETHEUS_INVERTER_NAME"] = "inverter01"
        os.environ["PLUGIN_PROMETHEUS_LISTEN_ADDRESS"] = "127.0.0.1"
        os.environ["PLUGIN_PROMETHEUS_LISTEN_PORT"] = "9090"
        os.environ["MQTT_HOST"] = "127.0.0.1"
        os.environ["DEYE_FEATURE_MQTT_PUBLISHER"] = "false"

    @classmethod
    def tearDownClass(cls):
        del os.environ["DEYE_LOGGER_IP_ADDRESS"]
        del os.environ["DEYE_LOGGER_IP_PORT"]
        del os.environ["DEYE_LOGGER_SERIAL_NUMBER"]
        del os.environ["PLUGIN_PROMETHEUS_INVERTER_NAME"]
        del os.environ["PLUGIN_PROMETHEUS_LISTEN_ADDRESS"]
        del os.environ["PLUGIN_PROMETHEUS_LISTEN_PORT"]
        del os.environ["MQTT_HOST"]
        del os.environ["DEYE_FEATURE_MQTT_PUBLISHER"]

    def setUp(self):
        conf = DeyeConfig.from_env()
        mqtt = DeyeMqttClient(conf)

        self.plugin = DeyePlugin(DeyePluginContext(conf, mqtt))
        self.prometheus = self.plugin.get_event_processors()[0]

    def tearDown(self):
        if self.plugin:
            self.plugin.stop()

    def test_healthz(self):
        with urllib.request.urlopen("http://127.0.0.1:9090/healthz") as response:
            self.assertEqual(200, response.status)
            self.assertEqual(
                "text/plain", response.headers.get("Content-Type"), "text/plain"
            )
            self.assertEqual("Healthy!", response.read().decode("utf-8"))

    def test_readyz_not_ready(self):
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen("http://127.0.0.1:9090/readyz")
        self.assertEqual(503, context.exception.code)
        self.assertEqual(
            "NOT READY (Waiting for inverter)", context.exception.read().decode("utf-8")
        )
        self.assertFalse(self.prometheus.is_ready())

    def test_readyz(self):
        events = DeyeEventList(
            [
                DeyeObservationEvent(
                    Observation(TestSensor("inverter/status"), time.time(), "normal")
                )
            ]
        )

        self.assertFalse(self.prometheus.is_ready())
        self.prometheus.process(events)
        self.assertTrue(self.prometheus.is_ready())

        with urllib.request.urlopen("http://127.0.0.1:9090/readyz") as response:
            self.assertEqual(200, response.status)
            self.assertEqual("text/plain", response.headers.get("Content-Type"))
            self.assertEqual("Ready!", response.read().decode("utf-8"))

    def test_metrics_not_ready(self):
        self.assertFalse(self.prometheus.is_ready())
        with urllib.request.urlopen("http://127.0.0.1:9090/metrics") as response:
            self.assertEqual(200, response.status)
            self.assertEqual(
                "text/plain; version=0.0.4; charset=utf-8",
                response.headers.get("Content-Type"),
            )
            self.assertEqual(
                "",
                response.read().decode("utf-8"),
            )

    def test_metrics(self):
        tstamp = time.time()
        events = []

        with open(Path(__file__).parent / "test_input.json") as f:
            items = json.loads(f.read())
            for item in items:
                events.append(
                    DeyeObservationEvent(
                        Observation(
                            TestSensor(f"{item['name']}"), tstamp, item["value"]
                        )
                    )
                )

        self.assertFalse(self.prometheus.is_ready())
        self.prometheus.process(DeyeEventList(events))
        self.assertTrue(self.prometheus.is_ready())

        with open(Path(__file__).parent / "test_output.txt") as f:
            lines1 = f.read().splitlines()

        with urllib.request.urlopen("http://127.0.0.1:9090/metrics") as response:
            self.assertEqual(200, response.status)
            self.assertEqual(
                "text/plain; version=0.0.4; charset=utf-8",
                response.headers.get("Content-Type"),
            )
            lines2 = response.read().decode("utf-8").splitlines()

        self.assertEqual(len(lines1), len(lines2))

        for index, line1 in enumerate(lines1):
            self.assertEqual(line1, lines2[index])

    def test_not_found(self):
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen("http://127.0.0.1:9090/")

        body = context.exception.read().decode("utf-8")

        self.assertEqual(404, context.exception.code)
        self.assertIn("Error code: 404", body)
        self.assertIn("Message: Not Found", body)

    if __name__ == "__main__":
        unittest.main()
