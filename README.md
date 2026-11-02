# Enterprise IP CCTV Surveillance & NVR Storage Engine

[![Live Demo](https://img.shields.io/badge/Demo-Live%20NOC%20Dashboard-06b6d4)](https://mhmithun.github.io/Enterprise-CCTV-Surveillance-NVR-Engine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Audit Compliance](https://img.shields.io/badge/Compliance-RSC%20%7C%20WRAP%2030--Day-green.svg)](#compliance-auditing)

Enterprise multi-channel IP CCTV surveillance topology design, H.265+ storage & RAID 5 dimensioning engine, and automated RTSP stream dropout monitoring daemon engineered for large-scale manufacturing facilities, industrial campuses, and corporate headquarters.

---

## 📸 Architecture & Live Web Dashboard

The project includes an **interactive NOC CCTV Command Dashboard** (`index.html`) demonstrating:
- **4-Channel Live Camera HUD**: Stream timecodes, resolution presets, live bitrate, and recording status.
- **RTSP Stream Drop Simulator**: Real-time heartbeat detection, video loss detection, and instant incident logging.
- **Interactive NVR Storage & RAID 5 Calculator**: Dynamically balances camera channels, retention days, codec savings (H.265+ vs H.264), and calculates required 8TB enterprise drives with fault-tolerant parity.

---

## 🛠️ Key Capabilities & Technical Features

1. **RTSP Stream Drop Monitoring Daemon (`cctv_core/stream_monitor_daemon.py`)**:
   - Asynchronous TCP socket handshake polling on RTSP port 554 across all camera channels.
   - Measures network round-trip latency and detects packet loss.
   - Automatically raises incident alerts on consecutive dropouts and sends Telegram webhook notifications.

2. **Industrial Storage & RAID 5 Dimensioning Engine (`cctv_core/storage_calculator.py`)**:
   - Math model calculating raw and effective storage based on resolution (1080p, 4MP, 4K) and codec efficiency.
   - Computes drive redundancy for RAID 5 (N+1) and RAID 6 (N+2) disk arrays using 8TB enterprise drives.
   - Validates Accord/RSC and WRAP audit compliance (30-day continuous recording retention).

3. **ONVIF Profile S/G Device Discovery (`cctv_core/onvif_discovery.py`)**:
   - Implements WS-Discovery UDP multicast (239.255.255.250:3702) probe to discover Hikvision, Dahua, Uniview, and Axis IP cameras.
   - Fetches RTSP media profiles and stream parameters automatically.

---

## 🚀 Quick Start

### 1. Run the Interactive Web Dashboard
Simply open `index.html` in any web browser, or launch with Python:
```bash
python -m http.server 8080
# Open http://localhost:8080 in your browser
```

### 2. Run the Python Health Monitoring Daemon
```bash
# Clone the repository
git clone https://github.com/MHMITHUN/Enterprise-CCTV-Surveillance-NVR-Engine.git
cd Enterprise-CCTV-Surveillance-NVR-Engine

# Run the storage calculator CLI
python cctv_core/storage_calculator.py

# Run the stream monitor daemon
python cctv_core/stream_monitor_daemon.py

# Run ONVIF subnet camera discovery
python cctv_core/onvif_discovery.py
```

---

## 📊 Industrial Compliance & Audit Standards

In the RMG and manufacturing export sector, international buyers and safety regulators enforce strict surveillance guidelines:
- **Accord / RSC (RMG Sustainability Council)**: Mandatory 30-day continuous video retention across all factory entry/exit gates, emergency stairs, and perimeter security.
- **WRAP (Worldwide Responsible Accredited Production)**: Zero blind spots in finished goods storage and shipping loading docks.
- **SEDEX / C-TPAT Compliance**: Tamper-evident NVR storage lockdown and restricted access server racks.

This project delivers 100% compliance automation for these audit benchmarks.

---

## 📄 License & Maintainer

Maintained by **[MD. Mahamudul Hasan](https://github.com/MHMITHUN)**  
- GitHub: [@MHMITHUN](https://github.com/MHMITHUN)  
- LinkedIn: [linkedin.com/in/mahamudul0](https://linkedin.com/in/mahamudul0)  
- Email: mhmmithun1@gmail.com  

Released under the [MIT License](LICENSE).
