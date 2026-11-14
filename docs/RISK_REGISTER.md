# Risk Register — SmartLine 360

Tracked technical and operational risks across the lifecycle of the SmartLine 360 project.

| ID | Risk | Probability | Impact | Mitigation Plan | Status |
| -- | --- | --- | --- | --- | --- |
| R1 | TIA Portal project freezes or corrupts during online edits | Medium | Critical | Commit `.ap17` to Git after every working station or block change; keep dated backups in `plc-programs.backup/` | Mitigated |
| R2 | Virtual network route between Windows and S7-PLCSIM Advanced drops after TIA Portal closes | High | High | Assign permanent static IPv4 `192.168.0.50` (`255.255.255.0`) to `Siemens PLCSIM Virtual Ethernet Adapter` in `ncpa.cpl` | Resolved |
| R3 | Laptop runs out of RAM (16 GB) running TIA Portal + Factory I/O + Ignition + Docker simultaneously | Medium | Medium | Use lightweight Redpanda instead of JVM Kafka+Zookeeper; stop unused containers when editing CAD/PLC scenes | Mitigated |
| R4 | Node-RED Kafka contrib node fails to connect to local broker on port `9092` | High | High | Replace broken contrib node with maintained Kafka client library in `nod-red-flows/` and enforce `msg.topic = "production-events"` via `Kafka Topic Router` | Resolved |
| R5 | Machine fault reset wipes shift OEE and Availability counters mid-shift | High | High | Separate `#Button_FaultReset` from `#HMI_ShiftReset` in `FC50_KPIs` and set `Retain = Yes` on shift accumulators in `DB50_KPIs` | Resolved |
| R6 | Rising-edge Flux query (`difference()`) misses alarms that latched prior to the active Grafana time window | Medium | Medium | Pair the rising-edge `Shift Fault Occurrences` Pareto bar chart with an unaggregated `Alarm Chronology & State` State Timeline panel in `dashboards/` | Resolved |
| R7 | Docker containers lose historical telemetry on restart | Low | Critical | Bind persistent named volumes (`influxdb-data`, `grafana-data`, `redpanda-data`, `mosquitto-data`) in `docker/docker-compose.yml` | Mitigated |
| R8 | Time-series data leakage in predictive maintenance ML training | Medium | Medium | Split NASA CMAPSS training and test sets strictly by engine unit rather than random rows | Resolved |

## Triggered Risk & Resolution Log

* **R1 (Mitigated):** Maintained a dedicated `plc-programs.backup/` folder at the repository root to store clean checkpoints prior to modifying `FC50_KPIs` and `DB50_KPIs`.
* **R2 (Triggered & Resolved):** PLCSIM Advanced (`192.168.0.1`) became unreachable whenever TIA Portal closed because Windows discarded the temporary DCP address. Resolved permanently by configuring static IP `192.168.0.50` on the virtual adapter.
* **R4 (Triggered & Resolved):** Initial Node-RED Kafka node failed to connect to `127.0.0.1:9092`. Resolved by switching the Node-RED Kafka client library and adding the `Kafka Topic Router` function node in `nod-red-flows/`.
* **R5 (Triggered & Resolved):** Pressing the control panel reset after an E-Stop/gripper jam zeroed `OEE` and `Availability`. Resolved by decoupling machine fault reset from shift reset and adding `R_TRIG` edge detection for `MTBF`/`MTTR`.
* **R6 (Triggered & Resolved):** Latched alarms showed `0 events` on the Pareto bar chart when the `0 -> 1` transition fell outside the time picker window. Resolved by adding the `Alarm Chronology & State` (`State timeline`) panel alongside the Pareto chart in `dashboards/`.

## How to use this file
- Add a new row any time a new risk becomes apparent — don't wait for it to happen.
- When a risk is triggered, change **Status** to `Triggered`, and add a short note directly below the table describing what happened and how it was resolved (this feeds `LESSONS_LEARNED.md`).
- When a risk can no longer occur (e.g. milestone is done), change **Status** to `Retired`.