import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from datetime import datetime, time, date
import uuid
from psycopg2.extras import Json

# Database connection string
# db_url = "postgresql://postgres:kooksinthekitchen@db.ehrfwjekssrnbgmgxctg.supabase.co:5432/postgres"
db_url = "postgresql://postgres.ehrfwjekssrnbgmgxctg:kooksinthekitchen@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_all_sessions():
    """Retrieve all surf sessions with user display name information"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all session data plus the user display name from metadata, including end_time
            cur.execute("""
                SELECT s.*, 
                       u.email as user_email,
                       COALESCE(
                           u.raw_user_meta_data->>'display_name',
                           NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                           split_part(u.email, '@', 1)
                       ) as display_name
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
            sessions = cur.fetchall()
            # Convert to a list so we can modify it
            sessions_list = list(sessions)
            
            # Process each session to handle non-serializable types (like time objects)
            for i, session in enumerate(sessions_list):
                # Process time objects (start_time)
                if 'time' in session and isinstance(session['time'], time):
                    sessions_list[i]['time'] = session['time'].isoformat()
                
                # Process end_time objects
                if 'end_time' in session and isinstance(session['end_time'], time):
                    sessions_list[i]['end_time'] = session['end_time'].isoformat()
                
                # Process date objects
                if 'date' in session and isinstance(session['date'], date):
                    sessions_list[i]['date'] = session['date'].isoformat()
            
            return sessions_list
    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()


