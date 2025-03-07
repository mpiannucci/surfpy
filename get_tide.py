from datetime import datetime, timezone, timedelta
import surfpy
import json
import sys

def fetch_water_level(station_id, target_datetime=None):
    """Fetch water level for a given tide station at a specific time."""
    if target_datetime is None:
        target_datetime = datetime.now(timezone.utc)
    
    # Calculate start and end time - smaller window around target time
    start_time = target_datetime - timedelta(hours=1)
    end_time = target_datetime + timedelta(hours=1)
    
    try:
        # Create a tide station object
        dummy_location = surfpy.Location(0, 0)
        tide_station = surfpy.TideStation(station_id, dummy_location)
        
        # Generate URL for water level data with a smaller interval
        tide_url = tide_station.create_tide_data_url(
            start_time,
            end_time,
            datum=surfpy.TideStation.TideDatum.mean_lower_low_water,
            # Use 6-minute interval for more precise water level
            interval=surfpy.TideStation.DataInterval.default,
            unit=surfpy.units.Units.metric
        )
        
        print(f"Generated URL: {tide_url}")
        
        # Fetch the water level data
        import requests
        response = requests.get(tide_url)
        
        if response.status_code != 200:
            print(f"Error fetching water level data: HTTP {response.status_code}")
            print(f"Response: {response.text}")
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

def water_level_to_json(water_level, station_id):
    """Convert water level data to a JSON-serializable structure."""
    if not water_level:
        return {"error": "No water level data available"}
    
    return {
        "station_id": station_id,
        "date": water_level["date"].isoformat(),
        "water_level": water_level["height"],
        "units": "meters"  # Assuming metric units as specified in the request
    }

def main(station_id, timestamp=None):
    """Main function to get water level for a specific station."""
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
    
    print(f"Fetching water level for station {station_id} closest to {target_datetime}")
    
    # Get water level
    water_level = fetch_water_level(station_id, target_datetime)
    
    if not water_level:
        return {"error": f"No water level data found for station {station_id}"}
    
    # Convert to JSON
    result = water_level_to_json(water_level, station_id)
    return result

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python get_tide.py STATION_ID [TIMESTAMP]")
        print("Example: python get_tide.py 8447930")
        print("Example with timestamp: python get_tide.py 8447930 2023-10-01T12:00:00")
        sys.exit(1)
    
    station_id = sys.argv[1]
    timestamp = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = main(station_id, timestamp)
    print(json.dumps(result, indent=2))