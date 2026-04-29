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
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            except Exception as e:
                logging.error(f"Failed to load blocked processes: {e}")
        return {}

    def _save_blocked(self):
        try:
            with open(self.blocked_file, 'w') as f:
                json.dump(self.blocked_processes, f, indent=4)
            logging.debug(f"Saved blocked processes state to {self.blocked_file}")
        except Exception as e:
            logging.error(f"Failed to save blocked processes: {e}")

    def _sync_with_firewall(self):
        """
        Professional two-way sync between JSON state and Windows Firewall.
        1. Removes 'ghost' rules from Firewall that aren't in JSON.
        2. Restores missing rules in Firewall that are in JSON.
        """
        if not is_admin():
            logging.warning("Skipping firewall sync: Admin privileges required")
            return

        logging.info("Starting professional Firewall-State synchronization...")
        
        # 1. Get all firewall rules created by this app
        try:
            # We use CP1252 for Windows terminal output usually
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                capture_output=True,
                text=True,
                encoding='cp1252',
                errors='ignore'
            )
            output = result.stdout
            
            existing_firewall_rules = []
            for line in output.splitlines():
                if "Rule Name:" in line and "NetMonitor_Block_" in line:
                    rule_name = line.split("Rule Name:")[1].strip()
                    existing_firewall_rules.append(rule_name)
                    
            logging.debug(f"Found {len(existing_firewall_rules)} existing NetMonitor rules in Firewall")
        except Exception as e:
            logging.error(f"Failed to query firewall rules: {e}")
            existing_firewall_rules = []

        # 2. Identify rules to cleanup (In Firewall but NOT in JSON)
        json_rule_names = {info['rule_name'] for info in self.blocked_processes.values()}
        for fw_rule in existing_firewall_rules:
            if fw_rule not in json_rule_names:
                logging.info(f"Sync Cleanup: Removing orphaned firewall rule {fw_rule}")
                subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name={fw_rule}'], capture_output=True)

        # 3. Identify rules to restore (In JSON but NOT in Firewall)
        firewall_rule_set = set(existing_firewall_rules)
        for exe_path, info in self.blocked_processes.items():
            if info['rule_name'] not in firewall_rule_set:
                logging.info(f"Sync Restore: Re-applying missing firewall rule for {info['name']}")
                cmd = [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name={info["rule_name"]}', 'dir=out', 'action=block',
                    f'program={exe_path}', 'enable=yes'
                ]
                subprocess.run(cmd, capture_output=True)

        logging.info("Firewall synchronization complete")

    def block_process(self, pid):
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            name = proc.name()
            
            if exe_path in self.blocked_processes:
                logging.info(f"Process {name} is already documented as blocked")
                return True

            rule_name = f"NetMonitor_Block_{name}"
            cmd = [
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={rule_name}', 'dir=out', 'action=block',
                f'program={exe_path}', 'enable=yes'
            ]
            
            if is_admin():
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='cp1252')
                if result.returncode == 0:
                    self.blocked_processes[exe_path] = {'name': name, 'rule_name': rule_name}
                    self._save_blocked()
                    logging.info(f"Successfully blocked {name} (Path: {exe_path})")
                    return True
                else:
                    logging.error(f"Firewall command failed: {result.stderr}")
                    return False
            else:
                logging.warning(f"Admin privileges required to block {name}")
                return False
        except Exception as e:
            logging.error(f"Exception during block_process for PID {pid}: {e}")
            return False

    def unblock_process(self, pid):
        """Unblock a process by its PID (if it's currently running)"""
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            return self.unblock_by_exe(exe_path)
        except Exception as e:
            logging.debug(f"PID {pid} not found/accessible for unblocking: {e}")
            return False

    def unblock_by_exe(self, exe_path):
        """Unblock a process by its full executable path (works even if not running)"""
        try:
            if exe_path in self.blocked_processes:
                info = self.blocked_processes[exe_path]
                rule_name = info['rule_name']
                cmd = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name={rule_name}']
                
                if is_admin():
                    subprocess.run(cmd, capture_output=True)
                    del self.blocked_processes[exe_path]
                    self._save_blocked()
                    logging.info(f"Unblocked {exe_path} and removed from registry")
                    return True
                else:
                    logging.warning(f"Admin privileges required to unblock {exe_path}")
            return False
        except Exception as e:
            logging.error(f"Exception during unblock_by_exe for {exe_path}: {e}")
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
