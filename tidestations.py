from .basestations import BaseStations
from .tidestation import TideStation
from .location import Location
import json
try:
    import requests
except:
    pass

class TideStations(BaseStations):

    tide_stations_url = 'https://tidesandcurrents.noaa.gov/cgi-bin/map2/odinmap.cgi'

    def __init__(self, stations=None, fetch_date=None):
        super(TideStations, self).__init__()

        if stations is not None:
            self.stations = stations
        self.fetch_date = fetch_date

    def fetch_stations(self):
        all_stations_payload = {"mode": "json", "nelat": "90", "nelng": "180", "swlat": "-90", "swlng": "-180"}
        return self._fetch_stations(self.tide_stations_url, all_stations_payload)

    def parse_stations(self, raw_data):
        if raw_data is None:
            return False
        elif len(raw_data) < 1:
            return False

        raw_stations = json.loads(raw_data)['locations']
        self.stations = [TideStation(x['stnid'], Location(float(x['lat']), float(x['lng']), name=x['name']), state=x['state']) for x in raw_stations]

        return True