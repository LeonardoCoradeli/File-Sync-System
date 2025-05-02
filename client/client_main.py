# client/client_main.py
import sys
import getpass
import logging
import time
from client.stub import RemoteFileStub
from client.sync_monitor import SyncMonitor
from common.protocol import CommunicationMode, DEFAULT_MODE

# Configure client-side logging (can log to file or just console)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
client_logger = logging.getLogger('ClientMain')

def main():
    print("--- RMI File Sync Client ---")

    # Get connection details
    server_addr = input("Enter server address (e.g., localhost:8000): ")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ") # Use getpass for privacy

    # Get communication mode
    mode_str = input(f"Enter communication mode (R, RR, RRA) [default: {DEFAULT_MODE.value}]): ").upper()
    try:
        sync_mode = CommunicationMode(mode_str) if mode_str else DEFAULT_MODE
    except ValueError:
        print(f"Invalid mode '{mode_str}'. Using default: {DEFAULT_MODE.value}")
        sync_mode = DEFAULT_MODE

    # Create the stub (proxy)
    stub = RemoteFileStub(server_url=server_addr, username=username, password=password)
    client_logger.info(f"Client stub created for server {server_addr}")

    # Start the automatic sync monitor in a background thread
    monitor = SyncMonitor(stub=stub, sync_interval=15, mode=sync_mode) # Check every 15 seconds
    monitor.start()

    print("\nClient started. Automatic sync monitor is running in the background.")
    print("Press Ctrl+C to stop the client.")

    try:
        # Keep the main thread alive while the monitor runs
        while True:
            time.sleep(1)
            # You could add commands here for manual sync, status check etc.
            # command = input("> ")
            # if command.lower() == 'sync':
            #     print("Manual sync requested...")
            #     content_res = stub.get_file_content(mode=sync_mode)
            #     # etc...
    except KeyboardInterrupt:
        print("\nStopping client and monitor...")
        monitor.stop()
        client_logger.info("Client shutdown initiated by user.")
        # Give the monitor a moment to stop if needed
        time.sleep(1)
    finally:
        print("Client stopped.")

if __name__ == "__main__":
    main()