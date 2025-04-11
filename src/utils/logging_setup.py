import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()  # This automatically loads the variables defined in the .env file

def setup_logger():
    """
    Set up a logger that writes logs to both console and a file.
    Ensures no duplicate logs in the console and file.
    """
    logger = logging.getLogger('ADVF')
    logger.setLevel(logging.INFO)  # Set logging level to INFO (or as needed)

    # Fetch the log file path from the environment variable
    log_file_path = os.getenv('LOG_FILE_PATH', './logs/validation_execution.log')  # Default to './logs/validation_execution.log' if not set

    # Clear any existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')  # Ensure file output uses UTF-8 encoding
    file_handler.setLevel(logging.INFO)  # You can adjust this level if needed

    # Create a console handler to print logs to the console with UTF-8 support
    console_handler = logging.StreamHandler(sys.stdout)  # Use sys.stdout for better control
    console_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Example usage:
logger = setup_logger()
logger.info("Logger setup successfully")
