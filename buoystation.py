from .basestation import BaseStation
from .buoydata import BuoyData
from .buoyspectra import BuoySpectra
from .swell import Swell
from .location import Location
from datetime import datetime
from .tools import parse_float, steepness
from . import units
import re
try:
    import requests
except:
    pass
import math
import pytz


class BuoyStation(BaseStation):

    class BuoyType:
        none = ''
        buoy = 'buoy'
        fixed = 'fixed'
        oilrig = 'oilrig'
        dart = 'dart'
        tao = 'tao'
        other = 'other'

    def __init__(self, station_id, location, owner='', program='', active=False, currents=False, water_quality=False, dart=False, buoy_type=BuoyType.none, name=''):
        super(BuoyStation, self).__init__(station_id, location)

        # Attributes
        self.owner = owner
        self.program = program
        self.buoy_type = buoy_type
        self.active = active
        self.currents = currents
        self.water_quality = water_quality
        self.dart = dart

    @property
    def latest_reading_url(self):
        return 'https://www.ndbc.noaa.gov/data/latest_obs/' + self.station_id + '.txt'

    @property
    def meteorological_reading_url(self):
        return 'https://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.txt'

    @property
    def detailed_wave_reading_url(self):
        return 'https://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.spec'

    @property
    def wave_energy_reading_url(self):
        return 'https://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.data_spec'

    @property
    def directional_wave_reading_url(self):
        return 'https://www.ndbc.noaa.gov/data/realtime2/' + self.station_id + '.swdir'

    def parse_latest_reading_data(self, raw_data):
        raw_data = raw_data.split('\n')
        if len(raw_data) < 6:
            print('Invalid latest station data')
            return None

        data = BuoyData(units.Units.english)
        data.date = pytz.utc.localize(datetime.strptime(raw_data[4], '%H%M %Z %m/%d/%y'))
        print(data.date)
        print(raw_data[4])

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
                data.wind_compass_direction = units.degree_to_direction(data.wind_direction)
                data.wind_speed = units.convert(parse_float(raw_value[2]), units.Measurement.speed, units.Units.knots, units.Units.english)
            elif variable == 'gust':
                data.wind_gust = units.convert(parse_float(raw_value[0]), units.Measurement.speed, units.Units.knots, units.Units.english)
            elif variable == 'seas':
                data.wave_summary.wave_height = parse_float(raw_value[0])
            elif variable == 'peak period':
                data.wave_summary.period = parse_float(raw_value[0])
            elif variable == 'pres':
                data.pressure = parse_float(raw_value[0])
                if len(raw_value) > 1:
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

        if not math.isnan(swell_component.wave_height):
            data.swell_components.append(swell_component)
        if not math.isnan(wind_wave_component.wave_height):
            data.swell_components.append(wind_wave_component)
        if not math.isnan(wind_wave_component.wave_height) and not math.isnan(swell_component.wave_height):
            data.interpolate_dominant_wave_direction()

        data.find_expiration_date()
        return data

    def parse_meteorological_reading_data(self, raw_data, count_limit):
        raw_data = raw_data.split('\n')
        if len(raw_data) < 2:
            print('Failed to parse meteorological data')
            return None

        header_lines = 2
        data_lines = len(raw_data) - header_lines
        if data_lines > count_limit and count_limit > 0:
            data_lines = count_limit

        all_data = []
        for i in range(header_lines, header_lines + data_lines):
            raw_data_line = raw_data[i].split()
            data = BuoyData(units.Units.metric)
            data.date = pytz.utc.localize(datetime(*[int(x) for x in raw_data_line[0:5]]))
            data.wind_direction = parse_float(raw_data_line[5])
            data.wind_compass_direction = units.degree_to_direction(data.wind_direction)
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
            data.find_expiration_date()
            all_data.append(data)

        return all_data

    def parse_detailed_wave_reading_data(self, raw_data, count_limit):
        raw_data = raw_data.split('\n')
        if len(raw_data) < 2:
            print('Failed to parse detailed wave data')
            return None

        header_lines = 2
        data_lines = len(raw_data) - header_lines
        if data_lines > count_limit and count_limit > 0:
            data_lines = count_limit

        all_data = []
        for i in range(header_lines, header_lines + data_lines):
            raw_data_line = raw_data[i].split()
            data = BuoyData(units.Units.metric)
            swell_component = Swell(units.Units.metric)
            wind_wave_component = Swell(units.Units.metric)
            data.date = pytz.utc.localize(datetime(*[int(x) for x in raw_data_line[0:5]]))
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
            data.find_expiration_date()
            all_data.append(data)

        return all_data

    def parse_wave_spectra_reading_data(self, energy_data, directional_data, count_limit):
        energy_data = energy_data.split('\n')
        directional_data = directional_data.split('\n')
        if len(energy_data) != len(directional_data):
            print('Failed to parse wave spectra data')
            return None
        elif len(energy_data) < 2:
            print('Failed to parse wave spectra data')
            return None

        header_lines = 1
        data_lines = len(energy_data) - header_lines
        if data_lines > count_limit and count_limit > 0:
            data_lines = count_limit

        all_data = []
        for i in range(header_lines, header_lines + data_lines):
            raw_energy = energy_data[i].strip().replace(')', '').replace('(', '').split()
            raw_directional = directional_data[i].strip().replace(')', '').replace('(', '').split()

            spectra = BuoySpectra()
            data = BuoyData(units.Units.metric)
            data.date = pytz.utc.localize(datetime(*[int(x) for x in raw_energy[0:5]]))

            for j in range(5, len(raw_directional), 2):
                spectra.frequency.append(parse_float(raw_directional[j + 1]))
                spectra.angle.append(parse_float(raw_directional[j]))
                spectra.energy.append(parse_float(raw_energy[j + 1]))

            spectra.seperation_frequency = parse_float(raw_energy[5])

            data.wave_spectra = spectra
            data.wave_summary = spectra.wave_summary
            data.swell_components = spectra.swell_components
            data.steepness = steepness(data.wave_summary.wave_height, data.wave_summary.period)
            data.average_period = spectra.average_period

            data.find_expiration_date()

            all_data.append(data)

        return all_data

    def fetch_latest_reading(self):
        print(self.latest_reading_url)
        response = requests.get(self.latest_reading_url)
        if len(response.text) < 1:
            return None
        return self.parse_latest_reading_data(response.text)

    def fetch_meteorological_reading(self, data_count=20):
        response = requests.get(self.meteorological_reading_url)
        if len(response.text) < 1:
            return None
        return self.parse_meteorological_reading_data(response.text, data_count)

    def fetch_detailed_wave_reading(self, data_count=20):
        response = requests.get(self.detailed_wave_reading_url)
        if len(response.text) < 1:
            return None
        return self.parse_detailed_wave_reading_data(response.text, data_count)

    def fetch_wave_spectra_reading(self, data_count=20):
        energy_response = requests.get(self.wave_energy_reading_url)
        directional_response = requests.get(self.directional_wave_reading_url)
        if len(energy_response.text) < 1 or len(directional_response.text) < 1:
            return None
        return self.parse_wave_spectra_reading_data(energy_response.text, directional_response.text, data_count)

    @staticmethod
    def data_index_for_date(data, datetime):
        if len(data) < 1:
            return None

        min_duration = (datetime - data[0].date).seconds
        min_index = 0

        for i in range(1, len(data)):
            duration = (datetime - data[i].date).seconds
            if abs(duration) < min_duration:
                min_duration = duration
                min_index = i

        return min_index, min_duration
