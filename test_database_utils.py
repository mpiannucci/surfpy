from database_utils import get_all_sessions, get_session, create_session, update_session, delete_session
import json
from datetime import datetime

def test_get_all_sessions():
    print("\n=== Testing get_all_sessions ===")
    sessions = get_all_sessions()
    print(f"Found {len(sessions)} sessions")
    
    # Print first session if available
    if sessions:
        first = sessions[0]
        print("\nFirst session details:")
        for key in ['id', 'session_name', 'location', 'fun_rating']:
            if key in first:
                print(f"  {key}: {first[key]}")
    
    return sessions

def test_get_session(session_id):
    print(f"\n=== Testing get_session with ID: {session_id} ===")
    session = get_session(session_id)
    
    if session:
        print("Session details:")
        for key in ['id', 'session_name', 'location', 'fun_rating', 'time']:
            if key in session:
                print(f"  {key}: {session[key]}")
    else:
        print(f"No session found with ID: {session_id}")
    
    return session

def test_create_session():
    print("\n=== Testing create_session ===")
    
    # Sample NOAA data
    sample_noaa_data = {
        "wave_height": 3.5,
        "period": 12,
        "wind_speed": 8,
        "wind_direction": "NW",
        "timestamp": datetime.now().isoformat()
    }
    
    # Create test data
    new_session = {
        'session_name': f'Test Session {datetime.now().strftime("%H:%M:%S")}',
        'location': 'Mavericks',
        'fun_rating': 5,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'session_notes': 'Created by test script',
        'raw_data': json.dumps(sample_noaa_data)
    }
    
    print("Creating session with data:")
    for key, value in new_session.items():
        if key != 'raw_data':  # Skip printing raw_data for clarity
            print(f"  {key}: {value}")
    
    # Create the session
    created_session = create_session(new_session)
    if created_session:
        print(f"Session created successfully with ID: {created_session['id']}")
    else:
        print("Failed to create session")
    
    return created_session

def test_update_session(session_id):
    print(f"\n=== Testing update_session with ID: {session_id} ===")
    
    # Data to update
    update_data = {
        'fun_rating': 4,
        'session_notes': 'Updated by test script'
    }
    
    print("Updating with data:")
    for key, value in update_data.items():
        print(f"  {key}: {value}")
    
    # Update the session
    updated_session = update_session(session_id, update_data)
    if updated_session:
        print("Session updated successfully")
        print("Updated session details:")
        for key in ['id', 'session_name', 'fun_rating', 'session_notes']:
            if key in updated_session:
                print(f"  {key}: {updated_session[key]}")
    else:
        print(f"Failed to update session with ID: {session_id}")
    
    return updated_session

def test_delete_session(session_id):
    print(f"\n=== Testing delete_session with ID: {session_id} ===")
    
    # Delete the session
    result = delete_session(session_id)
    if result:
        print(f"Session with ID {session_id} deleted successfully")
    else:
        print(f"Failed to delete session with ID: {session_id}")
    
    return result

def run_all_tests():
    print("======= SURF DATABASE FUNCTION TESTS =======")
    
    # Test getting all sessions
    sessions = test_get_all_sessions()
    
    # If there are sessions, test getting a specific one
    if sessions:
        first_id = sessions[0]['id']
        test_get_session(first_id)
    
    # Test creating a session
    new_session = test_create_session()
    
    # If session was created, test updating and then deleting it
    if new_session:
        session_id = new_session['id']
        test_update_session(session_id)
        test_delete_session(session_id)
    
    print("\n======= TESTS COMPLETED =======")

if __name__ == "__main__":
    run_all_tests()