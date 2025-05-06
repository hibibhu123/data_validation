import csv
import os
from utils.generate_sql_files import generate_sql_files_from_csv
from utils.logging_setup import setup_logger

# Initialize the logger
logger = setup_logger()

def read_csv_data(file_path):
    """
    Reads the CSV file and returns a list of dictionaries representing the rows.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list: A list of dictionaries where each dictionary represents a row in the CSV file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    data = []
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:  # Note the encoding 'utf-8-sig'
        reader = csv.DictReader(file)
        for row in reader:
            # Strip any potential BOM from the keys
            data.append(row)
    return data

#To read "config" sheet from the input CSV file
def read_config_data(file_path):
    """
    Reads the second sheet or configuration part of the CSV file and returns parameters.

    Args:
        file_path (str): Path to the CSV file.
    
    Returns:
        dict: A dictionary containing configuration parameters.
    """
    config_data = {}
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Assuming the config is just key-value pairs like input_csv_template_path, feature_file_output_path
            for key, value in row.items():
                config_data[key.strip()] = value.strip()

    return config_data

def clean_sql(sql_text):
    """
    Removes newlines and excess spaces from SQL text to make it Gherkin-compatible.
    """
    if not isinstance(sql_text, str):
        return sql_text
    return ' '.join(sql_text.split())  # replaces all newlines, tabs, multiple spaces with single space


def generate_feature_file(csv_data, feature_file_path, sql_file_base_path):
    """
    Filters the CSV data to only include rows with 'Action == yes' and generates a Gherkin feature file.
    The 'Action' column will not be included in the feature file, and SQL file paths will be used for source and target SQL.

    Args:
        csv_data (list): A list of dictionaries representing the rows in the CSV file.
        feature_file_path (str): Path where the generated feature file will be saved.
        sql_file_base_path (str): Path where SQL files will be created.
    """

    # Call the function to generate SQL files and get paths for source and target SQL
    sql_paths = generate_sql_files_from_csv(csv_data, sql_file_base_path)

    # Define the Gherkin scenario template
    feature_template = """Feature: Data Validation

    Scenario Outline: <Sl_No>_<Source_Object>_<Target_Object>_<Validation_Type>
        Given I connect to the source "<Source_Object>" in "<Source_Location>"
        And I connect to the target "<Target_Object>" in "<Target_Location>"
        When I perform "<Validation_Type>" validation using source SQL "<Source_SQL>" and target SQL "<Target_SQL>"
        Then the "<Validation_Type>" validation between source and target is successful

    Examples:
    """

    # Filter the rows based on 'Action' column being 'yes'
    filtered_data = [row for row in csv_data if row.get("Action", "").lower() == "yes"]

    # If no rows with 'Action == yes' found, log and return
    if not filtered_data:
        logger.info("No data with 'Action == yes' found in the CSV. No feature file generated.")
        return

    # Add the headers (column names) from the filtered CSV data as the first row in the Examples section
    # Remove the 'Action' column from headers before writing
    headers = [header for header in filtered_data[0].keys() if header.lower() not in ["action"] ]
    header_row = "    | " + " | ".join(headers) + " |"  # Format the headers for the feature file
    feature_template += "\n" + header_row  # Append headers to the feature template

    # Add examples from filtered CSV data
    for row in filtered_data:
        sl_no = int(row["Sl_No"])

        # Fetch the SQL paths for the scenario
        scenario_sql = sql_paths.get(sl_no, {})

        # Replace the placeholders for Source_SQL and Target_SQL with the actual SQL file paths
        source_sql_path = scenario_sql.get("source", "NA")
        target_sql_path = scenario_sql.get("target", "NA")

        # Add the Sl_No, Source_Object, Target_Object in the scenario name and example
        example_row = "    | " + " | ".join([
            str(row[field]) if field.lower() not in ["source_sql", "target_sql"] else (
                source_sql_path if field.lower() == "source_sql" else target_sql_path
            ) for field in headers
        ]) + " |"

        feature_template += "\n" + example_row  # Append each example row to the feature template
        logger.debug(f"Added example row: {example_row}")

    # Write the generated feature to a new file
    with open(feature_file_path, 'w', encoding='utf-8') as feature_file:
        feature_file.write(feature_template)

    logger.info(f"Feature file {feature_file_path} generated successfully.")
    logger.info(f"Generated Feature File Content:\n{feature_template}\n")
