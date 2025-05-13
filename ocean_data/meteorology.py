"""
Ocean Data Module - Meteorology

This module provides functions for retrieving and processing meteorological data
from NDBC buoys using the surfpy library.

Functions:
    - fetch_met_buoy: Retrieve a meteorological buoy by ID
    - fetch_meteorological_data: Get weather data for a specific buoy and time
    - met_data_to_json: Convert meteorological data to JSON format
    - generate_dummy_met_data: Create placeholder data for testing
"""

from datetime import datetime, timezone
import surfpy
import math

# Import shared utilities
from .utils import find_closest_data

def fetch_met_buoy(buoy_id):
    """
    Fetch a meteorological buoy object by ID.
    
    Args:
        buoy_id (str): NDBC buoy ID
        
    Returns:
        surfpy.BuoyStation: Buoy station object or None if not found
    """
    try:
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        station = next((s for s in stations.stations if s.station_id == buoy_id), None)
        return station
    except Exception as e:
        print(f"Error fetching met buoy: {str(e)}")
        return None

def fetch_meteorological_data(buoy_id, target_datetime, count=500):
    """
    Fetch and process meteorological data for a specific buoy and time.
    
    Args:
        buoy_id (str): NDBC buoy ID
        target_datetime (datetime): Target datetime (timezone-aware)
        count (int, optional): Number of data points to fetch. Defaults to 500.
        
    Returns:
        list: List of processed meteorological data points in JSON format
    """
    try:
        # Ensure target_datetime is timezone-aware
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
            
        # Fetch buoy
        buoy = fetch_met_buoy(buoy_id)
        
        if not buoy:
            print(f"No meteorological buoy found with ID {buoy_id}")
            return [generate_dummy_met_data(target_datetime)]
            
        # Fetch meteorological data
        met_data = buoy.fetch_meteorological_reading(count)
        
        if not met_data:
            # Try fetch_latest_reading as an alternative
            latest_data = buoy.fetch_latest_reading()
            if latest_data:
                met_data = [latest_data]
            else:
                print(f"No meteorological data found for buoy {buoy_id}")
                return [generate_dummy_met_data(target_datetime)]
                
        # Find closest data point to target time
        closest_data = find_closest_data(met_data, target_datetime)
        
        if not closest_data:
            print(f"No matching meteorological data found for time {target_datetime}")
            return [generate_dummy_met_data(target_datetime)]
            
        # Convert to JSON format
        return met_data_to_json([closest_data])
        
    except Exception as e:
        print(f"Error fetching meteorological data: {str(e)}")
        import traceback
        traceback.print_exc()
        return [generate_dummy_met_data(target_datetime)]

def met_data_to_json(met_data):
    """
    Convert meteorological data to JSON format.
    
    Args:
        met_data (list): List of meteorological data objects
        
    Returns:
        list: JSON-serializable structure with meteorological data
    """
    met_json = []
    if met_data:
        for entry in met_data:
            data_point = {
                "date": entry.date.isoformat() if hasattr(entry, 'date') else datetime.now(timezone.utc).isoformat()
            }
            
            # Add meteorological attributes
            for attr in ['wind_speed', 'wind_direction', 'wind_gust', 'pressure', 
                        'air_temperature', 'water_temperature', 'dewpoint_temperature',
                        'visibility', 'pressure_tendency']:
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    # Don't include None or NaN values
                    if value is not None and not (isinstance(value, float) and math.isnan(value)):
                        data_point[attr] = value
            
            met_json.append(data_point)
    
    return met_json

def generate_dummy_met_data(target_datetime):
    """
    Generate dummy meteorological data for testing or when real data is unavailable.
    
    Args:
        target_datetime (datetime): Target datetime
        
    Returns:
        dict: Dummy meteorological data matching the structure of real data
    """
    # Format target_datetime for the dummy data
    datetime_str = target_datetime.isoformat()
    
    # Create dummy meteorological data
    dummy_data = {
        "date": datetime_str,
        "wind_speed": 5.0,
        "wind_direction": 180.0,
        "wind_gust": 7.0,
        "air_temperature": 20.0,
        "water_temperature": 15.0,
        "pressure": 1013.2,
        "dewpoint_temperature": 12.0
    }
    
    return dummy_data