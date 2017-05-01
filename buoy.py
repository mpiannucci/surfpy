from buoydata import BuoyData
from buoyspectra import BuoySpectra

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