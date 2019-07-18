from .basedata import BaseData
from . import units


class TideData(BaseData):

    def __init__(self, unit, date=None, expiration_date=None, water_level=float('nan'), water_level_datum=''):
        super(TideData, self).__init__(unit)

        # Date
        self.date = date
        self.expiration_date = expiration_date

        # Water Level
        self.water_level = water_level
        self.water_level_datum = water_level_datum

    def change_units(self, new_units):
        old_unit = self.unit
        super(TideData, self).change_units(new_units)

        self.water_level = units.convert(self.water_level, units.Measurement.length, old_unit, self.unit)
