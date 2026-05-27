# deye-exporter ![Static Badge](https://img.shields.io/badge/version-0.0.12-blue) ![Endpoint Badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Ftarmolehtpuu%2F2964adb9760e49d54940d571d30b55fe%2Fraw%2Fc59e29b7b499607e27f586380aadb2c12083c9aa%2Fdeye-exporter-cobertura-coverage.json)

Prometheus Exporter for Deye inverters implemented as a plugin
for [deye-inverter-mqtt](https://github.com/kbialek/deye-inverter-mqtt).

## Environment

deye-exporter adds the following env variables to deye-inverter-mqtt:

| NAME                                | REQUIRED | COMMENT                           |
|-------------------------------------|----------|-----------------------------------|
| **PLUGIN_PROMETHEUS_INVERTER_NAME** | Y        | Label inverter="inverter01"       |
| **PLUGIN_PROMETHEUS_LISTEN_ADDR**   | Y        | Listen addr for /metrics endpoint |
| **PLUGIN_PROMETHEUS_LISTEN_PORT**   | Y        | Listen port for /metrics endpoint |

For a complete list of env variables
see [deye-inverter-mqtt/config.env.example](https://github.com/kbialek/deye-inverter-mqtt/blob/main/config.env.example).

## Running

### 1. deye-inverter-mqtt plugin

If adding to an existing deye-inverter-mqtt installation, then it's possible to just download the plugin from the
releases page and make sure it gets copied or mounted into /plugins directory.

**Example:**

```bash
docker run \
  -p 9010:9010 \
  -v ./plugins:/opt/deye_inverter_mqtt/plugins:ro \
  -e DEYE_LOGGER_IP_ADDRESS=10.10.10.1 \
  -e DEYE_LOGGER_PORT=8899 \
  -e DEYE_LOGGER_PROTOCOL=tcp \
  -e DEYE_LOGGER_SERIAL_NUMBER=1234567890 \
  -e DEYE_DATA_READ_INTERVAL=60 \
  -e DEYE_PUBLISH_ON_CHANGE=false \
  -e DEYE_METRIC_GROUPS=deye_sg01hp3,deye_sg01hp3_battery,deye_sg01hp3_bms,deye_sg01hp3_ups,deye_sg01hp3_generator,deye_sg01hp3_systemtime,deye_sg01hp3_settings,settings \
  -e MQTT_HOST=127.0.0.1 \
  -e DEYE_FEATURE_MQTT_PUBLISHER=false \
  -e PLUGINS_DIR=plugins \
  -e PLUGINS_ENABLED=deye_plugin_prometheus \
  -e PLUGIN_PROMETHEUS_INVERTER_NAME=inverter01 \
  -e PLUGIN_PROMETHEUS_LISTEN_ADDR=0.0.0.0 \
  -e PLUGIN_PROMETHEUS_LISTEN_PORT=9010 \
  ghcr.io/kbialek/deye-inverter-mqtt

```

### 2. deye-exporter Docker

For convenience there is also a Docker image with the plugin already preconfigured published for the following os/arch
combinations:

- **linux/amd64**
- **linux/arm64**

**Example:**

```bash
docker run \
  -p 9010:9010 \
  -e DEYE_LOGGER_IP_ADDRESS=10.10.10.1 \
  -e DEYE_LOGGER_PORT=8899 \
  -e DEYE_LOGGER_SERIAL_NUMBER=1234567890 \
  -e DEYE_METRIC_GROUPS=deye_sg01hp3,deye_sg01hp3_battery,deye_sg01hp3_bms,deye_sg01hp3_ups,deye_sg01hp3_generator,deye_sg01hp3_systemtime,deye_sg01hp3_settings,settings \
  -e PLUGIN_PROMETHEUS_INVERTER_NAME=inverter01 \
  -e PLUGIN_PROMETHEUS_LISTEN_ADDR=0.0.0.0 \
  -e PLUGIN_PROMETHEUS_LISTEN_PORT=9010 \
  ghcr.io/tarmolehtpuu/deye-exporter:0.0.12
```

## Prometheus

Add a static config for all the inverters. If running all of them on localhost then run them on separate ports so
configuring Prometheus is less of a hassle.

```yaml
- job_name: deye-exporter
  static_configs:
    - targets:
        - localhost:9010
        - localhost:9011
        - localhost:9012
        - ...
```

