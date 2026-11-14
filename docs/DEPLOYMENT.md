# Deployment — SmartLine 360

How to bring the full 9-layer stack up in the right order and verify each
layer before moving to the next.

## Startup Order

Later layers depend on earlier ones being live — start in this sequence:

1. **Windows Virtual Network Check** — confirm `Siemens PLCSIM Virtual Ethernet Adapter` has static IPv4 `192.168.0.50` (`255.255.255.0`).
2. **S7-PLCSIM Advanced & TIA Portal** — start the S7-1500 simulation (`192.168.0.1`), download the program from `plc-programs/`, and put the CPU in `RUN`.
3. **Factory I/O** — open the scene in `factory-io-scenes/`, connect the **Siemens S7-1200/1500** driver (confirm green icon), and switch to **Run Mode** (`F5`).
4. **Ignition Gateway** — start the service (`http://localhost:8088`), open the Perspective project from `ignition-projects/`, and verify OPC-UA tags (`ns=4`, port `4840`) are live.
5. **Docker Compose IT Stack** — start Mosquitto, Redpanda, InfluxDB, and Grafana (`cd docker && docker compose up -d`).
6. **Node-RED** — start Node-RED (`http://localhost:1880`), import the flow from `nod-red-flows/`, and click **Deploy**.
7. **InfluxDB Kafka Consumer** — from the repository root, run `python influxdb-consumer.py` to stream events from Redpanda (`production-events`) into InfluxDB (`smartline_kpis`).
8. **Grafana & Power BI** — open Grafana (`http://localhost:3000`, `1 s` refresh, JSON models stored in `dashboards/`) and Power BI Desktop (`power-bi/`, `60 s` refresh).

---

## Docker Compose — IT Layer

`docker/docker-compose.yml`:

```yaml
version: "3.8"

services:
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: smartline-mqtt
    ports:
      - "1883:1883"
    command: >
      sh -c "echo 'listener 1883\nallow_anonymous true' > /mosquitto/config/mosquitto.conf && /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf"
    volumes:
      - mosquitto-data:/mosquitto/data

  redpanda:
    image: redpandadata/redpanda:latest
    container_name: smartline-kafka
    command:
      - redpanda start
      - --smp 1
      - --memory 1G
      - --overprovisioned
      - --node-id 0
      - --kafka-addr PLAINTEXT://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://127.0.0.1:9092
    ports:
      - "9092:9092"
    volumes:
      - redpanda-data:/var/lib/redpanda/data

  influxdb:
    image: influxdb:2.7
    container_name: smartline-historian
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_USER:-admin}
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD:-smartline2026}
      - DOCKER_INFLUXDB_INIT_ORG=${INFLUXDB_ORG:-um6p}
      - DOCKER_INFLUXDB_INIT_BUCKET=${INFLUXDB_BUCKET:-smartline_kpis}
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN:-super-secret-smartline-token}
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2

  grafana:
    image: grafana/grafana:latest
    container_name: smartline-dashboard
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-smartline}
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - influxdb

volumes:
  mosquitto-data:
  redpanda-data:
  influxdb-data:
  influxdb-config:
  grafana-data:
```

Bring the stack up or down:

```bash
cd docker
docker compose up -d      # start everything in the background
docker compose ps         # confirm all services are Up
docker compose logs -f    # tail logs across all services
docker compose down       # stop containers (data persists in named volumes)
docker compose down -v    # stop AND wipe all volumes — use with care
```

---

## Connecting Grafana to InfluxDB

1. In Grafana (`http://localhost:3000`), go to **Connections -> Data sources -> Add data source -> InfluxDB**.
2. Query language: **Flux**.
3. URL: `http://influxdb:8086` (internal Docker network hostname).
4. Organization: `um6p`, Default bucket: `smartline_kpis`, Token: value of `INFLUXDB_TOKEN`.
5. Click **Save & test** to verify connectivity, then import the dashboard JSON from `dashboards/`.

---

## Verifying Each Layer is Live

| Layer | How to Verify |
| --- | --- |
| Factory I/O <-> S7-1500 | Green driver icon in Factory I/O; sensor changes update PLC tags in TIA Portal online monitoring |
| OPC-UA Server (`ns=4`) | UaExpert connects to `opc.tcp://192.168.0.1:4840` and displays live values for all 23 tags |
| Ignition SCADA | Tag Browser shows Good quality; `S3_Palletizer` changes color according to roller/fault state |
| Node-RED & Mosquitto | `MQTT Payload Monitor` debug node prints formatted JSON every `1000 ms`; `kafka` node shows green `connected to 127.0.0.1:9092` |
| `influxdb-consumer.py` & InfluxDB | Consumer terminal logs incoming `production-events` messages; InfluxDB Data Explorer returns points in `smartline_kpis` |
| Grafana | Panels update every second with ~`263 ms` stream lag; `$Station` dropdown filters alarms cleanly |

---

## Shutdown Procedure

1. Switch Factory I/O back to **Edit Mode** before closing.
2. Stop `influxdb-consumer.py` (`Ctrl + C`).
3. Power off or stop the S7-1500 instance in **S7-PLCSIM Advanced** (retentive `DB50_KPIs` values are preserved).
4. Run `docker compose down` (without `-v`) inside `docker/`.