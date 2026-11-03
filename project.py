import sys 

from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.prompt import Prompt, Confirm
from rich import box
from nutri_track.children import register_child, get_child
from nutri_track.screening import record_screening_visit, get_latest_screening_visit
from nutri_track.assesment import calculate_assessment, save_assessment
from nutri_track.referals import create_referral
from nutri_track.enrollment import enroll_child
from nutri_track.reports import export_assessments_to_csv

console = Console()

def header(title, subtitle=None):
    """Display a formatted header with optional subtitle."""
    console.print()
    console.print(Panel.fit(f"[bold white]{title}[/]", 
                            subtitle=subtitle, border_style="cyan", padding=(0, 4)))
    
def success(msg): console.print(f"[bold green]✔[/] {msg}")
def error(msg):   console.print(f"[bold red]✘[/] {msg}")
def warn(msg):    console.print(f"[bold yellow]![/] {msg}")


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
        elif choice == '7':
            ui_export_data()
        elif choice == '8':
            print("Exiting the program.")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

def display_menu():
    console.print()
    console.print(Panel.fit("[bold cyan]NutriTrack[/]\n[dim]Child nutrition screening[/]",
                            border_style="cyan", padding=(1, 6)))
    menu = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    menu.add_column(style="bold cyan", justify="right")
    menu.add_column()
    items = [
        ("1", "Register a new child"),
        ("2", "Retrieve child information"),
        ("3", "Record screening visit"),
        ("4", "Calculate nutritional assessment"),
        ("5", "Create referral"),
        ("6", "Enroll child in feeding programme"),
        ("7", "Export assessments to CSV"),
        ("8", "Exit"),
    ]
    for key, label in items:
        menu.add_row(key, label)
    console.print(menu)
    return Prompt.ask("Enter your choice", choices=[k for k, _ in items], show_choices=False)

def ui_register_new_child():
    header("\n--- Register a New Child ---")
    sex = input("Enter child's sex (M/F): ").strip().upper()

    date_of_birth = input("Enter child's date of birth (YYYY-MM-DD): ").strip()

    #child must be less than 5 years old to register, and date of birth cannot be in the future
    try: 
        dob_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        today = datetime.now().date()

        age_in_months = (
            (today.year - dob_obj.year) * 12 
            + (today.month - dob_obj.month)
            - (today.day < dob_obj.day)
        )
        age_in_years = age_in_months // 12
        if age_in_years > 5:
            error("Error: Child must be under 5 years old to register.")
            return None
        if age_in_years < 0:
            error("Error: Date of birth cannot be in the future.")
            return None
        
    except ValueError:
        error("Error: Invalid date format. Please use YYYY-MM-DD.")
        return None
    #-------------------------------------------------------------------------------------

    dob_is_estimated = input("Is the date of birth estimated? (yes/no): ").strip().lower() == 'yes'
    child_id = register_child("data/nutritrack.db", date_of_birth, dob_is_estimated, age_in_months * 12, sex, "S01")  # Assuming settlement_id is "S01" for simplicity
    success(f'success! Child ID is {child_id}' if child_id else 'Failed to register child.')
    return child_id

def ui_retrieve_child_info():
    print("\n--- Retrieve Child Information ---")
    child_id = input("Enter child's ID: ").strip().upper()
    child_info = get_child("data/nutritrack.db", child_id)

    if child_info:
        header("Child Record")
        t = Table(box=box.ROUNDED, show_header=False, border_style="cyan")
        t.add_column(style="bold")
        t.add_column()
        t.add_row("Child ID", f"[bold cyan]{child_info[0]}[/]")
        t.add_row("Date of birth", str(child_info[1]))
        t.add_row("DOB estimated", "Yes" if child_info[2] else "No")
        t.add_row("Age (months)", str(child_info[3]))
        t.add_row("Sex", "Male" if child_info[4] == "M" else "Female")
        t.add_row("Settlement", str(child_info[5]))
        t.add_row("Registered", str(child_info[6]))
        console.print(t)
    else:
        error("No child found with the provided ID.")
    return child_info

