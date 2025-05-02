# client/client_main.py
import sys
import getpass
import logging
import time
from client.stub import RemoteFileStub
from client.sync_monitor import SyncMonitor
from common.protocol import CommunicationMode, DEFAULT_MODE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
client_logger = logging.getLogger('ClientMain')

def main():
    print("--- RMI File Sync Client ---")

    server_addr = input("Enter server address (e.g., localhost:8000): ")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    mode_str = input(f"Enter communication mode (R, RR, RRA) [default: {DEFAULT_MODE.value}]): ").upper()
    try:
        sync_mode = CommunicationMode(mode_str) if mode_str else DEFAULT_MODE
    except ValueError:
        print(f"Invalid mode '{mode_str}'. Using default: {DEFAULT_MODE.value}")
        sync_mode = DEFAULT_MODE

    stub = RemoteFileStub(server_url=server_addr, username=username, password=password)
    client_logger.info(f"Client stub created for server {server_addr}")

    monitor = SyncMonitor(stub=stub, sync_interval=15, mode=sync_mode)
    monitor.start()

    print("\nClient started. Automatic sync monitor is running in the background.")
    print("Press Ctrl+C to stop the client.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping client and monitor...")
        monitor.stop()
        client_logger.info("Client shutdown initiated by user.")
        time.sleep(1)
    finally:
        print("Client stopped.")

if __name__ == "__main__":
    main()