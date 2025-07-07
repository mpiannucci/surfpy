"""
Ocean Data Module - Tide

This module provides functions for retrieving and processing tide data
from NOAA tide stations using the surfpy library.

Functions:
    - fetch_tide_station: Retrieve a tide station by ID
    - fetch_tide_data: Get water level data for a specific station and time
    - water_level_to_json: Convert water level data to JSON format
    - generate_dummy_tide_data: Create placeholder data for testing
"""

from datetime import datetime, timezone, timedelta
import surfpy
import requests

# Import shared utilities
from .utils import convert_to_utc, meters_to_feet, is_valid_data, format_date

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

def fetch_tide_data(station_id, target_datetime=None, use_imperial_units=True):
    """
    Fetch and process water level data for a specific tide station and time.
    
    Args:
        station_id (str): NOAA tide station ID
        target_datetime (datetime, optional): Target datetime. Defaults to current time.
        use_imperial_units (bool, optional): Convert to imperial units (feet). Defaults to True.
        
    Returns:
        dict: Water level data in JSON format
    """
    try:
        # Default to current time if not provided
        if target_datetime is None:
            target_datetime = datetime.now(timezone.utc)
            
        # Ensure target_datetime is timezone-aware using utils
        target_datetime = convert_to_utc(target_datetime)
            
        # Fetch tide station
        station = fetch_tide_station(station_id)
        
        if not station:
            print(f"No tide station found with ID {station_id}")
            return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)
            
        # Fetch water level data
        water_level_data = fetch_water_level(station, target_datetime)
        
        if not water_level_data:
            print(f"No water level data found for station {station_id}")
            return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)
            
        # Convert to JSON format
        json_data = water_level_to_json(water_level_data, station, use_imperial_units)
        
        return json_data
    
    except Exception as e:
        print(f"Error retrieving tide data: {str(e)}")
        import traceback
        traceback.print_exc()
        return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)

def fetch_water_level(station, target_datetime):
    """
    Fetch water level for a given tide station at a specific time.
    
    Args:
        station (surfpy.TideStation): Tide station object
        target_datetime (datetime): Target datetime (timezone-aware)
        
    Returns:
        dict: Raw water level data point or None if not found
    """
    try:
        # Calculate start and end time - larger window to ensure we get data
        start_time = target_datetime - timedelta(hours=3)
        end_time = target_datetime + timedelta(hours=3)
        
        print(f"Fetching tide data from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"Target time: {target_datetime.strftime('%Y-%m-%d %H:%M')} UTC")
        
        # Generate URL for water level data with a smaller interval
        tide_url = station.create_tide_data_url(
            start_time,
            end_time,
            datum=surfpy.TideStation.TideDatum.mean_lower_low_water,
            # Use 6-minute interval for more precise water level
            interval=surfpy.TideStation.DataInterval.default,
            unit=surfpy.units.Units.metric
        )
        
        print(f"Tide API URL: {tide_url}")
        
        # Fetch the water level data
        response = requests.get(tide_url)
        
        if response.status_code != 200:
            print(f"Error fetching water level data: HTTP {response.status_code}")
            return None
        
        data_json = response.json()
        
        if 'predictions' not in data_json or not data_json['predictions']:
            print(f"No water level predictions found in response")
            return None
        
        print(f"Retrieved {len(data_json['predictions'])} tide data points")
        
        # Parse water level data
        water_levels = []
        for pred in data_json['predictions']:
            date_str = pred.get('t', '')
            height = float(pred.get('v', 0))
            
            try:
                # Parse the date - NOAA returns UTC times
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                # Make timezone-aware as UTC
                date_utc = date.replace(tzinfo=timezone.utc)
                water_levels.append({
                    "date": date_utc,
                    "height": height  # Height in meters (raw data)
                })
            except ValueError as e:
                print(f"Could not parse date: {date_str}, error: {e}")
        
        # Find the closest water level reading to target time
        if not water_levels:
            print("No valid water level data after parsing")
            return None
        
        # Calculate time differences and find the closest
        time_diffs = []
        for i, wl in enumerate(water_levels):
            diff = abs(wl["date"] - target_datetime)
            time_diffs.append((i, diff.total_seconds(), wl))
        
        # Sort by time difference
        time_diffs.sort(key=lambda x: x[1])
        
        # Get the closest reading
        closest_index, closest_diff_seconds, closest_reading = time_diffs[0]
        
        print(f"Closest reading found:")
        print(f"  Time: {closest_reading['date'].strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"  Height: {closest_reading['height']:.3f} meters")
        print(f"  Time difference: {closest_diff_seconds/60:.1f} minutes")
        
        return closest_reading
    
    except Exception as e:
        print(f"Error retrieving water level data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def water_level_to_json(water_level, station, use_imperial_units=True):
    """
    Convert water level data to a JSON-serializable structure.
    
    Args:
        water_level (dict): Water level data point
        station (surfpy.TideStation): Tide station object
        use_imperial_units (bool, optional): Convert to imperial units (feet). Defaults to True.
        
    Returns:
        dict: JSON-serializable structure with water level data
    """
    if not water_level:
        return {"error": "No water level data available"}
    
    # Get the water level height
    height_meters = water_level["height"]
    
    # Convert units if requested
    if use_imperial_units and is_valid_data(height_meters):
        height_value = round(meters_to_feet(height_meters), 2)
        units = "feet"
    else:
        height_value = height_meters
        units = "meters"
    
    return {
        "station_id": station.station_id,
        "location": {
            "latitude": station.location.latitude,
            "longitude": station.location.longitude
        },
        "state": station.state if hasattr(station, 'state') else None,
        "date": format_date(water_level["date"]),
        "water_level": height_value,
        "units": units
    }

def generate_dummy_tide_data(target_datetime, station_id, use_imperial_units=True):
    """
    Generate dummy tide data for testing or when real data is unavailable.
    
    Args:
        target_datetime (datetime): Target datetime
        station_id (str): NOAA tide station ID
        use_imperial_units (bool, optional): Whether to use imperial units. Defaults to True.
        
    Returns:
        dict: Dummy tide data matching the structure of real data
    """
    # Format target_datetime for the dummy data
    datetime_str = format_date(target_datetime)
    
    if use_imperial_units:
        # Create dummy tide data in imperial units (feet)
        height_value = 3.2  # feet
        units = "feet"
    else:
        # Create dummy tide data in metric units (meters)
        height_value = 1.0  # meters
        units = "meters"
    
    # Create dummy tide data
    dummy_data = {
        "station_id": station_id,
        "location": {
            "latitude": 0,
            "longitude": 0
        },
        "date": datetime_str,
        "water_level": height_value,
        "units": units
    }
    
    return dummy_data