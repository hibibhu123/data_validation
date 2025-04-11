import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def run_tests():
    results_dir = os.getenv("ALLURE_RESULTS_PATH")
    report_dir = os.getenv("ALLURE_REPORT_PATH")
    allure_cmd = r"C:\Installation\allure-commandline-2.14.0\allure-2.14.0\bin\allure.bat"

    if not results_dir or not report_dir:
        print("❌ Environment paths not loaded. Please check your .env file.")
        return

    print(f"📂 Allure Results: {results_dir}")
    print(f"📂 Allure Report : {report_dir}")

    # Clean and recreate directories
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir)

    if os.path.exists(report_dir):
        shutil.rmtree(report_dir)

    # Step 1: Run Behave tests
    print("🚀 Running Behave tests...")
    behave_cmd = ["behave", "-f", "allure_behave.formatter:AllureFormatter", "-o", results_dir]
    behave_result = subprocess.run(behave_cmd, capture_output=True, text=True)

    print(behave_result.stdout)
    if behave_result.stderr:
        print("⚠️ Behave STDERR:")
        print(behave_result.stderr)

    if behave_result.returncode != 0:
        print("⚠️ Behave tests failed — generating report anyway...")

    # Step 2: Generate Allure Report
    print("🛠️ Generating Allure report...")
    generate_cmd = [allure_cmd, "generate", results_dir, "-o", report_dir, "--clean"]
    generate_result = subprocess.run(generate_cmd, capture_output=True, text=True)

    print("📦 Allure Generate Output:")
    print(generate_result.stdout)
    if generate_result.returncode != 0:
        print("❌ Failed to generate Allure report.")
        print(generate_result.stderr)
        return

    # Step 3: Open report non-blocking
    print("🌐 Opening Allure report in browser...")
    subprocess.Popen([allure_cmd, "open", report_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    run_tests()
