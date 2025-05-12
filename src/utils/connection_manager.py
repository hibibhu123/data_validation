import os
import sys
import traceback
from dotenv import load_dotenv
import mysql.connector
import cx_Oracle
from utils.all_connections import (
    _connect_to_aws,
    _connect_to_azure,
    _connect_to_local
)
from utils.logging_setup import setup_logger

# Load environment variables from .env file
load_dotenv()

# Initialize the logger
logger = setup_logger()

# Dictionary to store active connections
connections = {}

def get_connection(location, obj):
    # Create a unique key to identify the connection
    connection_key = f"{location}_{obj}"
    logger.info(f"Connection key is created: {connection_key}")

    # Check if the connection is already established and cached
    if connection_key in connections:
        logger.info(f"Reusing existing connection for {connection_key} at {location} for object {obj}")
        return connections[connection_key]

    logger.info(f"Creating new connection for {connection_key} at {location} for object {obj}")
    connection = None

    try:
        if location == 'AWS':
            connection = _connect_to_aws()
            logger.info(f"Successfully connected to AWS for {connection_key}")

        elif location == 'Azure':
            connection = _connect_to_azure()
            logger.info(f"Successfully connected to Azure for {connection_key}")

        elif location == 'MYSQL':
            try:
                host = os.getenv("MYSQL_HOST")
                user = os.getenv("MYSQL_USER")
                password = os.getenv("MYSQL_PASSWORD")
                port = os.getenv("MYSQL_PORT", 3306)

                logger.info(f"MYSQL_HOST: {host}")
                logger.info(f"MYSQL_USER: {user}")
                logger.info(f"MYSQL_PASSWORD: {'SET' if password else 'NOT SET'}")
                logger.info(f"MYSQL_PORT: {port}")
                logger.info("Attempting to connect to MySQL...")

                connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    port=int(port),
                    connection_timeout=10
                )

                logger.info("Connection object created, checking connection status...")

                if connection.is_connected():
                    logger.info(f"Successfully connected to MySQL at {host}:{port}")
                else:
                    logger.error("Connection object created, but not connected to MySQL.")

            except mysql.connector.Error as mysql_err:
                logger.error(f"MySQL connection error: {str(mysql_err)}")
                traceback.print_exc()
                raise

            except Exception as e:
                logger.error(f"Unexpected error during MySQL connection: {str(e)}")
                traceback.print_exc()
                raise

        elif location == 'ORACLE':
            try:
                host = os.getenv("ORACLE_HOST")
                port = os.getenv("ORACLE_PORT")
                service_name = os.getenv("ORACLE_SERVICE_NAME")
                user = os.getenv("ORACLE_USER")
                password = os.getenv("ORACLE_PASSWORD")

                logger.info(f"ORACLE_HOST: {host}")
                logger.info(f"ORACLE_PORT: {port}")
                logger.info(f"ORACLE_SERVICE_NAME: {service_name}")
                logger.info(f"ORACLE_USER: {user}")
                logger.info(f"ORACLE_PASSWORD: {'SET' if password else 'NOT SET'}")

                dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
                connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)

                logger.info(f"Successfully connected to Oracle at {host}:{port}/{service_name}")

            except cx_Oracle.DatabaseError as ora_err:
                logger.error(f"Oracle connection error: {str(ora_err)}")
                traceback.print_exc()
                raise

            except Exception as e:
                logger.error(f"Unexpected error during Oracle connection: {str(e)}")
                traceback.print_exc()
                raise

        elif location == 'LOCAL':
            connection = _connect_to_local(location, obj)
            logger.info(f"Simulated connection to LOCAL for {connection_key}")

        else:
            raise ValueError(f"Unsupported connection type: {location}")

        # Store the new connection
        connections[connection_key] = connection
        return connection

    except Exception as e:
        logger.error(f"Failed to establish connection for {connection_key} due to: {str(e)}")
        traceback.print_exc()
        raise
