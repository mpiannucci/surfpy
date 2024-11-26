from .noaamodel import NOAAModel
from .location import Location
from .swell import Swell
from . import units
import pytz


class WaveModel(NOAAModel):

    # https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20230101/18/wave/gridded/gfswave.t18z.atlocn.0p16.f064.grib2
    _base_gfs_wave_grib_url = 'https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{0}/{3}/wave/gridded/{1}.t{3}z.{2}.f{4}.grib2'

    def create_grib_url(self, time_index, location=None):
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
        buoy_data_point.wave_summary.wave_height = data['swh'][i]
        buoy_data_point.wave_summary.period = data['perpw'][i]

        if data['shts'][i] > 0 and data['mpts'][i] > 0 and data['swdir'][i] > 0:
            swell_1 = Swell(units.Units.metric)
            swell_1.direction = data['swdir'][i]
            swell_1.compass_direction = units.degree_to_direction(
                swell_1.direction)
            swell_1.wave_height = data['shts'][i]
            swell_1.period = data['mpts'][i]
            buoy_data_point.swell_components.append(swell_1)

        if data['shts_2'][i] > 0 and data['mpts_2'][i] > 0 and data['swdir_2'][i] > 0:
            swell_2 = Swell(units.Units.metric)
            swell_2.direction = data['swdir_2'][i]
            swell_2.compass_direction = units.degree_to_direction(
                swell_2.direction)
            swell_2.wave_height = data['shts_2'][i]
            swell_2.period = data['mpts_2'][i]
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

# Global wave model with 25 km resolution with range -90:90, 0:359.75
def global_gfs_wave_model_25km():
    return WaveModel(
        name='gfswave',
        subset='global.0p25',
        description='GFS Wave Model: Global 25 km',
        bottom_left=Location(-90.00, 0.00),
        top_right=Location(90.00, 359.75),
        location_resolution=0.25,  # 25 km in degrees
        time_resolution=0.125, # Runs every 3 hours, 3/24 = 0.125
        max_index=384,
        hourly_cutoff_index=0
    )

# Global wave model with 16 km resolution with range -15:52.5, 0:359.83
def global_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='global.0p16',
        description='GFS Wave Model: Global 0.16 degree',
        bottom_left=Location(-15.00, 0.00),
        top_right=Location(52.5, 359.83),
        location_resolution=0.167,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )

# Arctic wave model with 9 km resolution with range 50:90, 0:360
def arctic_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='arctic.9km',
        description='GFS Wave Model: Arctic 9 km',
        bottom_left=Location(50.00, 0.00),
        top_right=Location(90.00, 360.00),
        location_resolution=0.0833,  # 9 km in degrees
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )

# Global south wave model with 25 km resolution with range -10.5:-79.5, 0:359.75
def southern_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='gsouth.0p25',
        description='GFS Wave Model: Southern Hemisphere 0.25 degree',
        bottom_left=Location(-10.5, 0),
        top_right=Location(-79.5, 359.75),
        location_resolution=0.25,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )

# Alaska wave model with 16 km resolution with range 44:75, 140:240
def alaska_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='alaska.0p16',
        description='GFS Wave Model: Alaska 0.16 degree',
        bottom_left=Location(44.00, 140.00),
        top_right=Location(75.00, 240.00),
        location_resolution=0.167,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )

# Atlantic wave model with 16 km resolution with range 0:55, 260:310
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

# Eastern Pacific wave model with 16 km resolution with range -20:30, 130:215
def eastpacific_gfs_wave_model():
    return WaveModel(
        name='gfswave',
        subset='epacif.0p16',
        description='GFS Wave Model: Eastern Pacific 0.16 degree',
        bottom_left=Location(-20.00, 130.00),
        top_right=Location(30.00, 215.00),
        location_resolution=0.167,
        time_resolution=0.125,
        max_index=384,
        hourly_cutoff_index=0
    )

# West coast wave model with 16 km resolution with range 25:50, 210:250
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