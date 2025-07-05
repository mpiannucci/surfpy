from flask import Flask, jsonify, request
from datetime import datetime, timezone, timedelta
import surfpy
from database_utils import get_db_connection, create_session, update_session, get_session, get_all_sessions, delete_session, verify_user_session, get_dashboard_stats
import json
from json_utils import CustomJSONEncoder
import math
import requests
import jwt
from functools import wraps
import pytz

# Import ocean data modules
from ocean_data.swell import fetch_swell_data
from ocean_data.meteorology import fetch_meteorological_data
from ocean_data.location import get_buoys_for_location, is_valid_location

app = Flask(__name__)

# Configure Flask to use our custom JSON encoder
app.json_encoder = CustomJSONEncoder

# Configuration for Supabase
SUPABASE_URL = "https://ehrfwjekssrnbgmgxctg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVocmZ3amVrc3NybmJnbWd4Y3RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA4NTc0NDksImV4cCI6MjA1NjQzMzQ0OX0.x0ig53ygst9XSZcsWwh4aDW8_TM9Es-cX-1cRVP0WF4"

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the token from the Authorization header
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Expected format: "Bearer <token>"
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"status": "fail", "message": "Invalid Authorization header format"}), 401
        
        # Check if token exists
        if not token:
            return jsonify({"status": "fail", "message": "Authentication token is missing"}), 401
        
        try:
            # Decode the token (without verification first just to get the user ID)
            payload = jwt.decode(token, options={"verify_signature": False})
            print(f"Decoded token payload: {payload}")  # Debug: print payload
            
            # In Supabase tokens, the user ID is in the 'sub' claim
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({"status": "fail", "message": "Invalid token - no user_id found"}), 401
            
            # For debugging, skip the verify_user_session check
            # if not verify_user_session(token):
            #     return jsonify({"status": "fail", "message": "Invalid or expired token"}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "fail", "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "fail", "message": "Invalid token"}), 401
        
        # Pass the user_id to the route handler
        return f(user_id, *args, **kwargs)
    
    return decorated

