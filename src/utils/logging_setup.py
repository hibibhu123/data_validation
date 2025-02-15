import logging
import os

def setup_logger(log_file='logs/validation.log', log_level=logging.INFO):
    """
    Set up the logger to log messages to a file and console.

    Args:
    - log_file (str): Path to the log file.
    - log_level (logging.LEVEL): Logging level (default is INFO).

    Returns:
    - logger (logging.Logger): Configured logger.
    """

    # Create the logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up logger
    logger = logging.getLogger('DataTestAutomation')
    logger.setLevel(log_level)

    # Log to file with overwrite (write mode)
    file_handler = logging.FileHandler(log_file, mode='w')  # Open file in write mode
    file_handler.setLevel(log_level)

    # Format for logs including milliseconds for more accurate timestamps
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                       datefmt='%Y-%m-%d %H:%M:%S')  # Custom date format
    file_handler.setFormatter(file_formatter)

    # Log to console with the same format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                                  datefmt='%Y-%m-%d %H:%M:%S'))  # Apply same formatter for console output

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

