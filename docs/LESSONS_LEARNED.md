# Lessons Learned — SmartLine 360

Fill this in progressively (after each milestone), not just at the end — it's
far easier to capture a lesson while it's fresh, and it gives you real
material for interview answers instead of a rushed writeup on the last day.

## How to use this file
After each milestone in `TIMELINE.md`, add an entry below. At project
closure, write the summary section at the bottom.

---

## M1 — OT Foundation
- **What went well:**
- **What went wrong / took longer than expected:**
- **What I'd do differently:**
- **Technical learning worth remembering:**

## M2 — SCADA & Integration
- **What went well:**
- **What went wrong / took longer than expected:**
- **What I'd do differently:**
- **Technical learning worth remembering:**

## M3 — IT/Data Pipeline
- **What went well:**
- **What went wrong / took longer than expected:**
- **What I'd do differently:**
- **Technical learning worth remembering:** 
  - **Architectural Decoupling:** Connecting IT applications directly to the PLC risks overloading the OT network. Using a middle messaging layer protects the physical production line from heavy IT queries.
  - **MQTT (The Environment):** Serves as a lightweight edge "bulletin board" ideal for constrained industrial networks. It allows the architecture to bypass the PLC for non-control IIoT data.
  - **Node-RED (The Worker):** Acts as the active edge gateway. It translates heavy OPC-UA polling into IT-friendly JSON, computes edge logic (like OEE), and bridges the gap by pushing local MQTT data to the enterprise Kafka stream.
  - **Broker Bridging:** MQTT and Kafka cannot talk directly because they are both passive brokers using different protocols. Node-RED is required as the active client to read from MQTT and act as a producer to push data to Kafka.

## M4 — Visualization & Closure
- **What went well:**
- **What went wrong / took longer than expected:**
- **What I'd do differently:**
- **Technical learning worth remembering:**

---

## Project Summary (write this last)

**What went well overall:**


**What went wrong overall:**


**What I would do differently if starting over:**


**Biggest technical skill gained:**


**Biggest project-management skill gained:**


**One-paragraph pitch for interviews**
_(Write a 3-5 sentence summary you could say out loud when asked "tell me
about a complex project you managed." Use the PM vocabulary table below.)_

---

## PM vocabulary cheat-sheet (for interview answers)

| Instead of saying... | Say this |
| --- | --- |
| "I did this project." | "I initiated and executed this project." |
| "I used TIA Portal." | "I managed the OT control layer using TIA Portal." |
| "I had a problem with Docker." | "I mitigated a risk by using Docker volumes for data persistence." |
| "I finished it in 6 weeks." | "I delivered the project on schedule by prioritizing core features." |
| "I put it on GitHub." | "I created a comprehensive handover package including full documentation and setup guides." |
