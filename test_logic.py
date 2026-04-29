from network_monitor import NetworkMonitor
import time
import sys

def test_monitor():
    monitor = NetworkMonitor()
    print("Testing network monitor (CLI mode)...")
    try:
        for i in range(10):
            stats = monitor.get_process_stats()
            print(f"\n--- Update {i+1} ---")
            if not stats:
                print("No processes with network activity detected.")
            for s in stats[:10]:
                print(f"PID: {s['pid']}, Name: {s['name']}, Speed: {s['formatted_speed']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest stopped.")

if __name__ == "__main__":
    test_monitor()
