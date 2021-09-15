from .noaamodel import NOAAModel
from .location import Location
from .swell import Swell
from . import units
from . import tools
from . import BuoyData
from datetime import datetime
import math
import pytz


class WaveModel(NOAAModel):

    # https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.20210324/06/wave/gridded/gfswave.t06z.atlocn.0p16.f006.grib2
    _base_gfs_wave_grib_url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{0}/{3}/wave/gridded/{1}.t{3}z.{2}.f{4}.grib2'

    def create_grib_url(self, time_index):
        model_run_time = self.latest_model_time()
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        hour_str = str(int(time_index)).rjust(3, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        url = self._base_gfs_wave_grib_url.format(
            date_str, self.name, self.subset, model_run_str, hour_str)
        return url

    def _to_buoy_data_wave(self, buoy_data_point, data, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = data['time'][i]
        raw_date = pytz.utc.localize(raw_date)
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wave_summary = Swell(units.Units.metric)
        buoy_data_point.wave_summary.direction = data['dirpw'][i]
        buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(
            buoy_data_point.wave_summary.direction)
        buoy_data_point.wave_summary.wave_height = data['htsgw'][i]
        buoy_data_point.wave_summary.period = data['perpw'][i]

        if data['swell'][i] > 0 and data['swper'][i] > 0 and data['swdir'][i] > 0:
            swell_1 = Swell(units.Units.metric)
            swell_1.direction = data['swdir'][i]
            swell_1.compass_direction = units.degree_to_direction(
                swell_1.direction)
            swell_1.wave_height = data['swell'][i]
            swell_1.period = data['swper'][i]
            buoy_data_point.swell_components.append(swell_1)

        if data['swell_2'][i] > 0 and data['swper_2'][i] > 0 and data['swdir_2'][i] > 0:
            swell_2 = Swell(units.Units.metric)
            swell_2.direction = data['swdir_2'][i]
            swell_2.compass_direction = units.degree_to_direction(
                swell_2.direction)
            swell_2.wave_height = data['swell_2'][i]
            swell_2.period = data['swper_2'][i]
            buoy_data_point.swell_components.append(swell_2)

        if data['wvhgt'][i] > 0 and data['wvper'][i] > 0 and data['wvdir'][i] > 0:
            wind_swell = Swell(units.Units.metric)
            wind_swell.direction = data['wvdir'][i]
            wind_swell.compass_direction = units.degree_to_direction(
                wind_swell.direction)
            wind_swell.wave_height = data['wvhgt'][i]
            wind_swell.period = data['wvper'][i]
            buoy_data_point.swell_components.append(wind_swell)

        return True

    def _to_buoy_data_weather(self, buoy_data_point, data, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = data['time'][i]
        raw_date = pytz.utc.localize(raw_date)
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wind_direction = data['wdir'][i]
        buoy_data_point.wind_compass_direction = units.degree_to_direction(
            buoy_data_point.wind_direction)
        buoy_data_point.wind_speed = data['wind'][i]

        return True


def atlantic_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='atlocn.0p16',
        description='GFS Wave Model: Atlantic 0.16 degree',
        bottom_left=Location(0.00, 260.00),
        top_right=Location(55.00011, 310.00011),
        location_resolution=0.167,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )


def us_west_coast_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='wcoast.0p16',
        description='GFS Wave Model: US West Coast 0.16 degree',
        bottom_left=Location(25.00, 210.00),
        top_right=Location(50.00005, 250.00008),
        location_resolution=0.167,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )