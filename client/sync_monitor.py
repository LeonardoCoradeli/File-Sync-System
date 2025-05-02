# client/sync_monitor.py
import time
import threading
import logging
import os
from common.utils import get_file_hash
from common.protocol import CommunicationMode

SLAVE_FILE = "client/slave.txt"

class SyncMonitor:
    """
    Monitors the master file version periodically and triggers synchronization
    if changes are detected.
    """
    def __init__(self, stub, sync_interval=10, mode=CommunicationMode.RR):
        self.stub = stub # The proxy/stub to communicate with the server
        self.sync_interval = sync_interval
        self.mode = mode # Communication mode for sync operations
        self.current_slave_version = self._get_local_version()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.logger = logging.getLogger('SyncMonitor')

    def _get_local_version(self):
        """Gets the hash of the local slave file."""
        # 6. Persistência Simples: Check local slave file
        return get_file_hash(SLAVE_FILE)

    def _update_slave_file(self, content):
        """Writes content to the slave file and updates local version."""
        try:
            with open(SLAVE_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            self.current_slave_version = self._get_local_version() # Update after writing
            self.logger.info(f"Successfully updated {SLAVE_FILE}. New hash: {self.current_slave_version}")
            print(f"[Monitor] Slave file '{SLAVE_FILE}' updated.")
            return True
        except IOError as e:
            self.logger.error(f"Failed to write to slave file {SLAVE_FILE}: {e}")
            print(f"[Monitor] Error: Could not write to slave file: {e}")
            return False

    def _run(self):
        """The main loop for the monitoring thread."""
        self.logger.info(f"Sync Monitor started. Interval: {self.sync_interval}s, Mode: {self.mode.value}")
        print(f"[Monitor] Starting automatic sync check every {self.sync_interval} seconds (Mode: {self.mode.value})...")

        while not self.stop_event.is_set():
            try:
                # 10. Detecção Automática de Alterações: Check master version
                print("[Monitor] Checking master file version...")
                self.logger.info("Polling server for master version.")
                version_result = self.stub.check_master_version(mode=self.mode) # Use configured mode

                if version_result and 'version' in version_result:
                    master_version = version_result['version']
                    self.logger.debug(f"Master version: {master_version}, Current slave version: {self.current_slave_version}")

                    if master_version != self.current_slave_version:
                        print(f"[Monitor] Change detected! Master version ({master_version}) differs from slave ({self.current_slave_version}).")
                        self.logger.info(f"Change detected. Master: {master_version}, Slave: {self.current_slave_version}. Fetching content.")

                        # Fetch the new content
                        content_result = self.stub.get_file_content(mode=self.mode) # Use configured mode for sync
                        if content_result and 'content' in content_result:
                            self._update_slave_file(content_result['content'])
                        elif content_result and 'error' in content_result:
                             print(f"[Monitor] Error fetching file content: {content_result['error']}")
                             self.logger.error(f"Error fetching file content: {content_result['error']}")
                        else:
                            print("[Monitor] Error: Received invalid response when fetching content.")
                            self.logger.error("Received invalid response when fetching content.")
                    else:
                        print("[Monitor] No changes detected.")
                        self.logger.info("No changes detected in master file version.")

                elif version_result and 'error' in version_result:
                    print(f"[Monitor] Error checking master version: {version_result['error']}")
                    self.logger.error(f"Error checking master version: {version_result['error']}")
                else:
                    print("[Monitor] Error: Received invalid response checking version.")
                    self.logger.error("Received invalid response when checking version.")

            except Exception as e:
                print(f"[Monitor] An unexpected error occurred: {e}")
                self.logger.exception("Unexpected error in monitor loop.")

            # Wait for the next interval or until stopped
            self.stop_event.wait(self.sync_interval)

        self.logger.info("Sync Monitor stopped.")
        print("[Monitor] Sync Monitor stopped.")

    def start(self):
        """Starts the monitoring thread."""
        if not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True) # Recreate if stopped previously
            self.thread.start()

    def stop(self):
        """Signals the monitoring thread to stop."""
        self.stop_event.set()
        # Optional: Join the thread if you need to wait for it to finish cleanly
        # self.thread.join()