from .noaamodel import NOAAModel
from .location import Location
from . import tools
from . import units
from datetime import datetime
import pytz
import math


class GFSModel(NOAAModel):
    _base_gfs_grib_url = (
        "https://nomads.ncep.noaa.gov/cgi-bin/filter_{model}.pl?"
        "file=gfs.t{run_time}z.pgrb2.{resolution}.f{forecast_hour}"
        "&lev_30-0_mb_above_ground=on&var_TMP=on&var_UGRD=on&var_VGRD=on"
        "&subregion={subregion}&dir=%2Fgfs.{date}%2F{run_time}/atmos"
    )

    def create_grib_url(self, time_index, location=None):
        model_run_time = self.latest_model_time()
        run_time = f"{model_run_time.hour:02}"
        forecast_hour = f"{int(time_index):03}"
        date = model_run_time.strftime('%Y%m%d')
        resolution = f"{math.floor(self.location_resolution)}p{int(self.location_resolution % 1 * 100)}"

        # Subregion filter (only if location is provided)
        subregion = (
            "on"
            f"&leftlon={math.floor(location.longitude):.2f}"
            f"&rightlon={math.ceil(location.longitude):.2f}"
            f"&toplat={math.ceil(location.latitude):.2f}"
            f"&bottomlat={math.floor(location.latitude):.2f}"
            if location else "off"
        )

        # Construct the URL 
        url = self._base_gfs_grib_url.format(
            model=self.name,
            run_time=run_time,
            resolution=resolution,
            forecast_hour=forecast_hour,
            subregion=subregion,
            date=date
        )
        return url


    def _to_buoy_data_weather(self, buoy_data_point, data, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = data['time'][i]
        raw_date = pytz.utc.localize(raw_date)
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wind_speed, buoy_data_point.wind_direction = tools.scalar_from_uv(data['u_3000'][i], data['v_3000'][i])
        buoy_data_point.compass_direction = units.degree_to_direction(buoy_data_point.wind_direction)
        buoy_data_point.air_temperature = units.convert(data['t_3000'][i], units.Measurement.temperature, units.Units.kelvin, units.Units.metric)
        
        return True

    def _to_buoy_data_wave(self, buoy_data_point, data, i):
        return True
    

def global_gfs_weather_model():
    return GFSModel(
        name='gfs_0p25',
        subset='global.0p25',
        description='Global GFS 0.25 deg',
        bottom_left=Location(-90.00000, 0.00000),
        top_right=Location(90.0000, 359.5000),
        location_resolution=0.25,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0)