# Authentication endpoints
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "fail", "message": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')  # Optional, defaults to empty string
        last_name = data.get('last_name', '')    # Optional, defaults to empty string
        
        if not email or not password:
            return jsonify({"status": "fail", "message": "Email and password are required"}), 400
        
        # Create display name from first and last name
        display_name = f"{first_name} {last_name}".strip()
        if not display_name:
            # If no names provided, use email prefix as fallback
            display_name = email.split('@')[0]
            
        # Use Supabase's REST API for signup
        signup_url = f"{SUPABASE_URL}/auth/v1/signup"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "password": password,
            "data": {  # This goes into raw_user_meta_data
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name
            }
        }
        
        response = requests.post(signup_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "User registered successfully"}), 201
        else:
            return jsonify({"status": "fail", "message": response.json().get('message', 'Registration failed')}), response.status_code
            
    except Exception as e:
        print(f"Error during signup: {str(e)}")
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "fail", "message": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"status": "fail", "message": "Email and password are required"}), 400
            
        # Use Supabase's REST API for login
        login_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "password": password
        }
        
        response = requests.post(login_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            auth_data = response.json()
            return jsonify({
                "status": "success", 
                "data": {
                    "access_token": auth_data.get("access_token"),
                    "refresh_token": auth_data.get("refresh_token"),
                    "user": {
                        "id": auth_data.get("user", {}).get("id"),
                        "email": auth_data.get("user", {}).get("email")
                    }
                }
            }), 200
        else:
            return jsonify({"status": "fail", "message": response.json().get('message', 'Login failed')}), response.status_code
            
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500

# Surf Session endpoints (protected)

@app.route('/api/surf-sessions', methods=['POST'])
@token_required
def create_surf_session(user_id):
    try:
        session_data = request.get_json()
        
        if not session_data:
            return jsonify({"status": "fail", "message": "No data provided"}), 400
        
        # Extract required fields for buoy data
        session_date = session_data.get('date')
        session_time = session_data.get('time')
        end_time = session_data.get('end_time')
        location = session_data.get('location')
        tagged_users = session_data.get('tagged_users', [])  # NEW: Optional tagged users array
        
        # Validate required fields
        if not session_date:
            return jsonify({"status": "fail", "message": "date is required"}), 400
        if not session_time:
            return jsonify({"status": "fail", "message": "time is required"}), 400
        if not end_time:
            return jsonify({"status": "fail", "message": "end_time is required"}), 400
        if not location:
            return jsonify({"status": "fail", "message": "location is required"}), 400

        # NEW: Validate tagged_users if provided
        if tagged_users:
            if not isinstance(tagged_users, list):
                return jsonify({"status": "fail", "message": "tagged_users must be an array"}), 400
            
            # Validate that all tagged user IDs are valid UUIDs and exist
            for tagged_user_id in tagged_users:
                if not tagged_user_id or not isinstance(tagged_user_id, str):
                    return jsonify({"status": "fail", "message": "Invalid user ID in tagged_users"}), 400
                
                # Check if tagged user exists (optional validation)
                try:
                    from database_utils import get_db_connection
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            cur.execute("SELECT id FROM auth.users WHERE id = %s", (tagged_user_id,))
                            if not cur.fetchone():
                                return jsonify({"status": "fail", "message": f"User {tagged_user_id} not found"}), 400
                        conn.close()
                except Exception as e:
                    print(f"Error validating tagged user: {e}")
                    return jsonify({"status": "fail", "message": "Error validating tagged users"}), 400

        # Validate that end_time > time
        try:
            from datetime import time as time_obj
            start_time_obj = time_obj.fromisoformat(session_time)
            end_time_obj = time_obj.fromisoformat(end_time)
            
            if end_time_obj <= start_time_obj:
                return jsonify({
                    "status": "fail", 
                    "message": "end_time must be after start time"
                }), 400
                
        except ValueError:
            return jsonify({
                "status": "fail", 
                "message": "Invalid time format. Use HH:MM:SS format for both time and end_time"
            }), 400

        # Validate location using the ocean_data module
        if not is_valid_location(location):
            return jsonify({
                "status": "fail", 
                "message": f"Invalid location: {location}. Please provide a valid surf spot."
            }), 400
            
        # Get buoy mapping using the ocean_data module
        buoy_mapping = get_buoys_for_location(location)
        swell_buoy_id = buoy_mapping["swell"]
        met_buoy_id = buoy_mapping["met"]
        tide_station_id = buoy_mapping["tide"]

        # Combine date and time to create a datetime object (using start time for oceanographic data)
        try:
            # Combining date and time strings
            datetime_str = f"{session_date}T{session_time}"
            
            # Parse as naive datetime
            naive_datetime = datetime.fromisoformat(datetime_str)
            
            # Assume this is Eastern Time
            eastern = pytz.timezone('America/New_York')
            # Localize to Eastern Time
            localized_datetime = eastern.localize(naive_datetime)
            # Convert to UTC for data retrieval
            target_datetime = localized_datetime.astimezone(timezone.utc)
    
            print(f"Eastern time: {localized_datetime}, converted to UTC: {target_datetime}")
        except ValueError:
            return jsonify({
                "status": "fail", 
                "message": "Invalid date/time format. Use ISO format for date (YYYY-MM-DD) and time (HH:MM:SS)"
            }), 400

        # Fetch oceanographic data (using start time as before)
        swell_data = fetch_swell_data(swell_buoy_id, target_datetime, count=500)
        session_data['raw_swell'] = swell_data
        
        met_data = fetch_meteorological_data(met_buoy_id, target_datetime, count=500, use_imperial_units=True)
        session_data['raw_met'] = met_data

        # Fetch tide station data (keeping original logic for now)
        tide_station = fetch_tide_station(tide_station_id)
        tide_data = fetch_water_level(tide_station, target_datetime)

        # Process tide data (keeping original logic)
        if not tide_data or not tide_station:
            print(f"Warning: No tide data found for station {tide_station_id}. Using dummy data for testing.")
            dummy_tide_data = {
                "station_id": tide_station_id,
                "date": target_datetime.isoformat(),
                "water_level": 1.2,
                "units": "meters"
            }
            session_data['raw_tide'] = dummy_tide_data
        else:
            tide_data_json = water_level_to_json(tide_data, tide_station)
            session_data['raw_tide'] = tide_data_json
# In your surfdata.py file, replace the session creation logic section with this fix:

        # Add buoy IDs to session data
        session_data['swell_buoy_id'] = swell_buoy_id
        session_data['met_buoy_id'] = met_buoy_id
        session_data['tide_station_id'] = tide_station_id
        
        # NEW: Remove tagged_users from session_data before database operations
        # (tagged_users is only for API logic, not database storage)
        if 'tagged_users' in session_data:
            del session_data['tagged_users']
        
        # NEW: Create session with or without participants based on tagged_users
        if tagged_users:
            # Import the new function
            from database_utils import create_session_with_participants
            
            # Create session with tagged participants
            result = create_session_with_participants(session_data, user_id, tagged_users)
            
            if result:
                created_sessions = result['sessions']
                participants = result['participants']
                session_group_id = result['session_group_id']
                
                # Return enhanced response with tagging information
                return jsonify({
                    "status": "success",
                    "message": f"Surf session created successfully with {len(tagged_users)} tagged participants",
                    "data": {
                        "session_group_id": session_group_id,
                        "sessions_created": len(created_sessions),
                        "original_session_id": created_sessions[0]["id"],
                        "tagged_sessions": [
                            {"session_id": s["id"], "user_id": s["user_id"]} 
                            for s in created_sessions[1:]
                        ],
                        "participants": len(participants),
                        "location": location,
                        "date": session_date,
                        "time": session_time,
                        "end_time": end_time,
                        "swell_buoy_id": session_data.get('swell_buoy_id'),
                        "met_buoy_id": session_data.get('met_buoy_id'),
                        "tide_station_id": session_data.get('tide_station_id')
                    }
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to create session with participants"
                }), 500
        else:
            # Original behavior - create single session without tagging
            created_session = create_session(session_data, user_id)
            
            # Return original response format for backward compatibility
            return jsonify({
                "status": "success",
                "message": "Surf session created successfully",
                "data": {
                    "session_id": created_session["id"],
                    "location": location,
                    "date": session_date,
                    "time": session_time,
                    "end_time": end_time,
                    "swell_buoy_id": session_data.get('swell_buoy_id'),
                    "met_buoy_id": session_data.get('met_buoy_id'),
                    "tide_station_id": session_data.get('tide_station_id')
                }
            }), 200


    except Exception as e:
        print(f"Error creating surf session: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

# Get all surf sessions
@app.route('/api/surf-sessions', methods=['GET'])
@token_required
def get_surf_sessions(user_id):
    try:
        # NEW: Check for user_only query parameter
        user_only = request.args.get('user_only', 'false').lower() == 'true'
        
        if user_only:
            # Import and use the new user-specific function
            from database_utils import get_user_sessions
            sessions = get_user_sessions(user_id)
        else:
            # Existing behavior - get all sessions from all users
            sessions = get_all_sessions()
            
        return jsonify({"status": "success", "data": sessions}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error retrieving surf sessions: {str(e)}"}), 500
    
# Get a specific surf session
@app.route('/api/surf-sessions/<int:session_id>', methods=['GET'])
@token_required
def get_surf_session(user_id, session_id):
    try:
        # Get session regardless of user
        session = get_session(session_id)
        if not session:
            return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
        return jsonify({"status": "success", "data": session}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error retrieving surf session: {str(e)}"}), 500

# Update a surf session
# 2. UPDATED UPDATE SESSION ENDPOINT
@app.route('/api/surf-sessions/<int:session_id>', methods=['PUT'])
@token_required
def update_surf_session(user_id, session_id):
    try:
        session_data = request.get_json()
        
        if not session_data:
            return jsonify({"status": "fail", "message": "No data provided"}), 400
        
        # Get existing session
        existing_session = get_session(session_id)
        if not existing_session:
            return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
        
        # Check if user owns this session
        if existing_session.get('user_id') != user_id:
            return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
        
        # Extract fields that might need to be updated
        session_date = session_data.get('date', existing_session.get('date'))
        session_time = session_data.get('time', existing_session.get('time'))
        end_time = session_data.get('end_time', existing_session.get('end_time'))
        location = session_data.get('location', existing_session.get('location'))
        
        # NEW: Validate end_time if provided in update
        if 'time' in session_data or 'end_time' in session_data:
            # Use updated values or fall back to existing values
            start_time_to_check = session_data.get('time', existing_session.get('time'))
            end_time_to_check = session_data.get('end_time', existing_session.get('end_time'))
            
            if start_time_to_check and end_time_to_check:
                try:
                    from datetime import time as time_obj
                    start_time_obj = time_obj.fromisoformat(start_time_to_check)
                    end_time_obj = time_obj.fromisoformat(end_time_to_check)
                    
                    if end_time_obj <= start_time_obj:
                        return jsonify({
                            "status": "fail", 
                            "message": "end_time must be after start time"
                        }), 400
                        
                except ValueError:
                    return jsonify({
                        "status": "fail", 
                        "message": "Invalid time format. Use HH:MM:SS format for both time and end_time"
                    }), 400
        
        if location:
            # Validate location using the ocean_data module
            if not is_valid_location(location):
                return jsonify({
                    "status": "fail", 
                    "message": f"Invalid location: {location}. Please provide a valid surf spot."
                }), 400
                
            # Get buoy mapping using the ocean_data module
            buoy_mapping = get_buoys_for_location(location)
            session_data['swell_buoy_id'] = buoy_mapping["swell"]
            session_data['met_buoy_id'] = buoy_mapping["met"]
            session_data['tide_station_id'] = buoy_mapping["tide"]
        
        # If date or time changed, update buoy data
        if (session_date != existing_session.get('date') or 
            session_time != existing_session.get('time')):
            
            # Create a datetime object from the date and time
            try:
                datetime_str = f"{session_date}T{session_time}"
                naive_datetime = datetime.fromisoformat(datetime_str)
                
                # Convert to Eastern Time, then UTC
                eastern = pytz.timezone('America/New_York')
                localized_datetime = eastern.localize(naive_datetime)
                target_datetime = localized_datetime.astimezone(timezone.utc)
            except ValueError:
                return jsonify({
                    "status": "fail", 
                    "message": "Invalid date/time format. Use ISO format for date (YYYY-MM-DD) and time (HH:MM:SS)"
                }), 400
                
            # Fetch updated oceanographic data
            swell_buoy_id = session_data.get('swell_buoy_id', existing_session.get('swell_buoy_id'))
            if swell_buoy_id:
                swell_data = fetch_swell_data(swell_buoy_id, target_datetime, count=500)
                session_data['raw_swell'] = swell_data
            
            met_buoy_id = session_data.get('met_buoy_id', existing_session.get('met_buoy_id'))
            if met_buoy_id:
                met_data = fetch_meteorological_data(met_buoy_id, target_datetime, count=500, use_imperial_units=True)
                session_data['raw_met'] = met_data
                        
            tide_station_id = session_data.get('tide_station_id', existing_session.get('tide_station_id'))
            if tide_station_id:
                tide_station = fetch_tide_station(tide_station_id)
                tide_data = fetch_water_level(tide_station, target_datetime)
                if tide_data and tide_station:
                    tide_data_json = water_level_to_json(tide_data, tide_station)
                    session_data['raw_tide'] = tide_data_json
        
        # Update the session in the database
        updated_session = update_session(session_id, session_data, user_id)
        
        if updated_session:
            return jsonify({
                "status": "success",
                "message": "Surf session updated successfully",
                "data": {
                    "session_id": session_id,
                    "location": updated_session.get('location'),
                    "date": updated_session.get('date'),
                    "time": updated_session.get('time'),
                    "end_time": updated_session.get('end_time'),  # NEW: Include end_time in response
                    "swell_buoy_id": updated_session.get('swell_buoy_id'),
                    "met_buoy_id": updated_session.get('met_buoy_id'),
                    "tide_station_id": updated_session.get('tide_station_id')
                }
            }), 200
        else:
            return jsonify({"status": "fail", "message": "Failed to update surf session"}), 500
    
    except Exception as e:
        print(f"Error updating surf session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

# Delete a surf session
@app.route('/api/surf-sessions/<int:session_id>', methods=['DELETE'])
@token_required
def delete_surf_session(user_id, session_id):
    try:
        result = delete_session(session_id, user_id)
        if result:
            return jsonify({"status": "success", "message": f"Session with id {session_id} deleted"}), 200
        else:
            return jsonify({"status": "fail", "message": f"Session with id {session_id} not found"}), 404
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "fail", "message": f"Error deleting surf session: {str(e)}"}), 500

@app.route('/api/test', methods=['GET'])
def test_route():
    return jsonify({"status": "success", "message": "API is working"}), 200

# TIDE FUNCTIONS (TO BE REFACTORED LATER)

def fetch_tide_station(station_id):
    """Fetch a tide station object by ID."""
    try:
        # Create a dummy location (since we already have the station ID)
        dummy_location = surfpy.Location(0, 0)
        
        # Create a TideStation object directly
        tide_station = surfpy.TideStation(station_id, dummy_location)
        return tide_station
    except Exception as e:
        print(f"Error fetching tide station: {str(e)}")
        return None

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
    
    # Convert feet to meters if needed (optional)
    FEET_TO_METERS = 0.3048
    
    return {
        "station_id": station.station_id,
        "location": {
            "latitude": station.location.latitude,
            "longitude": station.location.longitude
        },
        "state": station.state if hasattr(station, 'state') else None,
        "date": water_level["date"].isoformat(),
        "water_level": water_level["height"],  # Height in meters
        "units": "meters"  # Assumes the data is in meters
    }

@app.route('/api/dashboard', methods=['GET'])
@token_required
def get_dashboard(user_id):
    try:
        dashboard_data = get_dashboard_stats(user_id)
        
        if dashboard_data is None:
            return jsonify({"status": "fail", "message": "Failed to retrieve dashboard data"}), 500
        
        return jsonify({
            "status": "success",
            "data": dashboard_data
        }), 200
        
    except Exception as e:
        print(f"Error in dashboard endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# User search
@app.route('/api/users/search', methods=['GET'])
@token_required
def search_users(user_id):
    try:
        # Get the search query from URL parameters
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({"status": "fail", "message": "Search query 'q' parameter is required"}), 400
        
        if len(query) < 2:
            return jsonify({"status": "fail", "message": "Search query must be at least 2 characters"}), 400
        
        # Search for users in the database
        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Search across display_name, first_name, last_name, and email
                # Using ILIKE for case-insensitive partial matching
                search_pattern = f"%{query}%"
                
                cur.execute("""
                    SELECT 
                        id as user_id,
                        email,
                        COALESCE(
                            raw_user_meta_data->>'display_name',
                            NULLIF(TRIM(COALESCE(raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(raw_user_meta_data->>'last_name', '')), ''),
                            split_part(email, '@', 1)
                        ) as display_name,
                        raw_user_meta_data->>'first_name' as first_name,
                        raw_user_meta_data->>'last_name' as last_name
                    FROM auth.users 
                    WHERE 
                        -- Search in display_name
                        (raw_user_meta_data->>'display_name' ILIKE %s) OR
                        -- Search in first_name
                        (raw_user_meta_data->>'first_name' ILIKE %s) OR  
                        -- Search in last_name
                        (raw_user_meta_data->>'last_name' ILIKE %s) OR
                        -- Search in email
                        (email ILIKE %s) OR
                        -- Search in combined first + last name
                        (TRIM(COALESCE(raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(raw_user_meta_data->>'last_name', '')) ILIKE %s)
                    AND id != %s  -- Exclude the current user from results
                    ORDER BY 
                        -- Prioritize exact matches in display_name
                        CASE WHEN raw_user_meta_data->>'display_name' ILIKE %s THEN 1 ELSE 2 END,
                        display_name
                    LIMIT 20  -- Limit results to prevent overwhelming the frontend
                """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, user_id, query))
                
                users = cur.fetchall()
                
                # Format the results for the frontend
                results = []
                for user in users:
                    results.append({
                        "user_id": user['user_id'],
                        "display_name": user['display_name'],
                        "email": user['email'],
                        # Optional: include first/last name for additional context
                        "first_name": user.get('first_name'),
                        "last_name": user.get('last_name')
                    })
                
                return jsonify({
                    "status": "success",
                    "data": results,
                    "query": query,
                    "count": len(results)
                }), 200
                
        except Exception as e:
            print(f"Database error in user search: {str(e)}")
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in user search: {str(e)}")
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


# You'll also need to add this import at the top of your file if it's not already there:
from psycopg2.extras import RealDictCursor