# Initialize the logger
from utils.logging_setup import setup_logger

logger = setup_logger()

def get_metadata(sql, location, object_name):
    # Function to get column names and types for metadata validation
    # This can involve executing the SQL and parsing the results
    logger.info(f"Fetching metadata for {object_name} at {location} using SQL: {sql}")
    # Simulate metadata fetching logic here
    metadata = [("id", "int"), ("name", "varchar"), ("age", "int")]  # Example result
    return metadata