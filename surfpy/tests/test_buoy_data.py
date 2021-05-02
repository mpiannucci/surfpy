from unittest import TestCase
import os

import surfpy

class TestBuoyData(TestCase):

    WAVE_FORECAST_BULLETIN_FILE = os.path.join(os.path.dirname(__file__), 'data', 'gfswave-44097.bull')

    def test_parse_wave_bulletin(self):
        block_island_station = surfpy.BuoyStation('44097', location=surfpy.Location(latitude=40.98, longitude=-71.12))

        with open(TestBuoyData.WAVE_FORECAST_BULLETIN_FILE, 'r') as wave_forecast_bulletin_file:
            raw_wave_bulletin_data = wave_forecast_bulletin_file.read()

        wave_forecast_data = block_island_station.parse_wave_forecast_bulletin(raw_wave_bulletin_data, 61)
        self.assertTrue(wave_forecast_data != None)
        self.assertTrue(len(wave_forecast_data) == 61, msg=f'Data count: {len(wave_forecast_data)}') 
