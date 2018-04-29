from .noaamodel import NOAAModel
from .location import Location
from .swell import Swell
from . import units
from datetime import datetime
import math
import pytz


class WaveModel(NOAAModel):

    _base_multigrid_ascii_url = 'http://nomads.ncep.noaa.gov:9090/dods/wave/mww3/{0}/{1}{0}_{2}.ascii?time[{5}:{6}],dirpwsfc.dirpwsfc[{5}:{6}][{3}][{4}],htsgwsfc.htsgwsfc[{5}:{6}][{3}][{4}],perpwsfc.perpwsfc[{5}:{6}][{3}][{4}],swdir_1.swdir_1[{5}:{6}][{3}][{4}],swdir_2.swdir_2[{5}:{6}][{3}][{4}],swell_1.swell_1[{5}:{6}][{3}][{4}],swell_2.swell_2[{5}:{6}][{3}][{4}],swper_1.swper_1[{5}:{6}][{3}][{4}],swper_2.swper_2[{5}:{6}][{3}][{4}],ugrdsfc.ugrdsfc[{5}:{6}][{3}][{4}],vgrdsfc.vgrdsfc[{5}:{6}][{3}][{4}],wdirsfc.wdirsfc[{5}:{6}][{3}][{4}],windsfc.windsfc[{5}:{6}][{3}][{4}],wvdirsfc.wvdirsfc[{5}:{6}][{3}][{4}],wvhgtsfc.wvhgtsfc[{5}:{6}][{3}][{4}],wvpersfc.wvpersfc[{5}:{6}][{3}][{4}]'
    _base_multigrid_grib_url = 'http://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl?file={0}.t{1}z.f{2}.grib2&all_lev=on&all_var=on&subregion=&leftlon={4}&rightlon={5}&toplat={6}&bottomlat={7}&dir=%2Fmulti_1.{3}'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        url = self._base_multigrid_ascii_url.format(datestring, self.name, hourstring, lat_index, lon_index, start_time_index, end_time_index)
        return url

    def create_grib_url(self, location, time_index):
        model_run_time = self.latest_model_time()
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        hour_str = str(int(time_index*self.time_resolution_hours)).rjust(3, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        url = self._base_multigrid_grib_url.format(self.name, model_run_str, hour_str, date_str, float(math.floor(location.longitude)), float(math.ceil(location.longitude)), float(math.ceil(location.latitude)), float(math.floor(location.latitude)))
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

        buoy_data_point.wave_summary.direction = self.data['dirpwsfc'][i]
        buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(buoy_data_point.wave_summary.direction)
        buoy_data_point.wave_summary.wave_height = self.data['htsgwsfc'][i]
        buoy_data_point.wave_summary.period = self.data['perpwsfc'][i]

        if self.data['swell_1'][i] < 9.0e20 and self.data['swper_1'][i] < 9.0e20 and self.data['swdir_1'][i] < 9.0e20:
            swell_1 = Swell(units.Units.metric)
            swell_1.direction = self.data['swdir_1'][i]
            swell_1.compass_direction = units.degree_to_direction(swell_1.direction)
            swell_1.wave_height = self.data['swell_1'][i]
            swell_1.period = self.data['swper_1'][i]
            buoy_data_point.swell_components.append(swell_1)

        if self.data['swell_2'][i] < 9.0e20 and self.data['swper_2'][i] < 9.0e20 and self.data['swdir_2'][i] < 9.0e20:
            swell_2 = Swell(units.Units.metric)
            swell_2.direction = self.data['swdir_2'][i]
            swell_2.compass_direction = units.degree_to_direction(swell_2.direction)
            swell_2.wave_height = self.data['swell_2'][i]
            swell_2.period = self.data['swper_2'][i]
            buoy_data_point.swell_components.append(swell_2)

        if self.data['wvhgtsfc'][i] < 9.0e20 and self.data['wvpersfc'][i] < 9.0e20 and self.data['wvdirsfc'][i] < 9.0e20:
            wind_swell = Swell(units.Units.metric)
            wind_swell.direction = self.data['wvdirsfc'][i]
            wind_swell.compass_direction = units.degree_to_direction(wind_swell.direction)
            wind_swell.wave_height = self.data['wvhgtsfc'][i]
            wind_swell.period = self.data['wvpersfc'][i]
            buoy_data_point.swell_components.append(wind_swell)

        buoy_data_point.wind_direction = self.data['wdirsfc'][i]
        buoy_data_point.wind_compass_direction = units.degree_to_direction(buoy_data_point.wind_direction)
        buoy_data_point.wind_speed = self.data['windsfc'][i]
        return True

    def _to_buoy_data_binary(self, buoy_data_point, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        raw_date = self.data['TIME'][i]
        raw_date = pytz.utc.localize(datetime.utcfromtimestamp(raw_time))
        if buoy_data_point.date == None:
            buoy_data_point.date = pytz.utc.localize(raw_date)
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wave_summary.direction = self.data['DIRPW'][i]
        buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(buoy_data_point.wave_summary.direction)
        buoy_data_point.wave_summary.wave_height = self.data['HTSGW'][i]
        buoy_data_point.wave_summary.period = self.data['PERPW'][i]

        if self.data['SWELL_1'][i] > 0 and self.data['SWPER_1'][i] > 0 and self.data['SWDIR_1'][i] > 0:
            swell_1 = Swell(units.Units.metric)
            swell_1.direction = self.data['SWDIR_1'][i]
            swell_1.compass_direction = units.degree_to_direction(swell_1.direction)
            swell_1.wave_height = self.data['SWELL_1'][i]
            swell_1.period = self.data['SWPER_1'][i]
            buoy_data_point.swell_components.append(swell_1)

        if self.data['SWELL_2'][i] > 0 and self.data['SWPER_2'][i] > 0 and self.data['SWDIR_2'][i] > 0:
            swell_2 = Swell(units.Units.metric)
            swell_2.direction = self.data['SWDIR_2'][i]
            swell_2.compass_direction = units.degree_to_direction(swell_2.direction)
            swell_2.wave_height = self.data['SWELL_2'][i]
            swell_2.period = self.data['SWPER_2'][i]
            buoy_data_point.swell_components.append(swell_2)

        if self.data['WVHGT'][i] > 0 and self.data['WVPER'][i] > 0 and self.data['WVDIR'][i] > 0:
            wind_swell = Swell(units.Units.metric)
            wind_swell.direction = self.data['WVDIR'][i]
            wind_swell.compass_direction = units.degree_to_direction(wind_swell.direction)
            wind_swell.wave_height = self.data['WVHGT'][i]
            wind_swell.period = self.data['WVPER'][i]
            buoy_data_point.swell_components.append(wind_swell)

        buoy_data_point.wind_direction = self.data['WDIR'][i]
        buoy_data_point.wind_compass_direction = units.degree_to_direction(buoy_data_point.wind_direction)
        buoy_data_point.wind_speed = self.data['WIND'][i]
        return True

def us_east_coast_wave_model():
    return WaveModel('multi_1.at_10m', 'Multi-grid wave model: US East Coast 10 arc-min grid', Location(0.00, 260.00), Location(55.00011, 310.00011), 0.167, 0.125)

def us_west_coast_wave_model():
    return WaveModel('multi_1.wc_10m', 'Multi-grid wave model: US West Coast 10 arc-min grid', Location(25.00, 210.00), Location(50.00005, 250.00008), 0.167, 0.125)

def pacific_islands_wave_model():
    return WaveModel('multi_1.ep_10m', 'Multi-grid wave model: Pacific Islands (including Hawaii) 10 arc-min grid', Location(-20.00, 130.00), Location(30.0001, 215.00017), 0.167, 0.125)
