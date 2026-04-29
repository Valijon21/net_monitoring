import psutil
import time
import subprocess
import logging
import json
import os
from utils import format_speed, is_admin

class NetworkMonitor:
    def __init__(self):
        self.prev_io = {}
        self.process_stats = {}
        self.blocked_file = os.path.join(os.path.dirname(__file__), "blocked_processes.json")
        self.blocked_processes = self._load_blocked() # exe_path -> {'name': name, 'rule_name': rule_name}
        self._sync_with_firewall()

    def get_process_stats(self):
        logging.debug("Starting process network scan cycle")
        stats = []
        # Get all network connections first to filter processes that are actually using the network
        network_pids = set()
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.pid:
                    network_pids.add(conn.pid)
        except psutil.AccessDenied:
            logging.warning("Access denied while fetching net_connections")
            pass

        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                pid = proc.info['pid']
                if network_pids and pid not in network_pids:
                    continue
                
                name = proc.info['name']
                io = proc.io_counters()
                
                curr_io = io.read_bytes + io.write_bytes
                if pid in self.prev_io:
                    speed = curr_io - self.prev_io[pid]
                else:
                    speed = 0
                
                self.prev_io[pid] = curr_io
                
                if speed > 0 or pid in self.process_stats:
                    stats.append({
                        'pid': pid,
                        'name': name,
                        'exe': proc.info['exe'],
                        'speed': speed,
                        'formatted_speed': format_speed(speed)
                    })
                    self.process_stats[pid] = speed
                elif pid in self.process_stats:
                     del self.process_stats[pid]

            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        
        # Add blocked processes that might not have active connections anymore
        for exe_path, info in self.blocked_processes.items():
            # Find if this exe is currently running to get its PID
            running_pid = None
            for proc in psutil.process_iter(['pid', 'exe']):
                try:
                    if proc.info['exe'] == exe_path:
                        running_pid = proc.info['pid']
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if running_pid:
                # If it's already in stats, mark it as blocked
                found = False
                for s in stats:
                    if s['pid'] == running_pid:
                        s['is_blocked'] = True
                        s['formatted_speed'] = "BLOCKED"
                        s['speed'] = 0
                        found = True
                        break
                
                if not found:
                    stats.append({
                        'pid': running_pid,
                        'name': info['name'],
                        'exe': exe_path,
                        'speed': 0,
                        'formatted_speed': "BLOCKED",
                        'is_blocked': True
                    })

        stats.sort(key=lambda x: x['pid']) # Sort by PID for UI stability
        return stats

    def get_total_traffic(self):
        net_io = psutil.net_io_counters()
        return {
            'sent': net_io.bytes_sent,
            'recv': net_io.bytes_recv,
            'total': net_io.bytes_sent + net_io.bytes_recv
        }

    def _load_blocked(self):
        if os.path.exists(self.blocked_file):
            try:
                with open(self.blocked_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load blocked processes: {e}")
        return {}

    def _save_blocked(self):
        try:
            with open(self.blocked_file, 'w') as f:
                json.dump(self.blocked_processes, f, indent=4)
            logging.debug(f"Saved blocked processes to {self.blocked_file}")
        except Exception as e:
            logging.error(f"Failed to save blocked processes: {e}")

    def _sync_with_firewall(self):
        # Optional: verify if rules in JSON still exist in Firewall
        # and if Firewall has rules not in JSON
        logging.info("Syncing with Windows Firewall rules...")
        try:
            output = subprocess.check_output('netsh advfirewall firewall show rule name=all', shell=True).decode('cp1252', errors='ignore')
            # Look for rules starting with Block- or NetMonitor-
            # Actually, let's stick to our JSON as source of truth for now but clean up
            pass
        except:
            pass

    def block_process(self, pid):
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            name = proc.name()
            rule_name = f"NetMonitor_Block_{name}"
            # netsh command to block outbound traffic for this exe
            cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=out action=block program="{exe_path}" enable=yes'
            if is_admin():
                 subprocess.run(cmd, shell=True, check=True)
                 self.blocked_processes[exe_path] = {'name': name, 'rule_name': rule_name}
                 self._save_blocked()
                 logging.info(f"Blocked process {name} via netsh (Rule: {rule_name})")
                 return True
            else:
                 logging.warning(f"Admin privileges required to block {name}")
                 return False
        except Exception as e:
            logging.error(f"Failed to block process {pid}: {e}")
            return False

    def unblock_process(self, pid):
        try:
            # Find the exe_path for this PID
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            return self.unblock_by_exe(exe_path)
        except Exception as e:
            logging.debug(f"Process {pid} not found for unblocking, trying fallback unblock")
            # If PID is gone, we might still have it in self.blocked_processes
            # But we don't know which exe_path it was from just the PID if it's gone
            return False

    def unblock_by_exe(self, exe_path):
        try:
            if exe_path in self.blocked_processes:
                info = self.blocked_processes[exe_path]
                rule_name = info['rule_name']
                cmd = f'netsh advfirewall firewall delete rule name="{rule_name}"'
                if is_admin():
                    subprocess.run(cmd, shell=True, check=True)
                    del self.blocked_processes[exe_path]
                    self._save_blocked()
                    logging.info(f"Unblocked process {exe_path} (Rule: {rule_name})")
                    return True
                else:
                    logging.warning(f"Admin privileges required to unblock {exe_path}")
            return False
        except Exception as e:
            logging.error(f"Failed to unblock process by exe {exe_path}: {e}")
            return False

    def unblock_all(self):
        # Helper to clean up rules created by this app
        if is_admin():
             for pid, info in list(self.blocked_processes.items()):
                 self.unblock_process(pid)

    def terminate_process(self, pid):
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            logging.info(f"Terminated process {pid}")
            return True
        except Exception as e:
            logging.error(f"Failed to terminate process {pid}: {e}")
            return False
