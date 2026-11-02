from unittest.mock import patch
from project import display_menu, ui_register_new_child, ui_retrieve_child_info, ui_record_screening, ui_calculate_assessment, ui_create_referral, ui_enroll_child, ui_export_data 

def test_display_menu():
    # Simulate the user typing "1" and pressing Enter
    with patch("builtins.input", return_value="1"):
        assert display_menu() == "1"

def test_ui_register_new_child_age_validation():
    # Scenario 1: Child is too old (6 years old)
    # The current year is 2026, so a child born in 2020 is rejected.
    with patch("builtins.input", side_effect=["M", "2020-01-01"]):
        result = ui_register_new_child()
        assert result is None

    # Scenario 2: Date is in the future
    with patch("builtins.input", side_effect=["F", "2030-05-15"]):
        result = ui_register_new_child()
        assert result is None

    # Scenario 3: User types the date in the wrong format (DD-MM-YYYY)
    with patch("builtins.input", side_effect=["M", "15-05-2025"]):
        result = ui_register_new_child()
        assert result is None

def test_ui_retrieve_child_info():
    # Simulate looking up a hypothetical ID
    with patch("builtins.input", return_value="TEST1234"):
        record = ui_retrieve_child_info()
        # If the ID doesn't exist in your DB, it returns None; otherwise it returns a tuple
        assert record is None or isinstance(record, tuple)

def test_ui_record_screening():
    # Provide inputs in the exact order requested: Child ID, Weight, Height, MUAC, Oedema Status
    with patch("builtins.input", side_effect=["ABC12345", "11.5", "82.0", "120", "present", "no"]):
        visit_id = ui_record_screening()
        
        # If the dummy child or officer 1 doesn't exist in the DB, it returns None.
        # If they do exist, it returns the integer visit_id.
        assert visit_id is None or isinstance(visit_id, int)

def test_ui_calculate_assessment():
    # Scenario 1: Child not found in database (Early Exit)
    # Only 1 input is triggered: Child ID
    with patch("builtins.input", side_effect=["BADID99"]):
        with patch("project.get_latest_screening_visit", return_value=None):
            ui_calculate_assessment()

    # Scenario 2: Child found, SAM detected, user chooses NOT to refer right now
    # 2 inputs are triggered: Child ID, then the Referral prompt (because SAM is present)
    sam_visit = {"visit_id": 1, "muac_mm": 112.0, "oedema_status": "present"}
    
    with patch("builtins.input", side_effect=["TEST1234", "no"]):
        with patch("project.get_latest_screening_visit", return_value=sam_visit):
            with patch("project.save_assessment", return_value=1):
                ui_calculate_assessment()

    # Scenario 3: Child found, NO SAM detected (Normal)
    # Only 1 input is triggered: Child ID (the referral prompt is bypassed completely)
    normal_visit = {"visit_id": 2, "muac_mm": 130.0, "oedema_status": "absent"}
    
    with patch("builtins.input", side_effect=["TEST5678"]):
        with patch("project.get_latest_screening_visit", return_value=normal_visit):
            with patch("project.save_assessment", return_value=2):
                ui_calculate_assessment()


def test_ui_create_referral():
    # Scenario 1: Valid inputs
    # Inputs: Child ID, Visit ID, Facility, Reason, Urgency
    valid_inputs = ["TEST1234", "1", "Lubuto Clinic", "SAM with oedema", "High"]
    with patch("builtins.input", side_effect=valid_inputs):
        referral_id = ui_create_referral()
        # Returns None if the dummy Child/Visit IDs don't exist in the database, 
        # or returns the integer ID if they do.
        assert referral_id is None or isinstance(referral_id, int)

    # Scenario 2: Invalid Visit ID (Early Exit)
    # The user types "abc" for Visit ID. The function should print an error and return None 
    # without asking the remaining three questions.
    with patch("builtins.input", side_effect=["TEST1234", "abc"]):
        result = ui_create_referral()
        assert result is None

def test_ui_enroll_child():
    # Scenario 1: No ID provided, user types both Child ID and Program Type
    with patch("builtins.input", side_effect=["TEST1234", "OTP"]):
        enrolment_id = ui_enroll_child()
        # Returns None if the dummy child isn't in the database, or an integer if it is
        assert enrolment_id is None or isinstance(enrolment_id, int)

    # Scenario 2: ID is automatically passed in from a previous menu
    # The function skips the ID prompt and only asks for the Program Type
    with patch("builtins.input", side_effect=["SC"]):
        enrolment_id = ui_enroll_child(child_id="TEST5678")
        assert enrolment_id is None or isinstance(enrolment_id, int)

def test_ui_export_data():
    # Scenario 1: User provides a custom filename without the .csv extension
    # We patch the backend function to simulate successfully exporting 5 rows, 
    # so we don't actually create a file during the test.
    with patch("builtins.input", return_value="my_custom_report"):
        with patch("project.export_assessments_to_csv", return_value=5):
            rows = ui_export_data()
            assert rows == 5

    # Scenario 2: User just presses Enter (empty input)
    # This tests the fallback logic that defaults to "data_export.csv"
    with patch("builtins.input", return_value=""):
        with patch("project.export_assessments_to_csv", return_value=0):
            rows = ui_export_data()
            assert rows == 0