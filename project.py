import sys 
from nutri_track.children import register_child, get_child
from nutri_track.screening import record_screening_visit

def main():
    while True: 
        choice = display_menu()
        if choice == '1':
            ui_register_new_child()
        elif choice == '2':
            ui_retrieve_child_info()
        elif choice == '3':
            ui_record_screening()
        elif choice == '8':
            print("Exiting the program.")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

def display_menu():
    print("\n---- NutriTrack ---")
    print("1. Register a new child")
    print("2. Retrieve child information")
    print("3. Record screening visit")
    print("8. Exit")
    return input("Enter your choice: ")

def ui_register_new_child():
    print("\n--- Register a New Child ---")
    sex = input("Enter child's sex (M/F): ").strip().upper()
    date_of_birth = input("Enter child's date of birth (YYYY-MM-DD): ").strip()
    dob_is_estimated = input("Is the date of birth estimated? (yes/no): ").strip().lower() == 'yes'
    child_id = register_child("data/nutritrack.db", date_of_birth, dob_is_estimated, None, sex, 1)  # Assuming settlement_id is 1 for simplicity
    print(f'success! Child ID is {child_id}' if child_id else 'Failed to register child.')
    return child_id

def ui_retrieve_child_info():
    print("\n--- Retrieve Child Information ---")
    child_id = input("Enter child's ID: ").strip().upper()
    child_info = get_child("data/nutritrack.db", child_id)
    print(f"Child Information: {child_info}" if child_info else "Child not found.")

def ui_record_screening():
    """4. Add the new UI function to collect measurements."""
    print("\n--- Record Screening Visit ---")
    child_id = input("Enter NutriTrack ID: ").strip().upper()
    weight = float(input("Weight (kg): ").strip())
    height = float(input("Height/Length (cm): ").strip())
    
    # Hardcoding officer 1 and settlement 1 for testing purposes
    visit_id = record_screening_visit("data/nutritrack.db", child_id, 1, 1, weight, height)
    
    if visit_id:
        print(f"Success! Visit recorded with ID {visit_id}")
    else:
        print("Failed to record visit. Ensure the Child ID is correct.")
    return visit_id

if __name__ == "__main__":
    main()

