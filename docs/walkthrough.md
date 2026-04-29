# Walkthrough - Network Traffic Monitor and Manager

I have successfully developed the "Network Traffic Monitor and Manager" application. The implementation follows professional standards, using a virtual environment and a modular code architecture.

## Changes Made
- **[network_monitor.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/network_monitor.py)**: Core logic for real-time per-process traffic monitoring and Windows-based blocking/limiting. Now includes **JSON persistence** (blocked_processes.json) to remember blocked apps after restart.
- **[ui.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/ui.py)**: A dark-themed, professional PyQt6 GUI with real-time Matplotlib charts. Integrated logging for all user interactions (button clicks, process termination, etc.).
- **[utils.py](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/utils.py)**: Enhanced with a professional logging system featuring `RotatingFileHandler` (5MB limit, 5 backups) and dual output (file + console).
- **Documentation**: All planning and task documents are saved in the `[docs/](file:///c:/Users/nout.plus/Desktop/Proyekt/net_monitoring/docs/)` folder within the project for future reference.

## Verification Results
- **Core Logic**: Verified using `test_logic.py`. The monitor successfully identifies network-active processes and calculates their throughput accurately.
- **Logging**: Verified by checking `network_monitor.log`. All actions and background scans are recorded with timestamps.
- **Safety**: Administrative privileges are correctly handled and logged.

## How to Run
1. Open a terminal as **Administrator**.
2. Navigate to: `c:\Users\nout.plus\Desktop\Proyekt\net_monitoring`.
3. Install dependencies (if not done yet):
   ```powershell
   .\venv\Scripts\python.exe -m pip install psutil PyQt6 matplotlib
   ```
4. Run the application:
   ```powershell
   .\venv\Scripts\python.exe main.py
   ```

> [!NOTE]
> Detailed records of the application's activity can be found in `network_monitor.log`. This is extremely useful for debugging and tracking usage.
