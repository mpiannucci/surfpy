
wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

def degree_to_direction(degree):
    # Normalize to a positive float
    degree = abs(degree)

    # ake sure its in the range
    if degree > 361:
        return "NULL"

    wind_index = int((degree+11.25)/22.5 - 0.02)
    if wind_index >= len(wind_directions):
        wind_index = 0
    return wind_directions[wind_index%len(wind_directions)]

def direction_to_degree(direction):
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

class Measurement:
    length = 'length'
    speed = 'speed'
    temperature = 'temperature'
    pressure = 'pressure'

def convert(value, measure, source_unit, dest_unit):
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
    return value

def earths_radius(unit):
    if unit == Units.metric:
        return 6371.0
    elif unit == Units.english:
        return 3956.0
    else:
        return 1.0
