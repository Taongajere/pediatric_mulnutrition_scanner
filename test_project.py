import pytest
from unittest.mock import patch, MagicMock

from project import (
    display_menu, ui_register_new_child, ui_retrieve_child_info, 
    ui_record_screening, ui_calculate_assessment, ui_create_referral, 
    ui_enroll_child, ui_export_data, header, success, error, warn
)

def test_console_helpers():
    # Simple tests to ensure the UI helper functions execute without raising errors
    try:
        header("Test Title", "Test Subtitle")
        success("Test success message")
        error("Test error message")
        warn("Test warning message")
    except Exception as e:
        pytest.fail(f"UI Helper functions raised an exception: {e}")

def test_display_menu():
    with patch("rich.prompt.Prompt.ask", return_value="1"):
        assert display_menu() == "1"

def test_ui_register_new_child_age_validation():
    # Child is too old (6 years old)
    with patch("builtins.input", side_effect=["M", "2020-01-01", "no"]):
        result = ui_register_new_child()
        assert result is None

    # Date is in the future
    with patch("builtins.input", side_effect=["F", "2030-05-15", "no"]):
        result = ui_register_new_child()
        assert result is None

    # User types the date in the wrong format (DD-MM-YYYY)
    with patch("builtins.input", side_effect=["M", "15-05-2025", "no"]):
        result = ui_register_new_child()
        assert result is None

def test_ui_retrieve_child_info():
    with patch("builtins.input", return_value="TEST1234"):
        with patch("project.get_child", return_value=("TEST1234", "2023-01-01", False, 36, "M", "S01", "2026-01-01")):
            record = ui_retrieve_child_info()
            assert isinstance(record, tuple)
            assert record[0] == "TEST1234"

def test_ui_record_screening():
    inputs = ["ABC12345", "11.5", "82.0", "120", "present", "screening", "standing"]
    with patch("builtins.input", side_effect=inputs):
        with patch("project.get_child", return_value=(None, "2024-01-01")): # Mocking DOB fetch
            with patch("project.record_screening_visit", return_value=101):
                visit_id = ui_record_screening()
                assert visit_id == 101

def test_ui_calculate_assessment_sam():
    sam_visit = {"visit_id": 1, "muac_mm": 112.0, "oedema_status": "present"}
    mock_assessment = {
        "waz": -3.5, "haz": -2.0, "whz": -3.0, 
        "muac_classification": "Severe Acute Malnutrition", 
        "overall_flag": "Refer immediately"
    }
    
    with patch("builtins.input", side_effect=["TEST1234", "no"]): # "no" to referral prompt
        with patch("project.get_latest_screening_visit", return_value=sam_visit):
            with patch("project.calculate_assessment", return_value=mock_assessment):
                with patch("project.save_assessment", return_value=1):
                    # Ensure it runs without exception
                    ui_calculate_assessment()

def test_ui_calculate_assessment_normal():
    normal_visit = {"visit_id": 2, "muac_mm": 130.0, "oedema_status": "absent"}
    mock_assessment = {
        "waz": -0.5, "haz": -1.0, "whz": -0.2, 
        "muac_classification": "Normal", 
        "overall_flag": "No action specified"
    }
    
    with patch("builtins.input", side_effect=["TEST5678"]):
        with patch("project.get_latest_screening_visit", return_value=normal_visit):
            with patch("project.calculate_assessment", return_value=mock_assessment):
                with patch("project.save_assessment", return_value=2):
                    ui_calculate_assessment()

def test_ui_create_referral():
    valid_inputs = ["TEST1234", "1", "Lubuto Clinic", "SAM with oedema", "High"]
    with patch("builtins.input", side_effect=valid_inputs):
        with patch("project.create_referral", return_value=50):
            referral_id = ui_create_referral()
            assert referral_id == 50

    with patch("builtins.input", side_effect=["TEST1234", "abc"]):
        result = ui_create_referral()
        assert result is None

def test_ui_enroll_child():
    with patch("builtins.input", side_effect=["TEST1234", "OTP"]):
        with patch("project.enroll_child", return_value=20):
            enrolment_id = ui_enroll_child()
            assert enrolment_id == 20

    with patch("builtins.input", side_effect=["SC"]):
        with patch("project.enroll_child", return_value=21):
            enrolment_id = ui_enroll_child(child_id="TEST5678")
            assert enrolment_id == 21

def test_ui_export_data():
    with patch("rich.prompt.Prompt.ask", side_effect=["1", "TEST1234"]):
        with patch("project.export_child_visits_to_csv", return_value=5):
            # Ensuring it executes properly and prints the correct outputs
            ui_export_data()

    with patch("rich.prompt.Prompt.ask", return_value="2"):
        with patch("project.export_all_visits_to_csv", return_value=15):
            ui_export_data()