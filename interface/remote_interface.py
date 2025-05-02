# interface/remote_interface.py

# This file conceptually defines the remote interface (IDL - Interface Definition Language).
# In Python, this isn't strictly enforced like in Java RMI, but it serves as the contract
# between client and server for available remote methods.

class IRemoteFileSynchronizer:
    """
    Conceptual Interface defining methods available remotely on the server.
    The actual implementation will be in server/file_handler.py
    The client's stub (proxy) in client/stub.py will mirror these methods.
    """

    def get_file_content(self, username, password):
        """
        Retrieves the full content of the master file.
        Requires authentication.
        Returns: dict {'content': file_content} or {'error': message}
        """
        raise NotImplementedError

    def check_master_version(self, username, password):
        """
        Retrieves the version identifier (e.g., hash or timestamp) of the master file.
        Requires authentication.
        Returns: dict {'version': version_id} or {'error': message}
        """
        raise NotImplementedError

    def receive_ack(self, username, password, transaction_id):
        """
        Method for the client to send an acknowledgment (used in RR and RRA modes).
        Requires authentication.
        Returns: dict {'status': 'ack_received'} or {'error': message}
        """
        raise NotImplementedError