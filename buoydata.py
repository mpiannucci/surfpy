from . import units
from .swell import Swell
from .buoyspectra import BuoySpectra
from .basedata import BaseData
from operator import itemgetter
import datetime


class BuoyData(BaseData):

    def __init__(self, unit):
        super(BuoyData, self).__init__(unit)

        # Set up all of the data constructors
        # Date
        self.date = None
        self.expiration_date = None

        # Wind
        self.wind_direction = float('nan')
        self.wind_compass_direction = ''
        self.wind_speed = float('nan')
        self.wind_gust = float('nan')

        # Waves
        self.wave_summary = Swell(unit)
        self.swell_components = []
        self.steepness = ''
        self.average_period = float('nan')
        self.wave_spectra = BuoySpectra()
        self.minimum_breaking_height = float('nan')
        self.maximum_breaking_height = float('nan')

        # Meterology
        self.pressure = float('nan')
        self.air_temperature = float('nan')
        self.water_temperature = float('nan')
        self.dewpoint_temperature = float('nan')
        self.pressure_tendency = float('nan')
        self.water_level = float('nan')

        # Plots
        self.energy_spectra_plot = ''
        self.direction_spectra_plot = ''

    def change_units(self, new_units):
        old_unit = self.unit
        super(BuoyData, self).change_units(new_units)

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
        if time_now.minute < 25:
            self.expiration_date = time_now + datetime.timedelta(minutes=25 - time_now.minute)
        elif time_now.minute < 50:
            self.expiration_date = time_now + datetime.timedelta(minutes=50 - time_now.minute)
        else:
            self.expiration_date = time_now + datetime.timedelta(minutes=60 - time_now.minute)

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
        all_heights, self.swell_components = zip(*sorted(zip(all_heights, self.swell_components), reverse=True, key=lambda pair: pair[0][1]))
        self.minimum_breaking_height = all_heights[0][0]
        self.maximum_breaking_height = all_heights[0][1]

        if old_unit != self.unit:
            self.change_units(old_unit)
