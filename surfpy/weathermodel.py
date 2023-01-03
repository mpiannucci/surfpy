from .noaamodel import NOAAModel
from .location import Location
from . import tools
from . import units
from datetime import datetime
import pytz
import math


class GFSModel(NOAAModel):

    _base_gfs_grib_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_{0}.pl?file=gfs.t{1}z.pgrb2.{2}.f{3}&lev_10_m_above_ground=on&var_GUST=on&var_PRES=on&var_TMP=on&var_UGRD=on&var_VGRD=on&subregion=&leftlon={4}&rightlon={5}&toplat={6}&bottomlat={7}&dir=%2Fgfs.{8}%2F{1}'

    def create_grib_url(self, time_index):
        # TODO: Update this to use the new schema and match wavemodel.py
        model_run_time = self.latest_model_time()
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        hour_str = str(int(time_index)).rjust(3, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        model_degree = "{}p{}".format(math.floor(self.location_resolution), int(self.location_resolution % 1 * 100))
        url = self._base_gfs_grib_url.format(self.name, model_run_str, model_degree, hour_str, float(math.floor(location.longitude)), float(math.ceil(location.longitude)), float(math.ceil(location.latitude)), float(math.floor(location.latitude)), date_str)
        return url

    def _to_buoy_data_weather(self, buoy_data_point, data, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = data['TIME'][i]
        raw_date = pytz.utc.localize(raw_date)
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wind_speed, buoy_data_point.wind_direction = tools.scalar_from_uv(data['UGRD'][i], data['VGRD'][i])

        # TODO: Other important vars
        
        return True


# Change hourly_cutoff_index to 120 for hourly
# def hourly_gfs_model():
#     return GFSModel(name='gfs_0p25_1hr', 
#                     description='Global GFS 0.25 deg hourly', 
#                     bottom_left=Location(-90.00000, 0.00000), 
#                     top_right=Location(90.0000, 359.5000), 
#                     location_resolution=0.25, 
#                     time_resolution=0.125, 
#                     min_altitude=1000.0, 
#                     max_altitude=1.0, 
#                     altitude_resolution=21.717, 
#                     max_index=384, 
#                     hourly_cutoff_index=0)
