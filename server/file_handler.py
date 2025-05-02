# server/file_handler.py
import os
import logging
from common.utils import get_file_hash

MASTER_FILE = "server/master.txt"

class FileHandler:
    """
    Implements the actual logic for the remote methods defined conceptually
    in the interface. This is the 'service' object.
    6. Persistência Simples: Manages master.txt
    """
    def __init__(self):
        # Ensure master file exists
        if not os.path.exists(MASTER_FILE):
            try:
                with open(MASTER_FILE, 'w') as f:
                    f.write("Initial content of master file.\n")
                logging.info(f"Created master file: {MASTER_FILE}")
            except IOError as e:
                 logging.error(f"Could not create master file {MASTER_FILE}: {e}")


    def get_file_content(self):
        """Reads and returns the content of master.txt."""
        try:
            with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            logging.info(f"Read content from {MASTER_FILE}")
            # Note: Authentication is handled by the dispatcher before calling this
            return {'content': content}
        except FileNotFoundError:
            logging.error(f"Master file not found: {MASTER_FILE}")
            return {'error': 'Master file not found on server.'}
        except IOError as e:
            logging.error(f"Error reading master file {MASTER_FILE}: {e}")
            return {'error': f"IOError reading master file: {e}"}

    def check_master_version(self):
        """Returns the hash of the master file as its version."""
        # 10. Detecção Automática de Alterações no Arquivo Master (provides version info)
        # Using hash for versioning
        version_hash = get_file_hash(MASTER_FILE)
        if version_hash:
            logging.info(f"Checked master version (hash): {version_hash}")
            return {'version': version_hash}
        else:
             logging.error(f"Could not get hash for master file: {MASTER_FILE}")
             return {'error': 'Could not calculate master file version.'}

    def receive_ack(self, transaction_id):
         """Logs the reception of an acknowledgment."""
         # Part of RR / RRA implementation
         logging.info(f"Received acknowledgment for transaction: {transaction_id}")
         return {'status': 'ack_received'}