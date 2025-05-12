from datetime import date, datetime
import os
from utils.logging_setup import setup_logger
from utils.spark_setup import create_spark_session, spark_session  # Import the global spark_session
from utils.connection_manager import get_connection
from pyspark.sql import Row

# Initialize the logger
logger = setup_logger()

# Initialize connection manager
#connection_manager = ConnectionManager()

#Initialize Spark session
spark_session=create_spark_session()

def get_full_data(sql, location, object_name):
    """
    Executes the SQL query on the source or target system (either a local file or an RDBMS database)
    and returns the full data.

    Args:
        sql (str): The SQL query to execute (e.g., "SELECT * FROM table").
        location (str): The location of the source/target (e.g., "LOCAL", "MYSQL").
        object_name (str): The name of the object (e.g., table name or file path).

    Returns:
        list: A list of tuples representing the fetched data.
    """
    # Check the location type to determine how to process the query
    if location.strip().lower() == "local":
        # If the location is a local file (e.g., CSV, Parquet, etc.)
        logger.info(f"Fetching data from local file {object_name} using SQL: {sql}")
        
        # Load the file into a DataFrame based on the file extension (you can add more extensions if needed)
        if object_name.endswith(".csv"):
            logger.info("CSV file detected, proceeding to load data")
            try:
                # Assuming we're using Spark to load the file (for large datasets)
                df = spark_session.read.option("header", "true").option("encoding", "UTF-8").option("inferSchema", "true").csv(object_name)
                logger.info(f"Data loaded successfully, number of rows: {df.count()}")
                
                # Create a temporary view with the file name (without extension)
                view_name = os.path.splitext(os.path.basename(object_name))[0]
                logger.info(f"Creating temporary view with name: {view_name}")
                df.createOrReplaceTempView(view_name)

                # Execute the SQL query (SELECT * or any other query)
                logger.info(f"Executing SQL query: {sql}")
                data_df = spark_session.sql(sql)  # Execute the SQL query
                data = data_df.collect()  # Collect the result into a list of Row objects
                logger.info(f"Data fetched successfully from local file {object_name}")
                
                # Convert Row objects to tuples
                data = [tuple(row.asDict().values()) for row in data]

                # Check if data is already in tuple format (e.g., from MySQL)
                if isinstance(data, list) and isinstance(data[0], tuple):
                    logger.info("Data is already in tuple format (likely MySQL data). Returning as is.")
                    return data

                # Check if data is a list of Row objects (from Spark), convert it to tuples
                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], Row):
                    normalized_data = [tuple(row.asDict().values()) for row in data]
                    logger.info(f"Normalized Target Data (after conversion): {normalized_data}")
                    return normalized_data

            except Exception as e:
                logger.error(f"Error loading CSV file {object_name}: {e}")
                return []

        else:
            logger.error(f"Unsupported file type: {object_name}")
            return []

    elif location.strip().lower() in ["mysql", "postgres", "sqlserver", "oracle"]:
        # If the location is a relational database (e.g., MySQL, PostgreSQL, etc.)
        logger.info(f"Fetching data for object {object_name} in {location.upper()} database")

        # Fetch the connection using the ConnectionManager
        connection = get_connection(location, object_name)

        # If the connection is None (failed to establish), return
        if connection is None:
            logger.error(f"Failed to establish connection to {location} for object {object_name}.")
            return []

        try:
            # Execute the SQL query and fetch the result
            cursor = connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()  # Fetch all rows of data
            cursor.close()

            # Log the fetched data (for demonstration)
            logger.info(f"Fetched {len(result)} rows from {location.upper()} database {object_name}")
            return result  # Return the full data as a list of tuples

        except Exception as e:
            logger.error(f"Error executing SQL query on {location} for {object_name}: {e}")
            return []

    else:
        # If the location is not recognized, log an error and return an empty list
        logger.error(f"Unsupported location type: {location}")
        return []

def normalize_value(value):
    """
    Converts various data types into a consistent format for comparison:
    - Converts `datetime.date`, `datetime.datetime` to `'YYYY-MM-DD'`
    - Converts `'DD-MMM-YY'` (Oracle style) to `'YYYY-MM-DD'`
    - Converts `800.0` (float) to `800` (integer)
    - Ensures `None` values are handled correctly
    """
    if isinstance(value, (datetime, date)):  
        return value.strftime('%Y-%m-%d')  # Convert date to standard format

    elif isinstance(value, str):
        try:
            # Convert Oracle-style '17-DEC-80' to 'YYYY-MM-DD'
            return datetime.strptime(value, '%d-%b-%y').strftime('%Y-%m-%d')
        except ValueError:
            # Try 'YYYY-MM-DD' format (already correct)
            try:
                return datetime.strptime(value, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                return value  # Return as-is if not a date format

    elif isinstance(value, float) and value.is_integer():  
        return int(value)  # Convert 800.0 to 800
    
    return value  # Return non-date, non-numeric values as-is


def normalize_data_values(data):
    """
    Normalize all data values before comparison.
    Converts dates to 'yyyy-MM-dd' format to ensure uniformity across sources.
    """
    return [tuple(normalize_value(value) for value in row) for row in data]