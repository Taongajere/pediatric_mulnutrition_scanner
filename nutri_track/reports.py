import sqlite3
import csv

def export_assessments_to_csv(db_path, output_filename="assessment_report.csv"):
    """
    Extracts screening and assessment history by joining multiple tables,
    and exports the result to a CSV file for external analysis.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # We use JOINs to connect the child's identity to their specific visit measurements and flags
        cursor.execute('''
            SELECT 
                c.child_id, 
                s.visit_date, 
                m.weight_kg, 
                m.height_length_cm, 
                m.muac_mm, 
                m.oedema_status, 
                a.muac_classification, 
                a.overall_flag
            FROM children c
            JOIN screening_visits s ON c.id = s.child_id
            JOIN measurements m ON s.id = m.visit_id
            JOIN nutritional_assessment a ON s.id = a.visit_id
            ORDER BY s.visit_date DESC
        ''')
        
        rows = cursor.fetchall()
        
        with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow([
                "Child ID", "Visit Date", "Weight (kg)", "Height (cm)", 
                "MUAC (mm)", "Oedema", "Classification", "Action Flag"
            ])
            # Write the data rows
            writer.writerows(rows)
            
        return len(rows)
    except sqlite3.Error as e:
        print(f"Database extraction error: {e}")
        return None
    except IOError as e:
        print(f"File writing error: {e}")
        return None
    finally:
        conn.close()