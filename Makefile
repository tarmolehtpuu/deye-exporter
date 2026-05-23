OUTPUT_DIR := build/plugins
OUTPUT_FILE := $(OUTPUT_DIR)/deye_plugin_prometheus.py
SRC_FILES := src/prometheus.py src/metrics.py src/server.py src/plugin.py

define HEADER_TEMPLATE
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

.PHONY: all build clean

build: $(OUTPUT_FILE)

$(OUTPUT_FILE): $(SRC_FILES)
	@mkdir -p $(OUTPUT_DIR)
	@echo "Source filed changed. Rebuilding..."
	@echo "$$HEADER_TEMPLATE" > $(OUTPUT_FILE)
	@$(foreach file,$(SRC_FILES),grep -vE "import|getLogger" $(file) >> $(OUTPUT_FILE); )
	@uvx ruff format $(OUTPUT_FILE)

clean:
	rm -rf $(OUTPUT_DIR)