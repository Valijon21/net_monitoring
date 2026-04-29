import sys
import os
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QHeaderView, QLineEdit, QMessageBox)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread
from network_monitor import NetworkMonitor
from config import APP_NAME, REFRESH_INTERVAL
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#2b2b2b')
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e1e')
        self.axes.tick_params(colors='white')
        for spine in self.axes.spines.values():
            spine.set_color('white')
            
        super().__init__(fig)
        self.x_data = list(range(60))
        self.y_sent = [0] * 60
        self.y_recv = [0] * 60
        
    def update_data(self, sent_kb, recv_kb):
        self.y_sent.pop(0)
        self.y_sent.append(sent_kb)
        self.y_recv.pop(0)
        self.y_recv.append(recv_kb)
        
        self.axes.clear()
        self.axes.plot(self.x_data, self.y_sent, label='Sent (KB/s)', color='#00aaff', linewidth=2)
        self.axes.plot(self.x_data, self.y_recv, label='Recv (KB/s)', color='#55ff7f', linewidth=2)
        self.axes.legend(facecolor='#2b2b2b', labelcolor='white')
        self.axes.set_ylim(bottom=0)
        self.draw()

class DataWorker(QThread):
    data_received = pyqtSignal(dict, list) # global_stats, process_stats
    
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                g_stats = self.monitor.get_total_traffic()
                p_stats = self.monitor.get_process_stats()
                self.data_received.emit(g_stats, p_stats)
            except Exception as e:
                logging.error(f"Error in Background DataWorker: {e}")
            self.msleep(REFRESH_INTERVAL)

    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 700)
        self.monitor = NetworkMonitor()
        self.prev_total = self.monitor.get_total_traffic()
        
        self.init_ui()
        self.init_tray()
        self.apply_styles()
        
        # Initialize Background Worker instead of QTimer for polling
        self.worker = DataWorker(self.monitor)
        self.worker.data_received.connect(self.update_ui)
        self.worker.start()

    def init_tray(self):
        # Create Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a default icon or a specific one if available
        # For now, we'll try to find any icon or just use a standard one
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Create Tray Menu
        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.showNormal)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.force_quit)
        
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()

    def force_quit(self):
        self.worker.stop()
        self.worker.wait()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                APP_NAME,
                "Application is still running in the tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()
        else:
            self.force_quit()
            event.accept()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Header
        header_layout = QHBoxLayout()
        self.total_label = QLabel("Total Traffic: Sent: 0 KB/s | Recv: 0 KB/s")
        self.total_label.setObjectName("headerLabel")
        header_layout.addWidget(self.total_label)
        layout.addLayout(header_layout)
        
        # Chart
        self.canvas = ChartCanvas(self, width=8, height=3)
        layout.addWidget(self.canvas)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["PID", "Name", "Speed", "Action", "Control"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setObjectName("processTable")
        layout.addWidget(self.table)
        
        # Footer / Controls
        footer = QHBoxLayout()
        self.status_label = QLabel("Ready")
        footer.addWidget(self.status_label)
        layout.addLayout(footer)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: white; font-size: 14px; }
            #headerLabel { font-size: 18px; font-weight: bold; margin: 10px; }
            QTableWidget { 
                background-color: #2b2b2b; 
                color: white; 
                gridline-color: #444;
                border: none;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                padding: 5px;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton#blockBtn { background-color: #cc3333; }
            QPushButton#blockBtn:hover { background-color: #ff4444; }
            QPushButton#unblockBtn { background-color: #28a745; }
            QPushButton#unblockBtn:hover { background-color: #218838; }
        """)

    def update_ui(self, curr_total, process_stats):
        logging.debug("Updating UI from background worker signals")
        
        # Global stats calculation
        sent_speed = (curr_total['sent'] - self.prev_total['sent']) / (REFRESH_INTERVAL / 1000)
        recv_speed = (curr_total['recv'] - self.prev_total['recv']) / (REFRESH_INTERVAL / 1000)
        self.prev_total = curr_total
        
        self.total_label.setText(f"Total Traffic: Sent: {sent_speed/1024:.2f} KB/s | Recv: {recv_speed/1024:.2f} KB/s")
        self.canvas.update_data(sent_speed/1024, recv_speed/1024)
        
        # Per-process stats
        stats = process_stats
        current_pids = {s['pid']: s for s in stats}
        
        rows_to_remove = []
        for i in range(self.table.rowCount()):
            pid_item = self.table.item(i, 0)
            if pid_item:
                pid = int(pid_item.text())
                if pid in current_pids:
                    s = current_pids[pid]
                    self.table.item(i, 2).setText(s['formatted_speed'])
                    
                    is_blocked = s.get('is_blocked', False)
                    block_btn = self.table.cellWidget(i, 4)
                    if isinstance(block_btn, QPushButton):
                        expected_text = "Unblock" if is_blocked else "Block"
                        if block_btn.text() != expected_text:
                            block_btn.setText(expected_text)
                            block_btn.setObjectName("unblockBtn" if is_blocked else "blockBtn")
                            self.apply_styles()
                            block_btn.clicked.disconnect()
                            block_btn.clicked.connect(lambda checked, p=pid, b=is_blocked: self.handle_block(p, b))

                    del current_pids[pid]
                else:
                    rows_to_remove.append(i)
        
        for row in sorted(rows_to_remove, reverse=True):
            self.table.removeRow(row)
            
        for pid, s in current_pids.items():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(s['pid'])))
            self.table.setItem(i, 1, QTableWidgetItem(s['name']))
            self.table.setItem(i, 2, QTableWidgetItem(s['formatted_speed']))
            
            term_btn = QPushButton("End Process")
            term_btn.clicked.connect(lambda checked, p=s['pid']: self.handle_terminate(p))
            self.table.setCellWidget(i, 3, term_btn)
            
            is_blocked = s.get('is_blocked', False)
            btn_text = "Unblock" if is_blocked else "Block"
            block_btn = QPushButton(btn_text)
            block_btn.setObjectName("unblockBtn" if is_blocked else "blockBtn")
            block_btn.clicked.connect(lambda checked, p=s['pid'], b=is_blocked: self.handle_block(p, b))
            self.table.setCellWidget(i, 4, block_btn)

    def handle_terminate(self, pid):
        logging.info(f"User requested termination of process {pid}")
        if self.monitor.terminate_process(pid):
            self.status_label.setText(f"Terminated process {pid}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to terminate process {pid}")

    def handle_block(self, pid, already_blocked=False):
        if already_blocked:
            if self.monitor.unblock_process(pid):
                self.status_label.setText(f"Unblocked process {pid}")
            else:
                QMessageBox.warning(self, "Error", "Failed to unblock. Ensure Admin privileges.")
        else:
            if self.monitor.block_process(pid):
                self.status_label.setText(f"Blocked process {pid}")
                QMessageBox.information(self, "Success", f"Process {pid} blocked via Firewall.")
            else:
                QMessageBox.warning(self, "Error", "Failed to block. Check Admin privileges.")

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
