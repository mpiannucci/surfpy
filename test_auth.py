import psycopg2
from database_utils import get_db_connection, get_all_sessions, create_session, get_session, delete_session

def test_database_functions():
    print("Starting database functions test...")
    
    # Step 1: Check database connection
    print("Step 1: Testing database connection...")
    conn = get_db_connection()
    if conn:
        print("Database connection successful!")
        conn.close()
    else:
        print("Failed to connect to database")
        return
    
    # Step 2: Get a user ID from the database manually
    print("\nStep 2: Retrieving a user ID from the database...")
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Try to get any user from the auth.users table
            cur.execute("SELECT id FROM auth.users LIMIT 1")
            user_result = cur.fetchone()
            conn.close()
            
            if not user_result:
                print("No users found in the database. Please create a user in Supabase first.")
                return
                
            test_user_id = user_result[0]
            print(f"Retrieved user ID: {test_user_id}")
            
    except Exception as e:
        print(f"Error retrieving user ID: {str(e)}")
        return
    
    # Step 3: Test creating a session with user_id
    print("\nStep 3: Testing session creation with user_id...")
    test_session = {
        "location": "lido",
        "date": "2025-04-05",
        "time": "10:00:00",
        "session_name": "Test Auth Session",
        "fun_rating": 8
    }
    
    try:
        created_session = create_session(test_session, test_user_id)
        if created_session:
            session_id = created_session["id"]
            print(f"Successfully created test session with ID: {session_id}")
        else:
            print("Failed to create test session")
            return
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return
    
    # Step 4: Test retrieving sessions for user
    print("\nStep 4: Testing session retrieval for user...")
    try:
        sessions = get_all_sessions(test_user_id)
        if sessions:
            print(f"Successfully retrieved {len(sessions)} sessions for user")
            for session in sessions:
                print(f"  - {session.get('session_name', 'Unnamed')} ({session.get('date', 'No date')})")
        else:
            print("No sessions found for user")
    except Exception as e:
        print(f"Error retrieving sessions: {str(e)}")
        return
    
    # Step 5: Test retrieving a specific session
    print("\nStep 5: Testing retrieval of a specific session...")
    try:
        session = get_session(session_id, test_user_id)
        if session:
            print(f"Successfully retrieved session: {session['session_name']}")
        else:
            print("Failed to retrieve specific session")
            return
    except Exception as e:
        print(f"Error retrieving specific session: {str(e)}")
        return
    
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_database_functions()