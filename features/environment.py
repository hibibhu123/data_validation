import os
import shutil
import subprocess
import logging
import time
from utils.file_handling import generate_feature_file, read_csv_data
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



def after_scenario(context, scenario):
    """
    This method will be executed after each scenario.
    You can clean up or reset any global resources here.
    """
    # Add any cleanup or logging for individual scenarios if needed
    logger.info(f"########################  Scenario {scenario.name} completed  #################################### \n")
    pass

def before_scenario(context, scenario):
    """
    This method will be executed after each scenario.
    You can clean up or reset any global resources here.
    """
    # Add any cleanup or logging for individual scenarios if needed
    logger.info(f"***************************  Scenario {scenario.name} started  **************************************")
    pass

