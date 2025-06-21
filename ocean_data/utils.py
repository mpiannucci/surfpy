"""
Ocean Data Module - Utilities

This module provides shared utility functions for working with oceanographic data.

Functions:
    - find_closest_data: Find data point closest to a specific time
    - convert_to_utc: Ensure datetime is in UTC
    - meters_to_feet: Convert measurements from meters to feet
    - mps_to_knots: Convert wind speed from m/s to knots
    - celsius_to_fahrenheit: Convert temperature from Celsius to Fahrenheit
    - convert_met_data_to_imperial: Convert all meteorological data to imperial units
"""

from datetime import datetime, timezone
import math

def find_closest_data(data_list, target_datetime):
    """
    Find the data entry closest to the given target datetime.
    
    Args:
        data_list (list): List of data objects with date attribute
        target_datetime (datetime): Target datetime (timezone-aware)
        
    Returns:
        object: Data object closest to the target time or None if no data
    """
    if not data_list:
        return None
        
    # Ensure target_datetime is timezone-aware
    if target_datetime.tzinfo is None:
        target_datetime = target_datetime.replace(tzinfo=timezone.utc)
        
    # Find the closest entry by time difference
    return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def convert_to_utc(dt):
    """
    Ensure a datetime is in UTC timezone.
    
    Args:
        dt (datetime): Input datetime
        
    Returns:
        datetime: Timezone-aware datetime in UTC
    """
    if dt.tzinfo is None:
        # Assume UTC if no timezone is specified
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC if in a different timezone
        return dt.astimezone(timezone.utc)

def meters_to_feet(meters):
    """
    Convert measurement from meters to feet.
    
    Args:
        meters (float): Measurement in meters
        
    Returns:
        float: Measurement in feet
    """
    METERS_TO_FEET = 3.28084
    return meters * METERS_TO_FEET

def mps_to_knots(mps):
    """
    Convert wind speed from meters per second to knots.
    
    Args:
        mps (float): Wind speed in meters per second
        
    Returns:
        float: Wind speed in knots
    """
    MPS_TO_KNOTS = 1.94384
    return mps * MPS_TO_KNOTS

def celsius_to_fahrenheit(celsius):
    """
    Convert temperature from Celsius to Fahrenheit.
    
    Args:
        celsius (float): Temperature in Celsius
        
    Returns:
        float: Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32

def convert_met_data_to_imperial(met_data):
    """
    Convert meteorological data from metric to imperial units.
    
    This function converts wind speeds from m/s to knots and temperatures
    from Celsius to Fahrenheit to match NDBC website display units.
    
    Args:
        met_data (list): List of meteorological data dictionaries
        
    Returns:
        list: Data with imperial units (wind in knots, temperature in °F)
    """
    converted_data = []
    
    for data_point in met_data:
        # Create a copy to avoid modifying the original data
        converted_point = data_point.copy()
        
        # Convert wind speeds from m/s to knots
        wind_fields = ['wind_speed', 'wind_gust']
        for field in wind_fields:
            if field in converted_point and is_valid_data(converted_point[field]):
                converted_point[field] = round(mps_to_knots(converted_point[field]), 1)
        
        # Convert temperatures from Celsius to Fahrenheit
        temp_fields = ['air_temperature', 'water_temperature', 'dewpoint_temperature']
        for field in temp_fields:
            if field in converted_point and is_valid_data(converted_point[field]):
                converted_point[field] = round(celsius_to_fahrenheit(converted_point[field]), 1)
        
        # Pressure remains in hPa (which equals mb - millibars)
        # Wind direction remains in degrees
        
        converted_data.append(converted_point)
    
    return converted_data

def is_valid_data(value):
    """
    Check if a data value is valid (not None or NaN).
    
    Args:
        value: Value to check
        
    Returns:
        bool: True if value is valid, False otherwise
    """
    if value is None:
        return False
        
    if isinstance(value, float) and math.isnan(value):
        return False
        
    return True

def format_date(dt):
    """
    Format datetime object to ISO format string.
    
    Args:
        dt (datetime or str): Datetime object or string
        
    Returns:
        str: ISO formatted datetime string
    """
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt