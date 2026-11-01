import sqlite3
from datetime import date

def create_referral(db_path, child_id, visit_id, facility_name, reason, urgency_level):
    """
    Creates a referral record for a child requiring clinical or nutritional care.
    Status defaults to 'Pending' until the child is confirmed enrolled at the facility.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO referrals (
                child_id, visit_id, referral_facility, referral_reason, 
                urgency_level, referral_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            child_id, visit_id, facility_name, reason, 
            urgency_level, date.today().isoformat(), 'Pending'
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Database error saving referral: {e}")
        return None
    finally:
        conn.close()