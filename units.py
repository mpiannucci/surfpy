import math


wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

def degree_to_direction(degree):
    # Normalize to a positive float
    degree = math.abs(degree)

    # ake sure its in the range
    if degree > 361:
        return "NULL"

    wind_index = int((degree+11.25)/22.5 - 0.02)
    if wind_index >= len(wind_directions):
        wind_index = 0
    return wind_directions[wind_index%len(wind_directions)]

def direction_to_degree(direction):
    direction = direction.lower()
    if direction is 'n' or direction is 'north':
        return 0.0
    elif direction is 'nne' or direction is 'north-northeast':
        return 22.5
    elif direction is 'ne' or direction is 'northeast':
        return 45.0
    elif direction is 'ene' or direction is 'east-northeast':
        return 67.5
    elif direction is 'e' or direction is 'east':
        return 90.0
    elif direction is 'ese' or direction is 'east-southeast':
        return 112.5
    elif direction is 'se' or direction is 'southeast':
        return 135.0
    elif direction is 'sse' or direction is 'south-southeast':
        return 157.5
    elif direction is 's' or direction is 'south':
        return 180
    elif direction is 'ssw' or direction is 'south-southwest':
        return 202.5
    elif direction is 'sw' or direction is 'southwest':
        return 225
    elif direction is 'wsw' or direction is 'west-southwest':
        return 247.5
    elif direction is 'w' or direction is 'west':
        return 270.0
    elif direction is 'wnw' or direction is 'west-northwest':
        return 292.5
    elif direction is 'nw' or direction is 'northwest':
        return 315.0
    elif direction is 'nnw' or direction is 'north-northwest':
        return 337.5
    else:
        return -1.0

class Units:
    metric = 'metric'
    english = 'english'
    knots = 'knots'

class Measurement:
    length = 'length'
    speed = 'speed'
    temperature = 'temperature'
    pressure = 'pressure'

def convert(value, measure, source_unit, dest_unit):
    if source_unit is Units.metric:
        if measure is Measurement.length:
            if dest_unit is Units.english:
                return value * 3.28
        elif measure is Measurement.speed:
            if dest_unit is Units.english:
                return value * 2.237
            elif dest_unit is Units.knots:
                return value * 1.944
        elif measure is Measurement.temperature:
            if dest_unit is Units.english:
                return (value * (9.0 / 5.0)) + 32.0
        elif measure is Measurement.pressure:
            if dest_unit is Units.english:
                return value / 33.8638
    elif source_unit is Units.english:
        if measure is Measurement.length:
            if dest_unit is Units.metric:
                return value / 3.28
        elif measure is Measurement.speed:
            if dest_unit is Units.metric:
                return value / 2.237
            elif dest_unit is Units.knots:
                return value / 1.15
        elif measure is Measurement.temperature:
            if dest_unit is Units.metric:
                return (value - 32.0) * (5.0 / 9.0)
        elif measure is Measurement.pressure:
            if dest_unit is Units.metric:
                return value * 33.8638
    elif source_unit is Units.knots:
        if measure is Measurement.speed:
            if dest_unit is Units.metric:
                return value * 0.514
            elif dest_unit is Units.english:
                return value * 1.15
    return value

def earths_radius(unit):
    if unit is Units.metric:
        return 6371.0
    elif unit is Units.english:
        return 3956.0
    else:
        return 1.0
