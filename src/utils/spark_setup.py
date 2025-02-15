from pyspark.sql import SparkSession
from utils.logging_setup import setup_logger

# Initialize the logger
logger = setup_logger()

# Global variable to store the Spark session
spark_session = None

def create_spark_session():
    global spark_session
    if spark_session is None:
        logger.info("Initializing Spark session...")
        spark_session = SparkSession.builder \
            .appName("DataValidation") \
            .getOrCreate()
    else:
        logger.info("Spark session already initialized.")
    return spark_session