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
        # TODO
        return False

    def parse_meteorological_reading_data(self, raw_data, count_limit=20):
        # TODO
        return False

    def parse_detailed_wave_reading_data(self, raw_data, count_limit=20):
        # TODO
        return False

    def parse_wave_spectra_reading_data(self, energy_data, directional_data, count_limit=20):
        # TODO
        return False

