import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from datetime import datetime, time, date
# from json_utils import CustomJSONEncoder

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
    """Retrieve all surf sessions"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM surf_sessions ORDER BY created_at DESC")
            sessions = cur.fetchall()
            # Convert to a list so we can modify it
            sessions_list = list(sessions)
            
            # Process each session to handle non-serializable types (like time objects)
            for i, session in enumerate(sessions_list):
                # Process time objects
                if 'time' in session and isinstance(session['time'], time):
                    sessions_list[i]['time'] = session['time'].isoformat()
                
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
    """Retrieve a single surf session by its ID"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM surf_sessions WHERE id = %s", (session_id,))
            session = cur.fetchone()
            if session:
                # Convert time objects to strings
                if 'time' in session and isinstance(session['time'], time):
                    session['time'] = session['time'].isoformat()
                
                # Convert date objects to strings
                if 'date' in session and isinstance(session['date'], date):
                    session['date'] = session['date'].isoformat()
                    
            return session
    except Exception as e:
        print(f"Error retrieving session: {e}")
        raise  # Re-raise to see the actual error
    finally:
        conn.close()

def create_session(session_data):
    """Create a new surf session in the database"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check the table structure to understand the ID column
            cur.execute("""
                SELECT column_name, column_default, is_identity 
                FROM information_schema.columns 
                WHERE table_name = 'surf_sessions' AND column_name = 'id'
            """)
            id_info = cur.fetchone()
            
            # Find the maximum ID value currently in the table
            cur.execute("SELECT MAX(id) FROM surf_sessions")
            max_id_result = cur.fetchone()
            max_id = max_id_result['max'] if max_id_result and 'max' in max_id_result else None
            
            # If max_id is None, start with 1, otherwise use max_id + 1
            next_id = 1 if max_id is None else max_id + 1
            print(f"Using next ID: {next_id}")
            
            # Always include the ID in the data to avoid conflicts
            session_data['id'] = next_id
            
            # Handle raw_data as JSONB
            if 'raw_data' in session_data:
                session_data['raw_data'] = Json(session_data['raw_data'])
            
            # Remove created_at if present
            if 'created_at' in session_data:
                del session_data['created_at']
                
            columns = ', '.join(session_data.keys())
            placeholders = ', '.join(['%s'] * len(session_data))
            
            query = f"""
            INSERT INTO surf_sessions ({columns}) 
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

def update_session(session_id, update_data):
    """Update an existing surf session"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Ensure id and created_at aren't in the update data
            if 'id' in update_data:
                del update_data['id']
            if 'created_at' in update_data:
                del update_data['created_at']
            
            # Handle raw_data as JSONB
            if 'raw_data' in update_data:
                update_data['raw_data'] = Json(update_data['raw_data'])
                
            # Build SET clause for the SQL query
            set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
            
            query = f"""
            UPDATE surf_sessions 
            SET {set_clause} 
            WHERE id = %s
            RETURNING *
            """
            
            # Add the session_id as the last parameter
            values = list(update_data.values()) + [session_id]
            
            cur.execute(query, values)
            conn.commit()
            
            # Handle serialization for time objects after fetching
            updated_session = cur.fetchone()
            if updated_session:
                # Convert time objects to strings
                if 'time' in updated_session and isinstance(updated_session['time'], time):
                    updated_session['time'] = updated_session['time'].isoformat()
                
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

def delete_session(session_id):
    """Delete a surf session by its ID"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM surf_sessions WHERE id = %s RETURNING id", (session_id,))
            deleted = cur.fetchone()
            conn.commit()
            return deleted is not None
    except Exception as e:
        print(f"Error deleting session: {e}")
        conn.rollback()
        raise  # Re-raise to see the actual error
    finally:
        conn.close()