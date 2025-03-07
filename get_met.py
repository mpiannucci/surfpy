from datetime import datetime, timezone
import surfpy
import json

def fetch_meteorological_data(station_id, count=500):
    """Fetch meteorological data for a given buoy station."""
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    station = next((s for s in stations.stations if s.station_id == station_id), None)
    
    if not station:
        return None
        
    met_data = station.fetch_meteorological_reading(count)
    return met_data

def find_closest_data(data_list, target_datetime):
    """Find the data entry closest to the given target datetime."""
    if not data_list:
        return None
    return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def meteorological_data_to_json(met_data):
    """Convert meteorological data to a JSON-serializable structure."""
    met_json = []
    if met_data:
        for entry in met_data:
            met_json.append({
                "date": entry.date.isoformat(),
                "wind_speed": entry.wind_speed,
                "wind_direction": entry.wind_direction,
                "pressure": entry.pressure if hasattr(entry, 'pressure') else None,
                "air_temperature": entry.air_temperature if hasattr(entry, 'air_temperature') else None,
                "water_temperature": entry.water_temperature if hasattr(entry, 'water_temperature') else None
            })

    return {"meteorological_data": met_json}

def main(station_id):
    """Main function that takes only the buoy ID as an argument."""
    target_datetime = datetime.now(timezone.utc)
    count = 500
    
    met_data = fetch_meteorological_data(station_id, count)
    
    if not met_data:
        return {"error": f"No meteorological data found for station {station_id}"}
    
    closest_met = find_closest_data(met_data, target_datetime)
    
    result = meteorological_data_to_json([closest_met] if closest_met else [])
    return result

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python get_meteorological_data.py BUOY_ID")
        sys.exit(1)
    
    buoy_id = sys.argv[1]
    result = main(buoy_id)
    print(json.dumps(result, indent=2))