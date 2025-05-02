# server/dispatcher.py
import http.server
import json
import logging
import uuid
from common.auth import authenticate, load_users
from common.utils import serialize_request, deserialize_response
from server.file_handler import FileHandler

class RMIDispatcherHandler(http.server.BaseHTTPRequestHandler):
    user_db = load_users()
    log_file = "server/sync.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    def _send_response(self, status_code, content_type, body):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        client_ip = self.client_address[0]
        transaction_id = str(uuid.uuid4())

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))

            method_name = request_data.get('method')
            args = request_data.get('args', {})
            auth_data = request_data.get('auth', {})
            client_mode_str = request_data.get('mode')

            username = auth_data.get('username')
            password = auth_data.get('password')

            logging.info(f"Attempt - IP: {client_ip}, User: {username}, Method: {method_name}, Mode: {client_mode_str}, TID: {transaction_id}")

            if not authenticate(username, password, self.user_db):
                logging.warning(f"Failed Auth - IP: {client_ip}, User: {username}, TID: {transaction_id}")
                error_response = json.dumps({'error': 'Authentication failed'}).encode('utf-8')
                self._send_response(401, 'application/json', error_response)
                return

            service_object = FileHandler()

            if hasattr(service_object, method_name):
                method_to_call = getattr(service_object, method_name)

                if method_name == 'get_file_content':
                    result = method_to_call()
                elif method_name == 'check_master_version':
                    result = method_to_call()
                elif method_name == 'receive_ack':
                    ack_tid = args.get('transaction_id')
                    if ack_tid:
                         result = method_to_call(transaction_id=ack_tid)
                    else:
                         result = {'error': 'Missing transaction_id for ACK'}
                else:
                    result = {'error': f'Method {method_name} not implemented or callable with provided args'}


                if 'error' not in result:
                    if client_mode_str in ["RR", "RRA"]:
                        result['transaction_id'] = transaction_id 
                    logging.info(f"Success - IP: {client_ip}, User: {username}, Method: {method_name}, Result Keys: {list(result.keys())}, TID: {transaction_id}")
                    response_body = json.dumps(result).encode('utf-8')
                    self._send_response(200, 'application/json', response_body)
                else:
                    logging.error(f"Execution Error - IP: {client_ip}, User: {username}, Method: {method_name}, Error: {result['error']}, TID: {transaction_id}")
                    response_body = json.dumps(result).encode('utf-8')
                    self._send_response(400, 'application/json', response_body)

            else:
                logging.error(f"Failed - IP: {client_ip}, User: {username}, Method: {method_name} not found, TID: {transaction_id}")
                error_response = json.dumps({'error': f'Method {method_name} not found on server'}).encode('utf-8')
                self._send_response(404, 'application/json', error_response)

        except json.JSONDecodeError:
            logging.error(f"Failed - IP: {client_ip}, Invalid JSON received, TID: {transaction_id}")
            error_response = json.dumps({'error': 'Invalid JSON format'}).encode('utf-8')
            self._send_response(400, 'application/json', error_response)
        except Exception as e:
            logging.exception(f"Internal Server Error - IP: {client_ip}, TID: {transaction_id}, Error: {e}")
            error_response = json.dumps({'error': f'Internal server error: {e}'}).encode('utf-8')
            self._send_response(500, 'application/json', error_response)

    def do_GET(self):
        self._send_response(200, 'text/plain', b'RMI Server is running. Use POST for RMI calls.')