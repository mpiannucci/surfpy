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

    _base_multigrid_ascii_url = 'https://nomads.ncep.noaa.gov:9090/dods/wave/mww3/{0}/{1}{0}_{2}.ascii?time[{5}:{6}],dirpwsfc.dirpwsfc[{5}:{6}][{3}][{4}],htsgwsfc.htsgwsfc[{5}:{6}][{3}][{4}],perpwsfc.perpwsfc[{5}:{6}][{3}][{4}],swdir_1.swdir_1[{5}:{6}][{3}][{4}],swdir_2.swdir_2[{5}:{6}][{3}][{4}],swell_1.swell_1[{5}:{6}][{3}][{4}],swell_2.swell_2[{5}:{6}][{3}][{4}],swper_1.swper_1[{5}:{6}][{3}][{4}],swper_2.swper_2[{5}:{6}][{3}][{4}],ugrdsfc.ugrdsfc[{5}:{6}][{3}][{4}],vgrdsfc.vgrdsfc[{5}:{6}][{3}][{4}],wdirsfc.wdirsfc[{5}:{6}][{3}][{4}],windsfc.windsfc[{5}:{6}][{3}][{4}],wvdirsfc.wvdirsfc[{5}:{6}][{3}][{4}],wvhgtsfc.wvhgtsfc[{5}:{6}][{3}][{4}],wvpersfc.wvpersfc[{5}:{6}][{3}][{4}]'
    _base_multigrid_grib_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl?file={0}.t{1}z.f{2}.grib2&all_lev=on&all_var=on&subregion=&leftlon={4}&rightlon={5}&toplat={6}&bottomlat={7}&dir=%2Fmulti_1.{3}'
    _base_multigrid_netcdf_url = 'https://nomads.ncep.noaa.gov/dods/wave/mww3/{0}/{1}{0}_{2}'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        url = self._base_multigrid_ascii_url.format(
            datestring, self.name, hourstring, lat_index, lon_index, start_time_index, end_time_index)
        return url

    def create_grib_url(self, location, time_index):
        model_run_time = self.latest_model_time()
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        hour_str = str(int(time_index)).rjust(3, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        url = self._base_multigrid_grib_url.format(self.name, model_run_str, hour_str, date_str, float(math.floor(location.longitude)), float(
            math.ceil(location.longitude)), float(math.ceil(location.latitude)), float(math.floor(location.latitude)))
        return url

    def create_netcdf_url(self):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        url = self._base_multigrid_netcdf_url.format(
            datestring, self.name, hourstring)
        return url

    def _to_buoy_data_ascii(self, buoy_data_point, data, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        # Make sure the timestamp exists and is the same as the data we are trying to fill
        raw_time = (data['time'][i] -
                    units.epoch_days_since_zero) * 24 * 60 * 60
        raw_date = pytz.utc.localize(datetime.utcfromtimestamp(raw_time))
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wave_summary = Swell(units.Units.metric)
        buoy_data_point.wave_summary.direction = data['dirpwsfc'][i]
        buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(
            buoy_data_point.wave_summary.direction)
        buoy_data_point.wave_summary.wave_height = data['htsgwsfc'][i]
        buoy_data_point.wave_summary.period = data['perpwsfc'][i]

        if data['swell_1'][i] < 9.0e20 and data['swper_1'][i] < 9.0e20 and data['swdir_1'][i] < 9.0e20:
            swell_1 = Swell(units.Units.metric)
            swell_1.direction = data['swdir_1'][i]
            swell_1.compass_direction = units.degree_to_direction(
                swell_1.direction)
            swell_1.wave_height = data['swell_1'][i]
            swell_1.period = data['swper_1'][i]
            buoy_data_point.swell_components.append(swell_1)

        if data['swell_2'][i] < 9.0e20 and data['swper_2'][i] < 9.0e20 and data['swdir_2'][i] < 9.0e20:
            swell_2 = Swell(units.Units.metric)
            swell_2.direction = data['swdir_2'][i]
            swell_2.compass_direction = units.degree_to_direction(
                swell_2.direction)
            swell_2.wave_height = data['swell_2'][i]
            swell_2.period = data['swper_2'][i]
            buoy_data_point.swell_components.append(swell_2)

        if data['wvhgtsfc'][i] < 9.0e20 and data['wvpersfc'][i] < 9.0e20 and data['wvdirsfc'][i] < 9.0e20:
            wind_swell = Swell(units.Units.metric)
            wind_swell.direction = data['wvdirsfc'][i]
            wind_swell.compass_direction = units.degree_to_direction(
                wind_swell.direction)
            wind_swell.wave_height = data['wvhgtsfc'][i]
            wind_swell.period = data['wvpersfc'][i]
            buoy_data_point.swell_components.append(wind_swell)

        buoy_data_point.wind_direction = data['wdirsfc'][i]
        buoy_data_point.wind_compass_direction = units.degree_to_direction(
            buoy_data_point.wind_direction)
        buoy_data_point.wind_speed = data['windsfc'][i]
        return True

    def _to_buoy_data_binary(self, buoy_data_point, data, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = data['TIME'][i]
        raw_date = pytz.utc.localize(raw_date)
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wave_summary = Swell(units.Units.metric)
        buoy_data_point.wave_summary.direction = data['DIRPW'][i]
        buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(
            buoy_data_point.wave_summary.direction)
        buoy_data_point.wave_summary.wave_height = data['HTSGW'][i]
        buoy_data_point.wave_summary.period = data['PERPW'][i]

        if data['SWELL_1'][i] > 0 and data['SWPER_1'][i] > 0 and data['SWDIR_1'][i] > 0:
            swell_1 = Swell(units.Units.metric)
            swell_1.direction = data['SWDIR_1'][i]
            swell_1.compass_direction = units.degree_to_direction(
                swell_1.direction)
            swell_1.wave_height = data['SWELL_1'][i]
            swell_1.period = data['SWPER_1'][i]
            buoy_data_point.swell_components.append(swell_1)

        if data['SWELL_2'][i] > 0 and data['SWPER_2'][i] > 0 and data['SWDIR_2'][i] > 0:
            swell_2 = Swell(units.Units.metric)
            swell_2.direction = data['SWDIR_2'][i]
            swell_2.compass_direction = units.degree_to_direction(
                swell_2.direction)
            swell_2.wave_height = data['SWELL_2'][i]
            swell_2.period = data['SWPER_2'][i]
            buoy_data_point.swell_components.append(swell_2)

        if data['WVHGT'][i] > 0 and data['WVPER'][i] > 0 and data['WVDIR'][i] > 0:
            wind_swell = Swell(units.Units.metric)
            wind_swell.direction = data['WVDIR'][i]
            wind_swell.compass_direction = units.degree_to_direction(
                wind_swell.direction)
            wind_swell.wave_height = data['WVHGT'][i]
            wind_swell.period = data['WVPER'][i]
            buoy_data_point.swell_components.append(wind_swell)

        buoy_data_point.wind_direction = data['WDIR'][i]
        buoy_data_point.wind_compass_direction = units.degree_to_direction(
            buoy_data_point.wind_direction)
        buoy_data_point.wind_speed = data['WIND'][i]

        return True

    def _to_buoy_data_netcdf(self, data):
        buoy_data = []

        time = data['time']
        for i in range(0, len(time)):
            buoy_data_point = BuoyData(unit=units.Units.metric)
            buoy_data_point.date = pytz.utc.localize(time[i])

            buoy_data_point.wave_summary = Swell(units.Units.metric)
            buoy_data_point.wave_summary.direction = data['dirpwsfc'][i].item()
            buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(
                buoy_data_point.wave_summary.direction)
            buoy_data_point.wave_summary.wave_height = data['htsgwsfc'][i].item()
            buoy_data_point.wave_summary.period = data['perpwsfc'][i].item()

            buoy_data_point.wind_speed = data['windsfc'][i].item()
            buoy_data_point.wind_direction = data['wdirsfc'][i].item()
            buoy_data_point.wind_compass_direction = units.degree_to_direction(buoy_data_point.wind_direction)

            if data['swell_1'][i] > 0:
                swell_1 = Swell(units.Units.metric)
                swell_1.direction = data['swdir_1'][i].item()
                swell_1.compass_direction = units.degree_to_direction(
                    swell_1.direction)
                swell_1.wave_height = data['swell_1'][i].item()
                swell_1.period = data['swper_1'][i].item()
                buoy_data_point.swell_components.append(swell_1)

            if data['swell_2'][i] > 0:
                swell_2 = Swell(units.Units.metric)
                swell_2.direction = data['swdir_2'][i].item()
                swell_2.compass_direction = units.degree_to_direction(
                    swell_2.direction)
                swell_2.wave_height = data['swell_2'][i].item()
                swell_2.period = data['swper_2'][i].item()
                buoy_data_point.swell_components.append(swell_2)

            if data['wvhgtsfc'][i] > 0:
                wind_swell = Swell(units.Units.metric)
                wind_swell.direction = data['wvdirsfc'][i].item()
                wind_swell.compass_direction = units.degree_to_direction(
                    wind_swell.direction)
                wind_swell.wave_height = data['wvhgtsfc'][i].item()
                wind_swell.period = data['wvpersfc'][i].item()
                buoy_data_point.swell_components.append(wind_swell)

                buoy_data_point.wind_direction = data['wdirsfc'][i].item()
                buoy_data_point.wind_compass_direction = units.degree_to_direction(
                    buoy_data_point.wind_direction)
                buoy_data_point.wind_speed = data['windsfc'][i].item()

            buoy_data.append(buoy_data_point)

        return buoy_data


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
