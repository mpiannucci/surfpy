import os
import sys
sys.path.insert(0, os.path.abspath(__file__))

from .serialize import *
from .buoystations import BuoyStations

class SerializationTest(object):

	def __init__(self):
		self.stations = BuoyStations()
		self.stations.fetch_stations()

	def location_test(self, station_id):
		b = self.stations.find_station(station_id)
		j = serialize(b.location)
		l = deserialize(j)
		print(l.__dict__)

	def station_test(self, station_id):
		b = self.stations.find_station(station_id)
		j = serialize(b)
		l = deserialize(j)
		print(serialize_to_dict(l))

	def stations_test(self):
		j = serialize(self.stations)
		l = deserialize(j)
		print(len(l.stations))

	def data_test(self, station_id):
		b = self.stations.find_station(station_id)
		d = b.fetch_latest_reading()
		j = serialize(d)
		l = deserialize(j)
		print(l.date)

if __name__ == '__main__':
	test = SerializationTest()
	test.location_test('44097')
	print('--------------------------------------')
	test.station_test('44097')
	print('--------------------------------------')
	test.stations_test()
	print('--------------------------------------')
	test.data_test('44097')