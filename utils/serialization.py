import json
import numpy as np
import torch
import tensorflow as tf

class MLTrackerJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MLTracker objects."""
    
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if torch.is_tensor(obj):
            return obj.cpu().detach().numpy().tolist()
        if tf.is_tensor(obj):
            return obj.numpy().tolist()
        return super().default(obj)

def serialize(obj):
    """Serialize an object to JSON."""
    return json.dumps(obj, cls=MLTrackerJSONEncoder)

def deserialize(json_str):
    """Deserialize a JSON string."""
    return json.loads(json_str)
