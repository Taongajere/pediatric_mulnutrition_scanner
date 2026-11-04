
import pandas as pd
import numpy as np

def calculate_wfh_zscore(age_at_visit, sex, height_cm, weight_kg):
    """
    Calculate Weight-for-Height Z-score using WHO LMS standards.
    Reference: WHO Weight-for-Height Boys 2-5 years.
    """
    # Determine the age group
    if 0 <= age_at_visit < 24:
        age_group = "0-to-2-years"
        begin = 'wfl'
    elif 24 <= age_at_visit <= 60:
        age_group = "2-to-5-years"
        begin = 'wfh'
    else:
        raise ValueError("Age must be between 0 and 60 months.")

    # Load the appropriate WHO reference table based on sex
    sex_str = str(sex).strip().lower()

    if sex_str in ['m', 'male']:
        sex = 'boys'
    elif sex_str in ['f', 'female']:
        sex = 'girls'

    file_path = f"data/WHO-2006-standards/{begin}_{sex.lower()}_{age_group}_zscores.xlsx"

    df = pd.read_excel(file_path)

    # Ensure numerical values
    height_column = 'Length' if begin == 'wfl' else 'Height'
    df[height_column] = pd.to_numeric(df[height_column])
    df["L"] = pd.to_numeric(df["L"])
    df["M"] = pd.to_numeric(df["M"])
    df["S"] = pd.to_numeric(df["S"])

    # Validate height range
    if not df[height_column].min() <= height_cm <= df[height_column].max():
        raise ValueError(
            f"{height_column} must be between "
        f"{df[height_column].min()} and {df[height_column].max()} cm."
        )

    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")

    # Get LMS values for the child's height.
    # Interpolation allows heights between table entries.
    L = np.interp(height_cm, df[height_column], df["L"])
    M = np.interp(height_cm, df[height_column], df["M"])
    S = np.interp(height_cm, df[height_column], df["S"])

    # Calculate Z-score using WHO LMS formula
    if L != 0:
        z_score = ((weight_kg / M) ** L - 1) / (L * S)
    else:
        z_score = np.log(weight_kg / M) / S

    return round(float(z_score), 2)

def calculate_lhfa_zscore(age_at_visit, sex, height_cm):
    """
    Calculate Height-for-age Z-score using WHO LMS standards.
    Reference: WHO Height-for-age Boys 2-5 years.
    """
    # Determine the age group
    if 0 <= age_at_visit <3:
        age_group = "0-to-13-weeks"
    elif 0 <= age_at_visit < 24:
        age_group = "0-to-2-years"
    elif 24 <= age_at_visit <= 60:
        age_group = "2-to-5-years"
    else:
        raise ValueError("Age must be between 0 and 60 months.")

    # Load the appropriate WHO reference table based on sex
    sex_str = str(sex).strip().lower()

    if sex_str in ['m', 'male']:
        sex = 'boys'
    elif sex_str in ['f', 'female']:
        sex = 'girls'

    file_path = f"data/WHO-2006-standards/lhfa_{sex.lower()}_{age_group}_zscores.xlsx"

    df = pd.read_excel(file_path)

    # find age value
    if age_at_visit < 3:
        age_value = age_at_visit / 4.348125
        age_column = 'Week'
    else:
        age_value = age_at_visit 
        age_column = 'Month'

    # 10. Interpolate LMS values using age
    L = np.interp(age_value, df[age_column], df["L"])
    M = np.interp(age_value, df[age_column], df["M"])
    S = np.interp(age_value, df[age_column], df["S"])   

    # Validate height range
    if not df[age_column].min() <= age_value <= df[age_column].max():
        raise ValueError(
            f"{age_column} must be between "
            f"{df[age_column].min()} and {df[age_column].max()} cm."
        )

    # Calculate Z-score using WHO LMS formula
    if L != 0:
        z_score = ((height_cm / M) ** L - 1) / (L * S)
    else:
        z_score = np.log(height_cm / M) / S

    return round(float(z_score), 2)

def calculate_wfa_zscore(age_at_visit, sex, weight_kg):
    """
    Calculate Height-for-age Z-score using WHO LMS standards.
    Reference: WHO Height-for-age Boys 2-5 years.
    """
    # Determine the age group
    if 0 <= age_at_visit <3:
        age_group = "0-to-13-weeks"
    elif 0 <= age_at_visit <= 60:
        age_group = "0-to-5-years"
    else:
        raise ValueError("Age must be between 0 and 60 months.")

    # Load the appropriate WHO reference table based on sex
    sex_str = str(sex).strip().lower()

    if sex_str in ['m', 'male']:
        sex = 'boys'
    elif sex_str in ['f', 'female']:
        sex = 'girls'

    file_path = f"data/WHO-2006-standards/wfa_{sex.lower()}_{age_group}_zscores.xlsx"

    df = pd.read_excel(file_path)

    # find age value
    if age_at_visit < 3:
        age_value = age_at_visit / 4.348125
        age_column = 'Week'
    else:
        age_value = age_at_visit 
        age_column = 'Month'

    # 10. Interpolate LMS values using age
    L = np.interp(age_value, df[age_column], df["L"])
    M = np.interp(age_value, df[age_column], df["M"])
    S = np.interp(age_value, df[age_column], df["S"])   

    # Validate height range
    if not df[age_column].min() <= age_value <= df[age_column].max():
        raise ValueError(
            f"{age_column} must be between "
            f"{df[age_column].min()} and {df[age_column].max()} cm."
        )

    if weight_kg < 0:
        raise ValueError ('weight must be above 0.00 Kgs')

    # Calculate Z-score using WHO LMS formula
    if L != 0:
        z_score = ((weight_kg / M) ** L - 1) / (L * S)
    else:
        z_score = np.log(weight_kg / M) / S

    return round(float(z_score), 2)

