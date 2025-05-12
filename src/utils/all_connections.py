import os
import traceback
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from utils.logging_setup import setup_logger
import cx_Oracle

# Load environment variables from .env file
load_dotenv()

# Initialize the logger
logger = setup_logger()

# Dictionary to store active connections
connections = {}

def _connect_to_mysql(host, user, password):
    logger.info(f"Attempting to connect to MySQL at host: {host}")
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
    except mysql.connector.Error as e:
        logger.error(f"MySQL Error: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        traceback.print_exc()
        return None
    else:
        logger.info("Reached after mysql.connector.connect()")
        if connection.is_connected():
            logger.info(f"Successfully connected to MySQL at {host}")
            return connection
        else:
            logger.error("Failed to connect to MySQL.")
            return None
    finally:
        logger.info("Exiting MySQL connection attempt.")

def _connect_to_oracle(host, port, service_name, user, password):
    try:
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        logger.info(f"Attempting to connect to Oracle at {host}:{port}/{service_name}")

        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)

        if connection:
            logger.info(f"Successfully connected to Oracle at {host}:{port}/{service_name}")
            return connection
        else:
            logger.error("Failed to connect to Oracle.")
            return None

    except cx_Oracle.DatabaseError as e:
        logger.error(f"Error while connecting to Oracle: {e}")
        return None


def _connect_to_aws():
    logger.debug(f"Connecting to AWS")
    # Implement actual AWS connection logic here
    return "AWS Connection Object"  # Placeholder

def _connect_to_azure():
    logger.debug(f"Connecting to Azure")
    # Implement actual Azure connection logic here
    return "Azure Connection Object"  # Placeholder

def _connect_to_local(location, obj):
    logger.info(f"Accessing local file: {location}\\{obj}")
    return "LOCAL Access Object"  # Placeholder for local access

# if __name__ == "__main__":
#     _connect_to_mysql(
#         os.getenv("MYSQL_HOST"),
#         os.getenv("MYSQL_USER"),
#         os.getenv("MYSQL_PASSWORD")
#     )
