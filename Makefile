OUTPUT_DIR := build/plugins
OUTPUT_FILE := $(OUTPUT_DIR)/deye_plugin_prometheus.py
SRC_FILES := src/metrics.py src/prometheus.py src/server.py src/plugin.py

define HEADER_TEMPLATE
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
from dataclasses import dataclass,field
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Union, Any, Dict, Optional, Tuple

from deye_config import DeyeEnv
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent

logger = logging.getLogger("DeyePluginPrometheus")
endef
export HEADER_TEMPLATE

.PHONY: all build clean lint format test

build: $(OUTPUT_FILE)

$(OUTPUT_FILE): $(SRC_FILES)
	@mkdir -p $(OUTPUT_DIR)
	@echo "$$HEADER_TEMPLATE" > $(OUTPUT_FILE)
	@$(foreach file,$(SRC_FILES),grep -vE "import|getLogger|^#" $(file) >> $(OUTPUT_FILE); )
	@uvx ruff format $(OUTPUT_FILE)

clean:
	rm -rf $(OUTPUT_DIR)

lint:
	uvx ruff check src/

format:
	uvx ruff format src/
	uvx ruff format tests/

test:
	PYTHONPATH=src:deye-inverter-mqtt/src uv run coverage run -m unittest discover -s tests/ -v
	uv run coverage xml
	uv run coverage html

