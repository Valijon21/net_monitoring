# Network Traffic Monitor

A professional Windows-based desktop application for real-time network traffic monitoring and process control. Built with Python and PyQt6, it allows users to monitor data usage, visualize traffic patterns, and manage network access for individual processes.

## 🚀 Features

- **Real-time Monitoring**: Track sent and received data rates globally and per-process.
- **Visual Analytics**: Dynamic charts showing network traffic history using Matplotlib.
- **Process Management**: 
  - **Block/Unblock**: Use Windows Firewall (`netsh`) to restrict network access for specific applications.
  - **Terminate**: Close processes directly from the UI.
- **Persistent Blocking**: Remembers blocked processes across sessions.
- **Professional UI**: Dark-themed, responsive interface built with PyQt6.

## 🛠️ Tech Stack

- **Python 3.10+**
- **PyQt6**: Core GUI framework.
- **psutil**: For retrieving network and system process information.
- **Matplotlib**: For real-time traffic visualization.
- **Windows Firewall (netsh)**: For application-level network blocking.

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Valijon21/net_monitoring.git
   cd net_monitoring
   ```

2. **Run the setup script**:
   The easiest way is to run the provided batch file:
   ```bash
   run.bat
   ```
   *Note: This script will create a virtual environment, install dependencies, and start the application.*

3. **Manual Setup**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   pip install -r requirements.txt
   python main.py
   ```

## ⚠️ Requirements

- **Admin Privileges**: Required for blocking/unblocking processes via the Windows Firewall.
- **Windows OS**: The blocking feature specifically utilizes Windows-native commands.

## 📂 Project Structure

- `main.py`: Entry point for the application.
- `network_monitor.py`: Core logic for data extraction and firewall management.
- `ui.py`: PyQt6 UI implementation and chart rendering.
- `utils.py`: Helper functions (logging, admin check, formatting).
- `config.py`: Global configuration parameters.

## 📝 License

This project is open-source and available under the MIT License.
