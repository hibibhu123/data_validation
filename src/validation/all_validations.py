from dotenv import load_dotenv
from utils.generate_sql_files import read_sql_from_file
from validation.count_validation import get_row_count
from validation.data_completeness_validation import get_full_data, normalize_data_values
from validation.metadata_validation import get_metadata
from utils.logging_setup import setup_logger


logger = setup_logger()

def perform_validation(validation_type, source_sql, target_sql, context):
    """ Perform the appropriate validation based on the validation type """

    try:
        # Read SQL from files
        source_sql = read_sql_from_file(source_sql)
        target_sql = read_sql_from_file(target_sql)
        logger.info(source_sql)
        logger.info(target_sql)

        if validation_type.lower() == "metadata":
            logger.info(f"Performing metadata validation for source: {context.source_object} and target: {context.target_object}")

            # Get metadata from source and target
            source_metadata = get_metadata(context.source_location, context.source_object)
            target_metadata = get_metadata(context.target_location, context.target_object)

            # Normalize metadata
            source_metadata = [(col_name.lower(), col_type.lower()) for col_name, col_type in source_metadata]
            target_metadata = [(col_name.lower(), col_type.lower()) for col_name, col_type in target_metadata]

            logger.info(f"Source Metadata (first 5 rows): {source_metadata[:5]}")
            logger.info(f"Target Metadata (first 5 rows): {target_metadata[:5]}")

            context.source_metadata = source_metadata
            context.target_metadata = target_metadata

            # Sort metadata for comparison
            sorted_source_metadata = sorted(source_metadata, key=lambda x: x[0].lower())
            sorted_target_metadata = sorted(target_metadata, key=lambda x: x[0].lower())

            # Compare metadata
            if sorted_source_metadata == sorted_target_metadata:
                logger.info("Metadata validation passed: Source and target have the same metadata.")
                return "Metadata validation passed"
            else:
                logger.error("Metadata mismatch found:")
                logger.error(f"Source Metadata: {sorted_source_metadata}")
                logger.error(f"Target Metadata: {sorted_target_metadata}")
                return "Metadata validation failed"

        elif validation_type.lower() == "data count":
            logger.info(f"Performing data count validation with source SQL: {source_sql} and target SQL: {target_sql}")

            # Get row count for both source and target
            source_row_count = get_row_count(source_sql, context.source_location, context.source_object)
            target_row_count = get_row_count(target_sql, context.target_location, context.target_object)

            context.source_row_count = source_row_count
            context.target_row_count = target_row_count

            if source_row_count == target_row_count:
                logger.info(f"Row count validation passed: {source_row_count} rows in both source and target.")
                return "Data count validation passed"
            else:
                logger.error(f"Row count mismatch: Source has {source_row_count}, but target has {target_row_count}.")
                return "Data count validation failed"

        elif validation_type.lower() == "data completeness":
            logger.info(f"Performing data completeness validation with source SQL: {source_sql} and target SQL: {target_sql}")

            # Get full data from source and target
            source_data = get_full_data(source_sql, context.source_location, context.source_object)
            target_data = get_full_data(target_sql, context.target_location, context.target_object)

            # Normalize data values for comparison
            normalized_source_data = normalize_data_values(source_data)
            normalized_target_data = normalize_data_values(target_data)

            context.source_data = normalized_source_data
            context.target_data = normalized_target_data

            # Compare the data completeness
            only_in_source = [item for item in normalized_source_data if item not in normalized_target_data]
            only_in_target = [item for item in normalized_target_data if item not in normalized_source_data]

            if not only_in_source and not only_in_target:
                logger.info("Data completeness validation passed.")
                return "Data completeness validation passed"
            else:
                logger.error(f"Data mismatch! Only in source: {only_in_source[:5]}, Only in target: {only_in_target[:5]}")
                return "Data completeness validation failed"

        else:
            logger.error(f"Unknown validation type: {validation_type}")
            raise ValueError(f"Unknown validation type: {validation_type}")
    
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        return f"{validation_type} validation failed due to error"
