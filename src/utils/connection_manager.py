import os
from dotenv import load_dotenv
import mysql
from utils.logging_setup import setup_logger
from mysql.connector import Error
import cx_Oracle

# Initialize the logger
logger = setup_logger()

# Load environment variables from .env file
load_dotenv()

class ConnectionManager:
    def __init__(self):
        self.connections = {}

    def get_connection(self,location, obj):
        # Create a unique key to identify the connection
        connection_key = f"{location}_{obj}"
        logger.info("Connection key is created " + connection_key)
        # Check if the connection is already established and cached
        if connection_key in self.connections:
            logger.info(f"Reusing existing connection for {connection_key} at {location} for object {obj}")
            return self.connections[connection_key]

        logger.info(f"Creating new connection for {connection_key} at {location} for object {obj}")

        connection = None
        logger.info (location)
        # Create a new connection based on the connection type
        try:
            if location == 'AWS':
                connection = self._connect_to_aws()
                logger.info(f"Successfully connected to AWS for {connection_key}")
            elif location == 'Azure':
                connection = self._connect_to_azure()
                logger.info(f"Successfully connected to Azure for {connection_key}")
            elif location == 'MYSQL':
                connection = self._connect_to_mysql()
                logger.info(f"Successfully connected to RDBMS for {connection_key}")
            elif location == "ORACLE":
                connection = self._connect_to_oracle() 
                logger.info(f"Successfully connected to RDBMS for {connection_key}")   
            elif location == 'LOCAL':
                connection = self._connect_to_local(location, obj)
                logger.info(f"Simulated connection to LOCAL for {connection_key}")
            else:
                # Raise error if the connection type is unsupported
                raise ValueError(f"Unsupported connection type: {location}")

        except Exception as e:
            logger.error(f"Failed to establish connection for {connection_key} due to {str(e)}")
            raise  # Re-raise the exception to propagate it

        # Store the new connection
        self.connections[connection_key] = connection
        return connection

    def _connect_to_aws(self):
        # Simulate AWS connection logic
        logger.debug(f"Connecting to AWS")
        # Implement the actual AWS connection logic here
        return "AWS Connection Object"  # Placeholder for the actual connection object

    def _connect_to_azure(self):
        # Simulate Azure connection logic
        logger.debug(f"Connecting to Azure")
        # Implement the actual Azure connection logic here
        return "Azure Connection Object"  # Placeholder for the actual connection object

    def _connect_to_mysql(self):
        try:
         # Read MySQL connection details from environment variables
            location = os.getenv("MYSQL_HOST") 
            user = os.getenv("MYSQL_USER")          
            password = os.getenv("MYSQL_PASSWORD") 
            
            # Log the connection attempt
            logger.info(f"Attempting to connect to MySQL at location: {location}")

            # Establish the connection
            connection = mysql.connector.connect(
                host=location,
                user=user,
                password=password
                
            )
            # Check if the connection was successful
            if connection.is_connected():
                logger.info(f"Successfully connected to the database at {location}")
                return connection  # Return the actual connection object
            else:
                logger.error("Failed to connect to the database.")
                return None
        
        except Error as e:
            # Handle MySQL connection errors
            logger.error(f"Error while connecting to MySQL: {e}")

    def _connect_to_local(self, location, obj):
        # Simulate LOCAL connection logic (no real connection is needed)

        logger.info(f"Accessing local file: {location}\\{obj}")
        # Since it's local, no connection is actually established. We just log the access.
        return "LOCAL Access Object"  # Placeholder for the actual "connection" or access object
    
    def _connect_to_oracle(self):
        try:
            # Read Oracle connection details from environment variables
            host = os.getenv("ORACLE_HOST")  
            port = os.getenv("ORACLE_PORT") 
            service_name = os.getenv("ORACLE_SERVICE_NAME")  
            user = os.getenv("ORACLE_USER")  
            password = os.getenv("ORACLE_PASSWORD")  

            # Construct Oracle DSN (Data Source Name)
            dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

            # Log the connection attempt
            logger.info(f"Attempting to connect to Oracle at {host}:{port}/{service_name}")

            # Establish the connection
            connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)

            # Check if the connection is successful
            if connection:
                logger.info(f"Successfully connected to the Oracle database at {host}:{port}/{service_name}")
                return connection  # Return the connection object
            else:
                logger.error("Failed to connect to the Oracle database.")
                return None

        except cx_Oracle.DatabaseError as e:
            # Handle Oracle connection errors
            logger.error(f"Error while connecting to Oracle: {e}")
            return None
