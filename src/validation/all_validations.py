from validation.count_validation import get_row_count
from validation.data_completeness_validation import get_full_data
from validation.metadata_validation import get_metadata
from utils.logging_setup import setup_logger

logger = setup_logger()

def perform_validation(validation_type, source_sql, target_sql, context):
    """ Perform the appropriate validation based on the validation type """

    if validation_type.lower() == "metadata":
        # Metadata validation - compare column names and types
        logger.info(f"Performing metadata validation with source SQL: {source_sql} and target SQL: {target_sql}")
        # Assume the `get_metadata` function fetches column names and data types
        source_metadata = get_metadata(source_sql, context.source_location, context.source_object)
        target_metadata = get_metadata(target_sql, context.target_location, context.target_object)
        context.source_metadata = source_metadata
        context.target_metadata = target_metadata
        
        # Compare metadata (columns and types)
        assert source_metadata == target_metadata, f"Metadata mismatch: {source_metadata} vs {target_metadata}"
        logger.info("Metadata validation passed.")
        return "Metadata validation passed"

    elif validation_type.lower() == "data count":
        # Row count validation - compare number of records
        logger.info(f"Performing data count validation with source SQL: {source_sql} and target SQL: {target_sql}")
        source_row_count = get_row_count(source_sql, context.source_location, context.source_object)
        target_row_count = get_row_count(target_sql, context.target_location, context.target_object)
        context.source_row_count = source_row_count
        context.target_row_count = target_row_count
        # Compare row counts
        if source_row_count == target_row_count:
            logger.info(f"Row count validation passed: Source and target have the same row count: {source_row_count}.")
            return f"Row count validation passed: Source and target have the same row count: {source_row_count}."
        else:
            logger.error(f"Row count mismatch: Source has {source_row_count}, but target has {target_row_count}.")
        return f"Row count mismatch: Source has {source_row_count}, but target has {target_row_count}."

    elif validation_type.lower() == "data completeness":
        # Complete data validation - compare full data between source and target
        logger.info(f"Performing data completeness validation with source SQL: {source_sql} and target SQL: {target_sql}")
        
        # Fetch source and target data
        source_data = get_full_data(source_sql, context.source_location, context.source_object)
        target_data = get_full_data(target_sql, context.target_location, context.target_object)
        context.source_data = source_data
        context.target_data = target_data
        
        # Compare data (all rows)
        # Find differences: data only in source, data only in target
        only_in_source = [item for item in source_data if item not in target_data]
        only_in_target = [item for item in target_data if item not in source_data]
        
        # Log mismatches
        if not only_in_source and not only_in_target:
            logger.info("Data completeness validation passed.")
            return "Data completeness validation passed"
        else:
            if only_in_source:
                logger.info(f"Data present only in source: {only_in_source}")
            if only_in_target:
                logger.info(f"Data present only in target: {only_in_target}")
            
            logger.error("Data completeness validation failed. Mismatches found.")
            return "Data completeness validation failed"

    else:
        logger.error(f"Unknown validation type: {validation_type}")
        raise ValueError(f"Unknown validation type: {validation_type}")
