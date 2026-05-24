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
