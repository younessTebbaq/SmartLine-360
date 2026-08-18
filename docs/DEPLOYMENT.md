# Deployment — SmartLine 360

How to bring the full stack up, in the right order, and verify each layer
before moving to the next.

## Startup order

Later layers depend on earlier ones being live — start in this order:

1. **Factory I/O** — open the scene, stay in Edit Mode for now.
2. **TIA Portal / PLCSIM** — start the PLC simulation.
3. **Connect Factory I/O to the PLC** — File → Driver Configuration → Siemens S7-1200/1500 → Connect. Confirm green connection icon.
4. **Factory I/O → Run Mode** (`F5`) — the physical simulation is now live and PLC-controlled.
5. **Ignition Gateway** — start it, open the project, confirm OPC-UA tags are live (not stale/grey).
6. **Docker Compose stack** (Kafka/Redpanda, InfluxDB, Grafana) — see below.
7. **Node-RED** — start it (Docker or standalone), deploy the OPC-UA→MQTT and MQTT→Kafka flows.
8. **Grafana** — dashboards should now start showing live data.
9. **Power BI** — open the `.pbix`, refresh the data connection.

## Docker Compose — IT layer

`docker/docker-compose.yml` (starting point — adjust images/versions as you finalize them):

```yaml
version: "3.8"

services:
  redpanda:
    image: redpandadata/redpanda:latest
    command:
      - redpanda start
      - --smp 1
      - --memory 1G
      - --overprovisioned
      - --node-id 0
      - --kafka-addr PLAINTEXT://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://redpanda:9092
    ports:
      - "9092:9092"
    volumes:
      - redpanda-data:/var/lib/redpanda/data

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_USER}
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD}
      - DOCKER_INFLUXDB_INIT_ORG=smartline360
      - DOCKER_INFLUXDB_INIT_BUCKET=station_data
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}
    volumes:
      - influxdb-data:/var/lib/influxdb2

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - influxdb

  node-red:
    image: nodered/node-red:latest
    ports:
      - "1880:1880"
    volumes:
      - node-red-data:/data
    depends_on:
      - redpanda

volumes:
  redpanda-data:
  influxdb-data:
  grafana-data:
  node-red-data:
```

Store secrets in `docker/.env` (gitignored — never commit this file):
```
INFLUXDB_USER=admin
INFLUXDB_PASSWORD=changeme
INFLUXDB_TOKEN=changeme-generate-a-real-token
GRAFANA_PASSWORD=changeme
```

Bring it up / down:
```bash
cd docker
docker compose up -d      # start everything in the background
docker compose ps         # confirm all services are Up
docker compose logs -f    # tail logs across all services
docker compose down       # stop everything (data persists in the named volumes)
docker compose down -v    # stop AND wipe all data — use with care
```

## Connecting Grafana to InfluxDB

1. In Grafana, go to **Connections → Data sources → Add data source → InfluxDB**.
2. Query language: **Flux**.
3. URL: `http://influxdb:8086` (container-to-container name, not `localhost`, since both run in the same Compose network).
4. Organization: `smartline360`, Token: the value of `INFLUXDB_TOKEN`, Default bucket: `station_data`.
5. Save & test — it should confirm the connection.

## Verifying each layer is actually live (not just "started")

| Layer | How to verify |
| --- | --- |
| Factory I/O ↔ PLC | Green connection icon in the Driver window; forcing a tag in Factory I/O changes the corresponding PLC tag |
| Ignition | Tag browser shows live (not grey/stale) values |
| Node-RED | Debug panel shows messages flowing on deploy |
| Kafka/Redpanda | `docker compose logs redpanda` shows no repeated connection errors from producers/consumers |
| InfluxDB | A manual Flux query in its UI returns recent points |
| Grafana | Dashboard panels update within ~2 seconds of a manual tag change in Factory I/O |

## Shutdown procedure

1. Stop Factory I/O Run Mode (return to Edit Mode) before closing, to avoid losing unsaved scene state.
2. Stop the PLC simulation in TIA Portal / PLCSIM.
3. `docker compose down` (without `-v`, to keep your data).
4. Close Ignition Gateway and Node-RED if running standalone.

## Environments

For a solo demo project, one environment is enough — but keep the `.env`
file separate from `docker-compose.yml` so credentials never end up in Git
history, and so you could point the same compose file at different
credentials later (e.g. a "clean demo" reset vs. your working data).
