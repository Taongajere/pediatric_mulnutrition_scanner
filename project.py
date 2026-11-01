import sys 
from nutri_track.children import register_child, get_child
from nutri_track.screening import record_screening_visit, get_latest_screening_visit
from nutri_track.assesment import calculate_assessment, save_assessment
from nutri_track.referals import create_referral
from nutri_track.enrollment import enroll_child


def main():
    while True: 
        choice = display_menu()
        if choice == '1':
            ui_register_new_child()
        elif choice == '2':
            ui_retrieve_child_info()
        elif choice == '3':
            ui_record_screening()
        elif choice == '4':
            ui_calculate_assessment()
        elif choice == '5':
            ui_create_referral()
        elif choice == '6':
            ui_enroll_child()
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
    print("4. Calculate nutritional assessment")
    print("5. Create referral")
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
    print("\n--- Record Screening Visit ---")
    child_id = input("Enter NutriTrack ID: ").strip().upper()
    weight = float(input("Weight (kg): ").strip())
    height = float(input("Height/Length (cm): ").strip())
    muac_mm = float(input("MUAC (mm): ").strip())
    oedema_status = input("Oedema status (present/absent): ").strip().lower()

    # Hardcoding officer 1 and settlement 1 for testing purposes
    visit_id = record_screening_visit("data/nutritrack.db", child_id, 1, 1, weight, height, muac_mm, oedema_status)

    if visit_id:
        print(f"Success! Visit recorded with ID {visit_id}")
    else:
        print("Failed to record visit. Ensure the Child ID is correct.")
    return visit_id

def ui_calculate_assessment():
    print("\n--- Calculate Nutritional Assessment ---")

    child_id = input("Enter NutriTrack ID: ").strip().upper()

    # retreive latest screening data for a child
    visit = get_latest_screening_visit("data/nutritrack.db", child_id)
    if not visit:
        print("No screening visit found for the specified child.")
        return

    assessment = calculate_assessment(visit['muac_mm'], visit['oedema_status'])
    print(f"Assessment Result: {assessment}")
    print(f"Classification: {assessment['muac_classification']}")
    print(f"Action: {assessment['overall_flag']}")

    # save the assessment to the database
    save_choice = input("Do you want to save this assessment? (yes/no): ").strip().lower()
    if save_choice == 'yes':
        visit_id = int(input("Enter the visit ID associated with this assessment: ").strip())
        saved_id = save_assessment("data/nutritrack.db", visit_id, assessment)
        print(f"Assessment saved with ID {saved_id}" if saved_id else "Failed to save assessment.")

    # flag assesment to automatically trigger referral if SAM is detected
    if "Severe" in assessment['muac_classification']:
        print("\n*** URGENT: SAM DETECTED ***")
        refer = input("Would you like to issue a referral now? (yes/no): ").strip().lower()
        if refer == 'yes':
            # Pass the known IDs directly to the referral function
            ui_create_referral(child_id=child_id, visit_id=visit_id)

def ui_create_referral(child_id=None, visit_id=None):
    print("\n--- Issue Clinical Referral ---")
    if child_id is None:
        child_id = input("Enter NutriTrack ID: ").strip().upper()
    if visit_id is None:
        visit_id = input("Enter Screening Visit ID: ").strip()
    
    if not visit_id.isdigit():
        print("Error: Visit ID must be a number.")
        return None
        
    facility = input("Referral Facility (e.g., Lubuto Clinic): ").strip()
    reason = input("Reason for Referral (e.g., SAM with oedema): ").strip()
    urgency = input("Urgency (High/Medium/Low): ").strip().capitalize()
    
    referral_id = create_referral(
        "data/nutritrack.db", 
        child_id,
        int(visit_id),
        facility,
        reason,
        urgency
    )
    
    if referral_id:
        print(f"Success! Referral {referral_id} issued to {facility}. Status set to 'Pending'.")
    else:
        print("Failed to issue referral. Verify the Child ID and Visit ID exist.")
        
    return referral_id

def ui_enroll_child(child_id=None):
    print("\n--- Enroll in Feeding Programme ---")

    if not child_id:
        child_id = input("Enter NutriTrack ID: ").strip().upper()
        
    print("Available Programs: SC (Stabilization Centre), OTP (Outpatient Therapeutic), SFP (Supplementary Feeding)")
    program = input("Enter Program Type (SC/OTP/SFP): ").strip().upper()
    
    enrolment_id = enroll_child("data/nutritrack.db", child_id, program)
    
    if enrolment_id:
        print(f"Success! Child {child_id} enrolled in {program}. Status set to 'Active'.")
    else:
        print("Failed to enroll child. Verify the Child ID exists.")
        
    return enrolment_id

if __name__ == "__main__":
    main()