def ui_record_screening():
    header("\n--- Record Screening Visit ---")
    child_id = input("Enter child ID: ").strip().upper()
    weight = float(input("Weight (kg): ").strip())
    height = float(input("Height/Length (cm): ").strip())
    muac_mm = float(input("MUAC (mm): ").strip())
    oedema_status = input("Oedema status (present/absent): ").strip().lower()
    visit_type = input("Visit type (screening/follow-up): ").strip().lower()
    measurement_position = input("Measurement position (standing/lying): ").strip().lower()
    
    # calculate age in months at visit based on child's date of birth
    dob_str = get_child("data/nutritrack.db", child_id)[1]  # Retrieve date of birth from the database
    dob_obj = datetime.strptime(dob_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    age_in_months_at_visit = (
                (today.year - dob_obj.year) * 12 
                + (today.month - dob_obj.month)
                - (today.day < dob_obj.day)
            )

    # Hardcoding officer 1 and settlement 1 for testing purposes
    visit_id = record_screening_visit("data/nutritrack.db", child_id, "OFF-01", "S01", weight, height, muac_mm, oedema_status, visit_type, measurement_position, age_in_months_at_visit)

    if visit_id:
        success(f"Success! Visit recorded with ID {visit_id}")
    else:
        error("Failed to record visit. Ensure the Child ID is correct.")
    return visit_id

def ui_calculate_assessment():
    header("\n--- Calculate Nutritional Assessment ---")

    child_id = input("Enter child ID: ").strip().upper()

    # retreive latest screening data for a child
    visit = get_latest_screening_visit("data/nutritrack.db", child_id)
    if not visit:
        error("No screening visit found for the specified child.")
        return None

    visit_id = visit['visit_id']

    assessment = calculate_assessment(visit['muac_mm'], visit['oedema_status'])
        # Extract assessment information
    classification = assessment['muac_classification']
    overall_flag = assessment['overall_flag']

     # Pick colour, label and icon from severity
    if "Severe" in classification:
        color, icon, status = "red", "🚨", "URGENT: SEVERE ACUTE MALNUTRITION"
    elif "Moderate" in classification:
        color, icon, status = "yellow", "⚠️ ", "WARNING: MODERATE MALNUTRITION"
    else:
        color, icon, status = "green", "✅", "NORMAL NUTRITIONAL STATUS"

    # Main result panel
    console.print()
    console.print(Panel(
        f"[bold {color}]{icon}  {status}[/]\n\n"
        f"[bold]Classification:[/] {classification}\n"
        f"[bold]Action:[/] {overall_flag}",
        title="[bold]NutriTrack · Nutritional Assessment[/]",
        subtitle=f"Child {child_id}  |  Visit {visit_id}",
        border_style=color,
        padding=(1, 3),
    ))

    # Z-score table
    indicators = Table(
        title="Anthropometric Indicators",
        title_style="bold",
        box=box.SIMPLE_HEAVY,
        header_style="bold cyan",
    )
    indicators.add_column("Indicator")
    indicators.add_column("Z-score", justify="right")

    for label, key in [
        ("Weight-for-age (WAZ)", "waz"),
        ("Height-for-age (HAZ)", "haz"),
        ("Weight-for-height (WHZ)", "whz"),
    ]:
        value = assessment[key]
        indicators.add_row(
            label,
            f"{value}" if value is not None else "[dim]Not assessed[/]",
        )

    console.print(indicators)
    
    # automatically save the assessment
    saved_id = save_assessment("data/nutritrack.db", visit_id, assessment)
    if saved_id:
        success(f"Assessment saved automatically with ID {saved_id}.")
    else:
        error("Failed to save assessment to the database.")
    
    # flag assesment to automatically trigger referral if SAM is detected
    if "Severe" in assessment['muac_classification']:
        error("\n*** URGENT: SAM DETECTED ***")
        refer = input("Would you like to issue a referral now? (yes/no): ").strip().lower()
        if refer == 'yes':
            # Pass the known IDs directly to the referral function
            ui_create_referral(child_id=child_id, visit_id=visit_id)

def ui_create_referral(child_id=None, visit_id=None):
    header("\n--- Issue Clinical Referral ---")
    if child_id is None:
        child_id = input("Enter NutriTrack ID: ").strip().upper()
    if visit_id is None:
        visit_id = input("Enter Screening Visit ID: ").strip()
    
    try:
        visit_id = int(visit_id)
    except (ValueError, TypeError):
        error("Error: Visit ID must be a number.")
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
        success(f"Success! Referral {referral_id} issued to {facility}. Status set to 'Pending'.")
    else:
        error("Failed to issue referral. Verify the Child ID and Visit ID exist.")
        
    return referral_id

def ui_enroll_child(child_id=None):
    header("\n--- Enroll in Feeding Programme ---")

    if not child_id:
        child_id = input("Enter NutriTrack ID: ").strip().upper()
        
    print("Available Programs: SC (Stabilization Centre), OTP (Outpatient Therapeutic), SFP (Supplementary Feeding)")
    program = input("Enter Program Type (SC/OTP/SFP): ").strip().upper()
    
    enrolment_id = enroll_child("data/nutritrack.db", child_id, program)
    
    if enrolment_id:
        success(f"Success! Child {child_id} enrolled in {program}. Status set to 'Active'.")
    else:
        error("Failed to enroll child. Verify the Child ID exists.")
        
    return enrolment_id

def ui_export_data():
    header("\n--- Export Data ---")
    filename = input("Enter output filename (default: data_export.csv): ").strip()
    
    # Apply default filename if user just presses Enter
    if not filename:
        filename = "data_export.csv"
        
    # Ensure it ends with .csv
    if not filename.endswith(".csv"):
        filename += ".csv"
        
    success(f"Extracting records to {filename}...")
    
    with console.status("[bold green]Exporting data...[/]", spinner="dots"):
        rows_exported = export_assessments_to_csv("data/nutritrack.db", filename)
    
    if rows_exported is not None:
        success(f"Success! {rows_exported} screening records exported to {filename}.")
    else:
        error("Failed to export data.")
        
    return rows_exported


if __name__ == "__main__":
    main()