def get_session(session_id):
    """Retrieve a single surf session including user display name"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Select session details including end_time
            cur.execute("""
                SELECT s.*, 
                       u.email as user_email,
                       COALESCE(
                           u.raw_user_meta_data->>'display_name',
                           NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                           split_part(u.email, '@', 1)
                       ) as display_name
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.id = %s
            """, (session_id,))
            session = cur.fetchone()
            if session:
                # Convert time objects to strings
                if 'time' in session and isinstance(session['time'], time):
                    session['time'] = session['time'].isoformat()
                
                # Convert end_time objects to strings
                if 'end_time' in session and isinstance(session['end_time'], time):
                    session['end_time'] = session['end_time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in session and isinstance(session['date'], date):
                    session['date'] = session['date'].isoformat()
                    
            return session
    except Exception as e:
        print(f"Error retrieving session: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def create_session(session_data, user_id):
    """Create a new surf session in the database for a specific user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check the table structure to understand the ID column
            cur.execute("""
                SELECT column_name, column_default, is_identity 
                FROM information_schema.columns 
                WHERE table_name = 'surf_sessions_duplicate' AND column_name = 'id'
            """)
            id_info = cur.fetchone()
            
            # Find the maximum ID value currently in the table
            cur.execute("SELECT MAX(id) FROM surf_sessions_duplicate")
            max_id_result = cur.fetchone()
            max_id = max_id_result['max'] if max_id_result and 'max' in max_id_result else None
            
            # If max_id is None, start with 1, otherwise use max_id + 1
            next_id = 1 if max_id is None else max_id + 1
            print(f"Using next ID: {next_id}")
            
            # Always include the ID in the data to avoid conflicts
            session_data['id'] = next_id
            
            # Add user_id to the session data
            session_data['user_id'] = user_id
            
            # Handle raw_swell as JSONB
            if 'raw_swell' in session_data:
                session_data['raw_swell'] = Json(session_data['raw_swell'])

            # Handle raw_met as JSONB
            if 'raw_met' in session_data:
                session_data['raw_met'] = Json(session_data['raw_met'])
            
            # Handle raw_tide as JSONB
            if 'raw_tide' in session_data:
                session_data['raw_tide'] = Json(session_data['raw_tide'])

            # Remove created_at if present (it should be automatically generated by the DB)
            if 'created_at' in session_data:
                del session_data['created_at']
                
            columns = ', '.join(session_data.keys())
            placeholders = ', '.join(['%s'] * len(session_data))
            
            query = f"""
            INSERT INTO surf_sessions_duplicate ({columns}) 
            VALUES ({placeholders})
            RETURNING *
            """
            
            cur.execute(query, list(session_data.values()))
            conn.commit()
            
            # Handle serialization for time objects after fetching
            new_session = cur.fetchone()
            if new_session:
                # Convert time objects to strings
                if 'time' in new_session and isinstance(new_session['time'], time):
                    new_session['time'] = new_session['time'].isoformat()
                
                # Convert end_time objects to strings
                if 'end_time' in new_session and isinstance(new_session['end_time'], time):
                    new_session['end_time'] = new_session['end_time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in new_session and isinstance(new_session['date'], date):
                    new_session['date'] = new_session['date'].isoformat()
                    
            return new_session
    except Exception as e:
        print(f"Error creating session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def update_session(session_id, update_data, user_id):
    """Update an existing surf session for a specific user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check if the session belongs to the user
            cur.execute("SELECT id FROM surf_sessions_duplicate WHERE id = %s AND user_id = %s", (session_id, user_id))
            if not cur.fetchone():
                # Session doesn't exist or doesn't belong to user
                return None
            
            # Ensure id, created_at, and user_id aren't in the update data
            if 'id' in update_data:
                del update_data['id']
            if 'created_at' in update_data:
                del update_data['created_at']
            if 'user_id' in update_data:
                del update_data['user_id']  # Prevent user_id from being changed
            
            # Handle raw_swell as JSONB
            if 'raw_swell' in update_data:
                update_data['raw_swell'] = Json(update_data['raw_swell'])
                
            # Handle raw_met as JSONB
            if 'raw_met' in update_data:
                update_data['raw_met'] = Json(update_data['raw_met'])
            
            # Handle raw_tide as JSONB
            if 'raw_tide' in update_data:
                update_data['raw_tide'] = Json(update_data['raw_tide'])

            # Build SET clause for the SQL query
            set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
            
            query = f"""
            UPDATE surf_sessions_duplicate 
            SET {set_clause} 
            WHERE id = %s AND user_id = %s
            RETURNING *
            """
            
            # Add the session_id and user_id as the last parameters
            values = list(update_data.values()) + [session_id, user_id]
            
            cur.execute(query, values)
            conn.commit()
            
            # Handle serialization for time objects after fetching
            updated_session = cur.fetchone()
            if updated_session:
                # Convert time objects to strings
                if 'time' in updated_session and isinstance(updated_session['time'], time):
                    updated_session['time'] = updated_session['time'].isoformat()
                
                # Convert end_time objects to strings
                if 'end_time' in updated_session and isinstance(updated_session['end_time'], time):
                    updated_session['end_time'] = updated_session['end_time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in updated_session and isinstance(updated_session['date'], date):
                    updated_session['date'] = updated_session['date'].isoformat()
                    
            return updated_session
    except Exception as e:
        print(f"Error updating session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def delete_session(session_id, user_id):
    """Delete a surf session by its ID for a specific user"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM surf_sessions_duplicate WHERE id = %s AND user_id = %s RETURNING id", 
                        (session_id, user_id))
            deleted = cur.fetchone()
            conn.commit()
            return deleted is not None
    except Exception as e:
        print(f"Error deleting session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def get_user_by_email(email):
    """Get user details by email"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Query the auth.users table (Supabase's built-in users table)
            cur.execute("SELECT * FROM auth.users WHERE email = %s", (email,))
            user = cur.fetchone()
            return user
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        conn.close()

def verify_user_session(access_token):
    """Verify a user's JWT token and return user_id if valid"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Query Supabase's sessions table to verify the token
            cur.execute("""
                SELECT user_id FROM auth.sessions 
                WHERE token = %s AND expires_at > NOW()
            """, (access_token,))
            session = cur.fetchone()
            if session:
                return session['user_id']
            return None
    except Exception as e:
        print(f"Error verifying user session: {e}")
        return None
    finally:
        conn.close()

def get_dashboard_stats(current_user_id):
    """Get comprehensive dashboard statistics for current user, other users, and community"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get current year for filtering
            current_year = datetime.now().year
            
            # 1. CURRENT USER STATS (Enhanced with time calculations)
            cur.execute("""
                SELECT 
                    -- All-time stats
                    COUNT(*) as total_sessions_all_time,
                    
                    -- This year stats
                    COUNT(CASE WHEN EXTRACT(YEAR FROM date) = %s THEN 1 END) as total_sessions_this_year,
                    
                    -- Sessions per week this year (approximate)
                    ROUND(
                        (COUNT(CASE WHEN EXTRACT(YEAR FROM date) = %s THEN 1 END)::numeric / 
                        GREATEST(EXTRACT(WEEK FROM CURRENT_DATE), 1))::numeric, 2
                    ) as sessions_per_week_this_year,
                    
                    -- Average fun rating this year
                    ROUND(
                        AVG(CASE WHEN EXTRACT(YEAR FROM date) = %s THEN CAST(fun_rating AS FLOAT) END)::numeric, 2
                    ) as avg_fun_rating_this_year,
                    
                    -- Average session duration in minutes (this year, sessions with end_time)
                    ROUND(
                        AVG(CASE 
                            WHEN EXTRACT(YEAR FROM date) = %s AND end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END)::numeric, 1
                    ) as avg_session_duration_minutes_this_year,
                    
                    -- Total surf time in minutes (this year, sessions with end_time)
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN EXTRACT(YEAR FROM date) = %s AND end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END), 0)::numeric, 1
                    ) as total_surf_time_minutes_this_year
                    
                FROM surf_sessions_duplicate 
                WHERE user_id = %s
            """, (current_year, current_year, current_year, current_year, current_year, current_user_id))
            
            current_user_stats = cur.fetchone()
            
            # 1b. CURRENT USER TOP LOCATIONS (NEW)
            cur.execute("""
                SELECT location, COUNT(*) as session_count 
                FROM surf_sessions_duplicate 
                WHERE user_id = %s AND EXTRACT(YEAR FROM date) = %s
                GROUP BY location 
                ORDER BY session_count DESC 
                LIMIT 3
            """, (current_user_id, current_year))
            
            user_top_locations = cur.fetchall()
            
            # 2. OTHER USERS STATS (Enhanced with time calculations)
            cur.execute("""
                SELECT 
                    s.user_id,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    
                    -- All-time stats
                    COUNT(*) as total_sessions_all_time,
                    
                    -- This year stats
                    COUNT(CASE WHEN EXTRACT(YEAR FROM s.date) = %s THEN 1 END) as total_sessions_this_year,
                    
                    -- Sessions per week this year
                    ROUND(
                        (COUNT(CASE WHEN EXTRACT(YEAR FROM s.date) = %s THEN 1 END)::numeric / 
                        GREATEST(EXTRACT(WEEK FROM CURRENT_DATE), 1))::numeric, 2
                    ) as sessions_per_week_this_year,
                    
                    -- Average fun rating this year
                    ROUND(
                        AVG(CASE WHEN EXTRACT(YEAR FROM s.date) = %s THEN CAST(s.fun_rating AS FLOAT) END)::numeric, 2
                    ) as avg_fun_rating_this_year,
                    
                    -- Average session duration in minutes (this year, sessions with end_time)
                    ROUND(
                        AVG(CASE 
                            WHEN EXTRACT(YEAR FROM s.date) = %s AND s.end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (s.end_time - s.time)) / 60 
                        END)::numeric, 1
                    ) as avg_session_duration_minutes_this_year,
                    
                    -- Total surf time in minutes (this year, sessions with end_time)
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN EXTRACT(YEAR FROM s.date) = %s AND s.end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (s.end_time - s.time)) / 60 
                        END), 0)::numeric, 1
                    ) as total_surf_time_minutes_this_year
                    
                FROM surf_sessions_duplicate s
                LEFT JOIN auth.users u ON s.user_id = u.id
                WHERE s.user_id != %s  -- Exclude current user
                GROUP BY s.user_id, u.raw_user_meta_data, u.email
                ORDER BY total_sessions_all_time DESC
            """, (current_year, current_year, current_year, current_year, current_year, current_user_id))
            
            other_users_stats = cur.fetchall()
            
            # 3. COMMUNITY STATS (Enhanced with time calculations)
            cur.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    ROUND(SUM(CAST(fun_rating AS FLOAT))::numeric, 1) as total_stoke,
                    
                    -- Community average session duration (sessions with end_time)
                    ROUND(
                        AVG(CASE 
                            WHEN end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END)::numeric, 1
                    ) as avg_session_duration_minutes,
                    
                    -- Total community surf time in minutes (sessions with end_time)
                    ROUND(
                        COALESCE(SUM(CASE 
                            WHEN end_time IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (end_time - time)) / 60 
                        END), 0)::numeric, 1
                    ) as total_surf_time_minutes
                    
                FROM surf_sessions_duplicate
                WHERE EXTRACT(YEAR FROM date) = %s
            """, (current_year,))
            
            community_stats = cur.fetchone()
            
            # 3b. COMMUNITY TOP LOCATION (NEW)
            cur.execute("""
                SELECT location, COUNT(*) as session_count
                FROM surf_sessions_duplicate 
                WHERE EXTRACT(YEAR FROM date) = %s
                GROUP BY location 
                ORDER BY session_count DESC 
                LIMIT 1
            """, (current_year,))
            
            community_top_location = cur.fetchone()
            
            # Convert results to dictionaries and handle None values
            current_user_data = dict(current_user_stats) if current_user_stats else {
                'total_sessions_all_time': 0,
                'total_sessions_this_year': 0,
                'sessions_per_week_this_year': 0,
                'avg_fun_rating_this_year': None,
                'avg_session_duration_minutes_this_year': None,
                'total_surf_time_minutes_this_year': 0
            }
            
            # Add top locations to current user data
            current_user_data['top_locations'] = [dict(loc) for loc in user_top_locations] if user_top_locations else []
            
            other_users_data = [dict(user) for user in other_users_stats] if other_users_stats else []
            
            community_data = dict(community_stats) if community_stats else {
                'total_sessions': 0,
                'total_stoke': 0,
                'avg_session_duration_minutes': None,
                'total_surf_time_minutes': 0
            }
            
            # Add top location to community data
            community_data['top_location'] = dict(community_top_location) if community_top_location else None
            
            return {
                'current_user': current_user_data,
                'other_users': other_users_data,
                'community': community_data
            }
            
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def generate_session_group_id():
    """Generate a unique UUID for linking related sessions"""
    return str(uuid.uuid4())

