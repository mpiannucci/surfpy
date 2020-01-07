from unittest import TestCase
import os

import surfpy

class TestBuoyStations(TestCase):

	ACTIVE_STATIONS_XML_FILE = os.path.join(os.path.dirname(__file__), 'data', 'activestations.xml')

	def test_parse_stations(self):
		parsed_stations = surfpy.BuoyStations(stations=[])

		with open(TestBuoyStations.ACTIVE_STATIONS_XML_FILE, 'r') as activestations_file:
			raw_stations_data = activestations_file.read()

		self.assertTrue(len(parsed_stations.stations) == 0, msg='Expected 0 stations but found {0}'.format(len(parsed_stations.stations)))
		self.assertTrue(parsed_stations.parse_stations(raw_stations_data))
		self.assertTrue(len(parsed_stations.stations) == 1423, msg='Expected 1423 stations but found {0}'.format(len(parsed_stations.stations)))
		self.assertTrue(parsed_stations.find_station('44097') is not None, msg='Buoy 44097 was not found')

	def test_fetch_stations(self):
		fetched_stations = surfpy.BuoyStations(stations=[])
		self.assertTrue(fetched_stations.fetch_stations())
		self.assertTrue(len(fetched_stations.stations) > 0)
		self.assertTrue(fetched_stations.find_station('44097') is not None)
