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


from deye_sensor import Sensor


class TestSensor(Sensor):
    def __init__(self, topic: str):
        self.topic = topic

    @property
    def reg_address(self) -> int:
        return 0

    @property
    def name(self) -> str:
        return "test_sensor"

    @property
    def mqtt_topic_suffix(self) -> str:
        return self.topic

    @property
    def unit(self) -> str:
        return ""

    @property
    def print_format(self) -> str:
        return ""

    @property
    def groups(self) -> list[str]:
        return []

    @property
    def data_type(self) -> str:
        return ""

    @property
    def scale_factor(self) -> float:
        return 1.0

    @property
    def is_readiness_check(self) -> bool:
        return False

    def read_value(self, registers: dict[int, bytearray]):
        return {}

    def write_value(self, value: str) -> dict[int, bytearray]:
        return {}

    def format_value(self, value):
        return value

    def in_any_group(self, active_groups: set[str]) -> bool:
        return False

    def get_registers(self) -> list[int]:
        return []
