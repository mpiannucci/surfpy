"""
Ocean Data Module - Swell

This module provides functions for retrieving and processing swell data
from NDBC buoys using the surfpy library.

Functions:
    - fetch_buoy_by_id: Retrieve a buoy object by its ID
    - fetch_swell_data: Get wave data for a specific buoy and time
    - find_closest_data: Find data points closest to a specific time
    - swell_data_to_json: Convert buoy data to JSON format
    - generate_dummy_swell_data: Create placeholder data for testing
"""

from datetime import datetime, timezone
import surfpy
import math
import copy

# Import shared utilities
from .utils import find_closest_data

def fetch_buoy_by_id(buoy_id):
    """
    Fetch a buoy object by its ID.
    
    Args:
        buoy_id (str): NDBC buoy ID
        
    Returns:
        surfpy.BuoyStation: Buoy station object or None if not found
    """
    try:
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        return next((s for s in stations.stations if s.station_id == buoy_id), None)
    except Exception as e:
        print(f"Error fetching buoy: {str(e)}")
        return None

def fetch_swell_data(buoy_id, target_datetime, count=500):
    """
    Fetch and process swell data for a specific buoy and time.
    
    Args:
        buoy_id (str): NDBC buoy ID
        target_datetime (datetime): Target datetime (timezone-aware)
        count (int, optional): Number of data points to fetch. Defaults to 500.
        
    Returns:
        list: List of processed swell data points in JSON format
    """
    try:
        # Ensure target_datetime is timezone-aware
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
            
        # Fetch buoy data
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        station = next((s for s in stations.stations if s.station_id == buoy_id), None)
        
        if not station:
            print(f"No station found with ID {buoy_id}")
            return [generate_dummy_swell_data(target_datetime)]
            
        # Fetch wave data
        wave_data = station.fetch_wave_spectra_reading(count)
        
        if not wave_data:
            print(f"No wave data found for buoy {buoy_id}")
            return [generate_dummy_swell_data(target_datetime)]
            
        # Find closest data point to target time
        closest_data = find_closest_data(wave_data, target_datetime)
        
        if not closest_data:
            print(f"No matching wave data found for time {target_datetime}")
            return [generate_dummy_swell_data(target_datetime)]
            
        # Convert to JSON format
        return swell_data_to_json([closest_data])
        
    except Exception as e:
        print(f"Error fetching swell data: {str(e)}")
        import traceback
        traceback.print_exc()
        return [generate_dummy_swell_data(target_datetime)]

def swell_data_to_json(wave_data):
    """
    Convert buoy wave data to JSON format with swell components.
    
    Args:
        wave_data (list): List of buoy data objects
        
    Returns:
        list: JSON-serializable structure with swell components
    """
    # Conversion factor from meters to feet
    METERS_TO_FEET = 3.28084
    
    # Convert buoy data to a JSON-serializable structure
    wave_json = []
    if wave_data:
        for entry in wave_data:
            swell_data = {}
            for i, swell in enumerate(entry.swell_components):
                # Convert height from meters to feet
                swell_height_feet = swell.wave_height * METERS_TO_FEET

                swell_data[f"swell_{i+1}"] = {
                    "height": round(swell_height_feet, 2),  # Now in feet
                    "period": swell.period,
                    "direction": swell.direction
                }

            wave_json.append({
                "date": entry.date.isoformat(),
                "swell_components": swell_data
            })

    return wave_json

def generate_dummy_swell_data(target_datetime):
    """
    Generate dummy swell data for testing or when real data is unavailable.
    
    Args:
        target_datetime (datetime): Target datetime
        
    Returns:
        dict: Dummy swell data matching the structure of real data
    """
    # Format target_datetime for the dummy data
    datetime_str = target_datetime.isoformat()
    
    # Create dummy data with multiple swell components
    dummy_data = {
        "date": datetime_str,
        "swell_components": {
            "swell_1": {"height": 2.5, "period": 12, "direction": 270},
            "swell_2": {"height": 1.2, "period": 8, "direction": 295}
        }
    }
    
    return dummy_data