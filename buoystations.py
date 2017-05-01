from buoy import Buoy


class BuoyStations(object):

    active_buoys_url="http://www.ndbc.noaa.gov/activestations.xml"

    def __init__(self):
        self.fetch_date = None
        self.stations = []

    def find_buoy(self, station_id):
        for station in self.stations:
            if station.station_id == station_id:
                return station
        return None

    def find_closest_buoy(self, location, buoy_type=''):
        if len(self.stations) < 1:
            return None

        closest_buoy = None
        closest_distance = float('inf')

        for station in self.stations:
            if not station.active:
                continue
            if len(buoy_type) > 0:
                if station.type is not buoy_type:
                    continue

            dist = location.distance(station.location)
            if dist < closest_distance:
                closest_buoy = station
                closest_distance = dist

        return closest_buoy

    def fetch_buoy_stations(self):
        return False

    def parse_buoy_stations(self, rawData):
        return False
