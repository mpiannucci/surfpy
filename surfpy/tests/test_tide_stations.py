from unittest import TestCase
import os

import surfpy

class TestTideStations(TestCase):

	def test_fetch_stations(self):
		fetched_stations = surfpy.TideStations(stations=[])
		self.assertTrue(fetched_stations.fetch_stations())
		self.assertTrue(len(fetched_stations.stations) > 0)
