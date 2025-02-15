import os
from utils.connection_manager import ConnectionManager
from utils.logging_setup import setup_logger
from utils.spark_setup import create_spark_session

# Initialize the logger
logger = setup_logger()

# Initialize connection manager
connection_manager = ConnectionManager()

#Initialize Spark session
spark_session=create_spark_session()

def normalize_data_type(db_type):
    """ Normalize database-specific data types to a common Spark type and remove extra parentheses. """
    # Handle the case where data type includes parentheses (e.g., IntegerType() vs IntegerType)
    db_type = str(db_type).lower().replace("()", "")
    
    mapping = {
        'char': 'StringType',
        'varchar': 'StringType',
        'text': 'StringType',
        'int': 'IntegerType',
        'integer': 'IntegerType',
        'number': 'IntegerType',
        'float': 'FloatType',
        'double': 'DoubleType',
        'decimal': 'DecimalType',
        'date': 'DateType',
        'datetime': 'TimestampType',
        'timestamp': 'TimestampType',
        'boolean': 'BooleanType'
    }

    for key in mapping:
        if key in db_type:
            return mapping[key]
    return 'StringType'  # default fallback



def get_metadata(location, object_name):
    """ Get metadata (columns and types) for a table or file. """
    logger.info(f"Fetching metadata for {object_name} at {location}")

    # Check if the location is a local file (CSV)
    if location.lower() == "local":
        # Check if the file exists
        if not os.path.exists(object_name):
            logger.error(f"File not found: {object_name}")
            raise FileNotFoundError(f"File not found: {object_name}")

        # Load the file into a Spark DataFrame to infer schema
        df = spark_session.read.csv(object_name, header=True, inferSchema=True)

        # Get column names and types from Spark DataFrame schema
        metadata = [(field.name, str(field.dataType).replace("()", "")) for field in df.schema.fields]
        logger.info(f"Metadata fetched for CSV: {metadata}")
        return metadata

    else:
        # If the location is not "local", it must be an RDBMS
        # Get connection using ConnectionManager
        connection = connection_manager.get_connection(location, object_name)

        if location.lower() == "mysql" or location.lower() == "postgres":
            # For MySQL/Postgres, use DESCRIBE/SHOW COLUMNS
            cursor = connection.cursor()
            cursor.execute(f"DESCRIBE {object_name}")
            result = cursor.fetchall()
            cursor.close()

            # Normalize metadata types
            metadata = [(row[0], normalize_data_type(row[1])) for row in result]

        elif location.lower() == "oracle":
            # Oracle query to get metadata
            cursor = connection.cursor()
            cursor.execute(f"SELECT column_name, data_type FROM all_tab_columns WHERE table_name = '{object_name.upper()}'")
            result = cursor.fetchall()
            cursor.close()

            # Normalize metadata types
            metadata = [(row[0], normalize_data_type(row[1])) for row in result]

        elif location.lower() == "sqlserver":
            # SQL Server query to get metadata
            cursor = connection.cursor()
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{object_name}'")
            result = cursor.fetchall()
            cursor.close()

            # Normalize metadata types
            metadata = [(row[0], normalize_data_type(row[1])) for row in result]

        else:
            logger.error(f"Unsupported location: {location}")
            raise ValueError(f"Unsupported location type: {location}")

        logger.info(f"Metadata fetched: {metadata}")
        return metadata
