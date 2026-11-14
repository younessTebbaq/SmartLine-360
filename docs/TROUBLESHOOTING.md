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
- Confirm PLCSIM Advanced (or the real PLC) is actually running and downloaded
  with the current S7-1500 program.
- Re-check **File → Driver Configuration → Siemens S7-1200/1500 →
  Configuration** — a mismatched IP/rack/slot is the usual cause.
- A tag that's grayed out specifically (rather than the whole driver failing)
  usually means that tag doesn't exist on the PLC side, or its data type
  doesn't match — hover over it for the exact error.

**Station 3 palletizer elevator rises empty ("Ghost Cycle")**
- If the entry sensor triggers the elevator before the pallet fully clears the
  entry rollers (`DO_S3_Roller4m_B`), the lift goes up empty while the pallet
  stays jammed on the rollers.
- **Fix:** Gate vertical motion with a positive seating interlock on input
  `%I2.1` (`"DI_S3_PalletLoaded"`) paired with a 6-second `TON` watchdog timer.
  If the pallet does not seat within 6 seconds, block the lift and trigger
  `Alarm_S3_PalletMisfeed`.

**Station 2 gripper jams on a crooked box, but `CycleTime` and `Throughput` look normal**
- Because `CycleTime` and `Throughput` are normally updated when a part completes
  a cycle, a mid-cycle jam leaves the last good values frozen in memory (e.g.,
  `CycleTime: 7.81 s`, `Throughput: 7.6 parts/min`).
- **Fix:** Supervise the gantry sequence with a step watchdog timer in the PLC.
  When the watchdog expires, raise `S2_GripperFault` and immediately write
  `DB50_KPIs.Throughput := 0.0`.

---

## TIA Portal / S7-PLCSIM Advanced

**TIA Portal freezes or the project file corrupts** *(Risk R1)*
- Don't try to force-recover a corrupted project — restore from your last
  Git commit or `plc-programs.backup/` instead. This is why committing after
  every working change matters.
- If it freezes mid-download to PLCSIM Advanced, close both, restart PLCSIM
  Advanced first, then reopen TIA Portal.

**PLCSIM Advanced won't link to TIA Portal or Factory I/O when TIA Portal is closed**
- Confirm you are running **S7-PLCSIM Advanced** (required for external OPC-UA
  and virtual Ethernet access) rather than Standard PLCSIM.
- **Subnet Isolation Fix:** The virtual S7-1500 PLC runs on `192.168.0.1`,
  which Windows cannot route to unless the virtual adapter is on the same
  subnet (TIA Portal only injects a temporary IP via DCP during downloads).
  Open Windows Network Connections (`ncpa.cpl`), select **Siemens PLCSIM
  Virtual Ethernet Adapter → IPv4 Properties**, and assign a permanent static
  IP of `192.168.0.50` with subnet mask `255.255.255.0`.
- Re-download the program after any tag table or `DB50_KPIs` change.

**Pressing the panel Reset button wipes out Shift OEE and Availability**
- Using a single reset bit for both machine fault recovery and shift counters
  zeros `DB50_KPIs` mid-shift whenever an operator clears an E-Stop or jam.
- **Fix:** Separate `#Button_FaultReset` (clears latched fault bits and resets
  actuators only) from `#HMI_ShiftReset` (the sole tag permitted to zero
  accumulators in `DB50_KPIs`).

**`MTBF` and `MTTR` values are wildly inaccurate**
- Incrementing `Shift_Failure_Count` while a fault bit is `TRUE` adds to the
  counter on every PLC scan cycle instead of once per breakdown.
- **Fix:** Gate `Shift_Failure_Count` with a rising-edge `R_TRIG` detector on
  `Status = 1` and wrap the `MTBF`/`MTTR` division in an `IF Shift_Failure_Count > 0`
  guard inside `FC50_KPIs`.

---

## Ignition SCADA

**Gateway page won't load at `localhost:8088`**
- Confirm the Ignition Gateway service is actually running
  (`services.msc` on Windows) — installing Ignition doesn't automatically start
  it on every boot.

**OPC-UA connection shows disconnected**
- Verify the S7-1500's built-in OPC-UA server is enabled in TIA Portal (CPU
  Properties → OPC UA → port `4840`, namespace `ns=4`) and that the program was
  re-downloaded to PLCSIM Advanced after enabling it.
- Check that Ignition's OPC-UA connection endpoint matches what TIA Portal and
  UaExpert report (`opc.tcp://192.168.0.1:4840`).

**Alarm fires when the machine is healthy and clears when jammed (Inverted Alarm)**
- In the Ignition Tag Editor, adding an alarm with mode `Equal` defaults to
  `Setpoint = 0`, which evaluates as active when the boolean tag is `0` (normal).
- **Fix:** Change the alarm configuration to `Mode = Equal` and `Setpoint = 1`.

**Station synoptic stays green during an active fault**
- If color bindings check the running conveyor tag first, a running roller overrides
  the fault color.
- **Fix:** Use a priority-ordered nested expression on `S3_Palletizer` so the
  fault state takes precedence:
  `if({[default]Alarm_S3_PalletMisfeed}, "#FF0000", if({[default]Outputs/DO_S3_Roller4m_B}, "#43A047", "#B0B7C0"))`

**Demo license keeps resetting your work**
- Expected behavior on the trial tier (resets every 2 hours). Save and export
  your project to `ignition-projects/` frequently.

---

## Docker / Mosquitto / Redpanda / InfluxDB / Grafana

**Container fails to start** *(Risk R2)*
```bash
docker compose logs <service-name>
```
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
