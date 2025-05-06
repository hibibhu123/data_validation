import os
import shutil
import pandas as pd
from utils.logging_setup import setup_logger

# Initialize the logger
logger = setup_logger()

def generate_sql_files_from_csv(csv_data, sql_file_base_path):
    # Remove and recreate the base scenario folder
    if os.path.exists(sql_file_base_path):
        shutil.rmtree(sql_file_base_path)
        logger.info(f"Deleted existing directory: {sql_file_base_path}")
    os.makedirs(sql_file_base_path)
    logger.info(f"Created base directory: {sql_file_base_path}")

    # Read the input CSV
    df = pd.DataFrame(csv_data)

    # Dictionary to store paths for use in feature file generation
    sql_paths = {}

    for index, row in df.iterrows():
        action_value = str(row.get('Action', '')).strip().lower()
        validation_type = str(row.get('Validation_Type', '')).strip().lower()

        if action_value != 'yes':
            logger.info(f"Skipping scenario {row['Sl_No']} as Action != 'yes'")
            continue

        if validation_type == 'metadata':
            logger.info(f"Skipping SQL file creation for scenario {row['Sl_No']} (metadata validation)")
            continue

        sl_no = int(row['Sl_No'])
        source_sql = str(row['Source_SQL']).strip()
        target_sql = str(row['Target_SQL']).strip()

        # Create the folder for the scenario (e.g., "scenario_1")
        scenario_folder = os.path.join(sql_file_base_path, f"scenario_{sl_no}")
        os.makedirs(scenario_folder, exist_ok=True)

        scenario_entry = {}

        # If source SQL is not "NA", write it to a file
        if source_sql and source_sql.upper() != "NA":
            source_file = os.path.join(scenario_folder, "source.sql")
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(source_sql)
            scenario_entry["source"] = source_file
            logger.info(f"Source SQL written for scenario {sl_no}: {source_file}")

        # If target SQL is not "NA", write it to a file
        if target_sql and target_sql.upper() != "NA":
            target_file = os.path.join(scenario_folder, "target.sql")
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(target_sql)
            scenario_entry["target"] = target_file
            logger.info(f"Target SQL written for scenario {sl_no}: {target_file}")

        if not scenario_entry:
            logger.info(f"No SQL written for scenario {sl_no} (both source and target are NA)")

        sql_paths[sl_no] = scenario_entry

    logger.info("SQL file generation completed for all valid scenarios.")
    return sql_paths

def read_sql_from_file(file_path):
    """Read SQL query from a file if the path is valid."""
    try:
        if not file_path or file_path.strip().upper() == "NA":
            logger.warning(f"Skipping SQL read because file_path is NA or empty: {file_path}")
            return None

        with open(file_path, 'r') as file:
            sql_query = file.read().strip()
        return sql_query

    except Exception as e:
        logger.error(f"Error reading SQL from file {file_path}: {e}")
        raise e

