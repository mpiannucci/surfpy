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
    count: int = 500,
    find_closest_only: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetch swell data for a specific buoy and time.
    
    This function is used in a Flask API to get data for a specific timestamp.
    
    Args:
        buoy_id (str): NDBC buoy ID
        target_datetime (datetime, optional): Target datetime for fetching specific data.
            If None, returns the most recent data.
        count (int, optional): Number of data points to fetch. Defaults to 500.
        find_closest_only (bool, optional): If True, only returns the closest data point to target_datetime.
            If False, returns all data points. Defaults to True.
        
    Returns:
        list: List of processed swell data points
    """
    try:
        if target_datetime and target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
            
        station = fetch_buoy_by_id(buoy_id)
        
        if not station:
            print(f"No station found with ID {buoy_id}")
            return [generate_dummy_swell_data(target_datetime or datetime.now(timezone.utc))]
            
        wave_data = station.fetch_wave_spectra_reading(count)
        
        if not wave_data:
            print(f"No wave data found for buoy {buoy_id}")
            return [generate_dummy_swell_data(target_datetime or datetime.now(timezone.utc))]
            
        if target_datetime and find_closest_only:
            closest_data = find_closest_data(wave_data, target_datetime)
            if closest_data:
                wave_data = [closest_data]
            else:
                print(f"No matching wave data found for time {target_datetime}")
                return [generate_dummy_swell_data(target_datetime)]
            
        return swell_data_to_json(wave_data)
        
    except Exception as e:
        print(f"Error fetching swell data: {str(e)}")
        import traceback
        traceback.print_exc()
        return [generate_dummy_swell_data(target_datetime or datetime.now(timezone.utc))]

def fetch_historical_swell_data(buoy_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Fetch a range of historical swell data from a buoy.
    
    Args:
        buoy_id (str): NDBC buoy ID
        start_date (datetime): The start of the historical period (UTC)
        end_date (datetime): The end of the historical period (UTC)
        
    Returns:
        list: A list of swell data points within the specified range.
    """
    try:
        station = fetch_buoy_by_id(buoy_id)
        if not station:
            print(f"No station found with ID {buoy_id}")
            return []

        # Fetch all available recent readings to ensure we cover the window
        wave_data = station.fetch_wave_spectra_reading() 
        
        if not wave_data:
            print(f"No historical wave data found for buoy {buoy_id}")
            return []

        # Filter the data to the requested time window and return the raw objects
        historical_data = [
            entry for entry in wave_data 
            if start_date <= entry.date.replace(tzinfo=timezone.utc) <= end_date
        ]
        
        return historical_data

    except Exception as e:
        print(f"Error fetching historical swell data: {str(e)}")
        return []

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
                swell_height_feet = meters_to_feet(swell.wave_height)
                swell_data[f"swell_{i+1}"] = {
                    "height": round(swell_height_feet, 2),
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
    """
    return {
        "date": target_datetime.isoformat(),
        "significant_wave_height": 2.5,
        "swell_components": {
            "swell_1": {"height": 2.5, "period": 12, "direction": 270},
            "swell_2": {"height": 1.2, "period": 8, "direction": 295}
        }
    }

def process_swell_response(swell_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process swell data for API response.
    """
    if not swell_data:
        return {"error": "No swell data available"}
    data = swell_data[0]
    return {
        "timestamp": data["date"],
        "swell_components": data["swell_components"],
        "significant_wave_height": data.get("significant_wave_height")
    }
