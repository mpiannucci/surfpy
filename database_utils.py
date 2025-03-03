import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Database connection string
db_url = "postgresql://postgres:kooksinthekitchen@db.ehrfwjekssrnbgmgxctg.supabase.co:5432/postgres"

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
            return list(sessions)
    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        return []
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
            return session
    except Exception as e:
        print(f"Error retrieving session: {e}")
        return None
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
            max_id = cur.fetchone()['max']
            
            # If max_id is None, start with 1, otherwise use max_id + 1
            next_id = 1 if max_id is None else max_id + 1
            print(f"Using next ID: {next_id}")
            
            # Always include the ID in the data to avoid conflicts
            session_data['id'] = next_id
            
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
            return cur.fetchone()
    except Exception as e:
        print(f"Error creating session: {e}")
        conn.rollback()
        return None
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
            return cur.fetchone()
    except Exception as e:
        print(f"Error updating session: {e}")
        conn.rollback()
        return None
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
        return False
    finally:
        conn.close()