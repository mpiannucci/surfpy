from buoydata import BuoyData
from buoyspectra import BuoySpectra
from swell import Swell
from datetime import datetime
from tools import parse_float
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
            raw_value = comps[1].strip().split()

            if variable == 'wind':
                data.wind_direction = parse_float(re.findall("\d+", raw_value[1])[0])
                data.wind_speed = units.convert(parse_float(raw_value[2]), units.Measurement.speed, units.Units.knots, units.Units.english)
            elif variable == 'gust':
                data.wind_gust = units.convert(parse_float(raw_value[0]), units.Measurement.speed, units.Units.knots, units.Units.english)
            elif variable == 'seas':
                data.wave_summary.wave_height = parse_float(raw_value[0])
            elif variable == 'peak period':
                data.wave_summary.period = parse_float(raw_value[0])
            elif variable == 'pres':
                data.pressure = parse_float(raw_value[0])
                if 'falling' in raw_value[1]:
                    data.pressure_tendency = -1.0
                elif 'rising' in raw_value[1]:
                    data.pressure_tendency = 1.0
                elif 'steady' in raw_value[1]:
                    data.pressure_tendency = 0.0
            elif variable == 'air temp':
                data.air_temperature = parse_float(raw_value[0])
            elif variable == 'water temp':
                data.water_temperature = parse_float(raw_value[0])
            elif variable == 'dew point':
                data.dewpoint_temperature = parse_float(raw_value[0])
            elif variable == 'swell':
                swell_component.wave_height = parse_float(raw_value[0])
            elif variable == 'wind wave':
                wind_wave_component.wave_height = parse_float(raw_value[0])
            elif variable == 'period':
                if not swell_period_read:
                    swell_component.period = parse_float(raw_value[0])
                    swell_period_read = True
                else:
                    wind_wave_component.period = parse_float(raw_value[0])
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

    def parse_meteorological_reading_data(self, raw_data, count_limit):
        raw_data = raw_data.split('\n')
        if len(raw_data) < 2:
            return False

        header_lines = 2
        data_lines = len(raw_data) - header_lines
        if data_lines > count_limit and count_limit > 0:
            data_lines = count_limit

        for i in range(header_lines, header_lines + data_lines):
            raw_data_line = raw_data[i].split()
            data = BuoyData(units.Units.metric)
            data.date = datetime(*[int(x) for x in raw_data_line[0:5]])
            data.wind_direction = parse_float(raw_data_line[5])
            data.wind_speed = parse_float(raw_data_line[6])
            data.wind_gust = parse_float(raw_data_line[7])
            data.wave_summary.wave_height = parse_float(raw_data_line[8])
            data.wave_summary.period = parse_float(raw_data_line[9])
            data.average_period = parse_float(raw_data_line[10])
            data.wave_summary.direction = parse_float(raw_data_line[11])
            data.wave_summary.compass_direction = units.degree_to_direction(data.wave_summary.direction)
            data.pressure = parse_float(raw_data_line[12])
            data.air_temperature = parse_float(raw_data_line[13])
            data.water_temperature = parse_float(raw_data_line[14])
            data.dewpoint_temperature = parse_float(raw_data_line[15])
            data.pressure_tendency = parse_float(raw_data_line[17])
            data.water_level = units.convert(parse_float(raw_data_line[18]), units.Measurement.length, units.Units.english, units.Units.metric)
            self.data.append(data)

        return True

    def parse_detailed_wave_reading_data(self, raw_data, count_limit):
        raw_data = raw_data.split('\n')
        if len(raw_data) < 2:
            return False

        header_lines = 2
        data_lines = len(raw_data) - header_lines
        if data_lines > count_limit and count_limit > 0:
            data_lines = count_limit

        for i in range(header_lines, header_lines + data_lines):
            raw_data_line = raw_data[i].split()
            data = BuoyData(units.Units.metric)
            swell_component = Swell(units.Units.metric)
            wind_wave_component = Swell(units.Units.metric)
            data.date = datetime(*[int(x) for x in raw_data_line[0:5]])
            data.wave_summary.wave_height = parse_float(raw_data_line[5])
            swell_component.wave_height = parse_float(raw_data_line[6])
            swell_component.period = parse_float(raw_data_line[7])
            wind_wave_component.wave_height = parse_float(raw_data_line[8])
            wind_wave_component.period = parse_float(raw_data_line[9])
            swell_component.compass_direction = raw_data_line[10]
            swell_component.direction = units.direction_to_degree(swell_component.compass_direction)
            wind_wave_component.compass_direction = raw_data_line[11]
            wind_wave_component.direction = units.direction_to_degree(wind_wave_component.compass_direction)
            data.steepness = raw_data_line[12]
            data.average_period = parse_float(raw_data_line[13])
            data.wave_summary.direction = parse_float(raw_data_line[14])
            data.wave_summary.compass_direction = units.degree_to_direction(data.wave_summary.direction)

            data.swell_components.append(swell_component)
            data.swell_components.append(wind_wave_component)
            data.interpolate_dominant_wave_period()
            data.interpolate_dominant_wave_direction()
            self.data.append(data)
        
        return True

    def parse_wave_spectra_reading_data(self, energy_data, directional_data, count_limit):
        # TODO
        return False

    def fetch_latest_wave_reading(self):
        response = requests.get(self.latest_reading_url)
        if len(response.text) < 1:
            return False
        return self.parse_latest_reading_data(response.text)

    def fetch_meteorological_reading(self, data_count=20):
        response = requests.get(self.meteorological_reading_url)
        if len(response.text) < 1:
            return False
        return self.parse_meteorological_reading_data(response.text, data_count)

    def fetch_detailed_wave_reading(self, data_count=20):
        response = requests.get(self.detailed_wave_reading_url)
        if len(response.text) < 1:
            return False
        return self.parse_detailed_wave_reading_data(response.text, data_count)
