import logging
import os
from dotenv import load_dotenv

from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data, create_db_engine

load_dotenv(override=True)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

CSV_PATH = os.getenv("CSV_PATH")

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format=("%(asctime)s | " "%(levelname)s | " "%(message)s"),
)


def run_pipeline():
    logging.info("Pipeline started!")

    try:

        # ================
        # Extract
        # ================

        logging.info("Extracting....")
        df = extract_data(CSV_PATH)
        logging.info(f"Extract completed: {len(df)} rows successfully!")

        # ================
        # Transform
        # ================

        logging.info("Transforming....")
        df = transform_data(df)
        logging.info(f"Transform completed: {len(df)} rows successfully!")

        # ================
        # Load
        # ================

        logging.info("Connecting to database....")
        engine = create_db_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
        logging.info("Database connected successfully!")

        logging.info("Loading....")
        new_df = load_data(df, engine)
        logging.info(f"Load completed: {len(new_df)} rows successfully!")

        logging.info("Pipeline completed successfully")

    except Exception as e:
        logging.exception(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
