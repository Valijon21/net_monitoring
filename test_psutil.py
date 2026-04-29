import psutil
import time

def test_monitoring():
    print("Monitoring total network I/O:")
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()
    print(f"Total Sent: {(net2.bytes_sent - net1.bytes_sent)/1024:.2f} KB/s")
    print(f"Total Recv: {(net2.bytes_recv - net1.bytes_recv)/1024:.2f} KB/s")

    print("\nAttempting per-process monitoring (top 5 by I/O):")
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            io = proc.io_counters()
            processes.append((proc.info['pid'], proc.info['name'], io.read_bytes + io.write_bytes))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x[2], reverse=True)
    for pid, name, io_sum in processes[:5]:
        print(f"PID: {pid}, Name: {name}, Total I/O (bytes): {io_sum}")

if __name__ == "__main__":
    test_monitoring()
