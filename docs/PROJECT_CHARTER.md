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
- A custom 3-station Factory I/O scene (infeed/sorting, assembly, packaging)
- PLC control logic in TIA Portal (S7-1200)
- SCADA/HMI layer in Ignition
- OPC-UA bridge from PLC to IT systems
- Node-RED for protocol translation (OPC-UA → MQTT → Kafka)
- Time-series storage in InfluxDB
- Operational dashboard in Grafana
- Business dashboard in Power BI (+ optional ML layer via FastAPI)
- Full documentation and version control on GitHub

**Out of scope**
- Physical/real hardware integration
- Multi-user authentication or production-grade security hardening
- High-availability / redundant deployment
- Mobile app or external-facing UI beyond the two dashboards

## Key Stakeholders
| Stakeholder | Interest |
| --- | --- |
| You (Project Engineer) | Deliver a working, demonstrable system; build OT-IT skills |
| Recruiters / Hiring Managers | Evidence of end-to-end systems thinking and delivery |
| Future self | Reusable reference architecture for future projects |

## Success Criteria
1. Factory I/O scene built and fully controlled by a TIA Portal PLC program.
2. Data flows automatically: PLC → OPC-UA → MQTT → Kafka → InfluxDB.
3. Grafana (operational) and Power BI (business) dashboards display live data
   from the same pipeline.
4. Full source, configs, and docs are version-controlled and reproducible
   from the GitHub repo by someone other than you.

## Main Constraints
| Constraint | Detail |
| --- | --- |
| Time | 6 weeks, part-time |
| Hardware | Single laptop, 16 GB RAM |
| Budget | Free / trial / student-licensed tools only |
| Team | Solo project |

## High-Level Milestones
See `docs/WORK_BREAKDOWN_STRUCTURE.md` and `docs/TIMELINE.md` for the
detailed breakdown.

| Milestone | Target |
| --- | --- |
| M1: OT Foundation | Week 1-2 |
| M2: SCADA & Integration | Week 3 |
| M3: IT/Data Pipeline | Week 4-5 |
| M4: Visualization & Closure | Week 6 |

## Approval
Solo project — self-approved on: _[fill in start date]_
