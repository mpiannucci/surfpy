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

    _base_filtered_multigrid_grib_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl?file={0}.t{1}z.f{2}.grib2&all_lev=on&all_var=on&subregion=&leftlon={4}&rightlon={5}&toplat={6}&bottomlat={7}&dir=%2Fmulti_1.{3}'
    _base_multigrid_netcdf_url = 'https://nomads.ncep.noaa.gov/dods/wave/mww3/{0}/{1}{0}_{2}'
    _base_multigrid_grib_url = 'https://ftp.ncep.noaa.gov/data/nccf/com/wave/prod/multi_1.{0}/{1}.t{2}z.f{3}.grib2'

    def create_grib_url(self, time_index):
        model_run_time = self.latest_model_time()
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        hour_str = str(int(time_index)).rjust(3, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        url = self._base_multigrid_grib_url.format(date_str, self.name, model_run_str, hour_str)
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
        buoy_data_point.wave_summary.wave_height = data['swh'][i]
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

        if data['shww'][i] > 0 and data['mpww'][i] > 0 and data['wvdir'][i] > 0:
            wind_swell = Swell(units.Units.metric)
            wind_swell.direction = data['wvdir'][i]
            wind_swell.compass_direction = units.degree_to_direction(
                wind_swell.direction)
            wind_swell.wave_height = data['shww'][i]
            wind_swell.period = data['mpww'][i]
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
        buoy_data_point.wind_speed = data['ws'][i]

        return True


def us_east_coast_wave_model():
    return WaveModel(name='multi_1.at_10m',
                     description='Multi-grid wave model: US East Coast 10 arc-min grid',
                     bottom_left=Location(0.00, 260.00),
                     top_right=Location(55.00011, 310.00011),
                     location_resolution=0.167,
                     time_resolution=0.125,
                     max_index=180,
                     hourly_cutoff_index=0)


def us_east_coast_wave_model_dense():
    return WaveModel(name='multi_1.at_4m',
                     description='Multi-grid wave model: US East Coast 4 arc-min grid',
                     bottom_left=Location(15.0, 261.00),
                     top_right=Location(47.00016, 300.000195),
                     location_resolution=0.067,
                     time_resolution=0.125,
                     max_index=180,
                     hourly_cutoff_index=0)


def us_west_coast_wave_model():
    return WaveModel(name='multi_1.wc_10m',
                     description='Multi-grid wave model: US West Coast 10 arc-min grid',
                     bottom_left=Location(25.00, 210.00),
                     top_right=Location(50.00005, 250.00008),
                     location_resolution=0.167,
                     time_resolution=0.125,
                     max_index=180,
                     hourly_cutoff_index=0)


def pacific_islands_wave_model():
    return WaveModel(name='multi_1.ep_10m',
                     description='Multi-grid wave model: Pacific Islands (including Hawaii) 10 arc-min grid',
                     bottom_left=Location(-20.00, 130.00),
                     top_right=Location(30.0001, 215.00017),
                     location_resolution=0.167,
                     time_resolution=0.125,
                     max_index=180,
                     hourly_cutoff_index=0)
