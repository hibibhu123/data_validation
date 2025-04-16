import os
import shutil
import csv
import logging
import re
from src.utils.file_handling import read_csv_data
from src.utils.logging_setup import setup_logger

from dotenv import load_dotenv  # For regular expression matching

# Load environment variables from .env file
load_dotenv()  # This automatically loads the variables defined in the .env file

# Initialize the logger
logger = setup_logger()


def before_all(context):
    input_file_path = os.getenv("INPUT_CSV_TEMPLATE_PATH")
    output_file_path = os.getenv("OUTPUT_CSV_FILE_PATH")

    # Remove old output file
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
        logger.info("Old output file removed before test run.")

    # Attempt to generate a new one if input exists
    if os.path.exists(input_file_path):
        ensure_output_file_exists(input_file_path, output_file_path)
        logger.info("Output file generated at test start.")
    else:
        logger.warning(f"Input file does not exist yet: {input_file_path}. Output will not be created now.")


def after_all(context):
    """
    This method will be run once after all tests are completed.
    You can add code for final cleanup or reporting here.
    """
    for handler in logger.handlers:
        handler.flush()
        handler.close()
    logging.shutdown()  # Ensure the logger is properly shut down

def ensure_output_file_exists(input_file_path, output_file_path):
    """
    Creates the output CSV based on rows in the input file with Action='yes' if it doesn't already exist.
    Adds a 'Validation Status' column with blank values.
    """
    if not os.path.exists(output_file_path):
        logger.info(f"Output file not found. Creating: {output_file_path}")
        input_data = read_csv_data(input_file_path)
        filtered_data = [row for row in input_data if row.get('Action', '').strip().lower() == 'yes']
        
        if filtered_data:
            fieldnames = list(filtered_data[0].keys())
            if 'Validation Status' not in fieldnames:
                fieldnames.append('Validation Status')
            
            # Add empty Validation Status for each row
            for row in filtered_data:
                row['Validation Status'] = ''
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Write to output file
            with open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filtered_data)
            logger.info(f"Output file created with filtered rows from input file.")
        else:
            logger.warning("No rows with Action='yes' found in input file. Output file not created.")

def update_validation_status(output_file_path, sl_no, status):
    """
    Updates the 'Validation Status' for the row with matching Sl_No in the output CSV file.
    """
    temp_file_path = os.path.join(os.path.dirname(output_file_path), "temp.csv")

    try:
        # Read the existing output CSV
        with open(output_file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            rows = list(reader)

        if 'Validation Status' not in fieldnames:
            fieldnames.append('Validation Status')

        updated = False
        # Iterate through rows to find matching Sl_No and update the Validation Status
        for row in rows:
            if row.get('Sl_No', '').strip() == sl_no.strip():
                row['Validation Status'] = status
                updated = True
                logger.info(f"Updated Sl_No {sl_no} with status: {status}")
                break

        if not updated:
            logger.warning(f"Sl_No {sl_no} not found in output file.")

        # Write updated rows to a temporary file
        with open(temp_file_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        # Replace the original output file with the updated temporary file
        shutil.move(temp_file_path, output_file_path)
        logger.info(f"Successfully updated Validation Status for Sl_No {sl_no} in: {output_file_path}")

    except Exception as e:
        logger.error(f"Error updating validation status: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def after_scenario(context, scenario):
    """
    This method will be executed after each scenario.
    It extracts the Sl_No from the scenario name and updates the corresponding row's Validation Status in the output CSV.
    """
    match = re.match(r"(\d+)_", scenario.name.strip())
    
    logger.info(f"Scenario Name: {scenario.name}")
    
    if match:
        scenario_sl_no = match.group(1).strip()
        logger.info(f"Extracted Sl_No: {scenario_sl_no}")
        
        # Determine scenario status
        scenario_status = "PASS" if scenario.status == "passed" else "FAIL"
        logger.info(f"Scenario Status: {scenario_status}")
        logger.info(f"Scenario '{scenario.name}' completed with status: {scenario_status}")
        
        # Define the path to the input and output files
        input_file_path = os.getenv('INPUT_CSV_TEMPLATE_PATH')
        output_file_path =os.getenv('OUTPUT_CSV_FILE_PATH')
        
        # Ensure the output file is generated if not present
        #ensure_output_file_exists(input_file_path, output_file_path)

        # Read input and update validation status only if Action is yes
        input_data = read_csv_data(input_file_path)
        for row in input_data:
            if row.get('Sl_No').strip() == scenario_sl_no and row.get('Action', '').strip().lower() == 'yes':
                update_validation_status(output_file_path, scenario_sl_no, scenario_status)
                break
    else:
        logger.warning(f"Could not extract Sl_No from scenario name: {scenario.name}")

def before_scenario(context, scenario):
    """
    This method will be executed before each scenario.
    """
    logger.info(f"***************************  Scenario {scenario.name} started  **************************************")
