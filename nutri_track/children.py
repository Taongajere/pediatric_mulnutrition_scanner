import sqlite3
import uuid 
from datetime import datetime

def generate_child_id():
    """Generate a unique child ID using UUID4."""
    return str(uuid.uuid4())[:8].upper()
    
def register_child(db_path, date_of_birth, dob_is_estimated, estimated_age_months, sex, settlement_id):
    """Register a new child with a unique ID."""
    child_id = generate_child_id()
    registration_date = datetime.now().date()  # Current date for registration

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO children (child_id, date_of_birth, dob_is_estimated, estimated_age_months, sex, settlement_id, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (child_id, date_of_birth, dob_is_estimated, estimated_age_months, sex, settlement_id, registration_date))
        
        conn.commit()
        return child_id  # Return the generated child ID for reference
    except sqlite3.IntegrityError as e:
        print(f"Error registering child: {e}")
        return None
    finally:
        conn.close()

def get_child(db_path, child_id):
    """Retrieve child information by child ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM children WHERE child_id = ?
    ''', (child_id,))
    
    child = cursor.fetchone()
    conn.close()
    
    return child