import database_utils
import json
from datetime import datetime

def test_email_inclusion():
    print("=== Testing User Email Inclusion in Database Functions ===")
    
    # Test get_all_sessions with email inclusion
    print("\nTesting get_all_sessions() with email inclusion:")
    all_sessions = database_utils.get_all_sessions()
    
    if not all_sessions:
        print("No sessions found in database.")
        return
    
    print(f"Found {len(all_sessions)} total sessions")
    
    # Check if user_email field exists
    has_email = 'user_email' in all_sessions[0]
    print(f"Sessions include user_email field: {has_email}")
    
    # Display sample data
    for i, session in enumerate(all_sessions[:3]):  # Show first 3 sessions
        user_info = f"User: {session.get('user_email', 'No email')} (ID: {session.get('user_id', 'No ID')})"
        session_info = f"Session: {session.get('session_name', 'Unnamed')} at {session.get('location', 'Unknown location')}"
        date_info = f"Date: {session.get('date', 'No date')}"
        
        print(f"Session {i+1}: {user_info} | {session_info} | {date_info}")
    
    # Test get_session with email inclusion
    if all_sessions:
        session_id = all_sessions[0]['id']
        print(f"\nTesting get_session() with email inclusion for session ID {session_id}:")
        session = database_utils.get_session(session_id)
        
        if not session:
            print(f"Failed to retrieve session with ID {session_id}")
            return
            
        has_email = 'user_email' in session
        print(f"Session includes user_email field: {has_email}")
        
        if has_email:
            print(f"Session details:")
            print(f"  ID: {session['id']}")
            print(f"  Name: {session.get('session_name', 'Unnamed')}")
            print(f"  User Email: {session.get('user_email', 'No email')}")
            print(f"  User ID: {session.get('user_id', 'No ID')}")
            print(f"  Location: {session.get('location', 'Unknown')}")
            print(f"  Date: {session.get('date', 'No date')}")
            print(f"  Rating: {session.get('fun_rating', 'Not rated')}/10")
        else:
            print("Session does not include user_email field")
    
    print("\n=== Tests Completed ===")

if __name__ == "__main__":
    test_email_inclusion()