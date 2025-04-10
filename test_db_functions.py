import database_utils
import json

def test_modified_functions():
    print("=== Testing Modified Database Functions ===")
    
    # Test get_all_sessions without user_id filter
    print("\nTesting get_all_sessions() without user filter:")
    all_sessions = database_utils.get_all_sessions()
    print(f"Found {len(all_sessions)} total sessions")
    for i, session in enumerate(all_sessions[:3]):  # Show first 3 sessions
        print(f"Session {i+1}: ID={session['id']}, User={session['user_id']}, Name={session.get('session_name', 'N/A')}")
    
    # Test get_session without user_id filter
    if all_sessions:
        session_id = all_sessions[0]['id']
        print(f"\nTesting get_session() without user filter for session ID {session_id}:")
        session = database_utils.get_session(session_id)
        if session:
            print(f"Successfully retrieved session: ID={session['id']}, User={session['user_id']}")
            print(f"Date: {session.get('date')}, Location: {session.get('location')}")
        else:
            print("Failed to retrieve session")
    
    print("\n=== Tests Completed ===")

if __name__ == "__main__":
    test_modified_functions()