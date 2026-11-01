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

def get_latest_screening_visit(db_path, child_id):
    """Retrieves the most recent screening visit for a given child."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name

    cursor = conn.cursor()

    cursor.execute('''
        SELECT visit_id, muac_mm, oedema_status
        FROM screening_visits
        WHERE child_id = ?
        ORDER BY visit_date DESC
        LIMIT 1
    ''', (child_id,))

    visit = cursor.fetchone()
    conn.close()
    return dict(visit) if visit else None