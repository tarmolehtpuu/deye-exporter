from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union, Any, Dict, Optional, Tuple

from metrics import METRICS
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent

logger = logging.getLogger("DeyePluginPrometheus")


@dataclass(frozen=True)
class Label:
    name: str
    value: Any

    def __post_init__(self):
        if not isinstance(self.value, str):
            object.__setattr__(self, "value", self.value)


@dataclass(frozen=True)
class Sample:
    labels: List[Label] = field(default_factory=list)
    vars: List[Label] = field(default_factory=list)
    value: Union[float, int, bool] = 0.0

    def __post_init__(self):
        if isinstance(self.value, bool):
            object.__setattr__(self, "value", 1.0 if self.value else 0.0)
        elif isinstance(self.value, (int, float)):
            object.__setattr__(self, "value", float(self.value))

    def formatted_value(self) -> str:
        if not isinstance(self.value, float):
            return str(self.value)

        return f"{self.value:.2f}".rstrip("0").rstrip(".")


class Type(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Metric:
    name: str
    type: Type
    desc: str

    @classmethod
    def builder(cls) -> MetricBuilder:
        return MetricBuilder()


class MetricBuilder:
    def __init__(self):
        self._name = ""
        self._type = Type.GAUGE
        self._desc = ""

    def name(self, name: str) -> MetricBuilder:
        self._name = name
        return self

    def counter(self) -> MetricBuilder:
        self._type = Type.COUNTER
        return self

    def gauge(self) -> MetricBuilder:
        self._type = Type.GAUGE
        return self

    def desc(self, desc: str) -> MetricBuilder:
        self._desc = desc
        return self

    def build(self) -> Metric:
        return Metric(self._name, self._type, self._desc)


@dataclass(frozen=True)
class MetricWithSamples:
    metric: Metric
    samples: List[Sample]

    def __init__(self, metric: Metric, samples: Union[Sample, List[Sample]]):
        object.__setattr__(self, "metric", metric)
        if isinstance(samples, Sample):
            object.__setattr__(self, "samples", [samples])
        else:
            object.__setattr__(self, "samples", list(samples))


class Exporter:
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
                    lines.append(f'{metric.name}{{{", ".join(labels)}}} {sample.formatted_value()}')
                else:
                    lines.append(f"{metric.name} {sample.formatted_value()}")

        if not lines:
            return str("")

        return "\n".join(lines)


class Registry(DeyeEventProcessor):
    RE_NAME = re.compile(r"([a-z]+)(\d+)")
    RE_NORMALIZE_1 = re.compile(r"\bl(\d+)\b")
    RE_NORMALIZE_2 = re.compile(r"/temp\b")
    RE_NORMALIZE_3 = re.compile(r"(bms|battery|pv)/(\d+)/")

    def __init__(self, labels: List[Label] = []):
        self._lock = threading.Lock()
        self._data: Dict[Metric, Dict[frozenset[Label], Union[float, int]]] = {}
        self._labels = labels

        logger.info("Prometheus listener started")

    def get_id(self):
        return "prometheus_listener"

    def process(self, events: DeyeEventList):
        logger.debug("Processing logger index: %s", events.logger_index)

        for event in events:
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

            # TODO: inject common labels maybe here?
            metric, labels = mapping
            logger.debug("Mapping: %s -> %s", key, metric.name)

            with self._lock:
                if metric not in self._data:
                    self._data[metric] = {}

                value = self._normalize_value(val)
                if not value:
                    logger.warning("Skipping: %s {labels=%s, value=None", metric.name, set(labels))
                else:
                    logger.debug("Updated: %s {labels=%s, value=%s}", metric.name, set(labels), str(value))
                    self._data[metric][labels] = value

        logger.debug("Processing complete for logger index: %s", events.logger_index)

    def metrics(self) -> Optional[str]:
        metrics: List[MetricWithSamples] = []

        with self._lock:
            for metric, labels in self._data.items():
                samples = []
                for l, v in labels.items():
                    samples.append(Sample(labels=self._labels + list(l), value=v))

                metrics.append(MetricWithSamples(metric, samples))

        if not metrics:
            logger.warning("No metrics to export. Inverter data may not have arrived yet.")
            return None

        return Exporter(metrics).export()

    def is_ready(self) -> bool:
        with self._lock:
            return len(self._data) > 0

    @classmethod
    def _resolve(cls, name: str) -> Optional[tuple[Metric, frozenset[Label]]]:
        name, _ = cls._normalize(name)
        labels = []

        def _extract(m):
            labels.append(Label(m.group(1), m.group(2)))
            return m.group(1)

        key = cls.RE_NAME.sub(_extract, name)
        if key in METRICS:
            return METRICS[key], frozenset(labels)

        return None

    @classmethod
    def _normalize(cls, name: str, value: Any) -> Tuple[str, Optional[float | int]]:
        # TODO split again
        name = cls.RE_NORMALIZE_1.sub(r"line\1", name)
        name = cls.RE_NORMALIZE_2.sub("/temperature", name)
        name = cls.RE_NORMALIZE_3.sub(r"\1\2/", name)
        name = name.strip("/")

        if isinstance(value, (int, float)):
            value = float(value)

        if isinstance(value, str):
            value = value.lower()
            if value in ("normal", "ok", "on", "connected", "true"):
                value = 1.0
            if value in ("off", "disconnected", "error", "fault", "false"):
                value = 0.0
            try:
                value = float(value)
            except ValueError:
                value = None

        return name, value
