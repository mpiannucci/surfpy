"""
Ocean Data Module - Swell

This module provides functions for retrieving and processing swell data
from NDBC buoys using the surfpy library.
"""

from datetime import datetime, timezone
import surfpy
import math
import json
from typing import List, Dict, Any, Optional, Union

# Import shared utilities
from .utils import find_closest_data, convert_to_utc, meters_to_feet

def fetch_buoy_by_id(buoy_id: str) -> Optional[surfpy.BuoyStation]:
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

def fetch_swell_data(
    buoy_id: str, 
    target_datetime: Optional[datetime] = None, 
    count: int = 500
) -> List[Dict[str, Any]]:
    """
    Fetch swell data for a specific buoy and time.
    
    This function can be used in multiple contexts:
    1. In a Flask API to get data for a specific timestamp
    2. In a data collection script to get data for a specific date range
    
    Args:
        buoy_id (str): NDBC buoy ID
        target_datetime (datetime, optional): Target datetime for fetching specific data.
            If None, returns the most recent data.
        count (int, optional): Number of data points to fetch. Defaults to 500.
        
    Returns:
        list: List of processed swell data points
    """
    try:
        # Ensure target_datetime is timezone-aware
        if target_datetime and target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
            
        # Fetch buoy data
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        station = next((s for s in stations.stations if s.station_id == buoy_id), None)
        
        if not station:
            print(f"No station found with ID {buoy_id}")
            return [generate_dummy_swell_data(target_datetime or datetime.now(timezone.utc))]
            
        # Fetch wave data
        wave_data = station.fetch_wave_spectra_reading(count)
        
        if not wave_data:
            print(f"No wave data found for buoy {buoy_id}")
            return [generate_dummy_swell_data(target_datetime or datetime.now(timezone.utc))]
            
        # If a specific time is requested, find the closest data point
        if target_datetime:
            closest_data = find_closest_data(wave_data, target_datetime)
            if closest_data:
                wave_data = [closest_data]
            else:
                print(f"No matching wave data found for time {target_datetime}")
                return [generate_dummy_swell_data(target_datetime)]
            
        # Convert to JSON format
        return swell_data_to_json(wave_data)
        
    except Exception as e:
        print(f"Error fetching swell data: {str(e)}")
        import traceback
        traceback.print_exc()
        if target_datetime:
            return [generate_dummy_swell_data(target_datetime)]
        else:
            return [generate_dummy_swell_data(datetime.now(timezone.utc))]

def swell_data_to_json(wave_data: List[Any]) -> List[Dict[str, Any]]:
    """
    Convert buoy wave data to JSON format with swell components.
    
    Args:
        wave_data (list): List of buoy data objects
        
    Returns:
        list: JSON-serializable structure with swell components
    """
    wave_json = []
    if wave_data:
        for entry in wave_data:
            swell_data = {}
            for i, swell in enumerate(entry.swell_components):
                # Convert height from meters to feet
                swell_height_feet = meters_to_feet(swell.wave_height)

                swell_data[f"swell_{i+1}"] = {
                    "height": round(swell_height_feet, 2),  # Now in feet
                    "period": swell.period,
                    "direction": swell.direction
                }

            wave_json.append({
                "date": entry.date.isoformat(),
                "swell_components": swell_data,
                "significant_wave_height": meters_to_feet(entry.significant_wave_height) if hasattr(entry, 'significant_wave_height') else None
            })

    return wave_json

def generate_dummy_swell_data(target_datetime: datetime) -> Dict[str, Any]:
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
        "significant_wave_height": 2.5,  # in feet
        "swell_components": {
            "swell_1": {"height": 2.5, "period": 12, "direction": 270},
            "swell_2": {"height": 1.2, "period": 8, "direction": 295}
        }
    }
    
    return dummy_data

def process_swell_response(swell_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process swell data for API response.
    
    This function is used by the Flask API to format the response.
    
    Args:
        swell_data (list): List of swell data points from fetch_swell_data
        
    Returns:
        dict: Formatted API response
    """
    if not swell_data:
        return {"error": "No swell data available"}
    
    # Get the first data point (which should be the closest to the requested time)
    data = swell_data[0]
    
    # Format for API response
    response = {
        "timestamp": data["date"],
        "swell_components": data["swell_components"],
        "significant_wave_height": data.get("significant_wave_height")
    }
    
    return response