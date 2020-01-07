from unittest import TestCase
import surfpy


class SerializationTest(TestCase):

	def test_serialize_location(self):
		original = surfpy.Location(latitude=41.8, longitude=-71.4, name="US Northeast Coast", altitude=0.0)
		s = surfpy.serialize(original)
		cloned = surfpy.deserialize(s)

		self.assertTrue(original.name == cloned.name)
		self.assertTrue(abs(original.latitude - cloned.latitude) < 0.000001)
		self.assertTrue(abs(original.longitude - cloned.longitude) < 0.000001)
		self.assertTrue(abs(original.altitude - cloned.altitude) < 0.000001)
