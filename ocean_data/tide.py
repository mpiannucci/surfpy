"""
Ocean Data Module - Tide

This module provides functions for retrieving and processing tide data
from NOAA tide stations using the surfpy library.
"""

from datetime import datetime, timezone, timedelta
import surfpy
import requests

# Custom class to mimic surfpy.TideData for historical data
class TideData:
    def __init__(self, date, water_level):
        self.date = date
        self.water_level = water_level

from .utils import convert_to_utc, meters_to_feet, is_valid_data, format_date

def fetch_tide_station(station_id):
    """
    Fetch a tide station object by ID.
    """
    try:
        dummy_location = surfpy.Location(0, 0)
        return surfpy.TideStation(station_id, dummy_location)
    except Exception as e:
        print(f"Error fetching tide station: {str(e)}")
        return None

def fetch_tide_data(station_id, target_datetime=None, use_imperial_units=True):
    """
    Fetch and process water level data for a specific tide station and time.
    """
    try:
        if target_datetime is None:
            target_datetime = datetime.now(timezone.utc)
        target_datetime = convert_to_utc(target_datetime)
        station = fetch_tide_station(station_id)
        if not station:
            print(f"No tide station found with ID {station_id}")
            return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)
        water_level_data = fetch_water_level(station, target_datetime)
        if not water_level_data:
            print(f"No water level data found for station {station_id}")
            return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)
        return water_level_to_json(water_level_data, station, use_imperial_units)
    except Exception as e:
        print(f"Error retrieving tide data: {str(e)}")
        return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)

def fetch_historical_tide_data(station_id: str, start_date: datetime, end_date: datetime, use_imperial_units: bool = True) -> list:
    """
    Fetch a range of historical tide data from a station.
    """
    try:
        station = fetch_tide_station(station_id)
        if not station:
            print(f"No tide station found with ID {station_id}")
            return []
        
        # The surfpy tide fetching is already range-based. We will parse the response
        # into TideData objects to match the forecast function's output type.
        tide_url = station.create_tide_data_url(
            start_date, end_date, datum=surfpy.TideStation.TideDatum.mean_lower_low_water,
            interval=surfpy.TideStation.DataInterval.hourly, unit=surfpy.units.Units.metric
        )
        response = requests.get(tide_url)
        if response.status_code != 200:
            return []
        data_json = response.json()
        if 'predictions' not in data_json or not data_json['predictions']:
            return []

        water_levels = []
        for pred in data_json['predictions']:
            date = datetime.strptime(pred.get('t', ''), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            height_meters = float(pred.get('v', 0))
            # Convert to a TideData object for consistency
            tide_obj = TideData(date=date, water_level=height_meters)
            water_levels.append(tide_obj)
        return water_levels

    except Exception as e:
        print(f"Error fetching historical tide data: {str(e)}")
        return []

def fetch_water_level(station, target_datetime):
    """
    Fetch water level for a given tide station at a specific time.
    """
    try:
        start_time = target_datetime - timedelta(hours=3)
        end_time = target_datetime + timedelta(hours=3)
        tide_url = station.create_tide_data_url(
            start_time, end_time, datum=surfpy.TideStation.TideDatum.mean_lower_low_water,
            interval=surfpy.TideStation.DataInterval.default, unit=surfpy.units.Units.metric
        )
        response = requests.get(tide_url)
        if response.status_code != 200:
            return None
        data_json = response.json()
        if 'predictions' not in data_json or not data_json['predictions']:
            return None
        water_levels = []
        for pred in data_json['predictions']:
            date = datetime.strptime(pred.get('t', ''), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            water_levels.append({"date": date, "height": float(pred.get('v', 0))})
        if not water_levels:
            return None
        return min(water_levels, key=lambda x: abs(x["date"] - target_datetime))
    except Exception as e:
        print(f"Error retrieving water level data: {str(e)}")
        return None

def water_level_to_json(water_level, station, use_imperial_units=True):
    """
    Convert water level data to a JSON-serializable structure.
    """
    if not water_level:
        return {"error": "No water level data available"}
    height_meters = water_level["height"]
    if use_imperial_units and is_valid_data(height_meters):
        height_value = round(meters_to_feet(height_meters), 2)
        units = "feet"
    else:
        height_value = height_meters
        units = "meters"
    return {
        "station_id": station.station_id,
        "location": {"latitude": station.location.latitude, "longitude": station.location.longitude},
        "state": station.state if hasattr(station, 'state') else None,
        "date": format_date(water_level["date"]),
        "water_level": height_value,
        "units": units
    }

def generate_dummy_tide_data(target_datetime, station_id, use_imperial_units=True):
    """
    Generate dummy tide data for testing.
    """
    datetime_str = format_date(target_datetime)
    if use_imperial_units:
        height_value, units = 3.2, "feet"
    else:
        height_value, units = 1.0, "meters"
    return {
        "station_id": station_id,
        "location": {"latitude": 0, "longitude": 0},
        "date": datetime_str,
        "water_level": height_value,
        "units": units
    }
