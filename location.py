import math
from . import units


class Location(object):

    def __init__(self, latitude=0.0, longitude=0.0, name='', altitude=0, depth=0.0, angle=0.0, slope=0.0):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.name = name
        self.depth = depth
        self.angle = angle
        self.slope = slope

    @property
    def adjusted_longitude(self):
        if self.longitude > 180:
            return self.longitude - 360.0
        else:
            return self.longitude

    @property
    def adjusted_latitude(self):
        if self.latitude > 90:
            return self.latitude - 180.0
        else:
            return self.latitude

    @property
    def absolute_longitude(self):
        if self.longitude < 0:
            return self.longitude+360.0
        else:
            return self.longitude

    @property
    def absolute_latitude(self):
        if self.latitude < 0:
            return self.latitude+ 180.0
        else:
            return self.latitude

    def distance(self, other_location, unit=units.Units.metric):
        lon1, lat1, lon2, lat2 = map(math.radians, [self.longitude, self.latitude, other_location.longitude, other_location.latitude])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = units.earths_radius(unit)
        return c * r