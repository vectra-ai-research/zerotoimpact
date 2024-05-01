import json
import os
from datetime import datetime

def read_from_desk(id, instance_path):
    filename=f"{instance_path}/{id}.json"

    if os.path.exists(filename):
        # If the file exists, open and read it
        with open(filename, "r") as file:
            return json.load(file)
    else:
        return None

def add_to_disk(filename, id, status, step, exchange, logs, resources, resourcesV2 = None):
    folder_path = os.path.dirname(filename)

    if folder_path:
        # If the folder does not exist, create it
        os.makedirs(folder_path, exist_ok=True)

    instance = {
        "id": id,
        "status":  status,
        "exchange": exchange,
        "logs":  logs,
        "step": step,
        "resources": resources,
        "resourcesV2": resourcesV2}
    
    instance = preprocess_object(instance)
    with open(filename, "w") as file:
        json.dump(instance, file, cls=ExcludingDateTimeAndMetadataEncoder)
    
import json
from datetime import datetime

class ExcludingDateTimeAndMetadataEncoder(json.JSONEncoder):
    """Custom encoder that excludes datetime objects."""
    def default(self, obj):
        # Handle datetime objects
        if isinstance(obj, datetime):
            return None  # Exclude datetime objects
        return super().default(obj)

def preprocess_object(obj):
    """Recursively remove 'ResponseMetadata' keys from dictionaries."""
    if isinstance(obj, dict):
        return {k: preprocess_object(v) for k, v in obj.items() if k != 'ResponseMetadata'}
    elif isinstance(obj, list):
        return [preprocess_object(elem) for elem in obj]
    return obj

 



