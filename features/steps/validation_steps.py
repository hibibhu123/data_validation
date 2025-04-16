import os
from behave import given, when, then
from dotenv import load_dotenv
from src.utils.connection_manager import ConnectionManager
from validation.count_validation import get_row_count
from utils.file_handling import generate_feature_file, read_csv_data
from utils.logging_setup import setup_logger
from validation.all_validations import perform_validation

# Initialize the logger
logger = setup_logger()

# Initialize connection manager
connection_manager = ConnectionManager()

# Load environment variables from .env file
load_dotenv()  # This automatically loads the variables defined in the .env file

# Fetch the parameter values from .env
#input_csv_template_path = os.getenv('INPUT_CSV_TEMPLATE_PATH')
#feature_file_path = os.path.join(os.getenv('FEATURE_FILE_PATH'), "validation.feature")

# Call feature file generation funtion here
#generate_feature_file(read_csv_data(input_csv_template_path),feature_file_path)

@given('I connect to the source "{source_object}" in "{source_location}"')
def step_impl_connect_source(context, source_object, source_location):
    # Use the provided source_object and source_location directly from the feature file
    logger.info(f"Connecting to source: {source_object} at {source_location}")
    # Store in context to use later in other steps if needed
    context.source_object = source_object
    context.source_location = source_location
    connection_manager.get_connection(source_location, source_object)

@given('I connect to the target "{target_object}" in "{target_location}"')
def step_impl_connect_target(context, target_object, target_location):
    # Store in context to use later in other steps if needed
    context.target_object = target_object
    context.target_location = target_location

    # Use the target_object and target_location directly from the feature file
    logger.info(f"Connecting to target: {target_object} at {target_location}")
    connection_manager.get_connection(target_location, target_object)

@when('I perform "{validation_type}" validation using source SQL "{source_sql}" and target SQL "{target_sql}"')
def step_impl_validation(context, validation_type, source_sql, target_sql):
    # Store the validation type, source SQL, and target SQL in the context for later use in @then step
    context.validation_type = validation_type
    context.source_sql = source_sql
    context.target_sql = target_sql
    
    # Call the helper function to perform the validation
    validation_result = perform_validation(validation_type, source_sql, target_sql, context)
    
    # Store the result in context (if needed) for use in the next step
    context.validation_result = validation_result

@then('the "{validation_type}" validation between source and target is successful')
def step_impl_validation_success(context, validation_type):
    # Logic to check if validation was successful based on validation_type
    logger.info(f"Checking if {validation_type} validation between source and target is successful.")
    
    # Use the validation result stored in context from the @when step
    validation_result = context.validation_result

    logger.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    logger.info(validation_result)
      
    # Assert that the validation was successful
    assert "passed" in validation_result, f"{validation_type} validation failed: {validation_result}"
    logger.info(f"{validation_type} validation successful: {validation_result}")
