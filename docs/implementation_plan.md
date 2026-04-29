# Implementation Plan - Network Traffic Monitor and Manager

This project aims to build a professional-grade Windows application to monitor and manage per-process network traffic in real-time.

## Proposed Changes

### Core Logic
#### [NEW] [network_monitor.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/network_monitor.py)
Responsible for:
- Collecting per-process network I/O stats using `psutil`.
- Calculating real-time upload/download speeds.
- Managing process blocking/termination (using `netsh` or direct process termination).

### UI Layer
#### [NEW] [ui.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/ui.py)
Responsible for:
- Building the PyQt6-based graphical interface.
- Integrating Matplotlib for real-time traffic visualization.
- Handling user interactions (e.g., clicking "End Process" or "Block").

### Integration & Entry Point
#### [NEW] [main.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/main.py)
The main entry point that initializes the backend monitor and the frontend UI, ensuring they communicate efficiently via signals or shared queues.

### Utilities & Config
#### [NEW] [utils.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/utils.py)
Helper functions for formatting (e.g., bytes to MB/s), logging, and system-level checks.

#### [NEW] [config.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/config.py)
Application settings (refresh intervals, UI themes, default units).

## Verification Plan

### Automated Tests
- Unit tests for traffic calculation logic in `network_monitor.py`.
- Mocking `psutil` results to verify speed calculations.

### Manual Verification
- Run the app and compare its reported speed with Task Manager or a browser-based speed test.
- Attempt to block a process (e.g., a browser tab) and verify internet loss for that specific process.
- Monitor system resource usage (RAM/CPU) while the app is running.
