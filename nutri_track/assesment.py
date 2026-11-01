import sqlite3
from datetime import date

def calculate_assessment(muac_mm, oedema_status):
    """
    Evaluates inputs based on the WHO 2013 Management of SAM guidelines.
    Outputs safe screening flags without claiming definitive medical diagnosis.
    """
    assessment = {
        "standard_version": "WHO Child Growth Standards",
        "protocol_version": "WHO_Management_of_SAM_2013",
        "overall_flag": "No acute malnutrition flagged",
        "muac_classification": "Normal",
        "waz": None, 
        "haz": None,
        "whz": None
    }

    # WHO SAM Criteria 1: Bilateral pitting oedema is an independent indicator of SAM
    if oedema_status and oedema_status.lower() == "present":
        assessment["muac_classification"] = "Severe Acute Malnutrition (SAM)"
        assessment["overall_flag"] = "Requires urgent clinical review (Bilateral pitting oedema present)"
        return assessment

    # WHO SAM Criteria 2: MUAC thresholds for children 6-59 months
    if muac_mm:
        if muac_mm < 115.0:
            assessment["muac_classification"] = "Severe Acute Malnutrition (SAM)"
            assessment["overall_flag"] = "Requires urgent clinical review (MUAC < 115mm)"
        elif 115.0 <= muac_mm < 125.0:
            assessment["muac_classification"] = "Moderate Acute Malnutrition (MAM)"
            assessment["overall_flag"] = "Requires assessment (115 <= MUAC < 125mm)"
    else:
        assessment["overall_flag"] = "Incomplete assessment: MUAC not provided"

    return assessment

def save_assessment(db_path, visit_id, assessment_data):
    """Saves the assessment outputs to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO nutritional_assessment (
                visit_id, waz, haz, whz, muac_classification, 
                overall_flag, standard_version, protocol_version, assessed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            visit_id, assessment_data["waz"], assessment_data["haz"], 
            assessment_data["whz"], assessment_data["muac_classification"], 
            assessment_data["overall_flag"], assessment_data["standard_version"], 
            assessment_data["protocol_version"], date.today().isoformat()
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Error saving assessment: {e}")
        return None
    finally:
        conn.close()