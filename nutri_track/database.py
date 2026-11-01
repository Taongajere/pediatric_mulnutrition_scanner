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
            registration_date TEXT NOT NULL,
            FOREIGN KEY (settlement_id) REFERENCES Settlements(settlement_id) 
        );   
    ''')

    conn.commit()
    conn.close()

# create the database and tables when the script is run directly
if __name__ == "__main__":
    init_db("data/nutritrack.db")
    print("Database tables created successfully.")