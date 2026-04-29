# 🌐 Network Traffic Monitor (Pro)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UI: PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)

A high-performance Windows desktop application for real-time network analysis, process-level traffic monitoring, and intelligent firewall management.

---

## ✨ Key Features

- **🚀 Real-time Analytics**: High-frequency monitoring of inbound and outbound traffic with **Asynchronous Multithreading** for zero UI lag.
- **📊 Dynamic Visualization**: Live Matplotlib charts integrated into a sleek PyQt6 dark-themed interface.
- **🛡️ Intelligent Firewall Control**: 
  - **Single-Click Block**: Instantly restrict network access for any process via Windows Firewall.
  - **Auto-Sync Engine**: Two-way synchronization between local registry and OS firewall rules.
  - **Orphan Cleanup**: Automatically identifies and removes "ghost" firewall rules.
- **📥 System Tray Background Execution**: Minimize to tray to keep the monitor running silently in the background.
- **⚙️ Process Management**: Terminate unresponsive or bandwidth-heavy apps directly from the dashboard.
- **🧪 Automated Stability**: Built-in unit testing suite using `pytest` to ensure core logical integrity.
- **📝 Persistent State**: Remembers your security configurations across system reboots.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **GUI Framework** | PyQt6 (with QThread & QSystemTrayIcon) |
| **System Info** | psutil |
| **Data Viz** | Matplotlib (Qt6 Backend) |
| **Testing** | pytest |
| **Security Layer** | Windows Advanced Firewall (Safe netsh execution) |

---

## 🚀 Installation & Setup

### Automated (Recommended)
Simply run the included batch file to set up the environment and launch:
```powershell
.\run.bat
```

### Manual Installation
1. **Prepare Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch Application**:
   ```bash
   python main.py
   ```

> [!IMPORTANT]
> **Administrative Privileges** are required for the Blocking/Unblocking features to interact with the Windows Firewall.

---

## 📂 Architecture Overview

- `main.py`: Application entry point and initialization logic.
- `network_monitor.py`: Core logic for packet statistics and firewall synchronization.
- `ui.py`: Custom-styled PyQt6 dashboard and charting engine.
- `config.py`: Configuration management (intervals, logging, etc).
- `blocked_processes.json`: Encrypted/structured local state for persistent security.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve performance or add new features.

## 📝 License

Distributed under the **MIT License**. See `LICENSE` for more information.
