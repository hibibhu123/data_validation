import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def run_tests():
    html_report_dir = os.getenv("HTML_REPORT_PATH")

    if not html_report_dir:
        print(" HTML_REPORT_PATH not found in .env file.")
        return

    # Convert to Path object for easy manipulation
    report_path = Path(html_report_dir).expanduser().resolve()
    html_file = report_path / "test_execution_report.html"
    print(html_file)

    # Clean and recreate report directory
    if report_path.exists():
        shutil.rmtree(report_path)
    report_path.mkdir(parents=True, exist_ok=True)

    print(f"📂 HTML report will be saved to: {html_file}")

    # Run Behave tests with HTML formatter
    try:
        print(" Running Behave tests...")
        result = subprocess.run(
            [
                "behave",
                "-f", "behave_html_formatter:HTMLFormatter",
                "-o", str(html_file)
            ],
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print("⚠️ STDERR:\n", result.stderr)

        # Open the report
        if html_file.exists():
            print("🌐 Opening HTML report in browser...")
            webbrowser.open(f"file:///{html_file}")
        else:
            print(" Report was not generated.")

    except subprocess.CalledProcessError as e:
        print(f" Error running Behave tests: {e}")

if __name__ == "__main__":
    run_tests()

   