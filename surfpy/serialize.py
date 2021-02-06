import datetime
import json
import pytz


def serialize_hook(val):
	if isinstance(val, datetime.datetime):
		return val.timestamp()
	else:
		try:
			out = {
				'classname__': val.__class__.__name__,
			}
			if hasattr(val, '__module__'):
				out['modulename__'] = val.__module__
			out.update(val.__dict__)
			return out
		except Exception:
			return None


def serialize(val):
	return json.dumps(val, default=serialize_hook).replace('NaN', 'null')


def serialize_to_dict(val):
	return json.loads(json.dumps(val, default=serialize_hook).replace('NaN', 'null'))


def deserialize_hook(raw):
	if 'classname__' in raw:
		class_name = raw.pop('classname__')

		if class_name == 'datetime.datetime':
			return datetime.datetime.fromtimestamp(raw['epoch'], pytz.utc)

		module_name = raw.pop('modulename__')
		module = __import__(module_name)
		class_ = getattr(module, class_name) 
		return class_(**raw)


def deserialize(raw):
	return json.loads(raw, object_hook=deserialize_hook)