from noaamodel import NOAAModel
from location import Location


class GFSWindModel(NOAAModel):

    _base_gfs_url = 'http://nomads.ncep.noaa.gov:9090/dods/{0}/gfs{1}/{0}_{2}.ascii?time[{6}:{7}],ugrd10m[{6}:{7}][{4}][{5}],vgrd10m[{6}:{7}][{4}][{5}],gustsfc[{6}:{7}][{4}][{5}]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        alt_index = self.altitude_index(location.altitude)
        url = self._base_gfs_url.format(datestring, hourstring, alt_index, lat_index, lon_index, start_time_index, end_time_index)
        return url

class NAMWindModel(NOAAModel):

    _base_nam_url = 'http://nomads.ncep.noaa.gov:9090/dods/nam/nam{1}/{0}_{2}.ascii?time[{6}:{7}],ugrd10m[{6}:{7}][{4}][{5}],vgrd10m[{6}:{7}][{4}][{5}],gustsfc[{6}:{7}][{4}][{5}]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        alt_index = self.altitude_index(location.altitude)
        url = self._base_nam_url.format(datestring, hourstring, alt_index, lat_index, lon_index, start_time_index, end_time_index)
        return url

def global_gfs_model():
    return GFSWindModel('gfs_0p50', 'Global GFS 0.5 deg', Location(-90.00000, 0.00000), Location(90.0000, 359.5000), 0.5, 0.125, min_alt=1000.0, max_altitude=1.0, alt_res=21.717)