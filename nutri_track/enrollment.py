import sqlite3
from datetime import date

def enroll_child(db_path, child_id, program_type, status="Active"):
    """
    Enrolls a child into a specific nutritional feeding programme.
    Defaults the admission status to 'Active'.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO programme_enrolment (
                child_id, programme_type, admission_date, status
            ) VALUES (?, ?, ?, ?)
        ''', (child_id, program_type, date.today().isoformat(), status))
        
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Database error saving enrolment: {e}")
        return None
    finally:
        conn.close()