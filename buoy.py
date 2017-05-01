from buoydata import BuoyData
from buoyspectra import BuoySpectra

class Buoy(object):

    def __init__(self, station_id, location):
        self.station_id = station_id
        self.location = location

        # Attributes
        self.owner = ''
        self.program = ''
        self.type = ''
        self.active = False
        self.currents = False
        self.water_quality = False
        self.dart = False

        # Data
        self.data = []