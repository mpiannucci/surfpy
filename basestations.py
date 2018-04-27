try:
    import requests
except:
    pass

class BaseStations(object):

    def __init__(self):
        self.fetch_date = None
        self.stations = []

    def find_station(self, station_id):
        for station in self.stations:
            if station.station_id == station_id:
                return station
        return None
    
    def find_station_name(self, station_name):
        for station in self.stations:
            if station.location.name == station_name:
                return station
        return None

    def find_closest_station(self, search_location):
        closest = self.find_closest_stations(search_location, 1)
        if len(closest) > 0:
            return closest[0]
        return None

    def find_closest_stations(self, search_location, count):
        if len(self.stations) < 1:
            return None
        elif count < 1:
            return None

        closest_stations = [None for x in range(0, count)]
        closest_distances = [float('inf') for x in range(0, count)]

        for station in self.stations:
            dist = search_location.distance(station.location)
            max_index = -1
            max_distance = float('inf')
            added = False
            for i in range(0, count):
                added = False
                if closest_stations[i] is None:
                    closest_stations[i] = station
                    closest_distances[i] = dist
                    added = True
                    break
                if dist < closest_distances[i]:
                    if max_distance > closest_distances[i]:
                        max_index = i

            if max_index >= 0 and not added:
                closest_stations[max_index] = station
                closest_distances[max_index] = dist

        closest_stations = [x for _, x in sorted(zip(closest_distances, closest_stations), key=lambda pair: pair[0])]
        return closest_stations

    def search_station_name(self, expr):
        return [x for x in self.stations if expr in x.location.name]

    def parse_stations(self, raw_data):
        return False
    
    def _fetch_stations(self, url, payload=None):
        if payload is None:
            response = requests.get(url)
        else:
            response = requests.post(url, data=payload)
        if not len(response.text):
            return False
        return self.parse_stations(response.text)
    
    def fetch_stations(self):
        return False