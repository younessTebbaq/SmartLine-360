# KPIs Guide — SmartLine 360

This document defines every KPI in the SmartLine 360 project: what it
means, how it is computed in the PLC, which PLC tag stores it, and where
it appears on the dashboards.

The KPIs are computed by `FC50_KPIs` (SCL) in the S7-1500 PLC program
and stored in the global data block `DB50_KPIs`. They are exposed to
the rest of the stack via the OPC-UA server.

---

## Table of Contents

- [KPI Storage — DB50_KPIs](#kpi-storage--db50_kpis)
- [KPI Computation — FC50_KPIs](#kpi-computation--fc50_kpis)
- [KPI Definitions](#kpi-definitions)
  1. [Production Count](#1-production-count)
  2. [Reject Count](#2-reject-count)
  3. [Reject Rate](#3-reject-rate)
  4. [Cycle Time](#4-cycle-time)
  5. [Throughput](#5-throughput)
  6. [Availability](#6-availability)
  7. [Performance](#7-performance)
  8. [Quality](#8-quality)
  9. [OEE](#9-oee)
  10. [Active Alarms](#10-active-alarms)
  11. [Downtime](#11-downtime)
  12. [Status](#12-status)
  13. [Timestamp](#13-timestamp)
- [Input Tags](#input-tags)
- [Data Flow](#data-flow)
- [Dashboard Mapping](#dashboard-mapping)
- [OPC-UA Exposure](#opc-ua-exposure)
- [Testing Checklist](#testing-checklist)

---

## KPI Storage — DB50_KPIs

All KPIs live in the global data block `DB50_KPIs`.

| Field | Type | Retain | Meaning |
| --- | --- | --- | --- |
| `ProductionCount` | DInt | Yes | Total finished items produced |
| `LoadedPalletCount` | Int | Yes | Total finished pallets at exit |
| `SortedCount` | DInt | No | Number of blue lids sorted out |
| `SortRate` | Real | No | Sort percentage |
| `CycleTime` | Real | No | Time between two consecutive items (ms) |
| `Throughput` | Real | No | Items per minute |
| `Availability` | Real | No | Run time ÷ planned time × 100 |
| `Performance` | Real | No | Actual rate ÷ ideal rate × 100 |
| `Yield` | Real | No | (total − sorted) / total |
| `OEE` | Real | No | Overall Equipment Effectiveness |
| `ActiveAlarms` | Int | No | Number of active alarms |
| `Downtime` | DInt | No | Total downtime in seconds |
| `Status` | Word | No | 0 = OK, 1 = Fault, 2 = E-Stop |
| `Timestamp` | DTL | No | Current PLC time |

**Retain policy.** Counters and accumulated time use `Retain = Yes` so
they survive a PLC power cycle. Computed KPIs use `Retain = No` because
they are recomputed on every scan.

---

## KPI Computation — FC50_KPIs

`FC50_KPIs` is an SCL function block called once per scan from OB1.

| Input parameter | Type | Source |
| --- | --- | --- |
| `CycleCount` | DInt | `Final_Product_Count` — production counter CV |
| `RejectCount` | DInt | `TotalItemsRejected` — reject counter CV |
| `RunTime` | DInt | `TotalRunTime` — run-time TON ET |
| `PlannedTime` | DInt | `ShiftPlannedTime` — setpoint |
| `IdealRate` | Real | `IdealRate` — setpoint |
| `ActiveAlarmCount` | Int | `ActiveAlarmCount` — alarm counter |
| `Downtime` | DInt | `TotalDowntime` — downtime TON ET |
| `EStopActive` | Bool | `EStop` — raw E-Stop input |
| `CurrentTimeIn` | DInt | `CurrentTime` — clock TON ET |

The function writes all computed values to `DB50_KPIs`.

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

---

## Input Tags

These tags must exist in the PLC tag table for `FC50_KPIs` to work:

| Tag | Address | Type | Retain | Purpose |
| --- | --- | --- | --- | --- |
| `TotalItemsRejected` | %QD42 | DInt | Yes | Reject counter CV |
| `TotalRunTime` | %QD46 | DInt | Yes | Run-time TON ET |
| `ShiftPlannedTime` | %MW50 | Int | Yes | Planned production time (s) |
| `IdealRate` | %MD52 | Real | No | Ideal rate (items/s) |
| `ActiveAlarmCount` | %MW56 | Int | No | Active alarm count |
| `TotalDowntime` | %QD58 | DInt | Yes | Downtime TON ET |
| `RejectPulse` | %M2.0 | Bool | No | One-shot on reject event |
| `ProductionPulse` | %M2.1 | Bool | No | One-shot on production event |
| `RunTimeEnable` | %M2.2 | Bool | No | Run-time TON enable |
| `DowntimeEnable` | %M2.3 | Bool | No | Downtime TON enable |
| `LastCycleCount` | %MD60 | DInt | No | Edge detection memory |
| `LastItemTime` | %MD64 | DInt | No | Last item timestamp |
| `CurrentTime` | %MD68 | DInt | No | Clock TON ET |

---

## Data Flow

```
FC2 (Station 2)          FC3 (Station 3)
    │ RejectPulse             │ ProductionPulse
    ▼                         ▼
Cnt_TotalRejected       Cnt_LoadedPallets
    │                         │
    ▼                         ▼
TotalItemsRejected      Final_Product_Count
    │                         │
    └─────────────┬─────────────┘
                  ▼
          FC50_KPIs (SCL)
                  │
                  ▼
          DB50_KPIs (Global DB)
                  │
                  ▼
          OPC-UA Server
                  │
          ┌───────┼───────┐
          ▼       ▼       ▼
      Ignition  Node-RED  InfluxDB
        HMI      → MQTT     → Grafana
                      → Kafka
                      → Power BI
```

---

## Dashboard Mapping

| KPI | Grafana (operational, 1 s) | Power BI (business, 1 min) |
| --- | --- | --- |
| OEE | Gauge + trend line | Trend chart |
| Throughput | Line chart | Line chart |
| Cycle Time | Line chart | — |
| Reject Rate | Line chart | Line chart |
| Availability | Stat panel | Stat panel |
| Performance | Stat panel | Stat panel |
| Quality | Stat panel | Stat panel |
| Production Count | Stat panel | Bar chart |
| Reject Count | Stat panel | Bar chart |
| Downtime | — | Stat panel |
| Active Alarms | Stat panel + alarm list | Stat panel |
| Status | Colored indicator | — |

---

## OPC-UA Exposure

The following `DB50_KPIs` fields are exposed via the S7-1500 OPC-UA
server. The full node path follows the convention
`SmartLine360/KPIs/<FieldName>`:

| OPC-UA Node | PLC Tag | Type |
| --- | --- | --- |
| `SmartLine360/KPIs/ProductionCount` | `DB50_KPIs.ProductionCount` | DInt |
| `SmartLine360/KPIs/RejectCount` | `DB50_KPIs.RejectCount` | DInt |
| `SmartLine360/KPIs/RejectRate` | `DB50_KPIs.RejectRate` | Real |
| `SmartLine360/KPIs/CycleTime` | `DB50_KPIs.CycleTime` | Real |
| `SmartLine360/KPIs/Throughput` | `DB50_KPIs.Throughput` | Real |
| `SmartLine360/KPIs/Availability` | `DB50_KPIs.Availability` | Real |
| `SmartLine360/KPIs/Performance` | `DB50_KPIs.Performance` | Real |
| `SmartLine360/KPIs/Quality` | `DB50_KPIs.Quality` | Real |
| `SmartLine360/KPIs/OEE` | `DB50_KPIs.OEE` | Real |
| `SmartLine360/KPIs/ActiveAlarms` | `DB50_KPIs.ActiveAlarms` | Int |
| `SmartLine360/KPIs/Downtime` | `DB50_KPIs.Downtime` | DInt |
| `SmartLine360/KPIs/Status` | `DB50_KPIs.Status` | Word |
| `SmartLine360/KPIs/Timestamp` | `DB50_KPIs.Timestamp` | DateAndTime |

---

## Testing Checklist

1. [ ] All input tags from the [Input Tags](#input-tags) table exist in the tag table
2. [ ] `DB50_KPIs` is created with all fields and correct retain settings
3. [ ] `FC50_KPIs` compiles with no errors
4. [ ] OB1 calls `FC5