def create_session_with_participants(session_data, creator_user_id, tagged_user_ids=None):
    """
    Create a session with optional tagged participants
    Returns the created sessions and participant records
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Generate a session group ID if we have tagged users
            session_group_id = generate_session_group_id() if tagged_user_ids else None
            
            # Add session_group_id to the original session data
            if session_group_id:
                session_data['session_group_id'] = session_group_id
            
            # 1. Create the original session for the creator
            original_session = create_session(session_data, creator_user_id)
            if not original_session:
                return None
            
            created_sessions = [original_session]
            participant_records = []
            
            # 2. Create participant record for the creator (using the same connection)
            if session_group_id:
                cur.execute("""
                    INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                """, (original_session['id'], creator_user_id, creator_user_id, 'creator'))
                
                creator_participant = cur.fetchone()
                if creator_participant:
                    participant_records.append(dict(creator_participant))
            
            # 3. Create duplicate sessions for tagged users (all in the same transaction)
            if tagged_user_ids:
                for tagged_user_id in tagged_user_ids:
                    # Create duplicate session data
                    duplicate_data = session_data.copy()
                    duplicate_data['user_id'] = tagged_user_id
                    duplicate_data['session_group_id'] = session_group_id
                    
                    # Find the next available ID
                    cur.execute("SELECT MAX(id) FROM surf_sessions_duplicate")
                    max_id_result = cur.fetchone()
                    max_id = max_id_result['max'] if max_id_result and 'max' in max_id_result else None
                    next_id = 1 if max_id is None else max_id + 1
                    
                    duplicate_data['id'] = next_id
                    
                    # Handle JSONB fields
                    if 'raw_swell' in duplicate_data:
                        if not isinstance(duplicate_data['raw_swell'], Json):
                            duplicate_data['raw_swell'] = Json(duplicate_data['raw_swell'])
                            
                    if 'raw_met' in duplicate_data:
                        if not isinstance(duplicate_data['raw_met'], Json):
                            duplicate_data['raw_met'] = Json(duplicate_data['raw_met'])
                            
                    if 'raw_tide' in duplicate_data:
                        if not isinstance(duplicate_data['raw_tide'], Json):
                            duplicate_data['raw_tide'] = Json(duplicate_data['raw_tide'])
                    
                    # Remove created_at if present
                    if 'created_at' in duplicate_data:
                        del duplicate_data['created_at']
                    
                    # Insert the duplicate session
                    columns = ', '.join(duplicate_data.keys())
                    placeholders = ', '.join(['%s'] * len(duplicate_data))
                    
                    query = f"""
                    INSERT INTO surf_sessions_duplicate ({columns}) 
                    VALUES ({placeholders})
                    RETURNING *
                    """
                    
                    cur.execute(query, list(duplicate_data.values()))
                    duplicate_session = cur.fetchone()
                    
                    if duplicate_session:
                        # Convert time objects to strings for JSON serialization
                        duplicate_session_dict = dict(duplicate_session)
                        if 'time' in duplicate_session_dict and isinstance(duplicate_session_dict['time'], time):
                            duplicate_session_dict['time'] = duplicate_session_dict['time'].isoformat()
                        if 'end_time' in duplicate_session_dict and isinstance(duplicate_session_dict['end_time'], time):
                            duplicate_session_dict['end_time'] = duplicate_session_dict['end_time'].isoformat()
                        if 'date' in duplicate_session_dict and isinstance(duplicate_session_dict['date'], date):
                            duplicate_session_dict['date'] = duplicate_session_dict['date'].isoformat()
                        
                        created_sessions.append(duplicate_session_dict)
                        
                        # Create participant record for tagged user (in the same transaction)
                        cur.execute("""
                            INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                            VALUES (%s, %s, %s, %s)
                            RETURNING *
                        """, (duplicate_session['id'], tagged_user_id, creator_user_id, 'tagged_participant'))
                        
                        tagged_participant = cur.fetchone()
                        if tagged_participant:
                            participant_records.append(dict(tagged_participant))
            
            # Commit the entire transaction
            conn.commit()
            
            return {
                'sessions': created_sessions,
                'participants': participant_records,
                'session_group_id': session_group_id
            }
            
    except Exception as e:
        print(f"Error creating session with participants: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_duplicate_session(original_session_data, new_user_id, session_group_id):
    """Create a duplicate session for a tagged user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Create a copy of the session data for the new user
            duplicate_data = original_session_data.copy()
            duplicate_data['user_id'] = new_user_id
            duplicate_data['session_group_id'] = session_group_id
            
            # Find the next available ID
            cur.execute("SELECT MAX(id) FROM surf_sessions_duplicate")
            max_id_result = cur.fetchone()
            max_id = max_id_result['max'] if max_id_result and 'max' in max_id_result else None
            next_id = 1 if max_id is None else max_id + 1
            
            duplicate_data['id'] = next_id
            
            # Handle JSONB fields - check if they're already Json objects or raw data
            if 'raw_swell' in duplicate_data:
                if isinstance(duplicate_data['raw_swell'], Json):
                    # Already a Json object, keep as is
                    pass
                else:
                    # Raw data, wrap in Json
                    duplicate_data['raw_swell'] = Json(duplicate_data['raw_swell'])
                    
            if 'raw_met' in duplicate_data:
                if isinstance(duplicate_data['raw_met'], Json):
                    # Already a Json object, keep as is
                    pass
                else:
                    # Raw data, wrap in Json
                    duplicate_data['raw_met'] = Json(duplicate_data['raw_met'])
                    
            if 'raw_tide' in duplicate_data:
                if isinstance(duplicate_data['raw_tide'], Json):
                    # Already a Json object, keep as is
                    pass
                else:
                    # Raw data, wrap in Json
                    duplicate_data['raw_tide'] = Json(duplicate_data['raw_tide'])
            
            # Remove created_at if present
            if 'created_at' in duplicate_data:
                del duplicate_data['created_at']
            
            columns = ', '.join(duplicate_data.keys())
            placeholders = ', '.join(['%s'] * len(duplicate_data))
            
            query = f"""
            INSERT INTO surf_sessions_duplicate ({columns}) 
            VALUES ({placeholders})
            RETURNING *
            """
            
            cur.execute(query, list(duplicate_data.values()))
            
            duplicate_session = cur.fetchone()
            if duplicate_session:
                # Convert time objects to strings for JSON serialization
                if 'time' in duplicate_session and isinstance(duplicate_session['time'], time):
                    duplicate_session['time'] = duplicate_session['time'].isoformat()
                if 'end_time' in duplicate_session and isinstance(duplicate_session['end_time'], time):
                    duplicate_session['end_time'] = duplicate_session['end_time'].isoformat()
                if 'date' in duplicate_session and isinstance(duplicate_session['date'], date):
                    duplicate_session['date'] = duplicate_session['date'].isoformat()
            
            return duplicate_session
            
    except Exception as e:
        print(f"Error creating duplicate session: {e}")
        raise
    finally:
        conn.close()

def create_participant_record(session_id, user_id, tagged_by_user_id, role):
    """Create a record in session_participants table"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO session_participants (session_id, user_id, tagged_by_user_id, role)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (session_id, user_id, tagged_by_user_id, role))
            
            participant = cur.fetchone()
            return participant
            
    except Exception as e:
        print(f"Error creating participant record: {e}")
        raise
    finally:
        conn.close()

def get_session_participants(session_id):
    """Get all participants for a session"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    sp.*,
                    u.email as user_email,
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name', '') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name', '')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name
                FROM session_participants sp
                LEFT JOIN auth.users u ON sp.user_id = u.id
                WHERE sp.session_id = %s
                ORDER BY sp.role DESC, sp.created_at ASC
            """, (session_id,))
            
            participants = cur.fetchall()
            return list(participants) if participants else []
            
    except Exception as e:
        print(f"Error getting session participants: {e}")
        return []
    finally:
        conn.close()