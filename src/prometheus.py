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


from __future__ import annotations

import logging
import re
import threading
from typing import List, Union, Any, Dict, Optional

from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent
from metrics import METRICS, MetricWithSamples, Metric, Label, Sample

logger = logging.getLogger("DeyePluginPrometheus")


class PrometheusExporter:
    def __init__(self, metrics: List[MetricWithSamples]):
        self._metrics: List[MetricWithSamples] = list(metrics)

    def export(self) -> str:
        lines: List[str] = []
        headers = set()

        for item in self._metrics:
            metric: Metric = item.metric

            if metric.name not in headers:
                lines.append(f"# HELP {metric.name} {metric.desc}")
                lines.append(f"# TYPE {metric.name} {metric.type}")
                headers.add(metric.name)

            for sample in item.samples:
                labels = []

                for label in sample.labels:
                    labels.append(f'{label.name}="{label.value}"')
                for label in sample.vars:
                    labels.append(f'{label.name}="{label.value}"')

                if labels:
                    lines.append(
                        f"{metric.name}{{{', '.join(labels)}}} {sample.formatted_value()}"
                    )
                else:
                    lines.append(f"{metric.name} {sample.formatted_value()}")

        if not lines:
            return str("")

        return "\n".join(lines)


class PrometheusRegistry(DeyeEventProcessor):
    RE_NAME = re.compile(r"([a-z]+)(\d+)")
    RE_NORMALIZE_1 = re.compile(r"\bl(\d+)\b")
    RE_NORMALIZE_2 = re.compile(r"/temp\b")
    RE_NORMALIZE_3 = re.compile(r"(bms|battery|pv)/(\d+)/")

    def __init__(self, labels=None):
        if labels is None:
            labels = []

        self._lock = threading.Lock()
        self._data: Dict[Metric, Dict[frozenset[Label], Union[float, int]]] = {}
        self._labels = labels

        logger.info("Prometheus listener started")

    def get_id(self):
        return "prometheus"

    def process(self, events: DeyeEventList):
        logger.debug("Processing logger index: %s", events.logger_index)

        items: list = events
        for event in items:
            if not isinstance(event, DeyeObservationEvent):
                continue

            key = event.observation.sensor.mqtt_topic_suffix
            val = event.observation.value

            # TODO: does this belong here?
            if key == "inverter/status" and isinstance(val, str):
                val = 1.0 if val.lower() == "normal" else 0.0

            mapping = self._resolve(key)
            if not mapping:
                logger.warning("Unmapped topic: %s", key)
                continue

            metric, labels = mapping
            logger.debug("Mapping: %s -> %s", key, metric.name)

            with self._lock:
                if metric not in self._data:
                    self._data[metric] = {}

                value = self._normalize_value(val)
                if value is None:
                    logger.warning(
                        "Skipping: %s {labels=%s, value=None", metric.name, set(labels)
                    )
                else:
                    logger.debug(
                        "Updated: %s {labels=%s, value=%s}",
                        metric.name,
                        set(labels),
                        str(value),
                    )
                    self._data[metric][labels] = value

        logger.debug("Processing complete for logger index: %s", events.logger_index)

    def metrics(self) -> Optional[str]:
        metrics: List[MetricWithSamples] = []

        with self._lock:
            for metric, items in self._data.items():
                samples = []
                for labels, value in items.items():
                    samples.append(
                        Sample(labels=self._labels + list(labels), value=value)
                    )

                metrics.append(MetricWithSamples(metric, samples))

        if not metrics:
            logger.warning(
                "No metrics to export. Inverter data may not have arrived yet."
            )
            return None

        return PrometheusExporter(metrics).export()

    def is_ready(self) -> bool:
        with self._lock:
            return len(self._data) > 0

    @classmethod
    def _resolve(cls, name: str) -> Optional[tuple[Metric, frozenset[Label]]]:
        name = cls._normalize_name(name)
        labels = []

        def _extract(m):
            labels.append(Label(m.group(1), m.group(2)))
            return m.group(1)

        key = cls.RE_NAME.sub(_extract, name)
        if key in METRICS:
            return METRICS[key], frozenset(labels)

        return None

    @classmethod
    def _normalize_name(cls, name: str) -> str:
        name = cls.RE_NORMALIZE_1.sub(r"line\1", name)
        name = cls.RE_NORMALIZE_2.sub("/temperature", name)
        name = cls.RE_NORMALIZE_3.sub(r"\1\2/", name)
        name = name.strip("/")
        return name

    @classmethod
    def _normalize_value(cls, value: Any) -> Optional[float | int]:
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            value = value.lower()
            if value in ("normal", "ok", "on", "connected", "true"):
                return 1.0
            if value in ("off", "disconnected", "error", "fault", "false"):
                return 0.0
            try:
                return float(value)
            except ValueError:
                return None

        return None
