from .basestations import BaseStations
from .buoystation import BuoyStation
from .location import Location
import xml.etree.ElementTree as ET
try:
    import requests
except:
    pass


class BuoyStations(BaseStations):

    active_buoys_url="https://www.ndbc.noaa.gov/activestations.xml"

    def __init__(self, stations=None, fetch_date=None):
        super(BuoyStations, self).__init__()

        if stations is not None:
            self.stations = stations
        self.fetch_date = fetch_date

    def find_closest_buoy(self, location, active=False, buoy_type=BuoyStation.BuoyType.none):
        if len(self.stations) < 1:
            return None

        closest_buoy = None
        closest_distance = float('inf')

        for station in self.stations:
            if active and not station.active:
                continue
            if buoy_type != BuoyStation.BuoyType.none:
                if station.buoy_type != buoy_type:
                    continue

            dist = location.distance(station.location)
            if dist < closest_distance:
                closest_buoy = station
                closest_distance = dist

        return closest_buoy

    def find_closest_buoys(self, location, count, active=False, buoy_type=BuoyStation.BuoyType.none):
        if len(self.stations) < 1:
            return None
        elif count < 1:
            return None

        closest_buoys = [None for x in range(0, count)]
        closest_distances = [float('inf') for x in range(0, count)]

        for station in self.stations:
            if active and not station.active:
                continue
            if buoy_type != BuoyStation.BuoyType.none:
                if station.buoy_type != buoy_type:
                    continue

            dist = location.distance(station.location)
            max_index = -1
            max_distance = float('inf')
            added = False
            for i in range(0, count):
                added = False
                if closest_buoys[i] is None:
                    closest_buoys[i] = station
                    closest_distances[i] = dist
                    added = True
                    break
                if dist < closest_distances[i]:
                    if max_distance > closest_distances[i]:
                        max_index = i

            if max_index >= 0 and not added:
                closest_buoys[max_index] = station
                closest_distances[max_index] = dist

        closest_buoys = [x for _, x in sorted(zip(closest_distances, closest_buoys), key=lambda pair: pair[0])]
        return closest_buoys

    def fetch_stations(self):
        return self._fetch_stations(self.active_buoys_url)

    def parse_stations(self, rawData):
        stations = ET.fromstring(rawData)
        if stations.tag != 'stations':
            return False

        for station in stations:
            attribs = station.attrib
            station_id = attribs['id']
            loc = Location(float(attribs['lat']), float(attribs['lon']), name=attribs['name'])
            if 'elev' in attribs:
                loc.altitude = float(attribs['elev'])
            buoy = BuoyStation(station_id, loc)
            buoy.owner = attribs['owner']
            buoy.program = attribs['pgm']
            buoy.buoy_type = attribs['type']
            if 'met' in attribs:
                buoy.active = 'y' in attribs['met']
            if 'currents' in attribs:
                buoy.currents = 'y' in attribs['currents']
            if 'waterquality' in attribs:
                buoy.water_quality = 'y' in attribs['waterquality']
            if 'dart' in attribs:
                buoy.dart = 'y' in attribs['dart']
            self.stations.append(buoy)
        return True
