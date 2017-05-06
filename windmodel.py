from noaamodel import NOAAModel
from location import Location


class GFSWindModel(NOAAModel):

    _base_gfs_url = 'http://nomads.ncep.noaa.gov:9090/dods/%[1]s/gfs%[2]s/%[1]s_%[3]s.ascii?time[%[7]d:%[8]d],ugrd10m[%[7]d:%[8]d][%[5]d][%[6]d],vgrd10m[%[7]d:%[8]d][%[5]d][%[6]d],gustsfc[%[7]d:%[8]d][%[5]d][%[6]d]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)

class NAMWindModel(NOAAModel):

    _base_nam_url = 'http://nomads.ncep.noaa.gov:9090/dods/nam/nam%[2]s/%[1]s_%[3]s.ascii?time[%[7]d:%[8]d],ugrd10m[%[7]d:%[8]d][%[5]d][%[6]d],vgrd10m[%[7]d:%[8]d][%[5]d][%[6]d],gustsfc[%[7]d:%[8]d][%[5]d][%[6]d]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)