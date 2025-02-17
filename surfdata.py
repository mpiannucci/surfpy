import os
from datetime import datetime, timezone
import surfpy

def fetch_buoy_data(station_id, count):
    stations = surfpy.BuoyStations()
    stations.fetch_stations()

    station = next((s for s in stations.stations if s.station_id == station_id), None)
    if station:
        wave_data = station.fetch_wave_spectra_reading(count)
        met_data = station.fetch_meteorological_reading(count)
        return wave_data, met_data
    else:
        print(f"No station found with ID {station_id}")
        return None, None

def find_closest_data(data_list, target_datetime):
    """Find the data entry closest to the given target datetime."""

    def find_closest_data(data_list, target_datetime):
        """Find the data entry closest to the given target datetime."""
        # Make sure the entry.date is timezone-aware
        return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def buoy_data_to_json(wave_data, met_data):
    """Convert buoy data to a JSON-serializable structure."""
    wave_json = []
    if wave_data:
        for entry in wave_data:
            swell_data = {f"swell_{i+1}": {"height": swell.wave_height, "period": swell.period, "direction": swell.direction}
                          for i, swell in enumerate(entry.swell_components)}
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

def get_buoy_data():
    station_id = '44097'
    target_datetime_str = '2025-02-16T12:00:00'
    count = 500

    if target_datetime_str:
        target_datetime = datetime.fromisoformat(target_datetime_str)
    else:
        target_datetime = datetime.now(timezone.utc)

    wave_data, met_data = fetch_buoy_data(station_id, count)

    if wave_data:
        closest_wave_data = find_closest_data(wave_data, target_datetime)
    else:
        closest_wave_data = None

    if met_data:
        closest_met_data = find_closest_data(met_data, target_datetime)
    else:
        closest_met_data = None

    buoy_data_json = buoy_data_to_json([closest_wave_data] if closest_wave_data else [],
                                       [closest_met_data] if closest_met_data else [])

    return buoy_data_json

def main():
    json = get_buoy_data()
    print(json)

if __name__ == '__main__':
    main()