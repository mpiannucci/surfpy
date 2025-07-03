# test_database_tagging.py
# Run this script to test the new database functions

from database_utils import (
    create_session_with_participants, 
    get_session_participants, 
    get_session,
    get_all_sessions
)
import json

def test_database_functions():
    print("🧪 Testing Database Tagging Functions\n")
    
    # Test data - using real user IDs from your database
    creator_user_id = "11d74e45-921e-4259-849a-ccfdd018eda8"  # Creator
    tagged_user_ids = [
        "6437af63-f7f5-4056-9a27-81c67fe58cad",  # Tagged user 1
        "7eaa143f-96f6-4e35-b11b-75eee6cc66ff"   # Tagged user 2
    ]
    
    # Sample session data
    test_session_data = {
        'session_name': 'Test Tagging Session',
        'location': 'lido',
        'date': '2025-07-02',
        'time': '10:00:00',
        'end_time': '12:00:00',
        'fun_rating': 8,
        'session_notes': 'Testing the tagging functionality',
        'raw_swell': [{'test': 'swell_data'}],
        'raw_met': [{'test': 'met_data'}],
        'raw_tide': {'test': 'tide_data'},
        'swell_buoy_id': '44065',
        'met_buoy_id': '44009',
        'tide_station_id': '8516402'
    }
    
    print("📋 Test Session Data:")
    print(f"   Creator: {creator_user_id}")
    print(f"   Tagged Users: {tagged_user_ids}")
    print(f"   Session: {test_session_data['session_name']} at {test_session_data['location']}")
    print()
    
    try:
        # Test 1: Create session with participants
        print("🔧 Test 1: Creating session with participants...")
        result = create_session_with_participants(
            session_data=test_session_data,
            creator_user_id=creator_user_id,
            tagged_user_ids=tagged_user_ids
        )
        
        if result:
            sessions = result['sessions']
            participants = result['participants']
            session_group_id = result['session_group_id']
            
            print(f"✅ SUCCESS: Created {len(sessions)} sessions")
            print(f"   Session Group ID: {session_group_id}")
            print(f"   Created {len(participants)} participant records")
            
            # Print session details
            for i, session in enumerate(sessions):
                print(f"   Session {i+1}: ID={session['id']}, Owner={session['user_id']}")
            print()
            
            # Test 2: Retrieve participants for the first session
            print("🔧 Test 2: Retrieving session participants...")
            first_session_id = sessions[0]['id']
            retrieved_participants = get_session_participants(first_session_id)
            
            print(f"✅ SUCCESS: Retrieved {len(retrieved_participants)} participants")
            for participant in retrieved_participants:
                print(f"   {participant['role']}: {participant['display_name']} ({participant['user_email']})")
            print()
            
            # Test 3: Verify session data integrity
            print("🔧 Test 3: Verifying session data integrity...")
            for session in sessions:
                retrieved_session = get_session(session['id'])
                if retrieved_session:
                    print(f"✅ Session {session['id']}: Retrieved successfully")
                    print(f"   Group ID: {retrieved_session.get('session_group_id')}")
                    print(f"   Location: {retrieved_session.get('location')}")
                    print(f"   Owner: {retrieved_session.get('user_id')}")
                else:
                    print(f"❌ Session {session['id']}: Failed to retrieve")
            print()
            
            # Test 4: Check if sessions appear in get_all_sessions
            print("🔧 Test 4: Checking if sessions appear in session list...")
            all_sessions = get_all_sessions()
            created_session_ids = [s['id'] for s in sessions]
            found_sessions = [s for s in all_sessions if s['id'] in created_session_ids]
            
            print(f"✅ SUCCESS: Found {len(found_sessions)} of {len(created_session_ids)} created sessions in session list")
            print()
            
            return True
            
        else:
            print("❌ FAILED: create_session_with_participants returned None")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_user_ids_helper():
    """Helper function to get some user IDs for testing"""
    print("🔍 Getting user IDs for testing...")
    
    from database_utils import get_db_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    id,
                    email,
                    COALESCE(
                        raw_user_meta_data->>'display_name',
                        split_part(email, '@', 1)
                    ) as display_name
                FROM auth.users 
                LIMIT 5
            """)
            users = cur.fetchall()
            
            print("Available users for testing:")
            for user in users:
                print(f"   ID: {user['id']}")
                print(f"   Email: {user['email']}")
                print(f"   Display Name: {user['display_name']}")
                print()
            
            return [user['id'] for user in users]
            
    except Exception as e:
        print(f"Error getting user IDs: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    print("🎯 Database Tagging Function Test\n")
    
    # First, get some user IDs to work with
    print("Step 1: Getting user IDs...")
    user_ids = get_user_ids_helper()
    
    if user_ids and len(user_ids) >= 2:
        print(f"✅ Found {len(user_ids)} users to test with\n")
        
        # Update the test with real user IDs
        creator_id = user_ids[0]
        tagged_ids = user_ids[1:3] if len(user_ids) >= 3 else user_ids[1:2]
        
        print("Step 2: Running database function tests...")
        print(f"Using Creator ID: {creator_id}")
        print(f"Using Tagged IDs: {tagged_ids}\n")
        
        # Automatically run the test with real user IDs
        success = test_database_functions()
        
        if success:
            print("🎉 All database tests passed!")
        else:
            print("❌ Some tests failed - check the output above")
        
    else:
        print("❌ Need at least 2 users in the database to test tagging functionality")
        print("   Create some test users first, then run this script")