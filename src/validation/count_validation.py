import os
from utils.spark_setup import create_spark_session, spark_session  # Import the global spark_session
from utils.logging_setup import setup_logger
from utils.connection_manager import ConnectionManager  # Import the ConnectionManager

# Initialize the logger
logger = setup_logger()

# Initialize spark from spark_setup
spark_session=create_spark_session()  

# Initialize the connection manager instance
connection_manager = ConnectionManager()

def get_row_count(sql_query, location, object_name):
    """
    Executes the SQL query on the source or target system (either Spark for files or RDBMS for databases) 
    and returns the row count.

    Args:
        sql_query (str): The SQL query to execute (e.g., "SELECT COUNT(*) FROM table").
        location (str): The location of the source/target, e.g., "LOCAL", "MYSQL".
        object_name (str): The name of the object (table/file name) to query.

    Returns:
        int: The row count result from executing the SQL query.
    """
    # Check the location type to determine how to process the query
    if location.strip().lower() == "local":
        # If the source/target is a local file (e.g., CSV, Parquet)
        logger.info(f"Processing row count for file {object_name} at location {location}")
        # Load the file into a DataFrame based on the file extension (you can add more extensions if needed)
        if object_name.endswith(".csv"):
            logger.info("CSV file detected, proceeding to load data")
            try:
                df = spark_session.read.option("header", "true").option("encoding", "UTF-8").csv(object_name)
                logger.info(f"Data loaded successfully, row count: {df.count()}")
            except Exception as e:
                logger.error(f"Error loading CSV file: {e}")
        elif object_name.endswith(".parquet"):
            df = spark_session.read.parquet(object_name)
        elif object_name.endswith(".orc"):
            df = spark_session.read.orc(object_name)
        elif object_name.endswith(".avro"):
            df = spark_session.read.format("avro").load(object_name)
        else:
            logger.error(f"Unsupported file type: {object_name}")
            return None
        
      
        # Create a temporary view so that you can run SQL queries on the data
        logger.info(f"Creating temporary view with the name: {object_name}")
        if df is not None:
            row_count = df.count()  # Get the row count
            logger.info(f"Data loaded successfully. Row count: {row_count}")
            if row_count > 0:
                # Create a temporary view using the base name of the file (without path or extension)
                view_name = os.path.splitext(os.path.basename(object_name))[0]  # Extract base name without extension
                logger.info(f"Creating temporary view with the name: {view_name}")
                df.createOrReplaceTempView(view_name)  # Using the extracted file name as the view name
                logger.info(f"Temporary view created for {object_name}")
            else:
                logger.error(f"Data frame for {object_name} is empty. Cannot create temp view.")
        else:
            logger.error(f"Failed to load data into DataFrame for {object_name}")

        logger.info("Data Frame created successfully from file")

        # Execute the SQL query (e.g., COUNT) on the loaded data
        try:
            logger.info(f"Executing SQL query: {sql_query}")
            row_count_df = spark_session.sql(sql_query)
            # Extract the row count (assuming the query returns a single value)
            row_count = row_count_df.collect()[0][0]  # Collect and extract the row count value
            logger.info(f"Row count from file {object_name}: {row_count}")
            return row_count
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return None

    elif location.strip().lower() in ["mysql", "postgres", "sqlserver", "oracle"]:
        # If the source/target is an RDBMS (MySQL, PostgreSQL, SQL Server, Oracle), get the connection from ConnectionManager
        logger.info(f"Processing row count for object {object_name} in {location.upper()} database at location {location}")
        
        # Fetch the connection using the ConnectionManager
        connection = connection_manager.get_connection(location, object_name)
        
        # If the connection is None (failed to establish), return
        if connection is None:
            logger.error(f"Failed to establish connection to {location} for object {object_name}.")
            return None
        
        try:
            # Execute the SQL query and fetch the result
            cursor = connection.cursor()
            cursor.execute(sql_query)
            result = cursor.fetchone()  # Fetch the row count (assuming the query returns a single value)
            row_count = result[0] if result else 0  # If no result, default to 0
            cursor.close()
            logger.info(f"Row count from {location.upper()} database {object_name}: {row_count}")
            return row_count
        
        except Exception as e:
            logger.error(f"Error executing query on {location} for {object_name}: {e}")
            return None

    else:
        # If the location is not recognized, log an error and return None
        logger.error(f"Unsupported location type: {location}")
        return None
