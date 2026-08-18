# Setup — SmartLine 360

Step-by-step install guide, in the order you'll actually need each tool
(matches the M1 → M4 milestone order in `WORK_BREAKDOWN_STRUCTURE.md`).

## Prerequisites

| Requirement | Notes |
| --- | --- |
| OS | Windows 10/11 (TIA Portal and Factory I/O are Windows-only) |
| RAM | 16 GB minimum — see `TROUBLESHOOTING.md` for managing memory pressure |
| Disk space | ~40 GB free (TIA Portal alone is sizeable) |
| Admin rights | Needed for installers and Docker |
| Internet | Needed for trial activations and Docker image pulls |

---

## M1 — OT Foundation

### 1. Factory I/O
1. Download the installer from the official Factory I/O website.
2. Install and start the **30-day trial** (no credit card needed for the trial tier at time of writing — confirm current terms on their site, they do change).
3. Note your trial start date in `docs/RISK_REGISTER.md` (R6) so you can track the clock.

### 2. TIA Portal (V18 or later) + S7-PLCSIM
1. Requires a Siemens account (free to create) to download the trial.
2. Install **TIA Portal** and, separately, **PLCSIM** (or PLCSIM Advanced if you want richer simulation features) — these are usually bundled in the same installer package.
3. Verify by opening TIA Portal, creating a blank project, and confirming you can add an S7-1200 CPU (e.g. CPU 1214C).

### 3. Connect Factory I/O ↔ PLCSIM
- No separate install — this is a driver configuration inside Factory I/O (**File → Driver Configuration → Siemens S7-1200/1500**). Covered in detail in the Factory I/O scene guide.

---

## M2 — SCADA & Integration

### 4. Ignition
1. Download Ignition from Inductive Automation (free trial, resets every 2 hours unless licensed — fine for development, just save your work often).
2. Install, then open the Gateway web page (`http://localhost:8088` by default) to create a new project.
3. Add an OPC-UA connection pointing at your S7-1200's OPC-UA server endpoint (enabled in TIA Portal under the CPU's protection & security / OPC UA settings).

---

## M3 — IT/Data Pipeline

### 5. Docker Desktop
1. Install Docker Desktop for Windows (enable WSL2 backend if prompted — it's faster).
2. Verify with `docker --version` and `docker compose version` in a terminal.

### 6. Kafka/Redpanda + InfluxDB + Grafana (via Docker Compose)
1. All three run from a single `docker/docker-compose.yml` you'll write in M3 (see `DEPLOYMENT.md` for the compose file and startup order).
2. No manual installs beyond Docker itself — everything runs in containers.

### 7. Node-RED
1. Install Node.js LTS first (Node-RED requires it).
2. Install Node-RED globally: `npm install -g --unsafe-perm node-red`
3. Install the OPC-UA and Kafka community nodes from inside the Node-RED palette manager:
   - `node-red-contrib-opcua`
   - `node-red-contrib-kafka` (or the specific Kafka node you settle on)
4. Start with `node-red` and open `http://localhost:1880`.

---

## M4 — Visualization & Closure

### 8. Power BI Desktop
1. Free download from Microsoft.
2. Install a connector/driver for InfluxDB if querying directly (InfluxDB's Flux SQL-like query support, or an ODBC bridge) — confirm current recommended method on InfluxDB's docs since this changes between versions.

### 9. Python + FastAPI (optional ML layer)
1. Install Python 3.11+.
2. `pip install fastapi uvicorn scikit-learn pandas influxdb-client`
3. Confirmed working: `uvicorn main:app --reload` serves your API locally for Power BI to query.

---

## Verifying your setup

Run through this checklist once everything above is installed:

- [ ] Factory I/O opens and an empty scene can be created
- [ ] TIA Portal opens and a blank S7-1200 project can be created
- [ ] PLCSIM launches and can be linked to a TIA Portal project
- [ ] Ignition Gateway page loads at `localhost:8088`
- [ ] `docker compose up` (with a placeholder compose file) starts without errors
- [ ] Node-RED loads at `localhost:1880` with the OPC-UA and Kafka nodes visible in the palette
- [ ] Power BI Desktop opens
- [ ] `uvicorn` serves a "hello world" FastAPI endpoint

If any of these fail, check `TROUBLESHOOTING.md` before moving on to the next milestone.
