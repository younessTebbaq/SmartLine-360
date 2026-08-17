# Risk Register — SmartLine 360

Reviewed weekly. Update **Status** as risks are mitigated, triggered, or retired.

| ID | Risk | Probability | Impact | Mitigation Plan | Status |
| -- | --- | --- | --- | --- | --- |
| R1 | TIA Portal project freezes or corrupts | High | Critical | Commit to Git after every successful change in TIA Portal; keep a dated backup copy in `plc-programs/backups/` before major edits | Open |
| R2 | Kafka/Redpanda container fails to start or crashes | Medium | High | Debug with `docker compose logs kafka`; keep MQTT → InfluxDB as a fallback path that bypasses Kafka if needed | Open |
| R3 | Laptop runs out of RAM (16 GB) with TIA Portal + Factory I/O + Docker stack running simultaneously | Medium | Medium | Close unnecessary apps/browser tabs; run only the containers needed for the current milestone; consider `docker compose stop` for unused services | Open |
| R4 | OPC-UA connection between TIA Portal/PLC and Ignition or Node-RED drops | Medium | Medium | Implement reconnect/retry logic in Node-RED; monitor connection status tag on the HMI | Open |
| R5 | Docker containers lose data on restart | Low | Critical | Use named Docker volumes for InfluxDB and Grafana so data persists across `docker compose down/up` | Open |
| R6 | Factory I/O 30-day trial expires before project is finished | Medium | High | Track trial start date here; if nearing expiry, prioritize finishing M1 (which needs Factory I/O) before other milestones | Open |
| R7 | Scope creep — trying to add features beyond the 9-layer stack | Medium | Medium | Anything not in `PROJECT_CHARTER.md` scope goes into a "Future Ideas" backlog instead of the active board | Open |
| R8 | Time overrun — 6-week estimate slips | Medium | Medium | Weekly check-in against `TIMELINE.md`; if behind, cut scope (e.g. simplify HMI or skip the FastAPI/ML add-on) rather than extend deadline indefinitely | Open |
| R9 | Loss of local work (no backup beyond laptop) | Low | Critical | Push to the GitHub remote at the end of every work session, not just at milestone completion | Open |

## How to use this file
- Add a new row any time a new risk becomes apparent — don't wait for it to happen.
- When a risk is triggered, change **Status** to `Triggered`, and add a short note directly below the table describing what happened and how it was resolved (this feeds `LESSONS_LEARNED.md`).
- When a risk can no longer occur (e.g. milestone is done), change **Status** to `Retired`.

## Triggered risk log
_(Add entries here as risks materialize, in the format: `[Date] R# — what happened — how it was resolved`)_
