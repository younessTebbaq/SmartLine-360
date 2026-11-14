# Development — SmartLine 360

How to modify, extend, and customize each layer of the SmartLine 360 stack
without breaking downstream contracts.

## Layer Contracts

Each layer communicates with its immediate neighbor through a strict technical contract:

| Boundary | Technical Contract |
| --- | --- |
| Factory I/O -> TIA Portal (S7-1500) | I/O addresses and tag names in the Driver Configuration mapping (e.g. `%I2.1` `"DI_S3_PalletLoaded"`) |
| S7-1500 -> Ignition & Node-RED | OPC-UA NodeIds in namespace `ns=4` on port `4840` (e.g. `ns=4;s="DB50_KPIs"."OEE"`) |
| Node-RED -> Mosquitto MQTT | Topic hierarchy `SmartLine360/<metric>` and JSON schema (`timestamp`, `station`, `metric`, `value`) |
| Mosquitto -> Redpanda/Kafka | Unified topic `production-events` routed via `Kafka Topic Router` on `127.0.0.1:9092` |
| Kafka -> InfluxDB (`influxdb-consumer.py`) | Bucket `smartline_kpis` (`org: um6p`), measurements (`DB50_KPIs` fields and `Alarm_*` streams) |
| InfluxDB -> Grafana (`dashboards/`) | Flux queries filtered by regex `/^Alarm_/` and the `$Station` variable (`All`, `S1`, `S2`, `S3`) |

Whenever you rename a tag in `DB50_KPIs` or add a new station alarm, update its reference across the Node-RED array, `influxdb-consumer.py`, and Grafana Flux queries before committing.

---

## Modifying PLC Logic (`plc-programs/` & `plc-programs.backup/`)

- **Backup First:** Before major edits in TIA Portal, save a copy of the `.ap19` project inside `plc-programs.backup/` (Risk R1 mitigation).
- **Station Control (`LAD`):** Keep physical actuator interlocks and step watchdogs in dedicated per-station blocks (`Station 1 Sorting`, `Station 2 Pick-and-Place`, `Station 3 Palletizing`).
- **KPI & Reliability Math (`FC50_KPIs` in `SCL`):** Keep OEE, Availability, Performance, Yield, MTBF, and MTTR inside `FC50_KPIs` writing to `DB50_KPIs`.
- **Reset Separation:** Do not tie a machine fault reset (`#Button_FaultReset`) to the shift accumulator reset (`#HMI_ShiftReset`).
- **Alarm Naming Convention:** Prefix boolean alarm measurements exported to InfluxDB with `Alarm_S1_`, `Alarm_S2_`, or `Alarm_S3_` so Grafana's `$Station` regex filter (`r["_measurement"] =~ /${Station:raw}/`) picks them up automatically.

---

## Modifying the Node-RED Pipeline (`nod-red-flows/`)

- Keep the two chains inside `SmartLine-360 Pipeline` decoupled:
  1. **Top Chain (`OPC-UA -> Mosquitto`):** `Poll 1000ms` -> `Set NodeId` -> `Read S7-1500 DB50` -> `Format JSON Payload` -> `Publish to Mosquitto`.
  2. **Bottom Chain (`Mosquitto -> Kafka`):** `Listen to Mosquitto Edge` -> `Kafka Topic Router` (`msg.topic = "production-events"`) -> `kafka` (`127.0.0.1:9092`).
- After modifying any node, click **Deploy** and export the updated flow JSON into `nod-red-flows/`.

---

## Modifying Dashboards (`dashboards/` & `power-bi/`)

- **Grafana (`dashboards/`):** Use a `State timeline` visualization (with `Merge equal consecutive values` enabled) for active state and duration tracking, and a `Bar chart` with `difference(nonNegative: true) |> sum()` for rising-edge fault occurrence counts. Export updated JSON models to `dashboards/`.
- **Power BI (`power-bi/`):** Save updated `.pbix` files in `power-bi/`.

---

## Extending beyond the 9-layer stack

Ideas that are explicitly **out of scope** for v1 (per `PROJECT_CHARTER.md`)
but worth a "Future Ideas" backlog entry instead of scope creep:
- Alerting (e.g. Grafana → email/Slack on line stoppage)
- A second simulated line for A/B comparison
- Authentication/roles on the dashboards
- Historian-style long-term data retention/downsampling policies in InfluxDB