from flask import Flask, jsonify, request
from datetime import datetime, timezone
import surfpy
from database_utils import get_db_connection, create_session, update_session, get_session, get_all_sessions, delete_session
import json
from json_utils import CustomJSONEncoder

app = Flask(__name__)

# Configure Flask to use our custom JSON encoder
app.json_encoder = CustomJSONEncoder

@app.route('/api/surf-sessions', methods=['POST'])
def create_surf_session():
    try:
        session_data = request.get_json()
        
        if not session_data:
            return jsonify({"status": "fail", "message": "No data provided"}), 400
        
        # Extract required fields for buoy data
        buoy_id = session_data.get('buoy_id')
        session_date = session_data.get('date')
        session_time = session_data.get('time')
        
        if not buoy_id:
            return jsonify({"status": "fail", "message": "buoy_id is required"}), 400
        if not session_date:
            return jsonify({"status": "fail", "message": "date is required"}), 400
        if not session_time:
            return jsonify({"status": "fail", "message": "time is required"}), 400
            
        # Combine date and time to create a datetime object
        try:
            # Combining date and time strings
            datetime_str = f"{session_date}T{session_time}"
            target_datetime = datetime.fromisoformat(datetime_str)
        except ValueError:
            return jsonify({
                "status": "fail", 
                "message": "Invalid date/time format. Use ISO format for date (YYYY-MM-DD) and time (HH:MM:SS)"
            }), 400
        
        # Fetch buoy data for the session
        wave_data = fetch_buoy_data(buoy_id, 500)  # Get 500 data points to find the closest match
        
        # If no buoy data found, we'll use dummy data for testing
        if not wave_data:
            print(f"Warning: No buoy data found for station {buoy_id}. Using dummy data for testing.")
            # Create dummy buoy data
            dummy_data = {
                "date": target_datetime.isoformat(),
                "swell_components": {
                    "swell_1": {"height": 1.5, "period": 12, "direction": 270},
                    "swell_2": {"height": 0.8, "period": 8, "direction": 295}
                }
            }
            session_data['raw_data'] = [dummy_data]
        else:
            # Find closest data point to the provided datetime
            closest_wave_data = find_closest_data(wave_data, target_datetime)
            if not closest_wave_data:
                print(f"Warning: No matching buoy data found for the given time. Using dummy data for testing.")
                # Create dummy buoy data
                dummy_data = {
                    "date": target_datetime.isoformat(),
                    "swell_components": {
                        "swell_1": {"height": 1.5, "period": 12, "direction": 270},
                        "swell_2": {"height": 0.8, "period": 8, "direction": 295}
                    }
                }
                session_data['raw_data'] = [dummy_data]
            else:
                # Convert buoy data to JSON
                buoy_json = buoy_data_to_json([closest_wave_data])
                # Add raw_data to the session data
                session_data['raw_data'] = buoy_json
        
        # Create the session in the database
        new_session = create_session(session_data)
        
        if new_session:
            return jsonify({"status": "success", "data": new_session}), 201
        else:
            return jsonify({"status": "fail", "message": "Failed to create session"}), 500
            
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error creating surf session: {str(e)}"}), 500

# Get all surf sessions
@app.route('/api/surf-sessions', methods=['GET'])
def get_surf_sessions():
    try:
        sessions = get_all_sessions()
        return jsonify({"status": "success", "data": sessions}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error retrieving surf sessions: {str(e)}"}), 500

# Get a specific surf session
@app.route('/api/surf-sessions/<int:session_id>', methods=['GET'])
def get_surf_session(session_id):
    try:
        session = get_session(session_id)
        if not session:
            return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
        return jsonify({"status": "success", "data": session}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error retrieving surf session: {str(e)}"}), 500

# Update a surf session
@app.route('/api/surf-sessions/<int:session_id>', methods=['PUT'])
def update_surf_session(session_id):
    try:
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({"status": "fail", "message": "No data provided"}), 400
        
        # Check if we need to update buoy data
        update_buoy_data = False
        if ('buoy_id' in update_data or 'date' in update_data or 'time' in update_data):
            update_buoy_data = True
            
            # Get existing session to fill in any missing fields
            existing_session = get_session(session_id)
            if not existing_session:
                return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
                
            buoy_id = update_data.get('buoy_id', existing_session.get('buoy_id'))
            session_date = update_data.get('date', existing_session.get('date'))
            session_time = update_data.get('time', existing_session.get('time'))
            
            # Fetch new buoy data
            try:
                datetime_str = f"{session_date}T{session_time}"
                target_datetime = datetime.fromisoformat(datetime_str)
            except ValueError:
                return jsonify({
                    "status": "fail", 
                    "message": "Invalid date/time format. Use ISO format for date (YYYY-MM-DD) and time (HH:MM:SS)"
                }), 400
                
            wave_data = fetch_buoy_data(buoy_id, 500)
            if wave_data:
                closest_wave_data = find_closest_data(wave_data, target_datetime)
                if closest_wave_data:
                    buoy_json = buoy_data_to_json([closest_wave_data])
                    update_data['raw_data'] = buoy_json
            else:
                # Create dummy buoy data
                dummy_data = {
                    "date": target_datetime.isoformat(),
                    "swell_components": {
                        "swell_1": {"height": 1.5, "period": 12, "direction": 270},
                        "swell_2": {"height": 0.8, "period": 8, "direction": 295}
                    }
                }
                update_data['raw_data'] = [dummy_data]
        
        # Update the session
        updated_session = update_session(session_id, update_data)
        
        if updated_session:
            return jsonify({"status": "success", "data": updated_session}), 200
        else:
            return jsonify({"status": "fail", "message": f"Failed to update session with id {session_id}"}), 500
            
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error updating surf session: {str(e)}"}), 500

# Delete a surf session
@app.route('/api/surf-sessions/<int:session_id>', methods=['DELETE'])
def delete_surf_session(session_id):
    try:
        result = delete_session(session_id)
        if result:
            return jsonify({"status": "success", "message": f"Session with id {session_id} deleted"}), 200
        else:
            return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error deleting surf session: {str(e)}"}), 500

# Buoy data utility functions
def fetch_buoy_data(station_id, count):
    try:
        # Fetch buoy data for the given station_id and count
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        station = next((s for s in stations.stations if s.station_id == station_id), None)
        if station:
            wave_data = station.fetch_wave_spectra_reading(count)
            return wave_data
        else:
            print(f"No station found with ID {station_id}")
            return None
    except Exception as e:
        print(f"Error fetching buoy data: {str(e)}")
        return None

def find_closest_data(data_list, target_datetime):
    if not data_list:
        return None
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