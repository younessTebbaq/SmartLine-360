# Work Breakdown Structure — SmartLine 360

This WBS splits the project into 4 milestones and ~26 tasks. Each task line
maps 1:1 to a card on the GitHub Project board (To Do → In Progress → Done).

---

## M1 — OT Foundation (Week 1-2)

| # | Task | Output | Repo location |
| - | --- | --- | --- |
| 1.1 | Build Factory I/O scene — Station 1 (Infeed & Color Sorting) | `.factoryio` scene | `factory-io-scenes/` |
| 1.2 | Build Factory I/O scene — Station 2 (Assembly) | same scene, extended | `factory-io-scenes/` |
| 1.3 | Build Factory I/O scene — Station 3 (Packaging & Palletizing) | same scene, extended | `factory-io-scenes/` |
| 1.4 | Export I/O tag list from Factory I/O | tag list | `docs/` (reference) |
| 1.5 | Create TIA Portal project + S7-1200 PLC | `.ap17` | `plc-programs/` |
| 1.6 | Write PLC tag table matching Factory I/O tags | tag table | `plc-programs/` |
| 1.7 | Write PLC logic — sorting sequence | FB/FC | `plc-programs/` |
| 1.8 | Write PLC logic — assembly sequence | FB/FC | `plc-programs/` |
| 1.9 | Write PLC logic — packaging/palletizing sequence | FB/FC | `plc-programs/` |
| 1.10 | Connect PLC (PLCSIM or Modbus TCP) to Factory I/O and test end-to-end | working simulation | — |
| 1.11 | Commit scene + PLC project to Git | git commit | — |

**Milestone exit criteria:** items flow through all 3 stations under full PLC control, with no manual forcing of tags required.

---

## M2 — SCADA & Integration (Week 3)

| # | Task | Output | Repo location |
| - | --- | --- | --- |
| 2.1 | Install Ignition, create new Gateway project | project | `ignition-projects/` |
| 2.2 | Configure OPC-UA connection: TIA Portal ↔ Ignition | OPC-UA config | `ignition-projects/` |
| 2.3 | Bind Ignition tags to PLC tags | tag bindings | `ignition-projects/` |
| 2.4 | Build HMI screen — line overview (3 stations) | HMI view | `ignition-projects/` |
| 2.5 | Build HMI screen — alarms/status | HMI view | `ignition-projects/` |
| 2.6 | Export/back up Ignition project | project export | `ignition-projects/` |

**Milestone exit criteria:** live PLC values are visible and controllable from the Ignition HMI.

---

## M3 — IT/Data Pipeline (Week 4-5)

| # | Task | Output | Repo location |
| - | --- | --- | --- |
| 3.1 | Write `docker-compose.yml` (Kafka/Redpanda, InfluxDB, Grafana) | compose file | `docker/` |
| 3.2 | Verify all containers start and stay healthy on 16 GB RAM | — | — |
| 3.3 | Install Node-RED + `node-red-contrib-opcua` | flow env | — |
| 3.4 | Build flow: OPC-UA read → MQTT publish | flow JSON | `node-red-flows/` |
| 3.5 | Build flow: MQTT → Kafka bridge | flow JSON | `node-red-flows/` |
| 3.6 | Configure InfluxDB bucket + write path (Telegraf or Python consumer) | config/script | `docker/` |
| 3.7 | Verify data lands in InfluxDB with correct timestamps | query test | — |
| 3.8 | Commit `docker/` and `node-red-flows/` to Git | git commit | — |

**Milestone exit criteria:** a value change on the PLC is visible in an InfluxDB query within a few seconds, with no manual steps.

---

## M4 — Visualization & Closure (Week 6)

| # | Task | Output | Repo location |
| - | --- | --- | --- |
| 4.1 | Build Grafana dashboard — real-time station status | dashboard | screenshot in `assets/` |
| 4.2 | Build Grafana dashboard — throughput/OEE-style metrics | dashboard | screenshot in `assets/` |
| 4.3 | Build Power BI dashboard — business KPIs | `.pbix` | `power-bi/` |
| 4.4 (optional) | Add Python FastAPI + scikit-learn predictive-maintenance endpoint | API | `power-bi/` or new `ml/` folder |
| 4.5 | Write architecture diagram | image | `assets/` |
| 4.6 | Write `README.md` (overview, architecture, setup) | doc | root |
| 4.7 | Fill in all `docs/` files | docs | `docs/` |
| 4.8 | Record demo video | video/link | `assets/` or README link |
| 4.9 | Final commit, tag release (e.g. `v1.0`) | git tag | — |
| 4.10 | Publish LinkedIn post with repo link | — | — |

**Milestone exit criteria:** a stranger can clone the repo, follow `SETUP.md`, and reproduce the full pipeline.

---

## Dependencies at a glance

```
M1 (OT Foundation)
  └─▶ M2 (SCADA) — needs working PLC tags
        └─▶ M3 (Data Pipeline) — needs OPC-UA server live
              └─▶ M4 (Visualization) — needs data in InfluxDB
```

M1 is the critical path — nothing downstream can start until the Factory I/O
scene and PLC logic are working together.
