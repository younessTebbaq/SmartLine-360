# Troubleshooting — SmartLine 360

Common issues by layer, roughly in the order you'll hit them (`SETUP.md` →
`DEPLOYMENT.md` order). If a fix here doesn't resolve it, check
`RISK_REGISTER.md` — some of these map directly to a tracked risk.

---

## Factory I/O

**Items don't appear on the conveyor**
- You almost certainly forgot an **Emitter** — every scene needs at least
  one to spawn items. Check its Configuration to confirm it's set to emit
  and not paused.

**Parts show a red outline and disappear in Run Mode**
- Red = intersecting another part. Switch back to Edit Mode, select the
  part, and reposition it until the red outline clears before re-entering
  Run Mode.

**Driver won't connect (grayed-out tags / no green icon)**
- Confirm PLCSIM (or the real PLC) is actually running and downloaded with
  the current program.
- Re-check **File → Driver Configuration → Siemens S7-1200/1500 →
  Configuration** — a mismatched IP/rack/slot is the usual cause.
- A tag that's grayed out specifically (rather than the whole driver failing)
  usually means that tag doesn't exist on the PLC side, or its data type
  doesn't match — hover over it for the exact error.

**Vision Sensor isn't detecting color as expected**
- Remember it only recognizes **Raw Material, Product Lid, and Product
  Base** (Blue/Green/Metal) — not generic Boxes. If your item type doesn't
  match, no color signal will ever fire.

---

## TIA Portal / PLCSIM

**TIA Portal freezes or the project file corrupts** *(Risk R1)*
- Don't try to force-recover a corrupted project — restore from your last
  Git commit instead. This is exactly why committing after every working
  change matters.
- If it freezes mid-download to PLCSIM, close both, restart PLCSIM first,
  then reopen TIA Portal.

**PLCSIM won't link to the TIA Portal project**
- Confirm both are the same PLCSIM type (Standard vs. Advanced) — mixing
  them is a common cause of silent connection failures.
- Re-download the program after any tag table change; PLCSIM doesn't always
  pick up tag renames automatically.

---

## Ignition

**Gateway page won't load at `localhost:8088`**
- Confirm the Ignition Gateway service is actually running
  (`services.msc` on Windows) — installing Ignition doesn't always start
  it automatically.

**OPC-UA connection shows disconnected**
- Verify the S7-1200's OPC-UA server is enabled in TIA Portal (CPU
  Properties → OPC UA) and that the program was re-downloaded after
  enabling it.
- Check that Ignition's OPC-UA connection URL/endpoint matches exactly
  what TIA Portal reports (including port).

**Demo license keeps resetting your work**
- Expected behavior on the free tier (resets every 2 hours). Save/export
  your project frequently rather than relying on the running Gateway state.

---

## Docker / Kafka / Redpanda / InfluxDB / Grafana

**Container fails to start** *(Risk R2)*
```bash
docker compose logs <service-name>
```
Read the actual error before restarting blindly — most failures are a port
conflict (something else already using 8086, 3000, 9092, etc.) or a missing
environment variable.

**Everything is slow / laptop fans spinning constantly** *(Risk R3)*
- You likely have TIA Portal + Factory I/O + the full Docker stack running
  at once. Stop containers you're not actively using:
  `docker compose stop <service-name>`
- Prefer Redpanda over full Kafka+Zookeeper if you haven't already — it's
  materially lighter.

**Data disappears after `docker compose down`** *(Risk R5)*
- You (or a script) likely ran `docker compose down -v`, which deletes
  volumes. Plain `docker compose down` preserves data. Check your compose
  file defines named volumes for `influxdb` and `grafana` data paths.

**Grafana dashboard shows "No data"**
- Check the data source test (Settings → Data Sources → Test) first —
  if that fails, the issue is InfluxDB connectivity/credentials, not the
  dashboard itself.
- Confirm the measurement/field names in your panel queries match what the
  consumer is actually writing (see the "contract" table in
  `DEVELOPMENT.md`) — a silent rename anywhere upstream breaks this.

---

## Node-RED

**OPC-UA node shows disconnected**
- Same checklist as the Ignition OPC-UA issue above — verify the endpoint
  URL and that the PLC's OPC-UA server is enabled and running.

**MQTT messages aren't reaching Kafka** *(Risk R4)*
- Test each hop independently: use an MQTT client (e.g. `mosquitto_sub`) to
  confirm messages are actually being published before assuming the
  Kafka bridge is broken.
- Add reconnect/retry logic on the MQTT node (Node-RED's default MQTT node
  supports this in its configuration) rather than letting a dropped
  connection silently stop the flow.

**Flow changes aren't reflected**
- You have to click **Deploy** after every change — easy to forget mid-debug.

---

## Power BI / FastAPI

**Power BI can't connect to InfluxDB**
- InfluxDB's recommended query interface changes between versions (Flux
  vs. InfluxQL vs. SQL in InfluxDB 3.x) — confirm which your installed
  version uses before assuming the connector is broken.
- As a fallback, have the FastAPI layer pre-query InfluxDB and expose a
  simple REST/JSON endpoint that Power BI hits instead of connecting to
  InfluxDB directly — simpler to debug.

**FastAPI endpoint returns an error / won't start**
- `uvicorn main:app --reload` prints the actual traceback — read it before
  re-running. Most common cause early on is a missing package
  (`pip install -r requirements.txt` if you've frozen one).

---

## General debugging approach

1. **Isolate the layer.** Test each hop (Factory I/O → PLC → OPC-UA →
   MQTT → Kafka → InfluxDB → dashboard) independently using each tool's
   own "watch/debug" view before assuming the whole chain is broken.
2. **Check the contract, not just the code.** Most "nothing is updating"
   issues are a renamed tag/topic/field that wasn't updated everywhere —
   see the contract table in `DEVELOPMENT.md`.
3. **When in doubt, roll back.** `git log` your way back to the last known
   working commit for the layer you're debugging rather than guessing
   forward.
4. **Log it.** If you hit something not listed here, add it — both for
   future-you and as evidence of debugging skill for `LESSONS_LEARNED.md`.
