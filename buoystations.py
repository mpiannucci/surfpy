from .buoy import Buoy
from .location import Location
import xml.etree.ElementTree as ET
import requests


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
                if station.type != buoy_type:
                    continue

            dist = location.distance(station.location)
            if dist < closest_distance:
                closest_buoy = station
                closest_distance = dist

        return closest_buoy

    def fetch_buoy_stations(self):
        response = requests.get(self.active_buoys_url)
        if not len(response.text):
            return False
        return self.parse_buoy_stations(response.text)

    def parse_buoy_stations(self, rawData):
        stations = ET.fromstring(rawData)
        if stations.tag != 'stations':
            return False

        for station in stations:
            attribs = station.attrib
            station_id = attribs['id']
            loc = Location(float(attribs['lat']), float(attribs['lon']), name=attribs['name'])
            if 'elev' in attribs:
                loc.altitude = float(attribs['elev'])
            buoy = Buoy(station_id, loc)
            buoy.owner = attribs['owner']
            buoy.program = attribs['pgm']
            buoy.type = attribs['type']
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
