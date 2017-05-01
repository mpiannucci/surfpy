import units
from swell import Swell
from buoyspectra import BuoySpectra
from basedata import BaseData


class BuoyData(BaseData):

    def __init__(self, unit):
        super(BuoyData, self).__init__(unit)

        # Set up all of the data constructors
        # Date
        self.date = None

        # Wind
        self.wind_direction = float('nan')
        self.wind_speed = float('nan')
        self.wind_gust = float('nan')

        # Waves
        self.wave_summary = Swell(unit)
        self.swell_components = []
        self.steepness = ''
        self.average_period = float('nan')
        self.wave_spectra = BuoySpectra()

        # Meterology
        self.pressure = float('nan')
        self.air_temperature = float('nan')
        self.water_temperature = float('nan')
        self.dewpoint_temperatures = float('nan')
        self.pressure_tendency = float('nan')
        self.water_level = float('nan')

    def change_units(self, new_units):
        old_unit = self.unit
        super(BuoyData, self).change_units(new_units)

        self.wave_summary.change_units(new_units)
        for swell in self.swell_components:
            swell.change_units(new_units)

        self.wind_speed = units.convert(self.wind_speed, units.Measurement.speed, old_unit, self.unit)
        self.wind_gust = units.convert(self.wind_gust, units.Measurement.speed, old_unit, self.unit)
        self.air_temperature = units.convert(self.air_temperature, units.Measurement.temperature, old_unit, self.unit)
        self.water_temperature = units.convert(self.water_temperature, units.Measurement.temperature, old_unit, self.unit)
        self.dewpoint_temperature = units.convert(self.dewpoint_temperature, units.Measurement.temperature, old_unit, self.unit)
        self.pressure = units.convert(self.pressure, units.Measurement.pressure, old_unit, self.unit)
        self.pressure_tendency = units.convert(self.pressure_tendency, units.Measurement.pressure, old_unit, self.unit)
        self.water_level = units.convert(self.water_level, units.Measurement.length, old_unit, self.unit)

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