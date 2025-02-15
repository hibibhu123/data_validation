import os
import shutil
import subprocess

def run_tests():
    # Define the paths
    feature_dir = "features"
    report_dir = "reports"
    allure_report_dir = "allure-report"

    # Ensure the report directory is deleted if it exists
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir)
    os.makedirs(report_dir)

    # Add Allure to PATH
    os.environ["PATH"] += os.pathsep + "C:\\allure-2.32.0\\bin"

    try:
        # Run the tests with Behave and Allure formatter
        result = subprocess.run("behave -f allure_behave.formatter:AllureFormatter -o " + report_dir, shell=True)
        
        # Check the result of subprocess (if tests failed)
        if result.returncode != 0:
            print(f"Tests failed with return code {result.returncode}. But we'll generate the Allure report.")

        # Generate the Allure report with --clean option
        subprocess.run("allure generate " + report_dir + " -o " + allure_report_dir + " --clean", shell=True, check=True)

        # Serve the Allure report
        subprocess.run("allure open " + allure_report_dir, shell=True, check=True)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_tests()
