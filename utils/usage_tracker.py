import json
from pathlib import Path

USAGE_FILE = Path("usage.json")

# Initialize the file if it doesn't exist
if not USAGE_FILE.exists():
    USAGE_FILE.write_text(json.dumps({}))

def increment_usage(endpoint: str):
    data = json.loads(USAGE_FILE.read_text())
    data[endpoint] = data.get(endpoint, 0) + 1
    USAGE_FILE.write_text(json.dumps(data))

def get_usage():
    return json.loads(USAGE_FILE.read_text())
