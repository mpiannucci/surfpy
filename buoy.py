from buoydata import BuoyData
from buoyspectra import BuoySpectra
from swell import Swell
from datetime import datetime
import units
import re
import requests

class Buoy(object):

    def __init__(self, station_id, location, owner = '', program='', active=False, currents=False, water_quality=False, dart=False):
        self.station_id = station_id
        self.location = location

        # Attributes
        self.owner = ''
        self.program = ''
        self.type = ''
        self.active = active
        self.currents = currents
        self.water_quality = water_quality
        self.dart = dart

        # Data
        self.data = []

    @property
    def latest_reading_url(self):
        return 'http://www.ndbc.noaa.gov/data/latest_obs/' + self.station_id + '.txt'

    @property
    def meteorological_reading_url(self):
        return 'http://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.txt'

    @property
    def detailed_wave_reading_url(self):
        return 'http://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.spec'

    @property
    def wave_energy_reading_url(self):
        return 'http://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.data_spec'

    @property
    def directional_wave_reading_url(self):
        return 'http://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.swdir'

    def parse_latest_reading_data(self, raw_data):
        raw_data = raw_data.split('\n')
        if len(raw_data) < 6:
            print(raw_data)
            return False

        data = BuoyData('english')
        data.date = datetime.strptime(raw_data[4], '%H%M %Z %m/%d/%y')

        swell_period_read = False
        swell_direction_read = False
        swell_component = Swell(units.Units.english)
        wind_wave_component = Swell(units.Units.english)

        for i in range(5, len(raw_data)):
            comps = raw_data[i].split(':')
            if len(comps) < 2:
                continue
            variable = comps[0].lower()
            raw_value = comps[1].strip().split(' ')

            if variable == 'wind':
                data.wind_direction = float(re.findall("\d+", raw_value[1])[0])
                data.wind_speed = units.convert(float(raw_value[2]), units.Measurement.speed, units.Units.knots, units.Units.english)
            elif variable == 'gust':
                data.wind_gust = units.convert(float(raw_value[0]), units.Measurement.speed, units.Units.knots, units.Units.english)
            elif variable == 'seas':
                data.wave_summary.wave_height = float(raw_value[0])
            elif variable == 'peak period':
                data.wave_summary.period = float(raw_value[0])
            elif variable == 'pres':
                data.pressure = float(raw_value[0])
                if 'falling' in raw_value[1]:
                    data.pressure_tendency = -1.0
                elif 'rising' in raw_value[1]:
                    data.pressure_tendency = 1.0
                elif 'steady' in raw_value[1]:
                    data.pressure_tendency = 0.0
            elif variable == 'air temp':
                data.air_temperature = float(raw_value[0])
            elif variable == 'water temp':
                data.water_temperature = float(raw_value[0])
            elif variable == 'dew point':
                data.dewpoint_temperature = float(raw_value[0])
            elif variable == 'swell':
                swell_component.wave_height = float(raw_value[0])
            elif variable == 'wind wave':
                wind_wave_component.wave_height = float(raw_value[0])
            elif variable == 'period':
                if not swell_period_read:
                    swell_component.period = float(raw_value[0])
                    swell_period_read = True
                else:
                    wind_wave_component.period = float(raw_value[0])
            elif variable == 'direction':
                if not swell_direction_read:
                    swell_component.compass_direction = raw_value[0]
                    swell_component.direction = units.direction_to_degree(swell_component.compass_direction)
                    swell_direction_read = True
                else:
                    wind_wave_component.compass_direction = raw_value[0]
                    wind_wave_component.direction = units.direction_to_degree(wind_wave_component.compass_direction)

        data.swell_components = [swell_component, wind_wave_component]
        data.interpolate_dominant_wave_direction()

        if len(self.data) > 0:
            self.data[0] = [data] + self.data
        else:
            self.data = [data]

        return True

    def parse_meteorological_reading_data(self, raw_data, count_limit=20):
        # TODO
        return False

    def parse_detailed_wave_reading_data(self, raw_data, count_limit=20):
        # TODO
        return False

    def parse_wave_spectra_reading_data(self, energy_data, directional_data, count_limit=20):
        # TODO
        return False

    def fetch_latest_wave_reading(self):
        response = requests.get(self.latest_reading_url)
        if len(response.text) < 1:
            return False
        return self.parse_latest_reading_data(response.text)
