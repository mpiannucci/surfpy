import json
import datetime

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime and time objects"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)

def json_serialize(obj):
    """Helper function to serialize objects to JSON with our custom encoder"""
    return json.dumps(obj, cls=CustomJSONEncoder)
