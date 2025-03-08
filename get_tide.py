from datetime import datetime, timezone, timedelta
import surfpy
import json
import sys

def find_closest_tide_station(latitude, longitude):
    """Find the closest tide station to a given location."""
    location = surfpy.Location(latitude, longitude)
    
    # Fetch all tide stations
    tide_stations = surfpy.TideStations()
    tide_stations.fetch_stations()
    
    # Find closest tide station
    closest_station = tide_stations.find_closest_station(location)
    
    return closest_station

def fetch_water_level(station, target_datetime=None):
    """Fetch water level for a given tide station at a specific time."""
    if target_datetime is None:
        target_datetime = datetime.now(timezone.utc)
    
    # Calculate start and end time - smaller window around target time
    start_time = target_datetime - timedelta(hours=1)
    end_time = target_datetime + timedelta(hours=1)
    
    try:
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
        import requests
        response = requests.get(tide_url)
        
        if response.status_code != 200:
            print(f"Error fetching water level data: HTTP {response.status_code}")
            return None
        
        data_json = response.json()
        
        if 'predictions' not in data_json or not data_json['predictions']:
            print(f"No water level predictions found in response")
            return None
        
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
            return None
        
        closest_reading = min(water_levels, 
                             key=lambda x: abs(x["date"].replace(tzinfo=timezone.utc) - target_datetime))
        
        return closest_reading
    
    except Exception as e:
        print(f"Error retrieving water level data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def water_level_to_json(water_level, station):
    """Convert water level data to a JSON-serializable structure."""
    if not water_level:
        return {"error": "No water level data available"}
    
    return {
        "station_id": station.station_id,
        "location": {
            "latitude": station.location.latitude,
            "longitude": station.location.longitude
        },
        "state": station.state if hasattr(station, "state") else None,
        "date": water_level["date"].isoformat(),
        "water_level": water_level["height"],
        "units": "meters"  # Assuming metric units as specified in the request
    }

def main(latitude, longitude, timestamp=None):
    """Main function to get water level for location."""
    # Parse timestamp or use current time
    if timestamp:
        try:
            target_datetime = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Invalid timestamp format: {timestamp}")
            print("Using current time instead.")
            target_datetime = datetime.now(timezone.utc)
    else:
        target_datetime = datetime.now(timezone.utc)
    
    print(f"Finding closest tide station to location: {latitude}, {longitude}")
    
    # Fetch all tide stations
    tide_stations = surfpy.TideStations()
    tide_stations.fetch_stations()
    
    # Get all stations sorted by distance
    location = surfpy.Location(latitude, longitude)
    nearby_stations = sorted(
        tide_stations.stations,
        key=lambda s: s.location.distance(location)
    )[:5]  # Get the 5 closest stations
    
    if not nearby_stations:
        return {"error": "Could not find any tide stations"}
    
    # Try each station until we get data
    result = None
    for station in nearby_stations:
        print(f"Trying tide station: {station.station_id} at {station.location.latitude}, {station.location.longitude}")
        
        water_level = fetch_water_level(station, target_datetime)
        
        if water_level:
            print(f"Successfully fetched water level data from station {station.station_id}")
            result = water_level_to_json(water_level, station)
            break
    
    if not result:
        return {"error": "No water level data found for any nearby tide stations"}
    
    return result

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python get_tide.py LATITUDE LONGITUDE [TIMESTAMP]")
        print("Example: python get_tide.py 40.7 -74.0")
        print("Example with timestamp: python get_tide.py 40.7 -74.0 2023-10-01T12:00:00")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: Latitude and longitude must be valid numbers")
        sys.exit(1)
    
    timestamp = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = main(latitude, longitude, timestamp)
    print(json.dumps(result, indent=2))