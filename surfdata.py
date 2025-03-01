from flask import Flask, jsonify, request
# import argparse
from datetime import datetime, timezone
import surfpy

app = Flask(__name__)

# In-memory storage for fetched buoy data
buoy_data_storage = []

@app.route('/api/buoy-data', methods=['POST'])
def get_buoy_data():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "fail", "message": "No data provided"}), 400
    
    station_id = data.get('station_id')
    target_datetime_str = data.get('target_datetime')
    count = data.get('count', 500)
    
    if not station_id:
        return jsonify({"status": "fail", "message": "station_id is required"}), 400
    
    # Process the date
    if target_datetime_str:
        try:
            target_datetime = datetime.fromisoformat(target_datetime_str)
        except ValueError:
            return jsonify({"status": "fail", "message": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    else:
        target_datetime = datetime.now(timezone.utc)
    
    try:
        # fetch raw buoy data
        wave_data = fetch_buoy_data(station_id, count)
        
        if wave_data:
            # Find the closest data point to the given timestamp
            closest_wave_data = find_closest_data(wave_data, target_datetime)
            result = buoy_data_to_json([closest_wave_data])

            # Store the processed data
            buoy_data_storage.append({
                "station_id": station_id,
                "target_datetime": target_datetime.isoformat(),
                "wave_data": result
            })

            return jsonify({
                "status": "success",
                "data": buoy_data_storage[-1]  # Return the latest stored data
            })
        else:
            return jsonify({"status": "fail", "message": "No wave data found"}), 404
    except Exception as e:
        return jsonify({"status": "fail", "message": f"Error fetching buoy data: {str(e)}"}), 500

@app.route('/get-all-data', methods=['GET'])
def get_all_data():
    return jsonify({'success': True, 'data': buoy_data_storage})

def fetch_buoy_data(station_id, count):
    # Fetch buoy data for the given station_id and count
    # station_id: identifier for the buoy station
    # count: number of historical readings to fetch
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    station = next((s for s in stations.stations if s.station_id == station_id), None)
    if station:
        wave_data = station.fetch_wave_spectra_reading(count)
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
    return wave_json

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)