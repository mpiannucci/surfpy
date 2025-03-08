from datetime import datetime, timezone
import surfpy
import json
import sys

def find_closest_buoy(latitude, longitude, active=True):
    """Find the closest buoy to a given location."""
    location = surfpy.Location(latitude, longitude)
    
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    
    # Find closest active buoy
    closest_buoy = stations.find_closest_buoy(
        location, 
        active=active,
        buoy_type=surfpy.BuoyStation.BuoyType.none
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
                    if value is not None:
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

def main(latitude, longitude):
    """Main function that takes a location and finds closest buoy."""
    target_datetime = datetime.now(timezone.utc)
    count = 500
    
    print(f"Finding closest buoy to location: {latitude}, {longitude}")
    closest_buoy = find_closest_buoy(latitude, longitude)
    
    if not closest_buoy:
        return {"error": "Could not find any active buoys"}
    
    print(f"Found closest buoy: {closest_buoy.station_id} at location: {closest_buoy.location.latitude}, {closest_buoy.location.longitude}")
    
    # Try to get meteorological data
    met_data = fetch_meteorological_data(closest_buoy, count)
    
    if not met_data:
        # Try to find another nearby buoy
        print("Searching for another nearby buoy with meteorological data...")
        location = surfpy.Location(latitude, longitude)
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        
        # Get all stations sorted by distance
        nearby_stations = sorted(
            stations.stations, 
            key=lambda s: s.location.distance(location)
        )
        
        # Skip the first one (it's the closest one we already tried)
        for station in nearby_stations[1:5]:  # Try the next 4 closest buoys
            print(f"Trying buoy {station.station_id}...")
            met_data = fetch_meteorological_data(station, count)
            if met_data:
                closest_buoy = station
                break
    
    if not met_data:
        return {"error": "No meteorological data found for any nearby buoys"}
    
    closest_met = find_closest_data(met_data, target_datetime)
    
    result = meteorological_data_to_json([closest_met] if closest_met else [], closest_buoy)
    return result

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