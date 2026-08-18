# Development — SmartLine 360

How to modify, extend, and customize each layer of the stack without
breaking the rest of the pipeline.

## General principle

Each layer only needs to agree with its **immediate neighbor** on a
contract (a tag name, a topic name, a schema). As long as you preserve that
contract — or update it everywhere it's referenced — you can change the
internals of any single layer freely.

| Layer | Contract with the next layer |
| --- | --- |
| Factory I/O → TIA Portal | Tag names in the Driver Configuration mapping |
| TIA Portal → Ignition/Node-RED | OPC-UA node IDs (PLC tag addresses exposed via OPC-UA) |
| Node-RED → Kafka | Topic names and JSON message schema |
| Kafka → InfluxDB | Measurement/field names written by the consumer |
| InfluxDB → Grafana/Power BI | Query/measurement names used in dashboard panels |

Whenever you rename a tag or restructure a message, grep the repo for the
old name before committing — a broken contract is the #1 cause of "the
dashboard just stopped updating."

## Adding a new station to the Factory I/O scene

1. Build the new station in Factory I/O per `factory-io-scene-guide.md`'s pattern (Emitter → detection → actuation → Remover).
2. Note the new tags it creates (visible via the Sensor/Actuator Tags overlay).
3. Re-export the tag mapping (**File → Driver Configuration → export**) and re-import into TIA Portal's tag table — don't hand-retype tags, it's error-prone.
4. Add the corresponding PLC logic as a **new function block**, not by editing existing blocks in place, so existing stations keep working while you build.
5. Add new OPC-UA exposure if the new tags aren't automatically covered by your existing OPC-UA server scope.
6. Extend the Node-RED flow with new subscribe/publish nodes for the new tags — copy the pattern of an existing station's nodes rather than starting from scratch.
7. Add new Grafana panels / InfluxDB fields as needed.

## Modifying PLC logic

- Keep one function block (FB) per station — mirrors the Factory I/O scene structure and keeps `git diff` readable.
- Back up the `.ap17` file before large restructuring (see `RISK_REGISTER.md` R1 — TIA Portal corruption risk).
- Test each station's logic in isolation using Factory I/O's tag **Force** feature before wiring it into the full sequence — this avoids debugging multiple stations at once.

## Modifying the Node-RED flow

- Keep OPC-UA→MQTT and MQTT→Kafka as **separate, named flows** (tabs) rather than one flow — makes it easier to test/restart one bridge without touching the other, and directly addresses the single-point-of-failure trade-off noted in `ARCHITECTURE.md`.
- Export flows to `node-red-flows/` after every meaningful change (Menu → Export → clipboard/file).

## Modifying the data pipeline (Docker stack)

- Add new services to `docker/docker-compose.yml` rather than creating a second compose file — keeps `docker compose up` a single command.
- If adding a new consumer (e.g. a second InfluxDB writer for a new topic), containerize it rather than running it as a bare local script, so `DEPLOYMENT.md` stays accurate.

## Modifying dashboards

- **Grafana:** export dashboard JSON (Dashboard settings → JSON Model) and commit it under `docker/grafana/dashboards/` so the dashboard is provisioned automatically on a fresh `docker compose up`, not manually recreated.
- **Power BI:** keep the `.pbix` in `power-bi/`; if you add a new visual, note the new InfluxDB query it depends on in this file so future-you remembers the dependency.

## Coding conventions

- Tag/topic naming: `smartline360/<station>/<part-type>_<n>` (e.g. `smartline360/station1/vision_sensor_1`) — consistent across OPC-UA, MQTT, and Kafka so you can `grep` a tag's full path across every layer.
- Commit messages: `feat(station-1): ...`, `fix(node-red): ...`, `docs: ...` — matches the per-station, per-layer commit granularity described in `WORK_BREAKDOWN_STRUCTURE.md`.
- Every new script gets a one-line docstring/header comment stating what layer it belongs to and what it consumes/produces.

## Extending beyond the 9-layer stack

Ideas that are explicitly **out of scope** for v1 (per `PROJECT_CHARTER.md`)
but worth a "Future Ideas" backlog entry instead of scope creep:
- Alerting (e.g. Grafana → email/Slack on line stoppage)
- A second simulated line for A/B comparison
- Authentication/roles on the dashboards
- Historian-style long-term data retention/downsampling policies in InfluxDB
