import json
import os
import logging

def load_users(users_file="server/users.json"):
    if not os.path.exists(users_file):
        default_users = {"admin": "password123", "client1": "syncpass"}
        try:
            with open(users_file, 'w') as f:
                json.dump(default_users, f, indent=4)
            logging.info(f"Created default users file: {users_file}")
            return default_users
        except IOError as e:
            logging.error(f"Could not create users file {users_file}: {e}")
            return {}

    try:
        with open(users_file, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Error loading users file {users_file}: {e}")
        return {}

def authenticate(username, password, user_db):
    """Checks if the username and password match the database."""
    if not username or not password:
        return False
    return username in user_db and user_db[username] == password