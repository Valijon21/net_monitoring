import pytest
from unittest.mock import MagicMock, patch
from network_monitor import NetworkMonitor
from utils import format_speed

def test_format_speed():
    assert format_speed(500) == "500.00 B/s"
    assert format_speed(1500) == "1.46 KB/s"
    assert format_speed(1500 * 1024) == "1.46 MB/s"

def test_load_blocked_empty():
    with patch("os.path.exists", return_value=False):
        monitor = NetworkMonitor()
        assert monitor.blocked_processes == {}

@patch("subprocess.run")
def test_unblock_by_exe(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    monitor = NetworkMonitor()
    monitor.blocked_processes = {"C:\\test.exe": {"name": "test.exe", "rule_name": "Rule1"}}
    
    with patch("network_monitor.is_admin", return_value=True):
        with patch.object(monitor, "_save_blocked"):
            res = monitor.unblock_by_exe("C:\\test.exe")
            assert res is True
            assert "C:\\test.exe" not in monitor.blocked_processes
            mock_run.assert_called()

def test_sync_with_firewall_no_admin():
    with patch("network_monitor.is_admin", return_value=False):
        monitor = NetworkMonitor()
        with patch("logging.warning") as mock_log:
            monitor._sync_with_firewall()
            mock_log.assert_called_with("Skipping firewall sync: Admin privileges required")
