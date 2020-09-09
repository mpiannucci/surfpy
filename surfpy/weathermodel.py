from .noaamodel import NOAAModel
from .location import Location
from . import tools
from . import units
from datetime import datetime
import pytz
import math


class GFSModel(NOAAModel):

    _base_gfs_ascii_url = 'https://nomads.ncep.noaa.gov:9090/dods/{0}/gfs{1}/{0}_{2}.ascii?time[{6}:{7}],ugrd10m[{6}:{7}][{4}][{5}],vgrd10m[{6}:{7}][{4}][{5}],gustsfc[{6}:{7}][{4}][{5}]'
    _base_gfs_grib_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_{0}.pl?file=gfs.t{1}z.pgrb2.{2}.f{3}&lev_10_m_above_ground=on&var_GUST=on&var_PRES=on&var_TMP=on&var_UGRD=on&var_VGRD=on&subregion=&leftlon={4}&rightlon={5}&toplat={6}&bottomlat={7}&dir=%2Fgfs.{8}%2F{1}'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        alt_index = self.altitude_index(location.altitude)
        url = self._base_gfs_ascii_url.format(self.name, datestring, hourstring, alt_index, lat_index, lon_index, start_time_index, end_time_index)
        return url

    def create_grib_url(self, location, time_index):
        model_run_time = self.latest_model_time()
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        hour_str = str(int(time_index)).rjust(3, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        model_degree = "{}p{}".format(math.floor(self.location_resolution), int(self.location_resolution % 1 * 100))
        url = self._base_gfs_grib_url.format(self.name, model_run_str, model_degree, hour_str, float(math.floor(location.longitude)), float(math.ceil(location.longitude)), float(math.ceil(location.latitude)), float(math.floor(location.latitude)), date_str)
        return url

    def _to_buoy_data_ascii(self, buoy_data_point, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        # Make sure the timestamp exists and is the same as the data we are trying to fill
        raw_time = (self.data['time'][i] - units.epoch_days_since_zero) * 24 * 60 * 60
        raw_date = pytz.utc.localize(datetime.utcfromtimestamp(raw_time))
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wind_speed, buoy_data_point.wind_direction = tools.scalar_from_uv(self.data['ugrd10m'][i], self.data['vgrd10m'][i])
        buoy_data_point.wind_compass_direction = units.degree_to_direction(buoy_data_point.wind_direction)
        buoy_data_point.wind_gust = self.data['gustsfc'][i]

        return True

    def _to_buoy_data_binary(self, buoy_data_point, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = self.data['TIME'][i]
        raw_date = pytz.utc.localize(raw_date)
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wind_speed, buoy_data_point.wind_direction = tools.scalar_from_uv(self.data['UGRD'][i], self.data['VGRD'][i])

        return True

class NAMModel(NOAAModel):

    _base_nam_url = 'http://nomads.ncep.noaa.gov:9090/dods/nam/nam{1}/{0}_{2}.ascii?time[{6}:{7}],ugrd10m[{6}:{7}][{4}][{5}],vgrd10m[{6}:{7}][{4}][{5}],gustsfc[{6}:{7}][{4}][{5}]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        alt_index = self.altitude_index(location.altitude)
        url = self._base_nam_url.format(datestring, hourstring, alt_index, lat_index, lon_index, start_time_index, end_time_index)
        return url

def hourly_gfs_model():
    return GFSModel(name='gfs_0p25_1hr', 
                    description='Global GFS 0.25 deg hourly', 
                    bottom_left=Location(-90.00000, 0.00000), 
                    top_right=Location(90.0000, 359.5000), 
                    location_resolution=0.25, 
                    time_resolution=0.125, 
                    min_altitude=1000.0, 
                    max_altitude=1.0, 
                    altitude_resolution=21.717, 
                    max_index=384, 
                    hourly_cutoff_index=120)


# https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl?file=gfs.t06z.pgrb2full.1hr.f159&lev_10_m_above_ground=on&var_GUST=on&var_PRES=on&var_TMP=on&var_UGRD=on&var_VGRD=on&subregion=&leftlon=-72.0&rightlon=-71.0&toplat=42.0&bottomlat=41.0&dir=%2Fgfs.20200909%2F06