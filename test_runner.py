import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from utils.file_handling import generate_feature_file, read_csv_data

# Load .env variables
load_dotenv()

def copy_environment_file():
    """
    This function copies the environment.py file to the features directory dynamically.
    """
    try:
        # Get the source and target paths
        src_path = Path(os.getenv("HOOK_PATH")) / "environment.py"  # Path where your environment.py is stored
        target_dir = Path(os.getenv("FEATURE_FILE_PATH"))  # This should be your target features directory
        
        # Ensure the target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the environment.py to the target directory
        shutil.copy(src_path, target_dir / "environment.py")
        print(f"Copied environment.py to {target_dir}/environment.py")
        
    except Exception as e:
        print(f"Error copying environment.py: {e}")

def run_tests():
    # Fetch all paths from .env
    input_csv_template_path = os.getenv("INPUT_CSV_TEMPLATE_PATH")
    sql_file_base_path = os.getenv("SQL_FILE_PATH")
    input_feature_dir = os.getenv("FEATURE_FILE_PATH")
    feature_file_name = os.getenv("FEATURE_FILE_NAME", "validation.feature")
    step_defs_path = os.getenv("STEPS_DIR_PATH")
    allure_results_dir = os.getenv("ALLURE_RESULTS_PATH")
    allure_report_dir = os.getenv("ALLURE_REPORT_PATH")
    html_report_dir = os.getenv("HTML_REPORT_PATH")
    allure_cmd = os.getenv("ALLURE_CLI_PATH")

    if not all([input_csv_template_path, input_feature_dir, step_defs_path, allure_results_dir, allure_report_dir, html_report_dir, allure_cmd]):
        print("One or more environment variables are missing. Please check your .env file.")
        return

    # Resolve paths
    feature_dir_path = Path(input_feature_dir).expanduser().resolve()
    steps_target_dir = feature_dir_path / "steps"
    feature_file_path = feature_dir_path / feature_file_name
    html_report_path = Path(html_report_dir).expanduser().resolve()
    html_file = html_report_path / "test_execution_report.html"

    print(f"input CSV file path: {input_csv_template_path}")
    print(f"sql file path      : {sql_file_base_path}")
    print(f"Feature Dir        : {feature_dir_path}")
    print(f"Feature File       : {feature_file_path}")
    print(f"Steps Source Dir   : {step_defs_path}")
    print(f"Steps Target Dir   : {steps_target_dir}")
    print(f"Allure Results Dir : {allure_results_dir}")
    print(f"Allure Report Dir  : {allure_report_dir}")
    print(f"HTML Report Path   : {html_file}")
    print(f"Allure CLI         : {allure_cmd}")

    # Clean and recreate required folders
    if feature_dir_path.exists():
        shutil.rmtree(feature_dir_path)
    feature_dir_path.mkdir(parents=True, exist_ok=True)

    if os.path.exists(allure_results_dir):
        shutil.rmtree(allure_results_dir)
    os.makedirs(allure_results_dir, exist_ok=True)

    if os.path.exists(allure_report_dir):
        shutil.rmtree(allure_report_dir)

    if html_report_path.exists():
        shutil.rmtree(html_report_path)
    html_report_path.mkdir(parents=True, exist_ok=True)

    # Copy step definitions to the new "steps" folder inside the feature dir
    steps_target_dir.mkdir(parents=True, exist_ok=True)
    for file in Path(step_defs_path).glob("*.py"):
        shutil.copy(file, steps_target_dir)

    # Copy environment.py before running tests
    copy_environment_file()

    # Pass the sql_file_base_path to generate_feature_file
    generate_feature_file(read_csv_data(input_csv_template_path), str(feature_file_path), sql_file_base_path)


    # Run Behave with the dynamically generated feature file path
    print("Running Behave tests with Allure and HTML formatters...")
    behave_cmd = [
        "behave", str(feature_dir_path),
        "-f", "allure_behave.formatter:AllureFormatter", "-o", allure_results_dir,
        "-f", "behave_html_formatter:HTMLFormatter", "-o", str(html_file)
    ]

    behave_result = subprocess.run(behave_cmd, capture_output=True, text=True)
    print(behave_result.stdout)
    if behave_result.stderr:
        print("Behave STDERR:")
        print(behave_result.stderr)

    if behave_result.returncode != 0:
        print("Behave tests failed — generating reports anyway...")

    # Generate Allure report
    print("Generating Allure report...")
    generate_cmd = [allure_cmd, "generate", allure_results_dir, "-o", allure_report_dir, "--clean"]
    generate_result = subprocess.run(generate_cmd, capture_output=True, text=True)

    print("Allure Generate Output:")
    print(generate_result.stdout)
    if generate_result.returncode != 0:
        print("Failed to generate Allure report.")
        print(generate_result.stderr)
    else:
        print("Opening Allure report in browser...")
        subprocess.Popen([allure_cmd, "open", allure_report_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Open HTML report
    if html_file.exists():
        print("Opening HTML report in browser...")
        webbrowser.open(f"file:///{html_file}")
    else:
        print("HTML report not found.")

    # Cleanup step definitions and environment.py after successful execution
    print("Cleaning up generated files...")
    cleanup_files(feature_dir_path)    

def cleanup_files(feature_dir_path):
    """Delete generated environment.py and stepdef files after successful execution."""
    step_defs_dir = feature_dir_path / "steps"
    environment_file = feature_dir_path / "environment.py"
    
    # Remove the step definition files
    if step_defs_dir.exists():
        shutil.rmtree(step_defs_dir)
        print("Step definition files deleted.")
    
    # Remove the environment.py file
    if environment_file.exists():
        os.remove(environment_file)
        print("Environment file deleted.")        

if __name__ == "__main__":
    run_tests()
