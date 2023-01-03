import datetime
import pytz
from . import units
from .buoydata import BuoyData
from . import tools

from io import StringIO, BytesIO
import struct

try:
    import pygrib
except: 
    pygrib = None

# https://ftp.ncep.noaa.gov/data/nccf/com/gfs/prod/gfs.20210131/18/gfs.t18z.pgrb2b.0p50.f156
# https://ftp.ncep.noaa.gov/data/nccf/com/wave/prod/multi_1.20210130/multi_1.at_4m.t00z.f000.grib2
# https://nomads.ncep.noaa.gov/pub/data/nccf/com/wave/prod/multi_1.20210130/multi_1.at_4m.t00z.f000.grib2


class NOAAModel(object):

    def __init__(self, name, subset, description, bottom_left, top_right, location_resolution, time_resolution, max_index, hourly_cutoff_index=0, max_altitude=0.0, min_altitude=0.0, altitude_resolution=0.0, data={}):
        self.name = name
        self.subset = subset
        self.description = description
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.max_altitude = max_altitude
        self.min_altitude = min_altitude
        self.altitude_resolution = altitude_resolution
        self.location_resolution = location_resolution
        self.time_resolution = time_resolution
        self.hourly_cutoff_index = hourly_cutoff_index
        self.max_index = max_index

    @property
    def time_resolution_hours(self):
        return self.time_resolution * 24.0

    def contains_location(self, location):
        if location.latitude > self.bottom_left.latitude and location.latitude < self.top_right.latitude:
            if location.absolute_longitude > self.bottom_left.absolute_longitude and location.absolute_longitude < self.top_right.absolute_longitude:
                return True
        return False

    def location_index(self, location):
        if not self.contains_location(location):
            print('Not in the grid')
            return -1, -1

        lat_offset = self.top_right.latitude - location.latitude
        lon_offset = location.absolute_longitude - self.bottom_left.absolute_longitude

        lat_index = int(lat_offset / self.location_resolution)
        lon_index = int(lon_offset / self.location_resolution)
        return lat_index, lon_index

    def altitude_index(self, altitude):
        if altitude > self.max_altitude or altitude < self.min_altitude:
            return -1

        return int(altitude / self.altitude_resolution)

    @staticmethod
    def latest_model_time():
        current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=-5)
        latest_model_hour = current_time.hour - (current_time.hour % 6)
        current_time = current_time + \
            datetime.timedelta(hours=-(current_time.hour-latest_model_hour))
        current_time = datetime.datetime(
            current_time.year, current_time.month, current_time.day, current_time.hour, 0)
        return pytz.utc.localize(current_time)

    def time_index(self, desired_time):
        model_time = self.latest_model_time()
        diff = (desired_time - model_time).days * 24.0
        if diff < 1:
            return -1
        if diff <= self.hourly_cutoff_index:
            return diff
        else:
            hours_res = self.time_resolution_hours
            return self.hourly_cutoff_index + ((diff - self.hourly_cutoff_index) / hours_res)

    def create_grib_url(self, time_index):
        return ''

    def create_grib_urls(self, start_time_index, end_time_index):
        urls = []
        for i in range(start_time_index, end_time_index + 1):
            if i > self.hourly_cutoff_index and (i - self.hourly_cutoff_index) % self.time_resolution_hours != 0:
                continue

            urls.append(self.create_grib_url(i))
        return urls

    def fetch_grib_data(self, time_index):
        url = self.create_grib_url(time_index)
        if not len(url):
            return None

        return tools.download_data(url)

    def fetch_grib_datas(self, start_time_index, end_time_index):
        urls = self.create_grib_urls(
            start_time_index, end_time_index)
        if not len(urls):
            return None

        return [tools.download_with_retry(url) for url in urls]

    def parse_grib_data(self, location, raw_data, data={}):
        if not pygrib:
            return None
        if not raw_data:
            return None
        elif not len(raw_data):
            return None

        # From https://github.com/jswhit/pygrib/issues/42#issuecomment-243643075
        f = BytesIO(raw_data)
        f.seek(0, 2)
        size = f.tell()
        f.seek(0)
        raw_messages = []
        while 1:
            # find next occurence of string 'GRIB' (or EOF).
            nbyte = f.tell()
            while 1:
                f.seek(nbyte)
                start = f.read(4)
                sstart = start.decode('ascii', errors='ignore')
                if sstart == '' or sstart == 'GRIB':
                    break
                nbyte = nbyte + 1
            #     if nbyte >= size:
            #         break

            # if nbyte >= size:
            #     break
            # otherwise, start (='GRIB') contains indicator message (section 0)
            if sstart == '':
                break
            startpos = f.tell()-4
            f.read(4)  # next four octets are reserved
            # 5th octet is length of grib message
            lengrib = struct.unpack('>q', f.read(8))[0]
            # read in entire grib message, append to list.
            f.seek(startpos)
            gribmsg = f.read(lengrib)
            raw_messages.append(gribmsg)

        # convert grib message string to grib message object 
        messages = [pygrib.fromstring(m) for m in raw_messages]   

        if not len(messages):
            return None

        # Parse out the timestamp first
        if data.get('time') is None:
            data['time'] = [messages[0].validDate]
        else:
            data['time'].append(messages[0].validDate)

        # Parse all of the variables into the map
        for message in messages:
            var = message.shortName

            if message.has_key('level'):
                if message.level > 1:
                    var += '_' + str(message.level)

            tolerence = self.location_resolution
            rawvalue, lats, lons = message.data(lat1=location.latitude-tolerence,lat2=location.latitude+tolerence,
                            lon1=location.absolute_longitude-tolerence,lon2=location.absolute_longitude+tolerence)
            value = rawvalue.mean().item()

            if data.get(var) is None:
                data[var] = [value]
            else:
                data[var].append(value)

        return data

    def parse_grib_datas(self, location, raw_data):
        if not len(raw_data):
            print('Failed to parse data, empty data array found')
            return None

        data = {}
        for dat in raw_data:
            new_data = self.parse_grib_data(location, dat, data)
            if new_data is not None:
                data = new_data

        return data

    def _to_buoy_data_wave(self, buoy_data_point, data, i):
        return False

    def _to_buoy_data_weather(self, buoy_data_point, data, i):
        return False

    def to_buoy_data_wave(self, data):
        buoy_data = []
        if not data:
            return buoy_data

        for i in range(0, len(data['time'])):
            buoy_data_point = BuoyData(units.Units.metric)
            if self._to_buoy_data_wave(buoy_data_point, data, i):
                buoy_data.append(buoy_data_point)

        return buoy_data

    def to_buoy_data_weather(self, data):
        buoy_data = []
        if not data:
            return buoy_data

        for i in range(0, len(data['time'])):
            buoy_data_point = BuoyData(units.Units.metric)
            if self._to_buoy_data_weather(buoy_data_point, data, i):
                buoy_data.append(buoy_data_point)

        return buoy_data

    def to_buoy_data(self, data):
        buoy_data = []
        if not data:
            return buoy_data

        for i in range(0, len(data['time'])):
            buoy_data_point = BuoyData(units.Units.metric)
            if self._to_buoy_data_wave(buoy_data_point, data, i):
                self._to_buoy_data_weather(buoy_data_point, data, i)
                buoy_data.append(buoy_data_point)

        return buoy_data

    def fill_buoy_data_wave(self, buoy_data, data):
        for i in range(0, len(buoy_data)):
            self._to_buoy_data_wave(buoy_data[i], data, i)
        return True

    def fill_buoy_data_weather(self, buoy_data, data):
        for i in range(0, len(buoy_data)):
            self._to_buoy_data_weather(buoy_data[i], data, i)
        return True
