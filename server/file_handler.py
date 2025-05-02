import os
import logging
from common.utils import get_file_hash

MASTER_FILE = "server/master.txt"

class FileHandler:
    def __init__(self):
        if not os.path.exists(MASTER_FILE):
            try:
                with open(MASTER_FILE, 'w') as f:
                    f.write("Initial content of master file.\n")
                logging.info(f"Created master file: {MASTER_FILE}")
            except IOError as e:
                 logging.error(f"Could not create master file {MASTER_FILE}: {e}")


    def get_file_content(self):
        try:
            with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            logging.info(f"Read content from {MASTER_FILE}")
            return {'content': content}
        except FileNotFoundError:
            logging.error(f"Master file not found: {MASTER_FILE}")
            return {'error': 'Master file not found on server.'}
        except IOError as e:
            logging.error(f"Error reading master file {MASTER_FILE}: {e}")
            return {'error': f"IOError reading master file: {e}"}

    def check_master_version(self):
        version_hash = get_file_hash(MASTER_FILE)
        if version_hash:
            logging.info(f"Checked master version (hash): {version_hash}")
            return {'version': version_hash}
        else:
             logging.error(f"Could not get hash for master file: {MASTER_FILE}")
             return {'error': 'Could not calculate master file version.'}

    def receive_ack(self, transaction_id):
         logging.info(f"Received acknowledgment for transaction: {transaction_id}")
         return {'status': 'ack_received'}