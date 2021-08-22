import math
import datetime
try:
    from netCDF4 import num2date
except:
    def num2date(dates):
        return dates


wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
epoch_days_since_zero = 719164


def degree_to_direction(degree):
    if math.isnan(degree):
        return 'NULL'

    # Normalize to a positive float
    degree = abs(degree)

    # ake sure its in the range
    if degree > 361:
        return 'NULL'

    wind_index = int((degree+11.25)/22.5 - 0.02)
    if wind_index >= len(wind_directions):
        wind_index = 0
    return wind_directions[wind_index%len(wind_directions)]


def direction_to_degree(direction):
    if direction is None:
        return -1.0
    direction = direction.lower()
    if direction == 'n' or direction == 'north':
        return 0.0
    elif direction == 'nne' or direction == 'north-northeast':
        return 22.5
    elif direction == 'ne' or direction == 'northeast':
        return 45.0
    elif direction == 'ene' or direction == 'east-northeast':
        return 67.5
    elif direction == 'e' or direction == 'east':
        return 90.0
    elif direction == 'ese' or direction == 'east-southeast':
        return 112.5
    elif direction == 'se' or direction == 'southeast':
        return 135.0
    elif direction == 'sse' or direction == 'south-southeast':
        return 157.5
    elif direction == 's' or direction == 'south':
        return 180
    elif direction == 'ssw' or direction == 'south-southwest':
        return 202.5
    elif direction == 'sw' or direction == 'southwest':
        return 225
    elif direction == 'wsw' or direction == 'west-southwest':
        return 247.5
    elif direction == 'w' or direction == 'west':
        return 270.0
    elif direction == 'wnw' or direction == 'west-northwest':
        return 292.5
    elif direction == 'nw' or direction == 'northwest':
        return 315.0
    elif direction == 'nnw' or direction == 'north-northwest':
        return 337.5
    else:
        return -1.0


class Units:
    metric = 'metric'
    english = 'english'
    knots = 'knots'
    kelvin = 'kelvin'


class Measurement:
    length = 'length'
    speed = 'speed'
    temperature = 'temperature'
    pressure = 'pressure'
    visibility = 'visibility'
    direction = 'direction'


def convert(value, measure, source_unit, dest_unit):
    if math.isnan(value):
        return value

    if source_unit == Units.metric:
        if measure == Measurement.length:
            if dest_unit == Units.english:
                return value * 3.28
        elif measure == Measurement.speed:
            if dest_unit == Units.english:
                return value * 2.237
            elif dest_unit == Units.knots:
                return value * 1.944
        elif measure == Measurement.temperature:
            if dest_unit == Units.english:
                return (value * (9.0 / 5.0)) + 32.0
        elif measure == Measurement.pressure:
            if dest_unit == Units.english:
                return value / 33.8638
    elif source_unit == Units.english:
        if measure == Measurement.length:
            if dest_unit == Units.metric:
                return value / 3.28
        elif measure == Measurement.speed:
            if dest_unit == Units.metric:
                return value / 2.237
            elif dest_unit == Units.knots:
                return value / 1.15
        elif measure == Measurement.temperature:
            if dest_unit == Units.metric:
                return (value - 32.0) * (5.0 / 9.0)
        elif measure == Measurement.pressure:
            if dest_unit == Units.metric:
                return value * 33.8638
    elif source_unit == Units.knots:
        if measure == Measurement.speed:
            if dest_unit == Units.metric:
                return value * 0.514
            elif dest_unit == Units.english:
                return value * 1.15
    elif source_unit == Units.kelvin:
        if measure == Measurement.temperature:
            if dest_unit == Units.metric:
                return value - 273.15
            elif dest_unit == Units.english:
                return value * (9.0/5.0) - 459.67
    return value


def earths_radius(unit):
    if unit == Units.metric:
        return 6371.0
    elif unit == Units.english:
        return 3956.0
    else:
        return 1.0


def unit_name(source_unit, source_meas, abbrev=True):
    if source_unit == Units.metric:
        if source_meas == Measurement.length:
            if abbrev:
                return 'm'
            else:
                return 'meters'
        elif source_meas == Measurement.speed:
            if abbrev:
                return 'm/s'
            else:
                return 'meters per second'
        elif source_meas == Measurement.temperature:
            if abbrev:
                return u'\xb0C'
            else:
                return u'\xb0 celsius'
        elif source_meas == Measurement.pressure:
            if abbrev:
                return 'hPa'
            else:
                return 'hecta pascals'
        elif source_meas == Measurement.visibility:
            if abbrev:
                return 'nmi'
            else:
                return 'nautical miles'
        elif source_meas == Measurement.direction:
            if abbrev:
                return u'\xb0'
            else:
                return 'degrees'
    elif source_unit == Units.english:
        if source_meas == Measurement.length:
            if abbrev:
                return 'ft'
            else:
                return 'feet'
        elif source_meas == Measurement.speed:
            if abbrev:
                return 'mph'
            else:
                return 'miles per hour'
        elif source_meas == Measurement.temperature:
            if abbrev:
                return u'\xb0F'
            else:
                return u'\xb0 fahrenheit'
        elif source_meas == Measurement.pressure:
            if abbrev:
                return 'in HG'
            else:
                return 'inches mercury'
        elif source_meas == Measurement.visibility:
            if abbrev:
                return 'nmi'
            else:
                return 'nautical miles'
        elif source_meas == Measurement.direction:
            if abbrev:
                return u'\xb0'
            else:
                return 'degrees'
    elif source_unit == Units.knots:
        if source_meas == Measurement.speed:
            if abbrev:
                return 'knt'
            else:
                return 'knots'
    return ''


def convert_netcdf_dates(date_var):
    cvt = num2date(date_var[:], date_var.units)
    return [datetime.datetime(year=x.year, month=x.month, day=x.day, hour=x.hour, minute=x.minute, second=x.second) for x in cvt]
