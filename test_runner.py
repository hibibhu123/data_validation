import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def run_tests():
    # Fetch all paths from .env
    allure_results_dir = os.getenv("ALLURE_RESULTS_PATH")
    allure_report_dir = os.getenv("ALLURE_REPORT_PATH")
    html_report_dir = os.getenv("HTML_REPORT_PATH")
    allure_cmd = os.getenv("ALLURE_CLI_PATH")

    if not (allure_results_dir and allure_report_dir and html_report_dir and allure_cmd):
        print("❌ Environment paths not loaded. Please check your .env file.")
        return

    # Resolve HTML file path
    html_report_path = Path(html_report_dir).expanduser().resolve()
    html_file = html_report_path / "test_execution_report.html"

    print(f"📂 Allure Results Dir : {allure_results_dir}")
    print(f"📂 Allure Report Dir  : {allure_report_dir}")
    print(f"📄 HTML Report Path   : {html_file}")
    print(f"🛠️ Allure CLI         : {allure_cmd}")

    # Clean existing directories
    if os.path.exists(allure_results_dir):
        shutil.rmtree(allure_results_dir)
    os.makedirs(allure_results_dir, exist_ok=True)

    if os.path.exists(allure_report_dir):
        shutil.rmtree(allure_report_dir)

    if html_report_path.exists():
        shutil.rmtree(html_report_path)
    html_report_path.mkdir(parents=True, exist_ok=True)

    # Run Behave with both formatters
    print("🚀 Running Behave tests with Allure and HTML formatters...")
    behave_cmd = [
        "behave",
        "-f", "allure_behave.formatter:AllureFormatter", "-o", allure_results_dir,
        "-f", "behave_html_formatter:HTMLFormatter", "-o", str(html_file)
    ]

    behave_result = subprocess.run(behave_cmd, capture_output=True, text=True)
    print(behave_result.stdout)
    if behave_result.stderr:
        print("⚠️ Behave STDERR:")
        print(behave_result.stderr)

    if behave_result.returncode != 0:
        print("⚠️ Behave tests failed — generating reports anyway...")

    # Generate Allure report
    print("🛠️ Generating Allure report...")
    generate_cmd = [allure_cmd, "generate", allure_results_dir, "-o", allure_report_dir, "--clean"]
    generate_result = subprocess.run(generate_cmd, capture_output=True, text=True)

    print("📦 Allure Generate Output:")
    print(generate_result.stdout)
    if generate_result.returncode != 0:
        print("❌ Failed to generate Allure report.")
        print(generate_result.stderr)
    else:
        print("🌐 Opening Allure report in browser...")
        subprocess.Popen([allure_cmd, "open", allure_report_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Open HTML report
    if html_file.exists():
        print("🌐 Opening HTML report in browser...")
        webbrowser.open(f"file:///{html_file}")
    else:
        print("❌ HTML report not found.")

if __name__ == "__main__":
    run_tests()
