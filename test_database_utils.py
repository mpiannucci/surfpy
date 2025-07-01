import sys
import os
from datetime import datetime, time, date
import uuid
import traceback

# Add the directory containing database_utils.py to the Python path
# This assumes database_utils.py is in the same directory as this test script
# If database_utils.py is in a different directory, adjust this path accordingly
# For example, if it's in a 'backend' folder: sys.path.append(os.path.abspath('../backend'))
sys.path.append(os.path.abspath('.'))

try:
    import database_utils
except ImportError:
    print("Error: Could not import database_utils. Make sure database_utils.py is in the same directory or its path is correctly added.")
    sys.exit(1)

def run_tests():
    print("--- Starting database_utils tests ---")

    # IMPORTANT: For testing, you MUST use a user_id that already exists in your Supabase auth.users table.
    # You can find existing user IDs in your Supabase dashboard under Authentication -> Users.
    # Replace 'YOUR_EXISTING_USER_ID_HERE' with an actual UUID from your database.
    test_user_id = "11d74e45-921e-4259-849a-ccfdd018eda8" # Example: "a41dd345-d9a4-4b3f-8be9-16550b5b97b0"
    
    # If you don't have an existing user ID, you'll need to create one via your app's signup
    # or directly in Supabase, then paste its ID here.
    
    if test_user_id == "YOUR_EXISTING_USER_ID_HERE" or not test_user_id:
        print("\nERROR: Please update 'test_user_id' in test_database_utils.py with a valid user ID from your Supabase auth.users table.")
        sys.exit(1)

    print(f"Using test_user_id: {test_user_id}")

    test_session_id = None # To store the ID of the created session

    try:
        # --- Test 1: create_session with end_time ---
        print("\n--- Test 1: Creating a session with end_time ---")
        session_data = {
            'session_name': 'Test Session with End Time',
            'location': 'lido',
            'fun_rating': 9,
            'date': date(2025, 7, 1),
            'time': time(8, 0, 0),  # Start time
            'end_time': time(10, 30, 0), # End time
            'session_notes': 'This is a test session created by the test script.',
            'swell_buoy_id': '44065',
            'met_buoy_id': '44009',
            'tide_station_id': '8516402',
            'raw_swell': [{"height": 2.5, "period": 8, "direction": 180}],
            'raw_met': [{"wind_speed": 10, "wind_direction": 270}],
            'raw_tide': {"water_level": 0.5}
        }

        created_session = database_utils.create_session(session_data, test_user_id)

        assert created_session is not None, "Test 1 Failed: Session creation returned None"
        assert 'id' in created_session, "Test 1 Failed: Created session missing ID"
        assert created_session['session_name'] == 'Test Session with End Time', "Test 1 Failed: Session name mismatch"
        assert created_session['user_id'] == test_user_id, "Test 1 Failed: User ID mismatch"
        
        # Check end_time specifically
        assert 'end_time' in created_session, "Test 1 Failed: Created session missing end_time"
        assert created_session['end_time'] == session_data['end_time'].isoformat(), \
            f"Test 1 Failed: end_time mismatch. Expected {session_data['end_time'].isoformat()}, Got {created_session['end_time']}"
        
        test_session_id = created_session['id']
        print(f"Test 1 Passed: Session created successfully with ID {test_session_id} and end_time {created_session['end_time']}")

        # --- Test 2: get_session to retrieve end_time ---
        print(f"\n--- Test 2: Retrieving session {test_session_id} and checking end_time ---")
        retrieved_session = database_utils.get_session(test_session_id)

        assert retrieved_session is not None, "Test 2 Failed: Session retrieval returned None"
        assert retrieved_session['id'] == test_session_id, "Test 2 Failed: Retrieved session ID mismatch"
        assert retrieved_session['user_id'] == test_user_id, "Test 2 Failed: Retrieved user ID mismatch"
        
        # Check end_time specifically
        assert 'end_time' in retrieved_session, "Test 2 Failed: Retrieved session missing end_time"
        assert retrieved_session['end_time'] == session_data['end_time'].isoformat(), \
            f"Test 2 Failed: Retrieved end_time mismatch. Expected {session_data['end_time'].isoformat()}, Got {retrieved_session['end_time']}"
        
        print(f"Test 2 Passed: Session {test_session_id} retrieved successfully with end_time {retrieved_session['end_time']}")

        # --- Test 3: get_all_sessions to check end_time presence ---
        print("\n--- Test 3: Retrieving all sessions and checking for end_time ---")
        all_sessions = database_utils.get_all_sessions()

        assert isinstance(all_sessions, list), "Test 3 Failed: get_all_sessions did not return a list"
        assert len(all_sessions) > 0, "Test 3 Failed: No sessions retrieved"
        
        found_test_session = False
        for session in all_sessions:
            if session.get('id') == test_session_id:
                found_test_session = True
                assert 'end_time' in session, "Test 3 Failed: Test session in all_sessions missing end_time"
                assert session['end_time'] == session_data['end_time'].isoformat(), \
                    f"Test 3 Failed: end_time mismatch in all_sessions. Expected {session_data['end_time'].isoformat()}, Got {session['end_time']}"
                break
        
        assert found_test_session, "Test 3 Failed: Created test session not found in all_sessions list"
        print("Test 3 Passed: end_time found and correctly formatted in get_all_sessions result.")

        # --- Test 4: update_session to modify end_time ---
        print(f"\n--- Test 4: Updating end_time for session {test_session_id} ---")
        new_end_time = time(11, 45, 0)
        update_data = {
            'end_time': new_end_time
        }
        updated_session = database_utils.update_session(test_session_id, update_data, test_user_id)

        assert updated_session is not None, "Test 4 Failed: Session update returned None"
        assert updated_session['id'] == test_session_id, "Test 4 Failed: Updated session ID mismatch"
        assert updated_session['end_time'] == new_end_time.isoformat(), \
            f"Test 4 Failed: Updated end_time mismatch. Expected {new_end_time.isoformat()}, Got {updated_session['end_time']}"
        
        print(f"Test 4 Passed: Session {test_session_id} updated successfully with new end_time {updated_session['end_time']}")

    except AssertionError as e:
        print(f"Assertion Error: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")
        traceback.print_exc()
    finally:
        # --- Cleanup: delete_session ---
        print(f"\n--- Cleanup: Deleting session {test_session_id} ---")
        if test_session_id:
            deleted = database_utils.delete_session(test_session_id, test_user_id)
            if deleted:
                print(f"Cleanup Passed: Session {test_session_id} deleted successfully.")
                # Verify deletion
                retrieved_after_delete = database_utils.get_session(test_session_id)
                assert retrieved_after_delete is None, "Cleanup Failed: Session still exists after deletion."
            else:
                print(f"Cleanup Failed: Could not delete session {test_session_id}.")
        else:
            print("No session was created to delete during cleanup.")
        print("\n--- Database utils tests finished ---")

if __name__ == "__main__":
    run_tests()
