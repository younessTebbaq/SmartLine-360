# Project Charter — SmartLine 360

## Project Name
SmartLine 360 — Digital Factory Intelligence Platform

## Project Objective
Design and implement a complete OT-IT data pipeline that connects a simulated
production line to real-time operational and business dashboards — covering
the full path from a PLC-controlled physical process to an executive-facing
analytics layer.

## Background / Motivation
Most portfolio projects show either the automation side (PLC logic) or the
data side (dashboards), rarely both connected end-to-end. SmartLine 360
closes that gap by building a 9-technology stack that mirrors a real Industry
4.0 deployment, on free/trial tools and a single laptop.

## Scope

**In scope**
- A custom 3-station Factory I/O scene (infeed & optical sorting, gantry pick-and-place assembly, packaging & palletizing)
- PLC control logic and deterministic OEE/MTBF/MTTR computation in TIA Portal (Siemens S7-1500 via PLCSIM Advanced, LAD + SCL in `FC50_KPIs` / `DB50_KPIs`)
- SCADA/HMI layer in Ignition Perspective (4 operator screens + 3-state color priority bindings)
- OPC-UA bridge from PLC to IT systems (Port 4840, `ns=4`, 23 structured tags)
- Node-RED for protocol translation (OPC-UA → Mosquitto MQTT → Kafka/Redpanda on topic `production-events`)
- Time-series storage in InfluxDB 2.7 (`smartline_kpis` bucket)
- Operational EMI dashboard in Grafana (1s refresh, 263 ms measured stream lag, State Timeline + Pareto diagnostics)
- Business dashboard in Power BI (60s refresh) + predictive maintenance ML layer via Python FastAPI (NASA CMAPSS Random Forest)
- Full documentation and version control on GitHub

**Out of scope**
- Physical/real hardware integration
- Multi-user authentication or production-grade security hardening
- High-availability / redundant deployment
- Mobile app or external-facing UI beyond the operational and executive dashboards

## Key Stakeholders
| Stakeholder | Interest |
| --- | --- |
| Youness Tebbaq (Project Engineer) | Deliver a working, demonstrable system; build end-to-end OT-IT & IIoT engineering skills |
| Recruiters / Hiring Managers / PFE Jury | Evidence of end-to-end systems thinking, industrial debugging, and delivery |
| Future self | Reusable reference architecture for future industrial automation and IIoT projects |

## Success Criteria
1. Factory I/O 3-station scene built and controlled by a TIA Portal S7-1500 PLC program with watchdog supervision (`HighSort`, `S2_GripperFault`, `Alarm_S3_PalletMisfeed`).
2. Data flows automatically: S7-1500 PLC → OPC-UA (`ns=4`) → Node-RED → Mosquitto MQTT → Kafka/Redpanda (`production-events`) → InfluxDB (`smartline_kpis`).
3. Grafana (operational, 1s refresh) and Power BI (business, 60s refresh) dashboards display live data from the same pipeline.
4. Full source, configs, and docs are version-controlled and reproducible from the GitHub repo by someone other than the author.

## Main Constraints
| Constraint | Detail |
| --- | --- |
| Time | 6 weeks, part-time |
| Hardware | Single laptop, 16 GB RAM |
| Budget | Free / trial / student-licensed tools only |
| Team | Solo project |

## High-Level Milestones
See `docs/WORK_BREAKDOWN_STRUCTURE.md` and `docs/KPI_GUIDE.md` for the
detailed breakdown.

| Milestone | Target |
| --- | --- |
| M1: OT Foundation (Factory I/O + S7-1500 LAD/SCL) | Week 1-2 |
| M2: SCADA & Integration (Ignition + OPC-UA `ns=4`) | Week 3 |
| M3: IT/Data Pipeline (Docker, Node-RED, MQTT, Redpanda, InfluxDB) | Week 4-5 |
| M4: Visualization, ML & Closure (Grafana, Power BI, FastAPI) | Week 6 |

## Approval
Solo project — self-approved on: **2026-08-15**