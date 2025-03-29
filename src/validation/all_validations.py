from validation.count_validation import get_row_count
from validation.data_completeness_validation import get_full_data, normalize_data_values, normalize_value
from validation.metadata_validation import get_metadata
from utils.logging_setup import setup_logger

logger = setup_logger()

def perform_validation(validation_type, source_sql, target_sql, context):
    """ Perform the appropriate validation based on the validation type """
    logger.info("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")

    if validation_type.lower() == "metadata":
        logger.info(f"Performing metadata validation for source: {context.source_object} and target: {context.target_object}")

        source_metadata = get_metadata(context.source_location, context.source_object)
        target_metadata = get_metadata(context.target_location, context.target_object)

        source_metadata = [(col_name.lower(), col_type.lower()) for col_name, col_type in source_metadata]
        target_metadata = [(col_name.lower(), col_type.lower()) for col_name, col_type in target_metadata]

        logger.info(f"Source Metadata (first 5 rows): {source_metadata[:5]}")
        logger.info(f"Target Metadata (first 5 rows): {target_metadata[:5]}")

        context.source_metadata = source_metadata
        context.target_metadata = target_metadata

        sorted_source_metadata = sorted(source_metadata, key=lambda x: x[0].lower())
        sorted_target_metadata = sorted(target_metadata, key=lambda x: x[0].lower())

        if sorted_source_metadata == sorted_target_metadata:
            logger.info("✅ Metadata validation passed: Source and target have the same metadata.")
            return "✅ Metadata validation passed: Source and target have the same metadata"
        else:
            logger.error("❌ Metadata mismatch found:")
            logger.error(f"Source Metadata: {sorted_source_metadata}")
            logger.error(f"Target Metadata: {sorted_target_metadata}")
            return "❌ Metadata mismatch"

    elif validation_type.lower() == "data count":
        logger.info(f"Performing data count validation with source SQL: {source_sql} and target SQL: {target_sql}")

        source_row_count = get_row_count(source_sql, context.source_location, context.source_object)
        target_row_count = get_row_count(target_sql, context.target_location, context.target_object)

        context.source_row_count = source_row_count
        context.target_row_count = target_row_count

        if source_row_count == target_row_count:
            logger.info(f"✅ Row count validation passed: {source_row_count} rows in both source and target.")
            return f"✅ Row count validation passed: {source_row_count} rows in both source and target."
        else:
            logger.error(f"❌ Row count mismatch: Source has {source_row_count}, but target has {target_row_count}.")
            return f"❌ Row count mismatch: Source has {source_row_count}, but target has {target_row_count}."

    elif validation_type.lower() == "data completeness":
        logger.info(f"Performing data completeness validation with source SQL: {source_sql} and target SQL: {target_sql}")

        source_data = get_full_data(source_sql, context.source_location, context.source_object)
        target_data = get_full_data(target_sql, context.target_location, context.target_object)

        normalized_source_data = normalize_data_values(source_data)
        normalized_target_data = normalize_data_values(target_data)

        context.source_data = normalized_source_data
        context.target_data = normalized_target_data

        only_in_source = [item for item in normalized_source_data if item not in normalized_target_data]
        only_in_target = [item for item in normalized_target_data if item not in normalized_source_data]

        if not only_in_source and not only_in_target:
            logger.info("✅ Data completeness validation passed.")
            return "✅ Data completeness validation passed"
        else:
            logger.error(f"❌ Data mismatch! Only in source: {only_in_source[:5]}, Only in target: {only_in_target[:5]}")
            return "❌ Data completeness validation failed"

    else:
        logger.error(f"Unknown validation type: {validation_type}")
        raise ValueError(f"Unknown validation type: {validation_type}")