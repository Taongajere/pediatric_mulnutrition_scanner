import sqlite3 

def init_db(db_path = "data/nutri_track.db"):
    # connect to the database file 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create the Settlemets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Settlements (
            settlement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            settlement_name TEXT NOT NULL,
            district TEXT,
            province TEXT
        );
    ''')

    # Create officers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Officers (
            officer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            officer_code TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            role TEXT
        );
    ''')

    # Create Children table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            child_id TEXT PRIMARY KEY,
            date_of_birth DATE NOT NULL,
            dob_is_estimated BOOLEAN,
            estimated_age_months INTEGER,
            sex TEXT NOT NULL,
            settlement_id INTEGER,
            registration_date DATE NOT NULL,
            FOREIGN KEY (settlement_id) REFERENCES Settlements(settlement_id) 
        );   
    ''')

    # Create Screening Visits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS screening_visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id TEXT NOT NULL,
            officer_id INTEGER NOT NULL,
            settlement_id INTEGER NOT NULL,
            visit_date DATE NOT NULL,
            visit_type TEXT,
            age_in_months_at_visit INTEGER,
            FOREIGN KEY (child_id) REFERENCES children (child_id),
            FOREIGN KEY (officer_id) REFERENCES officers (officer_id),
            FOREIGN KEY (settlement_id) REFERENCES settlements (settlement_id)
        )
    ''')

    # Create Measurements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER UNIQUE NOT NULL,
            child_id TEXT NOT NULL,
            weight_kg REAL,
            height_length_cm REAL,
            muac_mm REAL,
            oedema_status TEXT,
            measurement_position TEXT,
            FOREIGN KEY (visit_id) REFERENCES screening_visits (visit_id)
            FOREIGN KEY (child_id) REFERENCES children (child_id)
        )
    ''')

    # Create Nutritional Assessment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutritional_assessment (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER UNIQUE NOT NULL,
            waz REAL,
            haz REAL,
            whz REAL,
            muac_classification TEXT,
            overall_flag TEXT,
            standard_version TEXT,
            protocol_version TEXT,
            assessed_at TEXT,
            FOREIGN KEY (visit_id) REFERENCES screening_visits (visit_id)
        )
    ''')

    # Create Referrals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER NOT NULL,
            child_id TEXT NOT NULL,
            referral_facility TEXT,
            referral_reason TEXT,
            urgency_level TEXT,
            referral_date DATE NOT NULL,
            status TEXT,
            FOREIGN KEY (visit_id) REFERENCES screening_visits (visit_id)
        )
    ''')

    # Create Programme Enrolment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS programme_enrolment (
            enrolment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id TEXT NOT NULL,
            programme_type TEXT,
            admission_date DATE NOT NULL,
            end_date DATE,
            status TEXT,
            exit_reason TEXT,
            FOREIGN KEY (child_id) REFERENCES children (child_id)
        )
    ''')

    conn.commit()
    conn.close()

# create the database and tables when the script is run directly
if __name__ == "__main__":
    init_db("data/nutritrack.db")
    print("Database tables created successfully.")