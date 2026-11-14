# Setup — SmartLine 360

Step-by-step installation guide in the order required by the M1 -> M4 milestones.

## Prerequisites

| Requirement | Notes |
| --- | --- |
| OS | Windows 10/11 (TIA Portal, PLCSIM Advanced, and Factory I/O are Windows-only) |
| RAM | 16 GB minimum (BIOS virtualization SVM/VMX and WSL2 enabled for Docker and PLCSIM Advanced) |
| Disk space | ~40 GB free |
| Admin rights | Required for Npcap virtual network adapter and Docker Desktop |

---

## M1 — OT Foundation

### 1. Factory I/O
1. Download and install Factory I/O from the official website.
2. Open the scene inside `factory-io-scenes/` to verify the 3 stations (Infeed & Sorting, Pick-and-Place Gantry, Packaging & Palletizing) load properly.

### 2. TIA Portal V19 + S7-PLCSIM Advanced
1. Install **TIA Portal V19** and **S7-PLCSIM Advanced** (required to expose the S7-1500 OPC-UA server over a virtual network interface).
2. Configure the Windows Virtual Ethernet Adapter:
   - Press `Win + R`, type `ncpa.cpl`, and press Enter.
   - Right-click **Siemens PLCSIM Virtual Ethernet Adapter** -> **Properties** -> **Internet Protocol Version 4 (TCP/IPv4)**.
   - Set Static IP address: `192.168.0.50`, Subnet mask: `255.255.255.0`.
3. Open the TIA Portal project in `plc-programs/` (working backups are stored in `plc-programs.backup/`), verify the S7-1500 CPU IP is `192.168.0.1`, and confirm the OPC-UA server is enabled on port `4840`.

### 3. Connect Factory I/O <-> S7-PLCSIM Advanced
- In Factory I/O, go to **File -> Driver Configuration -> Siemens S7-1200/1500**, set the PLC IP to `192.168.0.1`, and click **Connect**.

---

## M2 — SCADA & Integration

### 4. Ignition 8.x (Perspective)
1. Install Ignition by Inductive Automation and open the Gateway at `http://localhost:8088`.
2. Under **Config -> OPC UA -> Server Connections**, add a connection to `opc.tcp://192.168.0.1:4840`.
3. Import the project from `ignition-projects/` into Ignition Designer to load the 4 HMI screens and tag bindings.
4. *(Optional)* Install **UaExpert** to inspect the `ns=4` namespace and verify all 23 tags directly.

---

## M3 — IT/Data Pipeline

### 5. Docker Desktop (Mosquitto, Redpanda, InfluxDB, Grafana)
1. Install Docker Desktop for Windows with the WSL2 backend enabled.
2. Verify installation:
   ```bash
   docker --version
   docker compose version
   ```
3. All four IT services (`mosquitto`, `redpanda`, `influxdb`, `grafana`) run from `docker/docker-compose.yml` — no standalone database installation required.

### 6. Node-RED (`nod-red-flows/`)
1. Install Node.js LTS, then install Node-RED globally:
   ```bash
   npm install -g --unsafe-perm node-red
   ```
2. Start Node-RED (`node-red`), open `http://localhost:1880`, and install the required palette packages via **Menu -> Manage palette**:
   - `node-red-contrib-opcua`
   - Kafka client package configured for `127.0.0.1:9092`
3. Import the flow JSON from `nod-red-flows/` and click **Deploy**.

### 7. Python Kafka-to-InfluxDB Consumer (`influxdb-consumer.py`)
1. Install Python 3.11+ and required packages:
   ```bash
   pip install kafka-python influxdb-client
   ```
2. Run the consumer script from the root directory:
   ```bash
   python influxdb-consumer.py
   ```

---

## M4 — Visualization & Predictive Maintenance

### 8. Grafana Dashboards (`dashboards/`)
1. Open Grafana at `http://localhost:3000` (`admin` / `smartline`).
2. Import the dashboard JSON model from `dashboards/`.

### 9. Power BI Desktop (`power-bi/`)
1. Install Microsoft Power BI Desktop.
2. Open the `.pbix` report inside `power-bi/` and refresh the data connection.

---

## Setup Verification Checklist

- [x] Static IP `192.168.0.50` is set on the Siemens PLCSIM Virtual Ethernet Adapter
- [x] S7-PLCSIM Advanced boots the S7-1500 instance at `192.168.0.1`
- [x] Factory I/O connects with a green driver indicator
- [x] UaExpert and Ignition browse `ns=4` on `opc.tcp://192.168.0.1:4840`
- [x] `docker compose up -d` starts Mosquitto (`1883`), Redpanda (`9092`), InfluxDB (`8086`), and Grafana (`3000`)
- [x] Node-RED connects to OPC-UA, Mosquitto, and Redpanda (`127.0.0.1:9092`)
- [x] `influxdb-consumer.py` writes `production-events` messages into InfluxDB (`smartline_kpis`)