import urllib.request
import urllib.error
import logging
from common.utils import serialize_request, deserialize_response
from common.protocol import CommunicationMode

class RemoteFileStub:
    def __init__(self, server_url, username, password):
        if not server_url.startswith("http://"):
             server_url = "http://" + server_url 
        self.server_url = server_url
        self.auth = {'username': username, 'password': password}
        self.logger = logging.getLogger('ClientStub')

    def _make_request(self, method_name, args=None, mode=CommunicationMode.R):
        """Internal helper to make HTTP POST requests."""
        req_data = serialize_request(method_name, args, self.auth, mode=mode)
        req = urllib.request.Request(self.server_url, data=req_data, headers={'Content-Type': 'application/json'}, method='POST')
        self.logger.info(f"Sending request: Method={method_name}, Mode={mode.value}, Args={args}")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_body = response.read()
                status_code = response.getcode()
                self.logger.info(f"Received response: Status={status_code}")
                if status_code == 200:
                    return deserialize_response(response_body)
                else:
                    error_info = deserialize_response(response_body)
                    self.logger.error(f"Server returned error {status_code}: {error_info}")
                    return {'error': f"Server error {status_code}: {error_info.get('error', 'Unknown')}"}
        except urllib.error.URLError as e:
            self.logger.error(f"Network error contacting {self.server_url}: {e}")
            return {'error': f"Network error: {e}"}
        except Exception as e:
            self.logger.exception(f"Unexpected error during request: {e}")
            return {'error': f"Unexpected client error: {e}"}

    def _send_ack(self, transaction_id):
        """Sends an acknowledgment for a specific transaction."""
        ack_args = {'transaction_id': transaction_id}
        result = self._make_request('receive_ack', args=ack_args, mode=CommunicationMode.R)
        if result and 'status' in result and result['status'] == 'ack_received':
            self.logger.info(f"Server acknowledged ACK for TID: {transaction_id}")
            return True
        else:
            self.logger.warning(f"Failed to get ACK confirmation for TID: {transaction_id}. Response: {result}")
            return False

    def get_file_content(self, mode=CommunicationMode.R):
        """Calls the remote get_file_content method."""
        print(f"[Stub] Requesting file content using mode: {mode.value}")
        self.logger.info(f"Requesting file content (mode={mode.value})")
        result = self._make_request('get_file_content', mode=mode)

        if mode == CommunicationMode.RR or mode == CommunicationMode.RRA:
            if result and 'error' not in result and 'transaction_id' in result:
                tid = result['transaction_id']
                print(f"[Stub] Received response, sending ACK for TID: {tid} (Mode: {mode.value})")
                self.logger.info(f"Sending ACK for TID={tid} (Mode={mode.value})")
                self._send_ack(tid)
            elif result and 'error' in result:
                 self.logger.warning(f"Not sending ACK due to error in response: {result['error']}")
            else:
                 self.logger.warning("No transaction ID received for ACK in RR/RRA mode.")

        print(f"[Stub] Operation get_file_content (Mode: {mode.value}) completed.")


    def check_master_version(self, mode=CommunicationMode.R):
        """Calls the remote check_master_version method."""
        print(f"[Stub] Checking master version using mode: {mode.value}")
        self.logger.info(f"Checking master version (mode={mode.value})")
        result = self._make_request('check_master_version', mode=mode)

        if mode == CommunicationMode.RR or mode == CommunicationMode.RRA:
            if result and 'error' not in result and 'transaction_id' in result:
                tid = result['transaction_id']
                print(f"[Stub] Received version response, sending ACK for TID: {tid} (Mode: {mode.value})")
                self.logger.info(f"Sending ACK for TID={tid} (Mode={mode.value})")
                self._send_ack(tid)
            elif result and 'error' in result:
                 self.logger.warning(f"Not sending ACK for version check due to error: {result['error']}")
            else:
                 self.logger.warning("No transaction ID received for version ACK in RR/RRA mode.")

        print(f"[Stub] Operation check_master_version (Mode: {mode.value}) completed.")
        return result