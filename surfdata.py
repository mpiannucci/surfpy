import os
from datetime import datetime, timezone
import surfpy

def fetch_buoy_data(station_id, count):
    # Fetch buoy data for the given station_id and count
    # station_id: identifier for the buoy station
    # count: number of historical readings to fetch
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    station = next((s for s in stations.stations if s.station_id == station_id), None)
    if station:
        wave_data = station.fetch_wave_spectra_reading(count)
        # met_data = station.fetch_meteorological_reading(count)
        return wave_data
    else:
        print(f"No station found with ID {station_id}")
        return None, None

def find_closest_data(data_list, target_datetime):
    # Find the data entry closest to the given target datetime
    # Make sure the entry.date is timezone-aware
    return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def buoy_data_to_json(wave_data):
    # Convert buoy data to a JSON-serializable structure
    wave_json = []
    if wave_data:
        for entry in wave_data:
            swell_data = {f"swell_{i+1}": {"height": swell.wave_height, "period": swell.period, "direction": swell.direction}
                          for i, swell in enumerate(entry.swell_components)}
            wave_json.append({
                "date": entry.date.isoformat(),
                "swell_components": swell_data
            })

    # met_json = []
    # if met_data:
    #     for entry in met_data:
    #         met_json.append({
    #             "date": entry.date.isoformat(),
    #             "wind_speed": entry.wind_speed,
    #             "wind_direction": entry.wind_direction
    #         })

    return wave_json

def main():
    # Fetch buoy data for a given station_id, target_datetime, and count
    station_id = '44097'
    target_datetime_str = ''
    count = 500

    if target_datetime_str:
        target_datetime = datetime.fromisoformat(target_datetime_str)
    else:
        target_datetime = datetime.now(timezone.utc)

    print(f"Fetching buoy data for station_id: {station_id}, count: {count}")
    wave_data = fetch_buoy_data(station_id, count)

    if wave_data:
        closest_wave_data = find_closest_data(wave_data, target_datetime)
        # print(f"Closest wave data: {closest_wave_data}")
    else:
        closest_wave_data = None
        print("No wave data found")


    # if met_data:
    #     closest_met_data = find_closest_data(met_data, target_datetime)
    #     # print(f"Closest met data: {closest_met_data}")
    # else:
    #     closest_met_data = None
    #     print("No met data found")


    buoy_data_json = buoy_data_to_json([closest_wave_data] if closest_wave_data else [])

    print(buoy_data_json)

if __name__ == '__main__':
    main()