# common/utils.py
import json
import hashlib
import os

def serialize_request(method_name, args=None, auth=None, transaction_id=None, mode=None):
    """Serializes data into JSON for HTTP body."""
    payload = {
        'method': method_name,
        'args': args or {},
        'auth': auth or {},
        'transaction_id': transaction_id,
        'mode': mode.value if mode else None # Include mode if relevant
    }
    return json.dumps(payload).encode('utf-8')

def deserialize_response(response_body):
    """Deserializes JSON response body."""
    try:
        return json.loads(response_body.decode('utf-8'))
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON response received'}

def get_file_hash(filepath):
    """Calculates the SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'rb') as file:
            while chunk := file.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError:
        return None # Indicate error reading file