from . import units
from . import tools
import math
from .basedata import BaseData


class Swell(BaseData):

    def __init__(self, unit, wave_height=float('nan'), period=float('nan'), direction=float('nan'), compass_direction=None, max_energy = 0, frequency_index = 0):
        super(Swell, self).__init__(unit)

        self.wave_height = wave_height
        self.period = period
        if not math.isnan(direction):
            self.direction = direction
            self.compass_direction = units.degree_to_direction(direction)
        elif compass_direction is not None:
            self.compass_direction = compass_direction
            self.direction = units.direction_to_degree(compass_direction)
        else:
            self.direction = float('nan')
            self.compass_direction = ''

        self.max_energy = max_energy
        self.frequency_index = frequency_index

    @property
    def summary(self):
        return '{0:.1f} {1} @ {2:.1f} s {3:.0f}\xb0 {4}'.format(self.wave_height, units.unit_name(self.unit, 
            units.Measurement.length), self.period, self.direction, self.compass_direction)

    def is_valid(self):
        return not math.isnan(self.wave_height) and not math.isnan(self.period) and len(self.compass_direction) > 0 and not math.isnan(self.direction)

    def change_units(self, new_units):
        old_units = self.unit
        super(Swell, self).change_units(new_units)

        self.wave_height = units.convert(self.wave_height, units.Measurement.length, old_units, self.unit)

    def breaking_wave_estimate(self, beach_angle, depth, beach_slope):
        # Interpolates the approximate breaking wave heights using the contained swell data. Data must
        # be in metric units prior to calling this function. The depth argument must be in meters.
    
        if self.is_valid() is not True:
            return

        self.change_units(units.Units.metric) 
        wave_breaking_height = 0.0

        if self.wave_height < 1000:
            incident_angle = abs(self.direction - beach_angle) % 360
            if incident_angle < 90:
                wave_breaking_height, _ = tools.breaking_characteristics(self.period, incident_angle, self.wave_height, beach_slope, depth)

        # Take the maximum breaking height and give it a scale factor of 0.9 for refraction
        # or anything we are not checking for.
        breaking_height = 0.8 * wave_breaking_height

        # For now assume this is significant wave height as the max and the rms as the min
        maximum_break_height = breaking_height
        minimum_break_height = breaking_height / 1.4
        return minimum_break_height, maximum_break_height
