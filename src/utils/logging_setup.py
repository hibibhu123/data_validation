import logging

def setup_logger(log_file='logs/validation.log'):
    """
    Set up a logger that writes logs to both console and a file.
    Ensures no duplicate logs in the console and file.
    """
    logger = logging.getLogger('ADVF')
    logger.setLevel(logging.INFO)  # Set logging level to INFO (or as needed)

    # Clear any existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)  # You can adjust this level if needed

    # Create a console handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger