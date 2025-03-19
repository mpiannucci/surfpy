from datetime import datetime, timezone
import surfpy
import json
import sys
import math

def find_closest_buoy(latitude, longitude, active=True):
    """Find the closest buoy to a given location."""
    location = surfpy.Location(latitude, longitude)
    
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    
    # Find closest active buoy
    closest_buoy = stations.find_closest_buoy(
        location, 
        active=active,
        buoy_type=surfpy.BuoyStation.BuoyType.buoy
    )
    
    return closest_buoy

def fetch_meteorological_data(buoy, count=500):
    """Fetch meteorological data for a given buoy."""
    if not buoy:
        return None
        
    try:
        met_data = buoy.fetch_meteorological_reading(count)
        
        if not met_data:
            # Try fetch_latest_reading as an alternative
            latest_data = buoy.fetch_latest_reading()
            if latest_data:
                return [latest_data]
                
        return met_data
    except Exception as e:
        print(f"Error fetching meteorological data: {str(e)}")
        return None

def find_closest_data(data_list, target_datetime):
    """Find the data entry closest to the given target datetime."""
    if not data_list:
        return None
    return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def meteorological_data_to_json(met_data, buoy=None):
    """Convert meteorological data to a JSON-serializable structure."""
    met_json = []
    if met_data:
        for entry in met_data:
            data_point = {"date": entry.date.isoformat() if hasattr(entry, 'date') else datetime.now().isoformat()}
            
            # Handle common meteorological attributes
            for attr in ['wind_speed', 'wind_direction', 'wind_gust', 'pressure', 
                         'air_temperature', 'water_temperature', 'dewpoint_temperature',
                         'visibility', 'pressure_tendency', 'tide']:
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    data_point[attr] = value
            
            met_json.append(data_point)
    
    result = {"meteorological_data": met_json}
    
    # Add buoy info if available
    if buoy:
        result["buoy_info"] = {
            "id": buoy.station_id,
            "location": {
                "latitude": buoy.location.latitude,
                "longitude": buoy.location.longitude
            }
        }
    
    return result

def has_valid_wind_data(met_data):
    """Check if the meteorological data contains valid wind speed values."""
    if not met_data:
        return False
    
    for entry in met_data:
        # Check if wind_speed exists and is not NaN
        if (hasattr(entry, 'wind_speed') and 
            entry.wind_speed is not None and 
            not (isinstance(entry.wind_speed, float) and math.isnan(entry.wind_speed))):
            return True
    
    return False

def main(latitude, longitude):
    """Main function that takes a location and finds closest buoy."""
    target_datetime = datetime.now(timezone.utc)
    count = 500
    
    print(f"Finding closest buoy to location: {latitude}, {longitude}")
    
    # Get all buoy stations (filtering by type will happen in the loop)
    location = surfpy.Location(latitude, longitude)
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    
    # Filter stations to only include type 'buoy'
    buoy_stations = []
    for station in stations.stations:
        # Explicitly check the buoy_type
        if station.buoy_type == surfpy.BuoyStation.BuoyType.buoy:
            buoy_stations.append(station)
    
    # Sort by distance
    nearby_stations = sorted(
        buoy_stations,
        key=lambda s: s.location.distance(location)
    )
    
    if not nearby_stations:
        return {"error": "Could not find any buoy stations in the area"}
    
    # Try buoys until we find one with wind data
    found_wind_data = False
    checked_count = 0
    
    for station in nearby_stations[:10]:  # Check up to 10 buoys
        checked_count += 1
        print(f"Trying buoy {station.station_id} (type: {station.buoy_type})...")
        
        met_data = fetch_meteorological_data(station, count)
        
        if met_data and has_valid_wind_data(met_data):
            print(f"Found buoy {station.station_id} with valid wind data")
            found_wind_data = True
            closest_met = find_closest_data(met_data, target_datetime)
            result = meteorological_data_to_json([closest_met] if closest_met else [], station)
            return result
    
    print(f"Checked {checked_count} buoys, couldn't find any with valid wind data")
    return {"error": "No buoys with valid wind data found"}

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python get_met.py LATITUDE LONGITUDE")
        print("Example: python get_met.py 36.6 -122.0")
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    except ValueError:
        print("Error: Latitude and longitude must be valid numbers")
        sys.exit(1)
    
    result = main(latitude, longitude)
    print(json.dumps(result, indent=2))