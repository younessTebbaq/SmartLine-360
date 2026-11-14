# KPIs Guide — SmartLine 360

This document defines every KPI in the SmartLine 360 project: what it
means, how it is computed in the S7-1500 PLC, which tag in `DB50_KPIs`
stores it, and where it appears on the dashboards.

The KPIs are computed deterministically by `FC50_KPIs` (SCL) in the
Siemens S7-1500 PLC program and stored in the global data block `DB50_KPIs`.
They are exposed to Ignition SCADA and Node-RED via the built-in OPC-UA
server (`ns=4`, port `4840`).

---

## Table of Contents

- [KPI Storage — DB50_KPIs](#kpi-storage--db50_kpis)
- [KPI Computation — FC50_KPIs](#kpi-computation--fc50_kpis)
- [Core SCL Implementations](#core-scl-implementations)
- [KPI Definitions](#kpi-definitions)
- [Supervised Watchdog Alarms](#supervised-watchdog-alarms)
- [Dashboard Mapping](#dashboard-mapping)
- [OPC-UA Exposure](#opc-ua-exposure)
- [Testing Checklist](#testing-checklist)

---

## KPI Storage — DB50_KPIs

All KPIs and shift accumulators live in the global data block `DB50_KPIs`.

| Field | Type | Retain | Meaning |
| --- | --- | --- | --- |
| `ProductionCount` | DInt | Yes | Total finished items produced across the line |
| `LoadedPalletCount` | Int | Yes | Total finished pallets discharged at Station 3 |
| `SortedCount` | DInt | Yes | Number of items diverted at Station 1 |
| `SortRate` | Real | No | Percentage of items diverted at Station 1 ($\%$) |
| `CycleTime` | Real | No | Time between two consecutive item completions ($\text{s}$ / $\text{ms}$) |
| `Throughput` | Real | No | Items per minute (forced to `0.0` when `S2_GripperFault` is active) |
| `Availability` | Real | No | $\text{RunTime} \div \text{PlannedTime} \times 100$ |
| `Performance` | Real | No | $\text{ActualRate} \div \text{IdealRate} \times 100$ |
| `Yield` | Real | No | $(\text{ProductionCount} - \text{SortedCount}) \div \text{ProductionCount} \times 100$ |
| `OEE` | Real | No | $(\text{Availability} \times \text{Performance} \times \text{Yield}) \div 10000.0$ |
| `Shift_Failure_Count` | Int | Yes | Discrete breakdown counter incremented on fault rising edge (`R_TRIG`) |
| `MTBF` | Real | No | Mean Time Between Failures ($\text{s}$) |
| `MTTR` | Real | No | Mean Time To Repair ($\text{s}$) |
| `ActiveAlarms` | Int | No | Count of currently active alarm flags |
| `Downtime` | DInt | Yes | Cumulative shift downtime in seconds |
| `Status` | Word | No | `0` = Normal, `1` = Fault Active, `2` = E-Stop Active |
| `Timestamp` | DTL | No | Current PLC system time (`RD_LOC_T`) |

**Retain and Reset Policy:**
- Shift accumulators (`ProductionCount`, `LoadedPalletCount`, `SortedCount`, `RunTime`, `Downtime`, `Shift_Failure_Count`) use `Retain = Yes` so shift totals survive a PLC power cycle or a `STOP -> RUN` transition.
- **Machine Fault Reset (`#Button_FaultReset`)** clears active alarms and resets pneumatic actuators to `Ready` without modifying `DB50_KPIs`.
- **Shift Reset (`#HMI_ShiftReset`)** is the only tag permitted to zero shift accumulators at the end of a production shift.

---

## KPI Computation — FC50_KPIs

`FC50_KPIs` is an SCL function called on every scan from `OB1`.

| Input Parameter | Type | Source |
| --- | --- | --- |
| `CycleCount` | DInt | Total production counter CV |
| `SortedCount` | DInt | Station 1 diversion counter CV |
| `RunTime` | DInt | Cumulative run-time timer ET ($\text{ms}$) |
| `PlannedTime` | DInt | Shift planned time setpoint ($\text{s}$) |
| `Downtime` | DInt | Cumulative downtime timer ET ($\text{s}$) |
| `IdealRate` | Real | Target production rate setpoint |
| `EStop` | Bool | Physical E-Stop input status |

---

## Core SCL Implementations

### 1. Availability & OEE Calculation

```scl
// Availability & OEE
IF #PlannedTime > 0 THEN
    // Divide RunTime by 1000.0 to convert milliseconds to seconds
    "DB50_KPIs".Availability := 100.0 * (DINT_TO_REAL(#RunTime) / 1000.0) / DINT_TO_REAL(#PlannedTime);
END_IF;

"DB50_KPIs".OEE := ("DB50_KPIs".Availability * "DB50_KPIs".Performance * "DB50_KPIs".Yield) / 10000.0;
```

### 2. Edge-Triggered MTBF & MTTR Calculation

```scl
// 1. Count discrete failure events (Rising Edge of a fault)
#Fault_Trigger(CLK := ("DB50_KPIs".Status = 1));
IF #Fault_Trigger.Q THEN
    "DB50_KPIs".Shift_Failure_Count := "DB50_KPIs".Shift_Failure_Count + 1;
END_IF;

// 2. Prevent division by zero
IF "DB50_KPIs".Shift_Failure_Count > 0 THEN
    "DB50_KPIs".MTTR := DINT_TO_REAL("DB50_KPIs".Downtime) / INT_TO_REAL("DB50_KPIs".Shift_Failure_Count);
    "DB50_KPIs".MTBF := (DINT_TO_REAL(#RunTime) / 1000.0) / INT_TO_REAL("DB50_KPIs".Shift_Failure_Count);
ELSE
    "DB50_KPIs".MTTR := 0.0;
    "DB50_KPIs".MTBF := DINT_TO_REAL(#RunTime) / 1000.0;
END_IF;
```

---

## KPI Definitions

### 1. Production Count

| Property | Value |
| --- | --- |
| **Definition** | Total number of finished items that have completed the full line |
| **Formula** | `ProductionCount = count of ProductionPulse events` |
| **PLC tag** | `Final_Product_Count` |
| **Source** | Counter in OB1, incremented on each `ProductionPulse` from FC3 |
| **Dashboard** | Both |

### 2. Loaded Pallet Count

| Property | Value |
| --- | --- |
| **Definition** | Total number of finished pallets completed by the palletizing station |
| **Formula** | `LoadedPalletCount = count of pallet exit events` |
| **PLC tag** | `LoadedPalletCount` |
| **Source** | Counter in OB1, incremented on each pallet completion |
| **Dashboard** | Both |

### 3. Sorted Count

| Property | Value |
| --- | --- |
| **Definition** | Total number of items sorted by the color sorting station |
| **Formula** | `SortedCount = count of sorted items` |
| **PLC tag** | `SortedCount` |
| **Source** | Counter updated at Station 1 sorting event |
| **Dashboard** | Grafana |

### 4. Sort Rate

| Property | Value |
| --- | --- |
| **Definition** | Percentage of items that were correctly sorted |
| **Formula** | `SortRate = (SortedCount / ProductionCount) × 100` |
| **PLC tag** | `SortRate` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Grafana |

**Example.** 100 items produced, 95 sorted correctly → `SortRate = 95%`.

### 5. Cycle Time

| Property | Value |
| --- | --- |
| **Definition** | Time between two consecutive item completions, in milliseconds |
| **Formula** | `CycleTime = CurrentTimeIn − LastItemTime` when `CycleCount` increments |
| **PLC tag** | `DB50_KPIs.CycleTime` |
| **Computation** | Inside `FC50_KPIs`, with edge detection on `CycleCount` |
| **Dashboard** | Grafana |

### 6. Throughput

| Property | Value |
| --- | --- |
| **Definition** | Number of items produced per minute |
| **Formula** | `Throughput = 60000 / CycleTime` |
| **PLC tag** | `DB50_KPIs.Throughput` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Grafana |

**Example.** Cycle time = 20 000 ms → `Throughput = 3 items/min`.

### 7. Availability

| Property | Value |
| --- | --- |
| **Definition** | Percentage of planned production time that the line was actually running |
| **Formula** | `Availability = (RunTime / PlannedTime) × 100` |
| **PLC tags** | `TotalRunTime` (numerator), `ShiftPlannedTime` (denominator) |
| **PLC tag (result)** | `DB50_KPIs.Availability` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Both |

**Example.** 6 hours run out of an 8-hour shift → `Availability = 75%`.

### 8. Performance

| Property | Value |
| --- | --- |
| **Definition** | How fast the line is running compared to its ideal speed |
| **Formula** | `Performance = (ActualRate / IdealRate) × 100` where `ActualRate = 1 / CycleTime` |
| **PLC tags** | `IdealRate` (setpoint), `CycleTime` (computed) |
| **PLC tag (result)** | `DB50_KPIs.Performance` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Both |

**Example.** Ideal rate = 2.5 items/s, actual = 2.0 items/s → `Performance = 80%`.

### 9. Yield

| Property | Value |
| --- | --- |
| **Definition** | Percentage of items that were not sorted out (good items ratio) |
| **Formula** | `Yield = (ProductionCount − SortedCount) / ProductionCount × 100` |
| **PLC tag** | `DB50_KPIs.Yield` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Both |

**Example.** 100 produced, 5 sorted out → `Yield = 95%`.

### 10. OEE

| Property | Value |
| --- | --- |
| **Definition** | Overall Equipment Effectiveness — single number combining Availability, Performance, and Quality/Yield |
| **Formula** | `OEE = (Availability × Performance × Yield) / 10000` |
| **PLC tag** | `DB50_KPIs.OEE` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Both |

**Example.** 75% × 80% × 95% ÷ 10 000 = 57%.

### 11. Active Alarms

| Property | Value |
| --- | --- |
| **Definition** | Number of alarms currently active on the line |
| **Formula** | `ActiveAlarms = count of TRUE alarm flags` |
| **PLC tags** | `Alarm_EStop`, `Alarm_Fault`, `Alarm_LowProduction`, `Alarm_HighReject`, `Alarm_S1_BeltJam`, `Alarm_S2_GripperFault`, `Alarm_S3_ElevatorFault`, `Alarm_S3_PalletFull` |
| **PLC tag (result)** | `DB50_KPIs.ActiveAlarms` |
| **Computation** | Inside `FC50_KPIs` — sums all active alarm flags |
| **Dashboard** | Grafana |

### 12. Downtime

| Property | Value |
| --- | --- |
| **Definition** | Total time the line was not running, in seconds |
| **Formula** | `Downtime = accumulated seconds while DowntimeEnable is TRUE` |
| **PLC tag** | `TotalDowntime` |
| **Source** | TON timer `Ton_TotalDowntime` in OB1 |
| **PLC tag (result)** | `DB50_KPIs.Downtime` |
| **Dashboard** | Power BI |

### 13. Status

| Property | Value |
| --- | --- |
| **Definition** | Line state code |
| **Formula** | `Status = 2 if E-Stop, 1 if alarm active, 0 otherwise` |
| **PLC tag** | `DB50_KPIs.Status` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Both |

| Code | Meaning |
| --- | --- |
| 0 | Normal operation |
| 1 | Fault active |
| 2 | E-Stop active |

### 14. Timestamp

| Property | Value |
| --- | --- |
| **Definition** | Current PLC time |
| **Formula** | PLC system clock |
| **PLC tag** | `DB50_KPIs.Timestamp` |
| **Computation** | Inside `FC50_KPIs` |
| **Dashboard** | Both |

### 15. MTBF & MTTR (`DB50_KPIs.MTBF`, `DB50_KPIs.MTTR`)
- **MTBF (Mean Time Between Failures):** Cumulative operating time divided by discrete rising-edge failure count.
- **MTTR (Mean Time To Repair):** Cumulative downtime divided by discrete rising-edge failure count.

---

## Supervised Watchdog Alarms

| Alarm Tag | Station | Trigger Condition |
| --- | --- | --- |
| `HighSort` (`Alarm_HighSort`) | Station 1 | Sorting diversion rate exceeds normal threshold |
| `S2_GripperFault` (`Alarm_S2_GripperFault`) | Station 2 | Step watchdog expires when a crooked box blocks the vacuum gripper mid-cycle; forces `Throughput := 0.0` |
| `Alarm_S3_PalletMisfeed` | Station 3 | 6-second `TON` watchdog expires if pallet fails to reach positive seating sensor `%I2.1` (`"DI_S3_PalletLoaded"`) inside `S3_Palletizer` |
| `Alarm_EStop` | Line-Wide | Physical Emergency Stop activated (`Status = 2`) |
| `Alarm_LowProduction` | Line-Wide | Throughput drops below target threshold |

---

## Dashboard Mapping

| KPI / Diagnostic | Ignition SCADA | Grafana (1s Refresh) | Power BI (60s Refresh) |
| --- | --- | --- | --- |
| OEE, Availability, Performance, Yield | KPI Screen gauges | Gauges + trend lines | Shift Overview & Weekly Benchmark |
| Cycle Time & Throughput | KPI Screen | Real-time line trend | Shift averages |
| Production & Loaded Pallet Counts | Synoptic counters | Stat panels | Planned vs. Actual bar charts |
| MTBF & MTTR | — | Reliability stat panels | Shift reliability summary |
| Active Fault State & Chronology | 3-state synoptic + Alarm table | `Alarm Chronology & State` (State Timeline) | Downtime minutes lost |
| Fault Frequency | Alarm history | `Shift Fault Occurrences` (Pareto bar chart) | Quality & downtime breakdown |

---

## OPC-UA Exposure

All `DB50_KPIs` fields and boolean alarm bits (23 tags total) are exposed via the S7-1500 OPC-UA server on port `4840` under namespace `ns=4` (e.g., `ns=4;s="DB50_KPIs"."OEE"`).

---

## Testing Checklist

1. [x] All input tags exist in the S7-1500 PLC tag table with `Retain` enabled on shift accumulators.
2. [x] `DB50_KPIs` compiles and exposes all 23 tags via the OPC-UA server (`ns=4`, port `4840`).
3. [x] `FC50_KPIs` executes in `OB1` with division-by-zero guards on `PlannedTime` and `Shift_Failure_Count`.
4. [x] Pressing the control panel fault reset (`#Button_FaultReset`) clears active faults without resetting `OEE` or `Availability`.
5. [x] Jamming the Station 2 gripper raises `S2_GripperFault` and forces `DB50_KPIs.Throughput` to `0.0` instead of holding the last `7.81 s` cycle value.