from unittest.mock import patch
from project import display_menu, ui_register_new_child, ui_retrieve_child_info

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