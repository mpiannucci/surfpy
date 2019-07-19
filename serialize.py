import datetime
import json
import pytz


def serialize_hook(val):
	if isinstance(val, datetime.datetime):
		return {
			'__class__': 'datetime.datetime',
			'epoch': val.timestamp(),
		}
	else:
		out = {
			'__class__': val.__class__.__name__,
			'__module__': val.__module__,
		}
		out.update(val.__dict__)
		return out


def serialize(val):
	return json.dumps(val, default=serialize_hook)


def serialize_to_dict(val):
	return json.loads(json.dumps(val, default=serialize_hook))


def deserialize_hook(raw):
	if '__class__' in raw:
		class_name = raw.pop('__class__')

		if class_name == 'datetime.datetime':
			return datetime.datetime.fromtimestamp(raw['epoch'], pytz.utc)

		module_name = raw.pop('__module__')
		module = __import__(module_name)
		class_ = getattr(module, class_name) 
		return class_(**raw)


def deserialize(raw):
	return json.loads(raw, object_hook=deserialize_hook)