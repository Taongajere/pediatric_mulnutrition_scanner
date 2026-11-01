import sqlite3
from datetime import date

def record_screening_visit(db_path, child_id, officer_id, settlement_id, weight, height, muac_mm, oedema_status):
    """Records a new screening visit and its corresponding measurements."""
    visit_date = date.today().isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create the visit record
        cursor.execute('''
            INSERT INTO screening_visits (
                child_id, officer_id, settlement_id, visit_date
            ) VALUES (?, ?, ?, ?)
        ''', (child_id, officer_id, settlement_id, visit_date))
        
        visit_id = cursor.lastrowid
        
        # 2. Create the linked measurement record
        cursor.execute('''
            INSERT INTO measurements (
                visit_id, weight_kg, height_length_cm, muac_mm, oedema_status
            ) VALUES (?, ?, ?, ?, ?)
        ''', (visit_id, weight, height, muac_mm, oedema_status))

        
        conn.commit()
        return visit_id
    except sqlite3.IntegrityError as e:
        # Catches foreign key errors (e.g., missing child, officer, or settlement)
        print(f"Error recording visit: {e}")
        return None
    finally:
        conn.close()

def get_latest_screening_visit(db_path, child_string_id):
    """
    Fetches the most recent screening visit measurements for a child.
    Includes the specific visit_id needed to save subsequent assessments.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    try:
        # Join the tables to find the child's most recent visit and measurements
        cursor.execute('''
            SELECT s.id AS visit_id, m.muac_mm, m.oedema_status
            FROM children c
            JOIN screening_visits s ON c.id = s.child_id
            JOIN measurements m ON s.id = m.visit_id
            WHERE c.child_id = ?
            ORDER BY s.visit_date DESC, s.id DESC
            LIMIT 1
        ''', (child_string_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()