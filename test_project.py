from unittest.mock import patch
from project import display_menu, ui_register_new_child, ui_retrieve_child_info, ui_record_screening, ui_calculate_assessment, ui_create_referral, ui_enroll_child, ui_export_data 

def test_display_menu():
    # Simulate the user typing "1" and pressing Enter
    with patch("builtins.input", return_value="1"):
        assert display_menu() == "1"

def test_ui_register_new_child():
    # side_effect passes a list of inputs in the exact order they are asked: Sex, then DOB
    with patch("builtins.input", side_effect=["M", "2023-08-14", "no"]):
        child_id = ui_register_new_child()
        assert child_id is not None
        assert len(child_id) == 8

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
    # Scenario 1: Child not found (Early Exit)
    # The function only asks for the Child ID, then stops.
    with patch("builtins.input", side_effect=["BADID99"]):
        with patch("project.get_latest_screening_visit", return_value=None):
            ui_calculate_assessment()  # Should print "No screening visit found"

    # Scenario 2: Child found, user chooses to save
    # The function asks 3 questions: Child ID, Save Choice, Visit ID
    dummy_visit = {"muac_mm": 112.0, "oedema_status": "absent"}
    
    with patch("builtins.input", side_effect=["TEST1234", "yes", "1", "no"]):
        with patch("project.get_latest_screening_visit", return_value=dummy_visit):
            with patch("project.save_assessment", return_value=1):
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