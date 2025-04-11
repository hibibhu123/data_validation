import os
import shutil
import csv
import logging
import re  # For regular expression matching
from utils.file_handling import read_csv_data
from utils.logging_setup import setup_logger

# Initialize the logger
logger = setup_logger()

def after_all(context):
    """
    This method will be run once after all tests are completed.
    You can add code for final cleanup or reporting here.
    """
    # Final cleanup actions after all scenarios have been run
    for handler in logger.handlers:
        handler.flush()
        handler.close()
    logging.shutdown()  # Ensure the logger is properly shut down

def update_test_result(output_file_path, sl_no, status):
    """
    Updates the 'Test_Result' for the row with matching Sl_No in the output CSV file.
    """
    temp_file_path = os.path.join(os.path.dirname(output_file_path), "temp.csv")

    try:
        # Read the existing output CSV
        with open(output_file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            rows = list(reader)

        if 'Test_Result' not in fieldnames:
            fieldnames.append('Test_Result')

        updated = False
        # Iterate through rows to find matching Sl_No and update the Test_Result
        for row in rows:
            if row.get('Sl_No', '').strip() == sl_no.strip():
                row['Test_Result'] = status
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
        logger.info(f"Successfully updated Test_Result for Sl_No {sl_no} in: {output_file_path}")

    except Exception as e:
        logger.error(f"Error updating Test_Result: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def after_scenario(context, scenario):
    """
    This method will be executed after each scenario.
    It extracts the Sl_No from the scenario name and updates the corresponding row's Test_Result in the output CSV.
    """
    # Extract Sl_No from scenario name (e.g., "22_something_something -- @1.1")
    match = re.match(r"(\d+)_", context.scenario.name.strip())
    
    logger.info(f"Scenario Name: {scenario.name}")
    
    if match:
        scenario_sl_no = match.group(1).strip()
        logger.info(f"Extracted Sl_No: {scenario_sl_no}")
        
        # Determine scenario status
        scenario_status = "PASS" if scenario.status == "passed" else "FAIL"
        logger.info(f"Scenario Status: {scenario_status}")
        logger.info(f"Scenario '{scenario.name}' completed with status: {scenario_status}")
        
        # Define the path to the input and output files
        input_file_path = "C:\\Bibhu\\Data_Validation\\src\\config\\input_template.csv"  # Update to actual input CSV path
        output_file_path = "output\\updated_test_results.csv"
        
        # Read the input CSV dynamically and filter rows with Action == 'yes'
        input_data = read_csv_data(input_file_path)
        
        # Look for the corresponding row with the same Sl_No and update the status
        for row in input_data:
            # Filter the rows where Action == 'yes' and match the Sl_No
            if row.get('Sl_No').strip() == scenario_sl_no and row.get('Action', '').strip().lower() == 'yes':
                # Update the Test_Result in the output CSV if the row has Action == 'yes'
                update_test_result(output_file_path, scenario_sl_no, scenario_status)
                break
    else:
        logger.warning(f"Could not extract Sl_No from scenario name: {scenario.name}")


def before_scenario(context, scenario):
    """
    This method will be executed before each scenario.
    You can clean up or reset any global resources here.
    """
    # Add any cleanup or logging for individual scenarios if needed
    logger.info(f"***************************  Scenario {scenario.name} started  **************************************")
    pass
