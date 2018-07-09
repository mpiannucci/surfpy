from .basedata import BaseData
from . import units


class TideData(BaseData):

    def __init__(self, unit):
        super(TideData, self).__init__(unit)

        # Date
        self.date = None
        self.expiration_date = None

        # Water Level
        self.water_level = float('nan')
        self.water_level_datum = ''

    def change_units(self, new_units):
        old_unit = self.unit
        super(TideData, self).change_units(new_units)

        self.water_level = units.convert(self.water_level, units.Measurement.length, old_unit, self.unit)
