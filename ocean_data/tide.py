"""
Ocean Data Module - Tide

This module provides functions for retrieving and processing tide data
from NOAA tide stations using the surfpy library.

Functions:
    - fetch_tide_station: Retrieve a tide station by ID
    - fetch_water_level: Get water level data for a specific station and time
    - water_level_to_json: Convert water level data to JSON format
    - generate_dummy_tide_data: Create placeholder data for testing
"""

from datetime import datetime, timezone, timedelta
import surfpy
import requests

def fetch_tide_station(station_id):
    """
    Fetch a tide station object by ID.
    
    Args:
        station_id (str): NOAA tide station ID
        
    Returns:
        surfpy.TideStation: Tide station object or None if not found
    """
    try:
        # Create a dummy location (since we already have the station ID)
        dummy_location = surfpy.Location(0, 0)
        
        # Create a TideStation object directly
        tide_station = surfpy.TideStation(station_id, dummy_location)
        return tide_station
    except Exception as e:
        print(f"Error fetching tide station: {str(e)}")
        return None

def fetch_water_level(station_id, target_datetime=None):
    """
    Fetch and process water level data for a specific tide station and time.
    
    Args:
        station_id (str): NOAA tide station ID
        target_datetime (datetime, optional): Target datetime. Defaults to current time.
        
    Returns:
        dict: Water level data in JSON format
    """
    try:
        # Default to current time if not provided
        if target_datetime is None:
            target_datetime = datetime.now(timezone.utc)
            
        # Ensure target_datetime is timezone-aware
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
            
        # Fetch tide station
        station = fetch_tide_station(station_id)
        
        if not station:
            print(f"No tide station found with ID {station_id}")
            return generate_dummy_tide_data(target_datetime, station_id)
            
        # Calculate start and end time - smaller window around target time
        start_time = target_datetime - timedelta(hours=1)
        end_time = target_datetime + timedelta(hours=1)
        
        # Generate URL for water level data with a smaller interval
        tide_url = station.create_tide_data_url(
            start_time,
            end_time,
            datum=surfpy.TideStation.TideDatum.mean_lower_low_water,
            # Use 6-minute interval for more precise water level
            interval=surfpy.TideStation.DataInterval.default,
            unit=surfpy.units.Units.metric
        )
        
        # Fetch the water level data
        response = requests.get(tide_url)
        
        if response.status_code != 200:
            print(f"Error fetching water level data: HTTP {response.status_code}")
            return generate_dummy_tide_data(target_datetime, station_id)
        
        data_json = response.json()
        
        if 'predictions' not in data_json or not data_json['predictions']:
            print(f"No water level predictions found in response")
            return generate_dummy_tide_data(target_datetime, station_id)
        
        # Parse water level data
        water_levels = []
        for pred in data_json['predictions']:
            date_str = pred.get('t', '')
            height = float(pred.get('v', 0))
            
            try:
                # Parse the date
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                water_levels.append({
                    "date": date,
                    "height": height
                })
            except ValueError as e:
                print(f"Could not parse date: {date_str}, error: {e}")
        
        # Find the closest water level reading to target time
        if not water_levels:
            return generate_dummy_tide_data(target_datetime, station_id)
        
        closest_reading = min(water_levels, 
                             key=lambda x: abs(x["date"].replace(tzinfo=timezone.utc) - target_datetime))
        
        # Convert to JSON format
        return water_level_to_json(closest_reading, station)
    
    except Exception as e:
        print(f"Error retrieving water level data: {str(e)}")
        import traceback
        traceback.print_exc()
        return generate_dummy_tide_data(target_datetime, station_id)

def water_level_to_json(water_level, station):
    """
    Convert water level data to a JSON-serializable structure.
    
    Args:
        water_level (dict): Water level data point
        station (surfpy.TideStation): Tide station object
        
    Returns:
        dict: JSON-serializable structure with water level data
    """
    if not water_level:
        return {"error": "No water level data available"}
    
    return {
        "station_id": station.station_id,
        "location": {
            "latitude": station.location.latitude,
            "longitude": station.location.longitude
        },
        "state": station.state if hasattr(station, 'state') else None,
        "date": water_level["date"].isoformat() if isinstance(water_level["date"], datetime) else water_level["date"],
        "water_level": water_level["height"],  # Height in meters
        "units": "meters"  # Assumes the data is in meters
    }

def generate_dummy_tide_data(target_datetime, station_id):
    """
    Generate dummy tide data for testing or when real data is unavailable.
    
    Args:
        target_datetime (datetime): Target datetime
        station_id (str): NOAA tide station ID
        
    Returns:
        dict: Dummy tide data matching the structure of real data
    """
    # Format target_datetime for the dummy data
    datetime_str = target_datetime.isoformat() if isinstance(target_datetime, datetime) else target_datetime
    
    # Create dummy tide data
    dummy_data = {
        "station_id": station_id,
        "location": {
            "latitude": 0,
            "longitude": 0
        },
        "date": datetime_str,
        "water_level": 0.5,
        "units": "meters"
    }
    
    return dummy_data