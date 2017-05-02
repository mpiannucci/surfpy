import datetime


class NOAAModel(object):

    def __init__(self, name, description, bottom_left, top_right, max_alt, min_alt, alt_res, loc_res, time_res):
        self.name = name
        self.description = description
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.max_altitude = max_alt
        self.min_altitude = min_alt
        self.altitude_resolution = alt_res
        self.location_resolution = loc_res
        self.time_resolution = time_res

    @property
    def time_resolution_hours(self):
        return self.time_resolution * 24.0

    def contains_location(self, location):
        if location.latitude > self.bottom_left.latitude and location.latitude < self.top_right.latitude:
            if location.longitude > self.bottom_left.longitude and location.longitude < self.top_right.longitude:
                return True
        return False

    def location_index(self, location):
        if not self.contains_location(location):
            return -1, -1

        lat_offset = location.latitude - self.bottom_left.latitude
        lon_offset = location.longitude - self.bottom_left.longitude

        lat_index = int(lat_offset / self.location_resolution)
        lon_index = int(lon_offset / self.location_resolution)
        return lat_index, lon_index

    def altitude_index(self, altitude):
        if altitude > self.max_altitude or altitude < self.min_altitude:
            return -1

        return int(altitude / self.altitude_resolution)

    def latest_model_time(self):
        current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=-5)
        latest_model_hour = current_time.hour - (current_time.hour % 6)
        current_time = current_time + datetime.timedelta(current_time.hour - latest_model_hour)
        return current_time

    def time_index(self, desired_time):
        model_time = self.latest_model_time()
        diff = (desired_time - model_time).days * 24.0
        if diff < 1:
            return -1
        hours_res = self.time_resolution_hours
        return (diff + (hours_res - (diff % hours_res))) / hours_res

