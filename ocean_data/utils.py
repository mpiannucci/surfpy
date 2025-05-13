"""
Ocean Data Module - Utilities

This module provides shared utility functions for working with oceanographic data.

Functions:
    - find_closest_data: Find data point closest to a specific time
    - convert_to_utc: Ensure datetime is in UTC
    - meters_to_feet: Convert measurements from meters to feet
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