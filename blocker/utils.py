import os
import json
from urllib.parse import urlparse

def is_valid_url(url):
    """Check if a given string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def ensure_directory(path):
    """Ensure a directory exists, create it if it doesn't"""
    if not os.path.exists(path):
        os.makedirs(path)

def load_json_file(filepath, default=None):
    """Load a JSON file, return default if file doesn't exist"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json_file(filepath, data):
    """Save data to a JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
