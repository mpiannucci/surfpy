from datetime import datetime, timezone
import surfpy

def fetch_buoy_data(station_id, count=500):
    """Fetch wave and meteorological data for a given buoy station."""
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    station = next((s for s in stations.stations if s.station_id == station_id), None)
    
    if not station:
        return None, None
        
    wave_data = station.fetch_wave_spectra_reading(count)
    met_data = station.fetch_meteorological_reading(count)
    return wave_data, met_data

def find_closest_data(data_list, target_datetime):
    """Find the data entry closest to the given target datetime."""
    if not data_list:
        return None
    return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def buoy_data_to_json(wave_data, met_data):
    """Convert buoy data to a JSON-serializable structure."""
    wave_json = []
    if wave_data:
        for entry in wave_data:
            swell_data = {
                f"swell_{i+1}": {
                    "height": swell.wave_height, 
                    "period": swell.period, 
                    "direction": swell.direction
                } for i, swell in enumerate(entry.swell_components)
            }
            wave_json.append({
                "date": entry.date.isoformat(),
                "swell_components": swell_data
            })

    met_json = []
    if met_data:
        for entry in met_data:
            met_json.append({
                "date": entry.date.isoformat(),
                "wind_speed": entry.wind_speed,
                "wind_direction": entry.wind_direction
            })

    return {
        "wave_data": wave_json,
        "meteorological_data": met_json
    }

def main(station_id):
    """Main function that takes only the buoy ID as an argument."""
    target_datetime = datetime.now(timezone.utc)
    count = 500
    
    wave_data, met_data = fetch_buoy_data(station_id, count)
    
    if not wave_data:
        return {"error": f"No data found for station {station_id}"}
    
    closest_wave = find_closest_data(wave_data, target_datetime)
    closest_met = find_closest_data(met_data, target_datetime)
    
    result = buoy_data_to_json([closest_wave] if closest_wave else [], 
                               [closest_met] if closest_met else [])
    return result

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python data_avail.py BUOY_ID")
        sys.exit(1)
    
    buoy_id = sys.argv[1]
    result = main(buoy_id)
    print(result)