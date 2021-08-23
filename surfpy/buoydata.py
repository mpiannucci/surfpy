from math import isnan
from typing import List
from . import units
from .swell import Swell
from .buoyspectra import BuoySpectra
from .basedata import BaseData
from operator import itemgetter
import datetime


class BuoyData(BaseData):

    def __init__(self, unit, date=None, expiration_date=None, wind_direction=float('nan'), wind_compass_direction='', 
        wind_speed=float('nan'), wind_gust=float('nan'), wave_summary=None, swell_components=None, steepness='', average_period=float('nan'),
        wave_spectra=None, minimum_breaking_height=float('nan'), maximum_breaking_height=float('nan'), pressure=float('nan'),
        air_temperature=float('nan'), water_temperature=float('nan'), dewpoint_temperature=float('nan'), pressure_tendency=float('nan'), 
        water_level=float('nan'), short_forecast=None):
        super(BuoyData, self).__init__(unit)

        # Set up all of the data constructors
        # Date
        self.date = date
        self.expiration_date = expiration_date

        # Wind
        self.wind_direction = wind_direction
        self.wind_compass_direction = wind_compass_direction
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust

        # Waves
        self.wave_summary = wave_summary
        self.swell_components = swell_components
        if self.swell_components is None:
            self.swell_components = []
        self.steepness = steepness
        self.average_period = average_period
        self.wave_spectra = wave_spectra
        self.minimum_breaking_height = minimum_breaking_height
        self.maximum_breaking_height = maximum_breaking_height

        # Meteorology
        self.pressure = pressure
        self.air_temperature = air_temperature
        self.water_temperature = water_temperature
        self.dewpoint_temperature = dewpoint_temperature
        self.pressure_tendency = pressure_tendency
        self.water_level = water_level
        self.short_forecast = short_forecast

    def change_units(self, new_units):
        old_unit = self.unit
        super(BuoyData, self).change_units(new_units)

        if self.wave_summary is not None:
            self.wave_summary.change_units(new_units)
        for swell in self.swell_components:
            swell.change_units(new_units)

        self.minimum_breaking_height = units.convert(self.minimum_breaking_height, units.Measurement.length, old_unit, self.unit)
        self.maximum_breaking_height = units.convert(self.maximum_breaking_height, units.Measurement.length, old_unit, self.unit)
        self.wind_speed = units.convert(self.wind_speed, units.Measurement.speed, old_unit, self.unit)
        self.wind_gust = units.convert(self.wind_gust, units.Measurement.speed, old_unit, self.unit)
        self.air_temperature = units.convert(self.air_temperature, units.Measurement.temperature, old_unit, self.unit)
        self.water_temperature = units.convert(self.water_temperature, units.Measurement.temperature, old_unit, self.unit)
        self.dewpoint_temperature = units.convert(self.dewpoint_temperature, units.Measurement.temperature, old_unit, self.unit)
        self.pressure = units.convert(self.pressure, units.Measurement.pressure, old_unit, self.unit)
        self.pressure_tendency = units.convert(self.pressure_tendency, units.Measurement.pressure, old_unit, self.unit)
        self.water_level = units.convert(self.water_level, units.Measurement.length, old_unit, self.unit)

    def find_expiration_date(self):
        time_now = datetime.datetime.now()
        if time_now.minute < 2:
            self.expiration_date = time_now + datetime.timedelta(minutes=35 - time_now.minute)
        elif time_now.minute < 50:
            self.expiration_date = time_now + datetime.timedelta(minutes=50 - time_now.minute)
        else:
            self.expiration_date = time_now + datetime.timedelta(minutes=(60 - time_now.minute) + 35)

    def interpolate_dominant_wave_direction(self):
        min_diff = float('inf')
        for swell in self.swell_components:
            diff = abs(swell.period - self.wave_summary.period)
            if diff < min_diff:
                min_diff = diff
                self.wave_summary.compass_direction = swell.compass_direction
                self.wave_summary.direction = swell.direction

    def interpolate_dominant_wave_period(self):
        min_diff = float('inf')
        for swell in self.swell_components:
            diff = abs(swell.wave_height - self.wave_summary.wave_height)
            if diff < min_diff:
                min_diff = diff
                self.wave_summary.period = swell.period

    def solve_breaking_wave_heights(self, location):
        old_unit = self.unit
        if self.unit != units.Units.metric:
            self.change_units(units.Units.metric)

        all_heights = [x.breaking_wave_estimate(location.angle, location.depth, location.slope) for x in self.swell_components]
        if len(all_heights) < 1:
            self.minimum_breaking_height = float('nan')
            self.maximum_breaking_height = float('nan')
        else:
            all_heights, self.swell_components = zip(*sorted(zip(all_heights, self.swell_components), reverse=True, key=lambda pair: pair[0][1]))
            self.minimum_breaking_height = all_heights[0][0]
            self.maximum_breaking_height = all_heights[0][1]

        if old_unit != self.unit:
            self.change_units(old_unit)

    def copy_wind_data(self, other):
        if other.unit != self.unit:
            other.change_units(self.unit)
        
        self.wind_speed = other.wind_speed
        self.wind_direction = other.wind_direction
        self.wind_compass_direction = other.wind_compass_direction


def merge_wave_weather_data(wave_data: List[BuoyData], weather_data: List[BuoyData]) -> List[BuoyData]:
    last_weather_index = 0
    
    for wave in wave_data:
        wave.change_units(units.Units.metric)
        if wave.date > weather_data[-1].date:
            return wave_data

        for i in range(last_weather_index, len(weather_data)):
            weather = weather_data[i]
            if weather.date != wave.date:
                continue

            weather.change_units(units.Units.metric)
            if weather.air_temperature is not None and not isnan(weather.air_temperature):
                wave.air_temperature = weather.air_temperature
            wave.short_forecast = weather.short_forecast
            if weather.wind_speed is not None and not isnan(weather.wind_speed):
                wave.wind_speed = weather.wind_speed
            if weather.wind_direction is not None and not isnan(weather.wind_direction):
                wave.wind_direction = weather.wind_direction
            if weather.wind_compass_direction is not None:
                wave.wind_compass_direction = weather.wind_compass_direction
            last_weather_index = i
            break
        
    return wave_data