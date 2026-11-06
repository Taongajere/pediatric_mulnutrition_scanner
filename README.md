# NutriTrack: Child Nutrition Screening System
#### Video Demo : https://youtu.be/xJhkjYO60HU


NutriTrack is a Command Line Interface (CLI) application designed to help health workers track, manage, and assess child nutritional health. It streamlines the process of registering children, recording screening visits, calculating World Health Organization (WHO) anthropometric Z-scores, and managing clinical interventions like referrals and feeding program enrollments.

## How It Works: Python & R Integration

NutriTrack calculates nutritional Z-scores (Weight-for-Age, Height-for-Age, Weight-for-Height) using the official World Health Organization (WHO) standards. 

**Design Evolution: Why R?**
Initially, NutriTrack was designed with a native Python implementation for calculating Z-scores. This first design relied on manually cross-referencing the WHO LMS (Lambda, Mu, Sigma) reference tables. However, because these reference tables are provided in discrete intervals (e.g., monthly age steps or specific length intervals), accurately mapping exact, continuous patient measurements (like an age in exact days) to the LMS values caused interpolation problems and slight inaccuracies. 

To ensure strict, medical-grade adherence to WHO standards without complex mathematical workarounds, the architecture was pivoted to utilize the official WHO `anthro` package, which is written in the **R** programming language.

To make this seamless in a Python CLI, NutriTrack uses a bridge:

1. When you choose to calculate an assessment, Python gathers the child's screening data and converts it into a JSON format.
2. Python quietly executes the `anthro_calculate.R` script in the background using your system's `Rscript` command.
3. The R script processes the continuous data through the WHO `anthro` package (which handles the exact LMS math natively) and returns the calculated Z-scores back to Python as JSON.
4. Python interprets this data, flags any severe malnutrition (SAM), and displays a color-coded alert on your screen.

## Prerequisites

To run NutriTrack, you will need the following installed on your system:

* **Python 3.8+**
* **R (Statistical Computing Environment)**

## Installation & Setup

### Step 1: Install R and Required Packages

Because NutriTrack relies on R to perform the heavy statistical lifting, you must have R installed and configured on your computer.

1. **Download R:** Go to the [Comprehensive R Archive Network (CRAN)](https://cran.r-project.org/) and download the installer for your operating system (Windows, macOS, or Linux).

2. **Add R to your PATH:** During installation (especially on Windows), ensure that R is added to your system's `PATH` environment variable. This allows Python to run the `Rscript` command from the terminal.

3. **Install R Packages:** Open your terminal or the R GUI console and run the following command to install the required packages:

   ```R
   install.packages(c("anthro", "jsonlite"))
   ```

### Step 2: Set Up the Python Environment

1. **Clone or Download the Repository**
   Navigate to the project directory in your terminal.

2. **Install Python Dependencies**
   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Initialize the Database

Before running the application for the first time, you must initialize the SQLite database. This creates the necessary tables and seeds default data (like default settlements and health officers).

```bash
python database.py
```

## Usage

Start the main application by running:

```bash
python project.py
```

You will be greeted by the NutriTrack main menu. Use your keyboard to select an option (1-8):

1. **Register a new child:** Enter basic demographics.
2. **Retrieve child information:** Look up a child's record by their generated ID.
3. **Record screening visit:** Enter clinical measurements.
4. **Calculate nutritional assessment:** Evaluates the latest screening data using WHO standards (Triggers the R script).
5. **Create referral:** Issue a pending referral to a medical facility.
6. **Enroll child in feeding programme:** Assign a child to SC, OTP, or SFP.
7. **Export assessments to CSV:** Generate report files in the `data/` folder.
8. **Exit:** Safely close the application.

## Testing

NutriTrack uses `pytest` and `unittest.mock` to simulate CLI interactions and test application logic without requiring manual input.

To run the test suite, simply execute:

```bash
pytest test_project.py
```

## File Structure

```text
nutritrack/
│
├── project.py               # Main CLI application and UI routing.
├── test_project.py          # Automated tests for the CLI menus and logic.
├── requirements.txt         # Python dependencies (rich, pandas, pytest, etc.).
├── anthro_calculate.R       # R script that calculates WHO Z-scores via stdin/stdout.
├── database.py              # SQLite schema definition and initialization script.
│
├── nutri_track/             # Core application modules
│   ├── children.py          # Handles child registration and data retrieval.
│   ├── screening.py         # Logs screening visits and measurements.
│   ├── assesment.py         # Bridges Python with the R script and saves results.
│   ├── referals.py          # Manages clinical referrals.
│   ├── enrollment.py        # Manages feeding program enrollments.
│   └── reports.py           # Handles SQL queries to export data to CSV.
│
└── data/
    └── nutritrack.db        # The local SQLite database (generated at runtime).
```