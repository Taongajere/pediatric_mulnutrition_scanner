import sqlite3
from datetime import date
from .z_score import calculate_lhfa_zscore, calculate_wfa_zscore, calculate_wfh_zscore, calculate_who_zscores

def calculate_assessment(db_path, visit_id):
    """
    Evaluates inputs based on the WHO 2013 Management of SAM guidelines.
    Outputs safe screening flags without claiming definitive medical diagnosis.
    """

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try: 
        # Retrieve child screening information
        query = '''
            SELECT
                c.child_id,
                c.date_of_birth
                c.sex,
                sv.visit_id,
                sv.age_in_months_at_visit,
                m.weight_kg,
                m.height_length_cm,
                m.muac_mm,
                m.oedema_status,
                m.measurement_position
            FROM children AS c
            INNER JOIN screening_visits AS sv
                ON sv.child_id = c.child_id
            LEFT JOIN measurements AS m 
                ON m.visit_id = sv.visit_id
            WHERE sv.visit_id = ?
                
        '''

        cursor.execute(query, (visit_id,))
        visit = cursor.fetchone()

        if visit is None:
            raise ValueError('Screening visit not found.') 

        #Retrieve the measurements
        age_at_visit = visit["age_in_months_at_visit"]
        sex = visit["sex"]
        date_of_birth = visit["date_of_birth"]
        weight_kg = visit["weight_kg"]
        height_cm = visit["height_length_cm"]
        muac_mm = visit["muac_mm"]
        oedema_status = visit["oedema_status"]
        measurement_position = visit['measurement_position']

        # Validate required measurements
        if any(value is None for value in [
            age_at_visit,
            sex,
            weight_kg,
            height_cm,
            muac_mm,
            oedema_status, 
            measurement_position, 
        ]):
            raise ValueError("Incomplete screening measurements.")

        #Calculate z_scores using WHO - R packgae
        z_scores = calculate_who_zscores(
            date_of_birth = date_of_birth,
            age_at_visit = age_at_visit,
            sex = sex,
            weight_kg = weight_kg,
            height_cm = height_cm,
            muac_mm = muac_mm,
            oedema_status = oedema_status,
            measurement_position = measurement_position
        )


        #Calculate Weight-for-Age Z-score (WAZ)
        waz = calculate_wfa_zscore(
            age_at_visit,
            sex,
            weight_kg
        )

        # Calculate Weight-for-Height/Length Z-score (WHZ)
        whz = calculate_wfh_zscore(
            age_at_visit,
            sex,
            height_cm,
            weight_kg
        )

        # Calculate Length/Height-for-Age Z-score (HAZ)
        haz = calculate_lhfa_zscore(
            age_at_visit,
            sex,
            height_cm,
        )

        # Classify MUAC
        if age_at_visit < 6:
            muac_classification = "Not classified using 6-59 month cut-offs"

        elif muac_mm < 115:
            muac_classification = "Severe acute malnutrition"

        elif muac_mm < 125:
            muac_classification = "Moderate acute malnutrition"

        else:
            muac_classification = "Normal"

        # Determine overall screening flag
        if str(oedema_status).strip().lower() in [
            "present", "bilateral pitting oedema"
        ]:
            overall_flag = "Bilateral oedema: urgent clinical assessment"

        elif whz < -3 or (age_at_visit >= 6 and muac_mm < 115):
            overall_flag = "Severe acute malnutrition: urgent referral"

        elif whz < -2 or (age_at_visit >= 6 and muac_mm < 125):
            overall_flag = "Moderate acute malnutrition: referral required"

        else:
            overall_flag = "No acute malnutrition flagged"

        # Return all four indicators
        assessment = {
            "standard_version": "WHO Child Growth Standards",
            "protocol_version": "WHO_Management_of_SAM_2013",

            "waz": waz,
            "haz": haz,
            "whz": whz,

            "muac_classification": muac_classification,

            "overall_flag": overall_flag
        }

        return assessment

    finally:
        conn.close()

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