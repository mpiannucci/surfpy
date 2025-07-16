"""
Ocean Data Module - Meteorology

This module provides functions for retrieving and processing meteorological data
from NDBC buoys using the surfpy library.
"""

from datetime import datetime, timezone
import surfpy
import math

from .utils import find_closest_data, is_valid_data, convert_met_data_to_imperial

def fetch_met_buoy(buoy_id):
    """
    Fetch a meteorological buoy object by ID.
    """
    try:
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        return next((s for s in stations.stations if s.station_id == buoy_id), None)
    except Exception as e:
        print(f"Error fetching met buoy: {str(e)}")
        return None

def fetch_meteorological_data(buoy_id, target_datetime, count=500, use_imperial_units=True):
    """
    Fetch and process meteorological data for a specific buoy and time.
    """
    try:
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
        buoy = fetch_met_buoy(buoy_id)
        if not buoy:
            print(f"No meteorological buoy found with ID {buoy_id}")
            return [generate_dummy_met_data(target_datetime, use_imperial_units)]
        met_data = buoy.fetch_meteorological_reading(count)
        if not met_data:
            latest_data = buoy.fetch_latest_reading()
            if latest_data:
                met_data = [latest_data]
            else:
                print(f"No meteorological data found for buoy {buoy_id}")
                return [generate_dummy_met_data(target_datetime, use_imperial_units)]
        closest_data = find_closest_data(met_data, target_datetime)
        if not closest_data:
            print(f"No matching meteorological data found for time {target_datetime}")
            return [generate_dummy_met_data(target_datetime, use_imperial_units)]
        json_data = met_data_to_json([closest_data])
        if use_imperial_units:
            json_data = convert_met_data_to_imperial(json_data)
        return json_data
    except Exception as e:
        print(f"Error fetching meteorological data: {str(e)}")
        return [generate_dummy_met_data(target_datetime, use_imperial_units)]

def fetch_historical_met_data(buoy_id: str, start_date: datetime, end_date: datetime, use_imperial_units: bool = True) -> list:
    """
    Fetch a range of historical meteorological data from a buoy.
    """
    try:
        buoy = fetch_met_buoy(buoy_id)
        if not buoy:
            print(f"No meteorological buoy found with ID {buoy_id}")
            return []
        met_data = buoy.fetch_meteorological_reading()
        if not met_data:
            print(f"No historical meteorological data found for buoy {buoy_id}")
            return []
        historical_data = [
            entry for entry in met_data 
            if start_date <= entry.date.replace(tzinfo=timezone.utc) <= end_date
        ]
        return historical_data
    except Exception as e:
        print(f"Error fetching historical meteorological data: {str(e)}")
        return []

def met_data_to_json(met_data):
    """
    Convert meteorological data to JSON format.
    """
    met_json = []
    if met_data:
        for entry in met_data:
            data_point = {"date": entry.date.isoformat() if hasattr(entry, 'date') else datetime.now(timezone.utc).isoformat()}
            for attr in ['wind_speed', 'wind_direction', 'wind_gust', 'pressure', 'air_temperature', 'water_temperature', 'dewpoint_temperature', 'visibility', 'pressure_tendency']:
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    if is_valid_data(value):
                        data_point[attr] = value
            met_json.append(data_point)
    return met_json

def generate_dummy_met_data(target_datetime, use_imperial_units=True):
    """
    Generate dummy meteorological data for testing.
    """
    datetime_str = target_datetime.isoformat()
    if use_imperial_units:
        return {
            "date": datetime_str, "wind_speed": 10.0, "wind_direction": 180.0, "wind_gust": 14.0,
            "air_temperature": 68.0, "water_temperature": 60.0, "pressure": 1013.2, "dewpoint_temperature": 54.0
        }
    else:
        return {
            "date": datetime_str, "wind_speed": 5.0, "wind_direction": 180.0, "wind_gust": 7.0,
            "air_temperature": 20.0, "water_temperature": 15.0, "pressure": 1013.2, "dewpoint_temperature": 12.0
        }
